# ============================================================
# PACKCHECK AI — COMPLIANCE ENGINE
# Applicability-aware packaged commodity compliance screening
# ============================================================

import re
from typing import Any, Dict, List


RULE_VERSION = "PackCheck-LM-2011-v2"
# ============================================================
# VERIFIED REQUIREMENT METADATA
# ============================================================
REQUIREMENT_METADATA = {
    "Product Name": {"requirement": "Common / generic name of the commodity", "legal_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 — Rule 6", "recommended_action": "Verify the commodity name on the package."},
    "Manufacturer / Packer / Importer": {"requirement": "Name and address of manufacturer / packer / importer", "legal_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 — Rule 6", "recommended_action": "Verify the responsible business entity details."},
    "Manufacturer Address": {"requirement": "Address of manufacturer / packer / importer", "legal_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 — Rule 6", "recommended_action": "Verify the declared address on the package."},
    "MRP": {"requirement": "Retail Sale Price / Maximum Retail Price (MRP)", "legal_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 — Rule 6", "recommended_action": "Verify the MRP declaration on the package."},
    "Net Quantity": {"requirement": "Net quantity of the commodity", "legal_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 — Rule 6", "recommended_action": "Verify the quantity and its unit on the package."},
    "Batch / Lot Number": {"requirement": "Batch / lot identification where applicable", "legal_reference": "Legal Metrology / applicable product-specific requirements", "recommended_action": "Confirm whether the requirement applies to this commodity and verify the batch/lot declaration."},
    "Manufacturing / Packing Date": {"requirement": "Month and year of manufacture / packing where applicable", "legal_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 — Rule 6", "recommended_action": "Verify the manufacturing / packing date on the package."},
    "Expiry / Best Before": {"requirement": "Expiry / best-before information where applicable", "legal_reference": "Applicable product-specific requirements", "recommended_action": "Confirm applicability and verify the expiry / best-before declaration."},
    "Ingredients": {"requirement": "Ingredient information where applicable", "legal_reference": "Applicable food labelling requirements", "recommended_action": "Confirm applicability and verify the ingredient declaration."},
    "FSSAI License / Registration": {"requirement": "FSSAI licence / registration identification where applicable", "legal_reference": "Applicable FSSAI requirements", "recommended_action": "Verify the licence / registration through the official FSSAI/FoSCoS pathway."},
    "Country of Origin": {"requirement": "Country of origin declaration where applicable", "legal_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 — Rule 6", "recommended_action": "Verify the country-of-origin declaration."},
    "Consumer Care Details": {"requirement": "Consumer care / contact details", "legal_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 — Rule 6", "recommended_action": "Verify the consumer-care contact information."},
    "Indian Standard (IS) Number": {"requirement": "Applicable Indian Standard (IS) identification", "legal_reference": "Applicable BIS / Indian Standard requirements", "recommended_action": "Confirm whether a BIS standard applies and verify the applicable IS identification."},
    "BIS License Number": {"requirement": "BIS certification / licence identification where applicable", "legal_reference": "Applicable BIS certification requirements", "recommended_action": "Verify the BIS licence through the official BIS pathway."},
    "Label Presentation": {"requirement": "Legibility and prominence of required declarations", "legal_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 — Rule 9(1)(a)", "recommended_action": "Inspect the physical package for legibility and prominence."},
    "Additional Declarations": {"requirement": "Applicable additional product-specific declarations", "legal_reference": "Applicable product-specific requirements", "recommended_action": "Confirm which additional declarations apply to this commodity."},
    "Product Category": {"requirement": "Product-category classification used for applicability decisions", "legal_reference": "PackCheck applicability classification", "recommended_action": "Review the detected category if the applicability decision appears incorrect."},
    "Product-Specific Certification / Requirements": {"requirement": "Additional technical, safety or certification requirements", "legal_reference": "Applicable product-specific requirements", "recommended_action": "Confirm the applicable regulator, standard or certification requirement."},
}




# ============================================================
# HELPERS
# ============================================================

def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return ", ".join(str(x) for x in value if x)
    return str(value).strip()


def _lower(value: Any) -> str:
    return _text(value).lower()


def _has(value: Any) -> bool:
    return bool(_text(value))


