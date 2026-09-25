import os
import json
import base64
import re
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(f"GEMINI_API_KEY not found in {ENV_FILE}")

GEMINI_API_KEY = GEMINI_API_KEY.strip()

# Gemini client
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# Use an ordered list so a temporary outage/overload on one model
# does not stop the entire PackCheck inspection.
MODEL_NAMES = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-3.8-flash",
]

# ============================================================
# SUPPORTED IMAGE FORMATS
# ============================================================

SUPPORTED_MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


# ============================================================
# EMPTY RESULT
# ============================================================

EMPTY_RESULT = {
    "category": None,
    "fssai_applicable": False,
    "bis_applicable": False,

    "product_name": None,
    "brand": None,

    "manufacturer": None,
    "manufacturer_address": None,

    "fssai_number": None,

    "is_number": None,
    "bis_license_number": None,

    "mrp": None,
    "net_quantity": None,

    "batch_number": None,

    "manufacturing_date": None,
    "expiry_date": None,
    "best_before": None,

    "country_of_origin": None,
    "consumer_care": None,

    "ingredients": None,

    "allergens": [],
    "warnings": [],
    "storage_conditions": [],

    "barcode_or_gtin": None,

    "additional_declarations": [],

    "confidence": {},

    "extraction_notes": [],
}


# ============================================================
# GEMINI PROMPT
# ============================================================

PROMPT = r"""
You are PackCheck AI, an evidence-extraction system for packaged
commodities in India.

You may receive ONE OR MULTIPLE photographs of the SAME physical
product/package.

IMPORTANT:
Treat all supplied images as different views/sides of the SAME package.

Combine information across all images.

For example:
- Image 1 may contain the front label.
- Image 2 may contain the back label.
- Image 3 may contain manufacturer/address information.
- Image 4 may contain MRP, batch number, date, barcode or regulatory marks.

Analyze ALL supplied images before producing the final JSON.

Extract ONLY information that is actually visible in at least one
supplied image.

Never invent, infer, complete, or guess missing values.

If a field is visible in one image, use it even if it is not visible
in the other images.

If the same field appears in multiple images and the values differ,
prefer the clearest visible value and mention the discrepancy in
extraction_notes.

FIRST identify the product category.

Use one of:

- Food / Beverage
- Cosmetic
- Personal Care
- Household Product
- Electrical Product
- Toy
- Textile
- Other

IMPORTANT EXTRACTION RULES:

- FSSAI number is relevant to food/beverage.
- Do not invent an FSSAI number for non-food products.
- If an Indian Standard appears, extract the FULL visible IS number.
  Example:
  "IS 13252 (Part 1): 2010"
- If a BIS licence/registration number appears, extract it exactly.
  Example:
  "R-91005576"
- An IS number is NOT proof of BIS certification.
- BIS applicability can be true when BIS/ISI/IS marking, a BIS
  licence/registration number, or clearly applicable BIS evidence
  is visible.
- Do not claim BIS certification merely because an IS number exists.
- A product may have BOTH FSSAI and BIS evidence.
- Keep extra markings, electrical ratings, model numbers, standards,
  warnings and certifications in additional_declarations.
- Distinguish product name, brand and manufacturer.
- Read MRP only when clearly associated with MRP / Maximum Retail Price.
- Read net quantity only when clearly associated with quantity,
  weight or volume.
- Batch/lot must contain the actual identifier, not merely the label
  word "Batch" or "Lot".
- Distinguish manufacturing/packing date from expiry,
  use-by and best-before.
- Extract manufacturer/packer/importer address only if visible.
- Extract consumer-care information only if visible.
- Extract ingredients/allergens/warnings/storage only when actually
  visible.
- Extract barcode/GTIN only when actually visible/readable.
- Do not manufacture a barcode number from an image where the digits
  cannot be read.
- Preserve exact visible wording where practical.
- Do not assume information from the product brand or known product.
- Missing information must remain null or an empty list.

Return ONLY valid JSON matching this schema:

{
  "category": null,
  "fssai_applicable": false,
  "bis_applicable": false,

  "product_name": null,
  "brand": null,

  "manufacturer": null,
  "manufacturer_address": null,

  "fssai_number": null,

  "is_number": null,
  "bis_license_number": null,

  "mrp": null,
  "net_quantity": null,

  "batch_number": null,

  "manufacturing_date": null,
  "expiry_date": null,
  "best_before": null,

  "country_of_origin": null,
  "consumer_care": null,

  "ingredients": null,

  "allergens": [],
  "warnings": [],
  "storage_conditions": [],

  "barcode_or_gtin": null,

  "additional_declarations": [],

  "confidence": {},

  "extraction_notes": []
}
"""