def _result(
    field: str,
    status: str,
    value: Any,
    message: str,
    rule: str,
    evidence: str = "",
    applicability: str = "Applicable",
    check_type: str = "presence",
    requirement: str = "",
    legal_reference: str = "",
    recommended_action: str = "",
) -> Dict[str, Any]:
    """Create a standardized, frontend-ready compliance result."""
    metadata = REQUIREMENT_METADATA.get(field, {})
    requirement = requirement or metadata.get("requirement", "")
    legal_reference = legal_reference or metadata.get("legal_reference", rule)
    recommended_action = recommended_action or metadata.get(
        "recommended_action", "Review the package and verify the applicable requirement."
    )
    return {
        "field": field,
        "status": status,
        "value": value,
        "message": message,
        "rule": rule,
        "requirement": requirement,
        "legal_reference": legal_reference,
        "evidence": evidence,
        "recommended_action": recommended_action,
        "applicability": applicability,
        "check_type": check_type,
    }

# ============================================================
# CATEGORY / APPLICABILITY
# ============================================================

def category_flags(category: Any) -> Dict[str, bool]:
    c = _lower(category)

    return {
        "food": any(x in c for x in [
            "food",
            "beverage",
            "drink",
            "packaged drinking water",
        ]),
        "cosmetic": any(x in c for x in [
            "cosmetic",
            "personal care",
            "beauty",
            "skin care",
            "hair care",
        ]),
        "electrical": any(x in c for x in [
            "electrical",
            "electronic",
            "appliance",
            "equipment",
        ]),
        "toy": "toy" in c,
        "battery": "battery" in c,
        "textile": "textile" in c,
        "chemical": any(x in c for x in [
            "chemical",
            "cleaning",
            "detergent",
        ]),
        "agricultural": any(x in c for x in [
            "agricultural",
            "fertilizer",
            "pesticide",
            "seed",
        ]),
        "automotive": any(x in c for x in [
            "automotive",
            "automobile",
            "vehicle",
            "motor",
        ]),
    }


# ============================================================
# BASIC FIELD VALIDATORS
# ============================================================

def validate_product_name(data: Dict[str, Any]) -> Dict[str, Any]:
    value = data.get("product_name")

    if _has(value):
        return _result(
            "Product Name",
            "PASS",
            value,
            "Product name detected.",
            "Legal Metrology (Packaged Commodities) Rules, 2011",
            str(value),
        )

    return _result(
        "Product Name",
        "MISSING",
        value,
        "Product name was not detected.",
        "Legal Metrology (Packaged Commodities) Rules, 2011",
    )


def validate_category(data: Dict[str, Any]) -> Dict[str, Any]:
    value = data.get("category")

    if _has(value):
        return _result(
            "Product Category",
            "PASS",
            value,
            "Product category detected.",
            "PackCheck applicability classification",
            str(value),
        )

    return _result(
        "Product Category",
        "REVIEW",
        value,
        "Product category could not be confidently determined.",
        "PackCheck applicability classification",
    )


def validate_manufacturer(data: Dict[str, Any]) -> Dict[str, Any]:
    value = data.get("manufacturer")

    if _has(value):
        return _result(
            "Manufacturer / Packer / Importer",
            "PASS",
            value,
            "Responsible business entity detected.",
            "Legal Metrology (Packaged Commodities) Rules, 2011",
            str(value),
        )

    return _result(
        "Manufacturer / Packer / Importer",
        "MISSING",
        value,
        "Manufacturer, packer or importer information was not detected.",
        "Legal Metrology (Packaged Commodities) Rules, 2011",
    )


def validate_address(data: Dict[str, Any]) -> Dict[str, Any]:
    value = data.get("manufacturer_address")

    if _has(value):
        return _result(
            "Manufacturer Address",
            "PASS",
            value,
            "Address detected.",
            "Legal Metrology (Packaged Commodities) Rules, 2011",
            str(value),
        )

    return _result(
        "Manufacturer Address",
        "MISSING",
        value,
        "Manufacturer / packer / importer address was not detected.",
        "Legal Metrology (Packaged Commodities) Rules, 2011",
    )


# ============================================================
# MRP
# ============================================================

def validate_mrp(data: Dict[str, Any]) -> Dict[str, Any]:
    value = data.get("mrp")

    if not _has(value):
        return _result(
            "MRP",
            "MISSING",
            value,
            "Maximum Retail Price was not detected.",
            "Legal Metrology (Packaged Commodities) Rules, 2011",
        )

    raw = _text(value)

    # Accept common formats such as:
    # ₹100
    # ₹ 100
    # Rs. 100
    # Rs 100
    # INR 100
    pattern = (
        r"(?:₹|rs\.?|inr)\s*"
        r"[\d,]+"
        r"(?:\.\d{1,2})?"
    )

    if re.search(pattern, raw, re.IGNORECASE):
        return _result(
            "MRP",
            "PASS",
            value,
            "MRP detected with a recognizable currency/value format.",
            "Legal Metrology (Packaged Commodities) Rules, 2011",
            raw,
            check_type="format",
        )

    # If Gemini extracted only a numeric value, do not automatically
    # call it missing. It needs inspector review for presentation format.
    if re.search(r"[\d,]+(?:\.\d{1,2})?", raw):
        return _result(
            "MRP",
            "REVIEW",
            value,
            "MRP value detected, but the complete statutory presentation could not be confirmed from the image.",
            "Legal Metrology (Packaged Commodities) Rules, 2011",
            raw,
            check_type="format",
        )

    return _result(
        "MRP",
        "REVIEW",
        value,
        "MRP information was detected but its format could not be validated.",
        "Legal Metrology (Packaged Commodities) Rules, 2011",
        raw,
        check_type="format",
    )


# ============================================================
# NET QUANTITY
# ============================================================

def validate_net_quantity(data: Dict[str, Any]) -> Dict[str, Any]:
    value = data.get("net_quantity")

    if not _has(value):
        return _result(
            "Net Quantity",
            "MISSING",
            value,
            "Net quantity was not detected.",
            "Legal Metrology (Packaged Commodities) Rules, 2011",
        )

    raw = _text(value)

    pattern = (
        r"\d+(?:\.\d+)?\s*"
        r"(?:kg|g|mg|l|litre|liter|ml|mL|millilitre|milliliter)"
        r"\b"
    )

    if re.search(pattern, raw, re.IGNORECASE):
        return _result(
            "Net Quantity",
            "PASS",
            value,
            "Net quantity detected with a recognizable unit.",
            "Legal Metrology (Packaged Commodities) Rules, 2011",
            raw,
            check_type="format",
        )

    return _result(
        "Net Quantity",
        "REVIEW",
        value,
        "Net quantity was detected, but its unit/presentation requires review.",
        "Legal Metrology (Packaged Commodities) Rules, 2011",
        raw,
        check_type="format",
    )


# ============================================================
# BATCH
# ============================================================

def validate_batch(data: Dict[str, Any]) -> Dict[str, Any]:
    value = data.get("batch_number")

    if _has(value):
        return _result(
            "Batch / Lot Number",
            "PASS",
            value,
            "Batch or lot identification detected.",
            "Legal Metrology / applicable product-specific requirements",
            str(value),
        )

    return _result(
        "Batch / Lot Number",
        "REVIEW",
        value,
        "Batch or lot information was not detected. Applicability may depend on product category.",
        "Legal Metrology / applicable product-specific requirements",
    )


# ============================================================
# DATES
# ============================================================

def validate_manufacturing_date(data: Dict[str, Any]) -> Dict[str, Any]:
    value = data.get("manufacturing_date")

    if _has(value):
        return _result(
            "Manufacturing / Packing Date",
            "PASS",
            value,
            "Manufacturing or packing date detected.",
            "Applicable packaged commodity requirements",
            str(value),
        )

    return _result(
        "Manufacturing / Packing Date",
        "REVIEW",
        value,
        "Manufacturing / packing date was not detected.",
        "Applicable packaged commodity requirements",
    )


def validate_expiry(data: Dict[str, Any]) -> Dict[str, Any]:
    expiry = data.get("expiry_date")
    best_before = data.get("best_before")

    if _has(expiry) or _has(best_before):
        value = expiry if _has(expiry) else best_before

        return _result(
            "Expiry / Best Before",
            "PASS",
            value,
            "Expiry or best-before information detected.",
            "Applicable product-specific requirements",
            str(value),
        )

    return _result(
        "Expiry / Best Before",
        "REVIEW",
        "",
        "Expiry or best-before information was not detected.",
        "Applicable product-specific requirements",
    )