# ============================================================
# IMAGE -> BASE64
# ============================================================

def image_to_base64(image_path):
    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    mime_type = SUPPORTED_MIME.get(
        path.suffix.lower()
    )

    if not mime_type:
        raise ValueError(
            "Unsupported image format. "
            "Use JPG, JPEG, PNG or WEBP."
        )

    return (
        base64.b64encode(
            path.read_bytes()
        ).decode("utf-8"),
        mime_type,
    )


# ============================================================
# JSON CLEANING
# ============================================================

def _coerce_json(text):
    text = str(text or "").strip()

    # Remove markdown JSON fences if Gemini adds them.
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.I,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    return json.loads(text)


# ============================================================
# NORMALISE
# ============================================================

def _normalise(value, fallback=None):
    if value is None or value == "":
        return fallback

    return value


# ============================================================
# DECLARATION TEXT
# ============================================================

def _declaration_text(declarations):
    parts = []

    for item in declarations or []:

        if isinstance(item, dict):
            parts.extend(
                str(v)
                for v in item.values()
                if v is not None
            )

        else:
            parts.append(
                str(item)
            )

    return " ".join(parts)


# ============================================================
# REGULATORY FIELD RECOVERY
# ============================================================

def _promote_regulatory_fields(result):

    declarations = (
        result.get("additional_declarations")
        or []
    )

    text = _declaration_text(
        declarations
    )

    # --------------------------------------------------------
    # Recover IS number
    # --------------------------------------------------------

    if not result.get("is_number"):

        match = re.search(
            r"\bIS\s+\d+(?:\s*\(Part\s*\d+\))?(?:\s*:\s*\d{4})?",
            text,
            re.I,
        )

        if match:
            result["is_number"] = (
                match.group(0).strip()
            )

    # --------------------------------------------------------
    # Recover BIS licence / registration
    # --------------------------------------------------------

    if not result.get("bis_license_number"):

        patterns = [

            r"BIS\s*(?:Registration|Licence|License)"
            r"\s*(?:No\.?|Number)?"
            r"\s*[:\-]?\s*"
            r"([A-Z0-9][A-Z0-9/_\-]{5,})",

            r"(?:Registration|Licence|License)"
            r"\s*(?:No\.?|Number)?"
            r"\s*[:\-]?\s*"
            r"([A-Z0-9][A-Z0-9/_\-]{5,})",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.I,
            )

            if match:

                result[
                    "bis_license_number"
                ] = match.group(1).strip()

                break

    # --------------------------------------------------------
    # BIS applicability
    # --------------------------------------------------------

    if (
        result.get("is_number")
        or result.get("bis_license_number")
    ):
        result["bis_applicable"] = True

    # --------------------------------------------------------
    # FSSAI applicability
    # --------------------------------------------------------

    category = str(
        result.get("category")
        or ""
    ).lower()

    if (
        "food" in category
        or "beverage" in category
    ):
        result["fssai_applicable"] = True

    elif not result.get("fssai_number"):
        result["fssai_applicable"] = False

    # --------------------------------------------------------
    # Ensure list fields are actually lists
    # --------------------------------------------------------

    if not isinstance(
        result.get("allergens"),
        list,
    ):
        result["allergens"] = (
            [str(result["allergens"])]
            if result.get("allergens")
            else []
        )

    if not isinstance(
        result.get("warnings"),
        list,
    ):
        result["warnings"] = (
            [str(result["warnings"])]
            if result.get("warnings")
            else []
        )

    if not isinstance(
        result.get("storage_conditions"),
        list,
    ):
        result["storage_conditions"] = (
            [str(result["storage_conditions"])]
            if result.get("storage_conditions")
            else []
        )

    if not isinstance(
        result.get("additional_declarations"),
        list,
    ):
        result["additional_declarations"] = (
            [str(result["additional_declarations"])]
            if result.get("additional_declarations")
            else []
        )

    # --------------------------------------------------------
    # Do not carry FSSAI into clearly non-food products
    # --------------------------------------------------------

    if (
        not result.get("fssai_applicable")
        and not result.get("fssai_number")
    ):
        result["fssai_number"] = None

    return result


# ============================================================
# CLEAN RESULT
# ============================================================

def _clean(raw):

    result = dict(
        EMPTY_RESULT
    )

    if isinstance(raw, dict):

        for key in result:

            if key in raw:
                result[key] = raw[key]

    result = _promote_regulatory_fields(
        result
    )

    result["extraction_notes"] = list(
        result.get("extraction_notes")
        or []
    )

    result["extraction_notes"].append(
        "Google Gemini Vision is the only extraction engine used."
    )

    result["extraction_notes"].append(
        "Fields are extracted only from information visually available in the supplied image(s)."
    )

    result["extraction_notes"].append(
        "All supplied images were treated as different views of the same physical package."
    )

    result["extraction_notes"].append(
        "IS numbers and BIS registration/licence identifiers are evidence fields; they are not treated as proof of certification."
    )

    return result


# ============================================================
# GEMINI REQUEST
# ============================================================

def _call_gemini(image_paths, model_name):

    contents = []

    # --------------------------------------------------------
    # Add ALL images to the same Gemini request
    # --------------------------------------------------------

    for image_path in image_paths:

        image_data, mime_type = image_to_base64(
            image_path
        )

        contents.append(
            types.Part.from_bytes(
                data=base64.b64decode(
                    image_data
                ),
                mime_type=mime_type,
            )
        )

    # Prompt comes AFTER all package images.
    contents.append(PROMPT)

    response = gemini_client.models.generate_content(
        model=model_name,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0,
        ),
    )

    return _clean(
        _coerce_json(
            response.text
        )
    )


# ============================================================
# PUBLIC FUNCTION
# ============================================================

def extract_label(image_path):

    """
    Extract package information using Gemini Vision.

    Accepts either:

        extract_label("front.jpg")

    OR:

        extract_label([
            "front.jpg",
            "back.jpg",
            "side.jpg"
        ])

    All images are sent together in ONE Gemini request and are
    treated as different views of the SAME package.
    """

    # --------------------------------------------------------
    # Support old single-image calls
    # --------------------------------------------------------

    if isinstance(
        image_path,
        (str, Path)
    ):

        image_paths = [
            str(image_path)
        ]

    elif isinstance(
        image_path,
        (list, tuple)
    ):

        image_paths = [
            str(path)
            for path in image_path
        ]

    else:

        raise TypeError(
            "image_path must be a file path or a list/tuple of file paths."
        )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    if not image_paths:

        raise ValueError(
            "No images were supplied."
        )

    if len(image_paths) > 10:

        raise ValueError(
            "Please upload a maximum of 10 images per inspection."
        )

    last_error = None
    errors = []

    # --------------------------------------------------------
    # Gemini request with model fallback
    #
    # A 503/429 is normally temporary. Retry the current model
    # once, then move to the next model in MODEL_NAMES.
    # --------------------------------------------------------

    for model_name in MODEL_NAMES:

        for attempt in range(2):

            try:
                result = _call_gemini(
                    image_paths,
                    model_name,
                )

                # Add image count to notes.
                result["extraction_notes"].append(
                    f"Gemini Vision analyzed {len(image_paths)} package image(s) together."
                )

                if len(image_paths) > 1:
                    result["extraction_notes"].append(
                        "Information from different package views was combined into one inspection result."
                    )

                if model_name != MODEL_NAMES[0]:
                    result["extraction_notes"].append(
                        f"Gemini Vision used fallback model: {model_name}."
                    )

                if attempt:
                    result["extraction_notes"].append(
                        "Gemini Vision succeeded after a temporary API error retry."
                    )

                return result

            except Exception as exc:

                last_error = exc
                error_text = str(exc)
                errors.append(
                    f"{model_name} attempt {attempt + 1}: {error_text}"
                )

                # Only retry/fallback on the transient conditions that
                # commonly indicate service overload/rate limiting.
                transient = (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text.upper()
                    or "429" in error_text
                    or "RESOURCE_EXHAUSTED" in error_text.upper()
                    or "TOO MANY REQUESTS" in error_text.upper()
                )

                if not transient:
                    break

    raise RuntimeError(
        "Gemini Vision extraction failed after trying all configured "
        f"models. Last error: {last_error}\n\n"
        "Attempts:\n" + "\n".join(errors)
    )