# ============================================================
# FOOD
# ============================================================

def validate_ingredients(data: Dict[str, Any]) -> Dict[str, Any]:
    value = data.get("ingredients")

    if _has(value):
        return _result(
            "Ingredients",
            "PASS",
            value,
            "Ingredient information detected.",
            "Applicable food labelling requirements",
            str(value),
        )

    return _result(
        "Ingredients",
        "REVIEW",
        value,
        "Ingredients were not detected. Confirm applicability and visibility on the package.",
        "Applicable food labelling requirements",
    )


def validate_fssai(data: Dict[str, Any]) -> Dict[str, Any]:
    value = data.get("fssai_number")

    if _has(value):
        return _result(
            "FSSAI License / Registration",
            "PASS",
            value,
            "FSSAI number detected. Official FoSCoS verification should be performed.",
            "Applicable FSSAI requirements",
            str(value),
            check_type="official_verification",
        )

    return _result(
        "FSSAI License / Registration",
        "MISSING",
        value,
        "FSSAI number was not detected.",
        "Applicable FSSAI requirements",
        check_type="official_verification",
    )


# ============================================================
# COUNTRY OF ORIGIN
# ============================================================

def validate_country(data: Dict[str, Any]) -> Dict[str, Any]:
    value = data.get("country_of_origin")

    if _has(value):
        return _result(
            "Country of Origin",
            "PASS",
            value,
            "Country-of-origin information detected.",
            "Legal Metrology (Packaged Commodities) Rules, 2011",
            str(value),
        )

    return _result(
        "Country of Origin",
        "REVIEW",
        value,
        "Country-of-origin information was not detected.",
        "Legal Metrology (Packaged Commodities) Rules, 2011",
    )


# ============================================================
# CONSUMER CARE
# ============================================================

def validate_consumer_care(data: Dict[str, Any]) -> Dict[str, Any]:
    value = data.get("consumer_care")

    if _has(value):
        return _result(
            "Consumer Care Details",
            "PASS",
            value,
            "Consumer care/contact information detected.",
            "Legal Metrology (Packaged Commodities) Rules, 2011",
            str(value),
        )

    return _result(
        "Consumer Care Details",
        "REVIEW",
        value,
        "Consumer care/contact information was not detected.",
        "Legal Metrology (Packaged Commodities) Rules, 2011",
    )


# ============================================================
# BIS
# ============================================================

def validate_is_number(data: Dict[str, Any]) -> Dict[str, Any]:
    value = data.get("is_number")

    if _has(value):
        return _result(
            "Indian Standard (IS) Number",
            "PASS",
            value,
            "IS number detected. This does not by itself prove BIS certification.",
            "Applicable BIS / Indian Standard requirements",
            str(value),
            check_type="official_verification",
        )

    return _result(
        "Indian Standard (IS) Number",
        "REVIEW",
        value,
        "No IS number was detected. Confirm whether a BIS standard is applicable.",
        "Applicable BIS / Indian Standard requirements",
    )


def validate_bis_license(data: Dict[str, Any]) -> Dict[str, Any]:
    value = data.get("bis_license_number")

    if _has(value):
        return _result(
            "BIS License Number",
            "PASS",
            value,
            "BIS license number detected. Official BIS verification should be performed.",
            "Applicable BIS certification requirements",
            str(value),
            check_type="official_verification",
        )

    return _result(
        "BIS License Number",
        "REVIEW",
        value,
        "BIS license number was not detected. Official verification may be required.",
        "Applicable BIS certification requirements",
        check_type="official_verification",
    )


# ============================================================
# FORMAT / PRESENTATION
# ============================================================

def validate_format_observation(
    observation: Dict[str, Any]
) -> Dict[str, Any]:

    declaration = _text(observation.get("declaration"))
    visible_text = _text(observation.get("visible_text"))

    location = _text(
        observation.get("location")
        or observation.get("placement")
    )

    visibility = _lower(observation.get("visibility"))
    readability = _lower(observation.get("readability"))
    font_assessment = _lower(
        observation.get("font_size_assessment")
    )
    evidence = _text(observation.get("evidence"))

    # We do NOT claim exact statutory font-size compliance from
    # an ordinary photograph without physical scale/calibration.
    if font_assessment in {
        "measured",
        "verified",
        "compliant",
    }:
        status = "PASS"
        message = (
            "Presentation evidence indicates the declaration is "
            "appropriately presented."
        )
    elif (
        visibility in {"clear", "visible", "good"}
        and readability in {"clear", "readable", "good"}
        and location
    ):
        status = "REVIEW"
        message = (
            "Declaration appears visible/readable, but exact statutory "
            "presentation measurements require verification."
        )
    else:
        status = "REVIEW"
        message = (
            "Presentation characteristics require inspector review."
        )

    return _result(
        declaration or "Label Presentation",
        status,
        visible_text,
        message,
        "Applicable declaration presentation requirements",
        evidence,
        check_type="presentation",
        legal_reference="Legal Metrology (Packaged Commodities) Rules, 2011 — Rule 9(1)(a)",
    )


def add_format_checks(
    checks: List[Dict[str, Any]],
    data: Dict[str, Any],
) -> None:

    observations = data.get("format_observations")

    if not isinstance(observations, list):
        observations = []

    if not observations:
        checks.append(
            _result(
                "Label Presentation",
                "REVIEW",
                "",
                (
                    "No structured presentation observations were "
                    "available. Exact font size, placement and visibility "
                    "should be reviewed by an inspector."
                ),
                "Applicable declaration presentation requirements",
                check_type="presentation",
                legal_reference="Legal Metrology (Packaged Commodities) Rules, 2011 — Rule 9(1)(a)",
            )
        )
        return

    for observation in observations:
        if isinstance(observation, dict):
            checks.append(
                validate_format_observation(observation)
            )


# ============================================================
# ADDITIONAL DECLARATIONS
# ============================================================

def validate_additional_declarations(
    data: Dict[str, Any]
) -> Dict[str, Any]:

    value = data.get("additional_declarations")

    if isinstance(value, list):
        items = [str(x).strip() for x in value if str(x).strip()]
    elif _has(value):
        items = [_text(value)]
    else:
        items = []

    if items:
        return _result(
            "Additional Declarations",
            "PASS",
            items,
            f"{len(items)} additional declaration(s) detected.",
            "Applicable product-specific requirements",
            " | ".join(items),
        )

    return _result(
        "Additional Declarations",
        "REVIEW",
        [],
        "No additional declarations were detected.",
        "Applicable product-specific requirements",
    )


# ============================================================
# OVERALL COMPLIANCE
# ============================================================

def _overall_status(checks: List[Dict[str, Any]]) -> str:

    statuses = {c.get("status") for c in checks}

    if "MISSING" in statuses:
        return "REVIEW"

    if "MISMATCH" in statuses:
        return "REVIEW"

    if "REVIEW" in statuses:
        return "REVIEW"

    return "PASS"


# ============================================================
# EXPLANATION HELPERS
# ============================================================

def explain_check(check: Dict[str, Any]) -> Dict[str, Any]:
    """Return a single check in a UI-friendly explanation format."""
    return {
        "title": check.get("field", "Compliance Check"),
        "status": check.get("status", "REVIEW"),
        "requirement": check.get("requirement", ""),
        "legal_reference": check.get("legal_reference") or check.get("rule", ""),
        "why_flagged": check.get("message", ""),
        "evidence": check.get("evidence", ""),
        "recommended_action": check.get("recommended_action", ""),
    }


# ============================================================
# MAIN ENGINE
# ============================================================

def check_compliance(data: Dict[str, Any]) -> Dict[str, Any]:

    if not isinstance(data, dict):
        return {
            "overall_status": "REVIEW",
            "checks": [],
            "summary": "Invalid extraction data.",
            "rule_version": RULE_VERSION,
            "disclaimer": (
                "This is a preliminary compliance screening tool "
                "and not legal certification."
            ),
        }

    flags = category_flags(data.get("category"))

    # Explicit applicability from extractor takes precedence
    # when available.
    fssai_applicable = data.get("fssai_applicable")

    if isinstance(fssai_applicable, bool):
        food_applicable = fssai_applicable
    else:
        food_applicable = flags["food"]

    bis_applicable = data.get("bis_applicable")

    if not isinstance(bis_applicable, bool):
        bis_applicable = bool(
            data.get("is_number")
            or data.get("bis_license_number")
        )

    checks: List[Dict[str, Any]] = []

    # --------------------------------------------------------
    # UNIVERSAL / COMMON PACKAGED COMMODITY CHECKS
    # --------------------------------------------------------

    checks.append(validate_product_name(data))
    checks.append(validate_category(data))
    checks.append(validate_manufacturer(data))
    checks.append(validate_address(data))
    checks.append(validate_mrp(data))
    checks.append(validate_net_quantity(data))
    checks.append(validate_batch(data))
    checks.append(validate_country(data))
    checks.append(validate_consumer_care(data))

    # --------------------------------------------------------
    # FOOD-SPECIFIC
    # --------------------------------------------------------

    if food_applicable:

        fssai_check = validate_fssai(data)
        checks.append(fssai_check)

        checks.append(validate_manufacturing_date(data))
        checks.append(validate_expiry(data))
        checks.append(validate_ingredients(data))

    # --------------------------------------------------------
    # COSMETICS
    # --------------------------------------------------------

    if flags["cosmetic"]:

        checks.append(validate_manufacturing_date(data))
        checks.append(validate_expiry(data))
        checks.append(validate_ingredients(data))

    # --------------------------------------------------------
    # BIS / IS
    # --------------------------------------------------------

    if bis_applicable:

        checks.append(validate_is_number(data))
        checks.append(validate_bis_license(data))

    # --------------------------------------------------------
    # OTHER PRODUCT-SPECIFIC CATEGORIES
    # --------------------------------------------------------

    if (
        flags["electrical"]
        or flags["toy"]
        or flags["battery"]
        or flags["textile"]
        or flags["chemical"]
        or flags["agricultural"]
        or flags["automotive"]
    ):
        checks.append(
            _result(
                "Product-Specific Certification / Requirements",
                "REVIEW",
                data.get("category"),
                (
                    "Product category may have additional technical, "
                    "safety or certification requirements. Confirm "
                    "applicable regulator/standard."
                ),
                "Applicable product-specific requirements",
                check_type="official_verification",
            )
        )

    # --------------------------------------------------------
    # ADDITIONAL DECLARATIONS
    # --------------------------------------------------------

    checks.append(
        validate_additional_declarations(data)
    )

    # --------------------------------------------------------
    # WHAT + HOW / PRESENTATION
    # --------------------------------------------------------

    add_format_checks(checks, data)

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    overall = _overall_status(checks)

    pass_count = sum(
        1 for c in checks if c.get("status") == "PASS"
    )

    review_count = sum(
        1
        for c in checks
        if c.get("status") in {"REVIEW", "MISMATCH"}
    )

    missing_count = sum(
        1
        for c in checks
        if c.get("status") == "MISSING"
    )

    findings = [
        {
            "field": check.get("field"),
            "status": check.get("status"),
            "message": check.get("message"),
            "requirement": check.get("requirement"),
            "legal_reference": check.get("legal_reference"),
            "evidence": check.get("evidence"),
            "recommended_action": check.get("recommended_action"),
        }
        for check in checks
        if check.get("status") in {"MISSING", "REVIEW", "MISMATCH"}
    ]

    return {
        "overall_status": overall,
        "rule_version": RULE_VERSION,
        "category": data.get("category"),
        "applicability": {
            "food": food_applicable,
            "fssai": food_applicable,
            "cosmetic": flags["cosmetic"],
            "bis": bis_applicable,
            "electrical": flags["electrical"],
            "toy": flags["toy"],
            "battery": flags["battery"],
            "textile": flags["textile"],
            "chemical": flags["chemical"],
            "agricultural": flags["agricultural"],
            "automotive": flags["automotive"],
        },
        "checks": checks,
        "findings": findings,
        "summary": {
            "total_checks": len(checks),
            "passed": pass_count,
            "review": review_count,
            "missing": missing_count,
        },
        "disclaimer": (
            "PackCheck AI provides preliminary compliance screening "
            "based on extracted package information and configured "
            "rules. It is not legal certification. Exact statutory "
            "presentation requirements, physical measurements and "
            "official registrations may require verification by an "
            "authorized inspector or the relevant authority."
        ),
    }