import json
import shutil
import tempfile
import time
from pathlib import Path

import streamlit as st
from PIL import Image, ImageOps, ImageDraw

from Extraction.extractor import extract_label
from Verification.compliance_engine import check_compliance
from Reports.report_generator import generate_report


# ============================================================
# PACKCHECK AI — MAIN STREAMLIT APPLICATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

RESULT_FILE = BASE_DIR / "packcheck_result.json"
VERIFICATION_FILE = BASE_DIR / "verification_result.json"

API_DIR = BASE_DIR / "api"
API_RESULT_FILE = API_DIR / "packcheck_result.json"
API_VERIFICATION_FILE = API_DIR / "verification_result.json"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PackCheck AI",
    page_icon="📦",
    layout="wide",
)


# ============================================================
# SESSION STATE
# ============================================================

if "result" not in st.session_state:
    st.session_state.result = None

if "image_path" not in st.session_state:
    st.session_state.image_path = None

if "image_paths" not in st.session_state:
    st.session_state.image_paths = []

if "verification" not in st.session_state:
    st.session_state.verification = None

if "report_path" not in st.session_state:
    st.session_state.report_path = None

if "last_report_id" not in st.session_state:
    st.session_state.last_report_id = None

if "selected_report_id" not in st.session_state:
    st.session_state.selected_report_id = None

if "verification_start_time" not in st.session_state:
    st.session_state.verification_start_time = None

if "verification_delay" not in st.session_state:
    st.session_state.verification_delay = 10

if "verification_file_mtime" not in st.session_state:
    st.session_state.verification_file_mtime = None

if "language" not in st.session_state:
    st.session_state.language = "English"

LANG = {
    "English": {
        "dashboard": "🏠 Dashboard",
        "new_inspection": "➕ New Inspection",
        "history": "🧾 Inspection History",
        "reports": "📄 Reports",
        "language": "Language",
        "english": "English",
        "hindi": "हिन्दी",
        "system_online": "🟢 System Online",
        "inspector": "Inspector",
        "new_title": "📦 PackCheck AI",
        "new_subtitle": "Record a package inspection and verify its declared information.",
        "upload": "📸 Upload Product Label Photos",
        "upload_help": "Upload clear photos of the same package. You can add multiple views such as front, back, side, top or bottom.",
        "selected": "📸 {count} photo(s) selected.",
        "package_views": "📷 Package Views",
        "inspection_package": "📦 Inspection Package",
        "ai_analysis": "🤖 AI Analysis",
        "photos": "Photos",
        "analyze": "🚀 Analyze Product",
        "history_title": "🧾 Inspection History",
        "reports_title": "📄 Inspection Reports",
        "no_history": "No inspection records yet.",
        "no_reports": "No reports have been generated yet.",
        "view_report": "👁️ View Report",
        "close_report": "✕ Close Report",
        "download_report": "⬇️ Download This Report",
        "inspection_overview": "Inspection Overview",
        "total_reports": "📋 TOTAL REPORTS",
        "passed": "✅ PASSED",
        "manual_inspection": "🔍 MANUAL INSPECTION",
        "all_completed": "All completed inspection reports",
        "no_issue": "No issue requiring further review",
        "requires_attention": "Requires inspector attention",
        "no_reports_dashboard": "No inspection reports yet. Start your first inspection to populate the dashboard.",
        "passed_reports": "✅ Passed Reports",
        "manual_reports": "🔍 Manual Inspection Reports",
        "recent_reports": "🧾 Recent Reports",
        "show_all": "↩️ Show All Reports",
        "report_preview": "Report Preview",
        "product": "Product",
        "manufacturer": "Manufacturer",
        "result": "Result",
        "created": "Created",
        "ready_next": "Ready for the next inspection?",
        "ai_extraction": '🤖 AI Extraction Result',
        "detected_product": 'DETECTED PRODUCT',
        "product_manufacturer": '📋 Product & Manufacturer',
        "product_name": "Product Name",
        "fssai_number": "FSSAI Number",
        "bis_evidence": "BIS Evidence",
        "is_standard": 'IS Standard',
        "bis_license": 'BIS Licence / Registration',
        "regulatory_identifier": "Regulatory Identifier",
        "manufacturer_address": "Manufacturer Address",
        "category": "Category",
        "country_origin": "Country of Origin",
        "package_information": '📦 Package Information',
        "mrp": 'MRP',
        "net_quantity": 'Net Quantity',
        "batch_lot": 'Batch / Lot',
        "barcode": 'Barcode / GTIN',
        "dates_shelf": '📅 Dates & Shelf Life',
        "manufacturing_date": "Manufacturing Date",
        "expiry_date": "Expiry Date",
        "best_before": "Best Before",
        "ingredients": '🥣 Ingredients',
        "safety": '🛡️ Safety Information',
        "allergens": "⚠️ Allergens",
        "warnings": "🚨 Warnings",
        "storage": "📦 Storage",
        "additional_declarations": '📑 Additional Declarations',
        "ai_notes": '🔎 AI Extraction Notes',
        "compliance": '🔎 Compliance Screening',
        "automated_insight_title": "🤖 Automated Compliance Insight",
        "issues_detected": "⚠️ Potential Compliance Issues Detected",
        "no_issues_detected": "✅ No Potential Compliance Issues Detected",
        "items_require_review": "{count} item(s) require review",
        "ai_insight": "AI Insight",
        "insight_pass": "The package information was successfully analyzed and no potential compliance issues were identified by the automated screening. Final verification remains with the authorized inspector.",
        "insight_attention": "The automated screening identified {count} item(s) that may require further review. Please verify the highlighted declarations before making a final regulatory decision.",
        "regulatory_disclaimer": "Final regulatory decisions remain with the authorized inspector.",
        "inspection_notice": "PackCheck provides automated preliminary screening and decision-support assistance. Results should be reviewed by the authorized inspector before any final regulatory decision.",
        "overall_pass": '🟢 Overall Screening: PASS',
        "overall_mismatch": '🔴 Overall Screening: MISMATCH',
        "overall_review": '🟡 Overall Screening: REVIEW',
        "missing": 'Missing',
        "review": 'Review',
        "mismatch": 'Mismatch',
        "field_checks": "Field-by-Field Checks",
        "fssai_verification": '🏛️ Official FSSAI Verification',
        "foscos_workflow": "FoSCoS Workflow",
        "bis_verification": '🏛️ Official BIS Verification',
        "bis_workflow": "BIS Workflow",
        "verification_result": "Verification Result",
        "packet_vs_official": 'Packet vs Official',
        "official_company": "Official Company",
        "license_type": "License Type",
        "official_status": "Official Status",
        "inspection_report": '📄 Inspection Report',
        "generate_pdf": '📄 Generate PDF Report',
        "download_inspection": '⬇️ Download Inspection Report',
        "prototype": "PackCheck AI is an academic/SIH prototype. It is not an official Government of India portal or certification authority."
    },
    "हिन्दी": {
        "dashboard": "🏠 डैशबोर्ड",
        "new_inspection": "➕ नया निरीक्षण",
        "history": "🧾 निरीक्षण इतिहास",
        "reports": "📄 रिपोर्ट",
        "language": "भाषा",
        "english": "English",
        "hindi": "हिन्दी",
        "system_online": "🟢 सिस्टम ऑनलाइन",
        "inspector": "निरीक्षक",
        "new_title": "📦 PackCheck AI",
        "new_subtitle": "पैकेज का निरीक्षण दर्ज करें और घोषित जानकारी का सत्यापन करें।",
        "upload": "📸 उत्पाद लेबल की तस्वीरें अपलोड करें",
        "upload_help": "एक ही पैकेज की स्पष्ट तस्वीरें अपलोड करें। आगे, पीछे, साइड, ऊपर या नीचे के दृश्य जोड़ सकते हैं।",
        "selected": "📸 {count} तस्वीरें चुनी गईं।",
        "package_views": "📷 पैकेज के दृश्य",
        "inspection_package": "📦 निरीक्षण पैकेज",
        "ai_analysis": "🤖 AI विश्लेषण",
        "photos": "तस्वीरें",
        "analyze": "🚀 उत्पाद का विश्लेषण करें",
        "history_title": "🧾 निरीक्षण इतिहास",
        "reports_title": "📄 निरीक्षण रिपोर्ट",
        "no_history": "अभी कोई निरीक्षण रिकॉर्ड नहीं है।",
        "no_reports": "अभी कोई रिपोर्ट तैयार नहीं हुई है।",
        "view_report": "👁️ रिपोर्ट देखें",
        "close_report": "✕ रिपोर्ट बंद करें",
        "download_report": "⬇️ यह रिपोर्ट डाउनलोड करें",
        "inspection_overview": "निरीक्षण अवलोकन",
        "total_reports": "📋 कुल रिपोर्ट",
        "passed": "✅ पास",
        "manual_inspection": "🔍 मैनुअल निरीक्षण",
        "all_completed": "सभी पूर्ण निरीक्षण रिपोर्ट",
        "no_issue": "आगे समीक्षा की आवश्यकता नहीं",
        "requires_attention": "निरीक्षक की समीक्षा आवश्यक",
        "no_reports_dashboard": "अभी कोई निरीक्षण रिपोर्ट नहीं है। डैशबोर्ड भरने के लिए पहला निरीक्षण शुरू करें।",
        "passed_reports": "✅ पास रिपोर्ट",
        "manual_reports": "🔍 मैनुअल निरीक्षण रिपोर्ट",
        "recent_reports": "🧾 हाल की रिपोर्ट",
        "show_all": "↩️ सभी रिपोर्ट दिखाएँ",
        "report_preview": "रिपोर्ट पूर्वावलोकन",
        "product": "उत्पाद",
        "manufacturer": "निर्माता",
        "result": "परिणाम",
        "created": "तैयार किया गया",
        "ready_next": "अगले निरीक्षण के लिए तैयार हैं?",
        "ai_extraction": "🤖 AI निष्कर्षण परिणाम",
        "detected_product": "पहचाना गया उत्पाद",
        "product_manufacturer": "📋 उत्पाद और निर्माता",
        "product_name": "उत्पाद का नाम",
        "fssai_number": "FSSAI नंबर",
        "bis_evidence": "BIS प्रमाण",
        "is_standard": "IS मानक",
        "bis_license": "BIS लाइसेंस / पंजीकरण",
        "regulatory_identifier": "नियामक पहचान",
        "manufacturer_address": "निर्माता का पता",
        "category": "श्रेणी",
        "country_origin": "मूल देश",
        "package_information": "📦 पैकेज जानकारी",
        "mrp": "अधिकतम खुदरा मूल्य",
        "net_quantity": "शुद्ध मात्रा",
        "batch_lot": "बैच / लॉट",
        "barcode": "बारकोड / GTIN",
        "dates_shelf": "📅 तिथियाँ और शेल्फ लाइफ",
        "manufacturing_date": "निर्माण तिथि",
        "expiry_date": "समाप्ति तिथि",
        "best_before": "बेस्ट बिफोर",
        "ingredients": "🥣 सामग्री",
        "safety": "🛡️ सुरक्षा जानकारी",
        "allergens": "⚠️ एलर्जेन्स",
        "warnings": "🚨 चेतावनियाँ",
        "storage": "📦 भंडारण",
        "additional_declarations": "📑 अतिरिक्त घोषणाएँ",
        "ai_notes": "🔎 AI निष्कर्षण नोट्स",
        "compliance": "🔎 अनुपालन जाँच",
        "automated_insight_title": "🤖 स्वचालित अनुपालन अंतर्दृष्टि",
        "issues_detected": "⚠️ संभावित अनुपालन समस्याएँ मिलीं",
        "no_issues_detected": "✅ संभावित अनुपालन समस्याएँ नहीं मिलीं",
        "items_require_review": "{count} आइटम की समीक्षा आवश्यक है",
        "ai_insight": "AI अंतर्दृष्टि",
        "insight_pass": "पैकेज की जानकारी का स्वचालित विश्लेषण पूरा हुआ और स्वचालित जाँच में कोई संभावित अनुपालन समस्या नहीं मिली। अंतिम सत्यापन अधिकृत निरीक्षक द्वारा किया जाना आवश्यक है।",
        "insight_attention": "स्वचालित जाँच में {count} आइटम मिले जिनकी आगे समीक्षा आवश्यक हो सकती है। अंतिम नियामक निर्णय से पहले चिन्हित घोषणाओं का सत्यापन करें।",
        "regulatory_disclaimer": "अंतिम नियामक निर्णय अधिकृत निरीक्षक द्वारा लिया जाना आवश्यक है।",
        "inspection_notice": "PackCheck स्वचालित प्रारंभिक जाँच और निर्णय-सहायता प्रदान करता है। किसी भी अंतिम नियामक निर्णय से पहले परिणामों की अधिकृत निरीक्षक द्वारा समीक्षा की जानी चाहिए।",
        "overall_pass": "🟢 समग्र जाँच: पास",
        "overall_mismatch": "🔴 समग्र जाँच: असंगति",
        "overall_review": "🟡 समग्र जाँच: समीक्षा",
        "missing": "अनुपस्थित",
        "review": "समीक्षा",
        "mismatch": "असंगति",
        "field_checks": "फ़ील्ड-दर-फ़ील्ड जाँच",
        "fssai_verification": "🏛️ आधिकारिक FSSAI सत्यापन",
        "foscos_workflow": "FoSCoS प्रक्रिया",
        "bis_verification": "🏛️ आधिकारिक BIS सत्यापन",
        "bis_workflow": "BIS प्रक्रिया",
        "verification_result": "सत्यापन परिणाम",
        "packet_vs_official": "पैकेज बनाम आधिकारिक रिकॉर्ड",
        "official_company": "आधिकारिक कंपनी",
        "license_type": "लाइसेंस प्रकार",
        "official_status": "आधिकारिक स्थिति",
        "inspection_report": "📄 निरीक्षण रिपोर्ट",
        "generate_pdf": "📄 PDF रिपोर्ट तैयार करें",
        "download_inspection": "⬇️ निरीक्षण रिपोर्ट डाउनलोड करें",
        "prototype": "PackCheck AI एक शैक्षणिक/SIH प्रोटोटाइप है। यह भारत सरकार का आधिकारिक पोर्टल या प्रमाणन प्राधिकरण नहीं है।"
    }
}

def t(key, **kwargs):
    value = LANG.get(st.session_state.language, LANG["English"]).get(key, key)
    return value.format(**kwargs)


# ============================================================
# HELPERS
# ============================================================

def safe_value(value):
    if value is None or value == "":
        return "Not detected"

    if isinstance(value, list):
        if not value:
            return "Not detected"

        return ", ".join(str(x) for x in value)

    return str(value)


def category_flags(category):
    text = str(category or "").lower()

    return {
        "food": any(
            x in text
            for x in (
                "food",
                "beverage",
                "drink"
            )
        ),

        "cosmetic": any(
            x in text
            for x in (
                "cosmetic",
                "personal care",
                "personal-care"
            )
        ),

        "electrical": any(
            x in text
            for x in (
                "electrical",
                "electronic",
                "appliance"
            )
        ),
    }


def status_icon(status):
    icons = {
        "PASS": "✅",
        "MISSING": "⚠️",
        "REVIEW": "🔎",
        "MISMATCH": "❌",
        "MATCH": "✅",
        "PARTIAL MATCH": "🟡",
        "VERIFIED": "🟢",
    }

    return icons.get(
        str(status).upper(),
        "•"
    )


# ============================================================
# MULTI-IMAGE HELPERS
# ============================================================

def create_combined_inspection_image(uploaded_files):
    """
    Combine multiple photos of the SAME package into one
    high-resolution vertical inspection image.

    This allows the existing extractor.py to continue receiving
    one image path while Gemini can see all package views
    in a single API request.

    Example:

        Front.jpg
        Back.jpg
        Side.jpg
        Bottom.jpg

    becomes:

        PackCheck_Combined_Inspection.jpg

    The images are kept in order and labelled.
    """

    if not uploaded_files:
        return None, []

    image_objects = []
    original_paths = []

    # --------------------------------------------------------
    # Save original uploaded images
    # --------------------------------------------------------

    for index, uploaded_file in enumerate(uploaded_files):

        suffix = Path(
            uploaded_file.name
        ).suffix.lower()

        if suffix not in (
            ".jpg",
            ".jpeg",
            ".png",
            ".webp"
        ):
            suffix = ".jpg"

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
            dir=BASE_DIR
        ) as temp_file:

            temp_file.write(
                uploaded_file.getbuffer()
            )

            original_path = Path(
                temp_file.name
            )

        original_paths.append(
            original_path
        )

        # ----------------------------------------------------
        # Open image safely
        # ----------------------------------------------------

        try:

            image = Image.open(
                original_path
            ).convert("RGB")

            image_objects.append(
                (
                    uploaded_file.name,
                    image
                )
            )

        except Exception as error:

            st.warning(
                f"⚠️ Could not read {uploaded_file.name}: "
                f"{error}"
            )


    if not image_objects:
        return None, original_paths


    # --------------------------------------------------------
    # Determine canvas width
    # --------------------------------------------------------

    MAX_WIDTH = 1800

    prepared_images = []

    for filename, image in image_objects:

        # Preserve aspect ratio.
        if image.width > MAX_WIDTH:

            ratio = (
                MAX_WIDTH /
                float(image.width)
            )

            new_height = int(
                image.height * ratio
            )

            image = image.resize(
                (
                    MAX_WIDTH,
                    new_height
                ),
                Image.Resampling.LANCZOS
            )

        prepared_images.append(
            (
                filename,
                image
            )
        )


    # --------------------------------------------------------
    # Calculate canvas dimensions
    # --------------------------------------------------------

    LABEL_HEIGHT = 70
    GAP = 25
    SIDE_PADDING = 30
    TOP_PADDING = 30
    BOTTOM_PADDING = 30

    canvas_width = max(
        image.width
        for _, image in prepared_images
    ) + (
        SIDE_PADDING * 2
    )

    canvas_height = (
        TOP_PADDING
        + BOTTOM_PADDING
    )

    for _, image in prepared_images:

        canvas_height += (
            LABEL_HEIGHT
            + image.height
            + GAP
        )


    # --------------------------------------------------------
    # Create combined canvas
    # --------------------------------------------------------

    canvas = Image.new(
        "RGB",
        (
            canvas_width,
            canvas_height
        ),
        "white"
    )

    draw = ImageDraw.Draw(
        canvas
    )

    current_y = TOP_PADDING


    # --------------------------------------------------------
    # Add each image
    # --------------------------------------------------------

    for index, (filename, image) in enumerate(
        prepared_images,
        start=1
    ):

        # Image label
        label = (
            f"VIEW {index} — {filename}"
        )

        draw.rectangle(
            [
                SIDE_PADDING,
                current_y,
                canvas_width - SIDE_PADDING,
                current_y + LABEL_HEIGHT
            ],
            fill="#eeeeee"
        )

        draw.text(
            (
                SIDE_PADDING + 20,
                current_y + 22
            ),
            label,
            fill="black"
        )

        current_y += LABEL_HEIGHT

        # Center image horizontally
        x = int(
            (
                canvas_width -
                image.width
            ) / 2
        )

        canvas.paste(
            image,
            (
                x,
                current_y
            )
        )

        current_y += (
            image.height + GAP
        )


    # --------------------------------------------------------
    # Save combined image
    # --------------------------------------------------------

    combined_path = (
        BASE_DIR /
        f"PackCheck_Combined_{int(time.time() * 1000)}.jpg"
    )

    canvas.save(
        combined_path,
        format="JPEG",
        quality=95,
        optimize=True
    )

    return combined_path, original_paths


# ============================================================
# SAVE PACKCHECK RESULT
# ============================================================

def save_packcheck_result(result):

    API_DIR.mkdir(
        exist_ok=True
    )

    data = json.dumps(
        result,
        indent=4,
        ensure_ascii=False
    )

    RESULT_FILE.write_text(
        data,
        encoding="utf-8"
    )

    API_RESULT_FILE.write_text(
        data,
        encoding="utf-8"
    )


# ============================================================
# LOAD VERIFICATION RESULT
# ============================================================

def load_verification_result():

    if API_VERIFICATION_FILE.exists():

        try:

            return json.loads(
                API_VERIFICATION_FILE.read_text(
                    encoding="utf-8"
                )
            )

        except Exception:
            return None

    if VERIFICATION_FILE.exists():

        try:

            return json.loads(
                VERIFICATION_FILE.read_text(
                    encoding="utf-8"
                )
            )

        except Exception:
            return None

    return None


# ============================================================
# COPY VERIFICATION TO ROOT
# ============================================================

def copy_verification_to_root():

    if API_VERIFICATION_FILE.exists():

        shutil.copy2(
            API_VERIFICATION_FILE,
            VERIFICATION_FILE
        )

        return True

    return VERIFICATION_FILE.exists()


# ============================================================
# REPORT HISTORY / DASHBOARD
# ============================================================

DATA_DIR = BASE_DIR / "data"
HISTORY_FILE = DATA_DIR / "report_history.json"


def ensure_history_file():

    DATA_DIR.mkdir(
        exist_ok=True
    )

    if not HISTORY_FILE.exists():

        HISTORY_FILE.write_text(
            "[]",
            encoding="utf-8"
        )


def load_report_history():

    ensure_history_file()

    try:

        data = json.loads(
            HISTORY_FILE.read_text(
                encoding="utf-8"
            )
        )

        return (
            data
            if isinstance(data, list)
            else []
        )

    except Exception:
        return []


def save_report_history(history):

    ensure_history_file()

    HISTORY_FILE.write_text(
        json.dumps(
            history,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


def next_report_id(history):

    highest = 0

    for record in history:

        report_id = str(
            record.get(
                "report_id",
                ""
            )
        )

        if report_id.startswith("PC-"):

            try:

                number = int(
                    report_id.split("-")[1]
                )

                highest = max(
                    highest,
                    number
                )

            except (
                ValueError,
                IndexError
            ):
                pass

    return f"PC-{highest + 1:04d}"


def get_final_report_status(
    compliance,
    verification
):

    compliance_status = str(
        (
            compliance or {}
        ).get(
            "overall_status",
            "REVIEW"
        )
    ).upper()

    verification_data = (
        verification or {}
    ).get(
        "verification",
        {}
    )

    verification_status = str(
        verification_data.get(
            "overallStatus",
            ""
        )
    ).upper()

    verification_type = str(
        verification_data.get(
            "type",
            ""
        )
    ).upper()

    extraction = (
        st.session_state
        .get("result", {})
        .get("extraction", {})
    )

    flags = category_flags(
        extraction.get("category")
    )

    fssai = extraction.get(
        "fssai_number"
    )

    bis_required_workflow = bool(
        extraction.get(
            "bis_applicable"
        )
    ) and (
        flags["electrical"]
        or extraction.get("is_number")
        or extraction.get(
            "bis_license_number"
        )
    )

    fssai_workflow = bool(
        fssai
    ) and flags["food"]

    if compliance_status == "PASS":

        if verification_status == "VERIFIED":
            return "PASSED"

        if (
            not verification
            and not fssai_workflow
            and not bis_required_workflow
        ):
            return "PASSED"

    return "MANUAL INSPECTION"


def add_report_record(
    report_path,
    result,
    verification
):

    history = load_report_history()

    extraction = (
        result.get(
            "extraction",
            {}
        )
        if isinstance(result, dict)
        else {}
    )

    compliance = (
        result.get(
            "compliance",
            {}
        )
        if isinstance(result, dict)
        else {}
    )

    report_id = next_report_id(
        history
    )

    record = {
        "report_id": report_id,

        "created_at":
            __import__(
                "datetime"
            ).datetime.now().isoformat(
                timespec="seconds"
            ),

        "product_name":
            safe_value(
                extraction.get(
                    "product_name"
                )
            ),

        "manufacturer":
            safe_value(
                extraction.get(
                    "manufacturer"
                )
            ),

        "category":
            safe_value(
                extraction.get(
                    "category"
                )
            ),

        "status":
            get_final_report_status(
                compliance,
                verification
            ),

        "compliance_status":
            str(
                compliance.get(
                    "overall_status",
                    "REVIEW"
                )
            ).upper(),

        "verification_status":
            str(
                (
                    verification or {}
                ).get(
                    "verification",
                    {}
                ).get(
                    "overallStatus",
                    "NOT COMPLETED"
                )
            ).upper(),

        "pdf_path":
            str(report_path),

        "pdf_name":
            Path(report_path).name
    }

    history.append(
        record
    )

    save_report_history(
        history
    )

    return record


def status_badge(status):

    status = str(
        status
    ).upper()

    if status == "PASSED":
        return "🟢 PASSED"

    return "🟡 MANUAL INSPECTION"


# ============================================================
# DASHBOARD
# ============================================================

def render_dashboard():

    history = load_report_history()

    total = len(history)

    passed = sum(
        1
        for record in history
        if record.get(
            "status"
        ) == "PASSED"
    )

    manual = sum(
        1
        for record in history
        if record.get(
            "status"
        ) != "PASSED"
    )

    st.markdown(
        """
        <style>
        .dashboard-title {
            font-size: 2.35rem;
            font-weight: 800;
            margin-bottom: 0.2rem;
        }

        .dashboard-subtitle {
            opacity: 0.68;
            font-size: 1.02rem;
            margin-bottom: 1.6rem;
        }

        .stat-card {
            border: 1px solid rgba(128,128,128,0.22);
            border-radius: 18px;
            padding: 20px 22px;
            min-height: 145px;
            background: rgba(128,128,128,0.045);
        }

        .stat-label {
            font-size: 0.78rem;
            font-weight: 750;
            letter-spacing: 0.08em;
            opacity: 0.65;
        }

        .stat-number {
            font-size: 2.25rem;
            font-weight: 800;
            margin-top: 10px;
        }

        .stat-help {
            font-size: 0.82rem;
            opacity: 0.62;
            margin-top: 4px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="dashboard-title">'
        '📦 PackCheck AI'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="dashboard-subtitle">'
        'Inspector Compliance Dashboard · '
        'Real inspection history'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        t("inspection_overview")
    )

    st.markdown(
        """
        <style>
        div[data-testid="stHorizontalBlock"]
        > div[data-testid="column"]
        div[data-testid="stButton"]
        > button {
            min-height: 145px;
            border-radius: 18px;
            border: 1px solid rgba(128,128,128,0.25);
            font-size: 1.05rem;
            font-weight: 700;
            white-space: pre-line;
            transition: all 0.15s ease;
        }

        div[data-testid="stHorizontalBlock"]
        > div[data-testid="column"]
        div[data-testid="stButton"]
        > button:hover {
            border-color: rgba(255,255,255,0.55);
            transform: translateY(-2px);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        if st.button(
            f"{t('total_reports')}\n\n{total}\n\n{t('all_completed')}",
            key="dashboard_total",
            use_container_width=True
        ):

            st.session_state.dashboard_filter = "ALL"
            st.rerun()

    with c2:

        if st.button(
            f"{t('passed')}\n\n{passed}\n\n{t('no_issue')}",
            key="dashboard_passed",
            use_container_width=True
        ):

            st.session_state.dashboard_filter = "PASSED"
            st.rerun()

    with c3:

        if st.button(
            f"{t('manual_inspection')}\n\n{manual}\n\n{t('requires_attention')}",
            key="dashboard_manual",
            use_container_width=True
        ):

            st.session_state.dashboard_filter = (
                "MANUAL INSPECTION"
            )

            st.rerun()

    st.divider()

    st.subheader(
        "📈 Inspection Overview"
    )

    if history:

        import pandas as pd

        chart_data = pd.DataFrame(
            {
                "Status": [
                    "Passed",
                    "Manual Inspection"
                ],

                "Reports": [
                    passed,
                    manual
                ]
            }
        ).set_index(
            "Status"
        )

        st.bar_chart(
            chart_data,
            height=260
        )

    else:

        st.info(
            t("no_reports_dashboard")
        )

    st.divider()

    selected_filter = st.session_state.get(
        "dashboard_filter",
        "ALL"
    )

    if selected_filter == "PASSED":

        visible_reports = [
            record
            for record in history
            if record.get(
                "status"
            ) == "PASSED"
        ]

        heading = "✅ Passed Reports"

    elif selected_filter == "MANUAL INSPECTION":

        visible_reports = [
            record
            for record in history
            if record.get(
                "status"
            ) != "PASSED"
        ]

        heading = (
            "🔍 Manual Inspection Reports"
        )

    else:

        visible_reports = history
        heading = "🧾 Recent Reports"

    st.subheader(
        heading
    )

    if selected_filter != "ALL":

        if st.button(
            "↩️ Show All Reports",
            key="show_all_reports"
        ):

            st.session_state.dashboard_filter = (
                "ALL"
            )

            st.rerun()

    visible_reports = list(
        reversed(
            visible_reports
        )
    )

    if visible_reports:

        for record in visible_reports:

            report_id = record.get(
                "report_id",
                "—"
            )

            product = record.get(
                "product_name",
                "Not detected"
            )

            manufacturer = record.get(
                "manufacturer",
                "Not detected"
            )

            status = record.get(
                "status",
                "MANUAL INSPECTION"
            )

            pdf_path = (
                Path(
                    record.get(
                        "pdf_path",
                        ""
                    )
                )
                if record.get(
                    "pdf_path"
                )
                else None
            )

            with st.container(
                border=True
            ):

                r1, r2, r3, r4 = st.columns(
                    [1.1, 2.1, 1.4, 1.2]
                )

                with r1:
                    st.markdown(
                        f"**{report_id}**"
                    )

                with r2:

                    st.markdown(
                        f"**{product}**"
                    )

                    st.caption(
                        manufacturer
                    )

                with r3:

                    st.write(
                        status_badge(
                            status
                        )
                    )

                with r4:

                    if st.button(
                        "👁️ View Report",
                        key=f"view_{report_id}",
                        use_container_width=True
                    ):

                        st.session_state.selected_report_id = (
                            report_id
                        )

                        st.rerun()

                if (
                    st.session_state.selected_report_id
                    == report_id
                ):

                    st.divider()

                    st.markdown(
                        f"### 📄 {report_id} — "
                        "Report Preview"
                    )

                    st.write(
                        f"**Product:** {product}"
                    )

                    st.write(
                        f"**Manufacturer:** "
                        f"{manufacturer}"
                    )

                    st.write(
                        f"**Result:** "
                        f"{status_badge(status)}"
                    )

                    st.write(
                        f"**Created:** "
                        f"{record.get('created_at', '—')}"
                    )

                    if (
                        pdf_path
                        and pdf_path.exists()
                    ):

                        pdf_bytes = (
                            pdf_path.read_bytes()
                        )

                        st.download_button(
                            "⬇️ Download This Report",
                            data=pdf_bytes,
                            file_name=pdf_path.name,
                            mime="application/pdf",
                            key=f"download_{report_id}",
                            use_container_width=True
                        )

                        import base64

                        pdf_b64 = (
                            base64.b64encode(
                                pdf_bytes
                            ).decode(
                                "ascii"
                            )
                        )

                        st.markdown(
                            f'<iframe '
                            f'src="data:application/pdf;'
                            f'base64,{pdf_b64}" '
                            f'width="100%" '
                            f'height="700" '
                            f'style="border:1px solid '
                            f'rgba(128,128,128,.25);'
                            f'border-radius:12px;">'
                            f'</iframe>',
                            unsafe_allow_html=True
                        )

                    else:

                        st.warning(
                            "The PDF file for this report "
                            "is not available at its saved path."
                        )

                    if st.button(
                        "✕ Close Report",
                        key=f"close_{report_id}"
                    ):

                        st.session_state.selected_report_id = None
                        st.rerun()

    else:

        st.info(
            "No reports match this category yet."
        )

    st.divider()

    st.markdown(
        t("ready_next")
    )

    if st.button(
        "➕ New Inspection",
        type="primary",
        use_container_width=True,
        key="dashboard_new_inspection"
    ):

        st.session_state.page = (
            "New Inspection"
        )

        st.session_state.dashboard_filter = (
            "ALL"
        )

        st.rerun()


# ============================================================
# NAVIGATION
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "dashboard_filter" not in st.session_state:
    st.session_state.dashboard_filter = "ALL"

with st.sidebar:

    st.markdown("## 📦 PackCheck AI")
    st.caption(t("system_online") + " · " + t("inspector"))

    st.divider()

    if st.button(
        t("dashboard"),
        use_container_width=True,
        key="nav_dashboard"
    ):
        st.session_state.page = "Dashboard"
        st.session_state.dashboard_filter = "ALL"
        st.session_state.selected_report_id = None
        st.rerun()

    if st.button(
        t("new_inspection"),
        use_container_width=True,
        key="nav_new_inspection"
    ):
        st.session_state.page = "New Inspection"
        st.session_state.selected_report_id = None
        st.rerun()

    if st.button(
        t("history"),
        use_container_width=True,
        key="nav_history"
    ):
        st.session_state.page = "History"
        st.session_state.selected_report_id = None
        st.rerun()

    if st.button(
        t("reports"),
        use_container_width=True,
        key="nav_reports"
    ):
        st.session_state.page = "Reports"
        st.session_state.selected_report_id = None
        st.rerun()

    st.divider()

    language_choice = st.selectbox(
        t("language"),
        ["English", "हिन्दी"],
        index=0 if st.session_state.language == "English" else 1,
        key="language_selector"
    )

    if language_choice != st.session_state.language:
        st.session_state.language = language_choice
        st.rerun()


# ============================================================
# DASHBOARD PAGE
# ============================================================

def render_record_list(title, empty_message):
    history = list(reversed(load_report_history()))

    st.title(title)
    st.caption(t("system_online") + " · " + t("inspector"))
    st.divider()

    if not history:
        st.info(empty_message)
        return

    for record in history:
        report_id = record.get("report_id", "—")
        product = record.get("product_name", "Not detected")
        manufacturer = record.get("manufacturer", "Not detected")
        status = record.get("status", "MANUAL INSPECTION")

        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([1.1, 2.4, 1.5, 1.3])
            with c1:
                st.markdown(f"**{report_id}**")
            with c2:
                st.markdown(f"**{product}**")
                st.caption(manufacturer)
            with c3:
                st.write(status_badge(status))
            with c4:
                if st.button(t("view_report"), key=f"list_view_{report_id}", use_container_width=True):
                    st.session_state.selected_report_id = report_id
                    st.rerun()

            if st.session_state.selected_report_id == report_id:
                st.divider()
                st.write(f"**Product:** {product}")
                st.write(f"**Manufacturer:** {manufacturer}")
                st.write(f"**Created:** {record.get('created_at', '—')}")

                pdf_path = Path(record.get("pdf_path", "")) if record.get("pdf_path") else None
                if pdf_path and pdf_path.exists():
                    pdf_bytes = pdf_path.read_bytes()
                    st.download_button(
                        t("download_report"),
                        data=pdf_bytes,
                        file_name=pdf_path.name,
                        mime="application/pdf",
                        key=f"list_download_{report_id}",
                        use_container_width=True
                    )
                else:
                    st.warning("The PDF file for this report is not available at its saved path.")

                if st.button(t("close_report"), key=f"list_close_{report_id}"):
                    st.session_state.selected_report_id = None
                    st.rerun()


if st.session_state.page == "Dashboard":

    render_dashboard()

# ============================================================
# HISTORY / REPORTS PAGES
# ============================================================

elif st.session_state.page == "History":
    render_record_list(t("history_title"), t("no_history"))

elif st.session_state.page == "Reports":
    render_record_list(t("reports_title"), t("no_reports"))


# ============================================================
# NEW INSPECTION PAGE
# ============================================================

else:

    # ========================================================
    # HEADER
    # ========================================================

    st.title(t("new_title"))

    st.write(t("new_subtitle"))

    st.divider()


    # ========================================================
    # MULTIPLE IMAGE UPLOAD
    # ========================================================

    uploaded_files = st.file_uploader(
        t("upload"),
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp"
        ],
        accept_multiple_files=True,
        help=t("upload_help")
    )


    # ========================================================
    # PROCESS MULTIPLE IMAGES
    # ========================================================

    if uploaded_files:

        st.success(t("selected", count=len(uploaded_files)))

        # ----------------------------------------------------
        # Show uploaded photos
        # ----------------------------------------------------

        st.markdown(t("package_views"))

        # Up to four columns per row.
        columns = st.columns(
            min(
                len(uploaded_files),
                4
            )
        )

        for index, uploaded_file in enumerate(
            uploaded_files
        ):

            with columns[
                index % len(columns)
            ]:

                st.image(
                    uploaded_file,
                    caption=(
                        f"View {index + 1}: "
                        f"{uploaded_file.name}"
                    ),
                    use_container_width=True
                )


        st.divider()


        # ----------------------------------------------------
        # Ready for analysis
        # ----------------------------------------------------

        left, right = st.columns(
            [1, 1]
        )

        with left:

            st.markdown(t("inspection_package"))

            st.write(f"**{t('photos')}:** {len(uploaded_files)}")

            for index, uploaded_file in enumerate(
                uploaded_files,
                start=1
            ):

                st.write(
                    f"{index}. "
                    f"{uploaded_file.name}"
                )


        with right:

            st.markdown(t("ai_analysis"))

            st.write(
                "All selected photos will be treated as "
                "different views of the SAME package."
            )

            st.info(
                "Gemini will receive one combined inspection "
                "image, so the extraction uses evidence from "
                "all uploaded views."
            )

            analyze_button = st.button(
                t("analyze"),
                type="primary",
                use_container_width=True
            )


        # ====================================================
        # ANALYZE
        # ====================================================

        if analyze_button:

            combined_path = None

            try:

                # ------------------------------------------------
                # CREATE COMBINED IMAGE
                # ------------------------------------------------

                with st.spinner(
                    "🖼️ Preparing all package views..."
                ):

                    combined_path, original_paths = (
                        create_combined_inspection_image(
                            uploaded_files
                        )
                    )

                if combined_path is None:

                    st.error(
                        "❌ Could not create the combined "
                        "inspection image."
                    )

                    st.stop()


                # ------------------------------------------------
                # STORE IMAGE PATHS
                # ------------------------------------------------

                st.session_state.image_paths = [
                    str(path)
                    for path in original_paths
                ]

                # The report generator continues using
                # image_path. We use the combined inspection
                # image so the PDF represents all uploaded views.
                st.session_state.image_path = (
                    str(combined_path)
                )


                # ------------------------------------------------
                # SHOW COMBINED IMAGE
                # ------------------------------------------------

                with st.expander(
                    "👁️ View Combined Inspection Image"
                ):

                    st.image(
                        str(combined_path),
                        caption=(
                            "All uploaded package views "
                            "combined for AI analysis"
                        ),
                        use_container_width=True
                    )


                # ------------------------------------------------
                # GEMINI EXTRACTION
                # ------------------------------------------------

                with st.spinner(
                    "🤖 Gemini Vision analyzing ALL package views..."
                ):

                    extraction = extract_label(
                        str(combined_path)
                    )


                # ------------------------------------------------
                # COMPLIANCE ENGINE
                # ------------------------------------------------

                with st.spinner(
                    "🔎 Running compliance screening..."
                ):

                    compliance = check_compliance(
                        extraction
                    )


                # ------------------------------------------------
                # REMOVE PREVIOUS VERIFICATION
                # ------------------------------------------------

                for old_file in (
                    API_VERIFICATION_FILE,
                    VERIFICATION_FILE,
                ):

                    try:

                        if old_file.exists():
                            old_file.unlink()

                    except Exception:
                        pass


                # ------------------------------------------------
                # ANALYSIS ID
                # ------------------------------------------------

                analysis_id = (
                    f"PC-{int(time.time() * 1000)}"
                )


                # ------------------------------------------------
                # COMPLETE RESULT
                # ------------------------------------------------

                result = {
                    "analysis_id":
                        analysis_id,

                    "extraction":
                        extraction,

                    "compliance":
                        compliance
                }


                # ------------------------------------------------
                # VERIFICATION WORKFLOWS
                # ------------------------------------------------

                flags = category_flags(
                    extraction.get(
                        "category"
                    )
                )

                fssai_for_verification = (
                    extraction.get(
                        "fssai_number"
                    )
                )

                bis_for_verification = (
                    bool(
                        extraction.get(
                            "bis_applicable"
                        )
                    )
                    and (
                        flags["electrical"]
                        or extraction.get(
                            "is_number"
                        )
                        or extraction.get(
                            "bis_license_number"
                        )
                    )
                )


                workflows = []


                if (
                    fssai_for_verification
                    and flags["food"]
                ):

                    workflows.append(
                        "FOSCOS"
                    )


                if bis_for_verification:

                    workflows.append(
                        "BIS"
                    )


                # ------------------------------------------------
                # VERIFICATION DELAY
                # ------------------------------------------------

                if workflows:

                    open_after = (
                        time.time() + 10
                    )

                    result["verification"] = {

                        "analysis_id":
                            analysis_id,

                        "open_after":
                            open_after,

                        "workflows":
                            workflows,

                        "type":
                            workflows[0]
                    }

                    st.session_state.verification_start_time = (
                        open_after
                    )

                else:

                    st.session_state.verification_start_time = (
                        None
                    )


                # ------------------------------------------------
                # SAVE JSON
                # ------------------------------------------------

                save_packcheck_result(
                    result
                )


                # ------------------------------------------------
                # SESSION
                # ------------------------------------------------

                st.session_state.result = (
                    result
                )

                st.session_state.verification = (
                    None
                )

                st.session_state.report_path = (
                    None
                )

                st.session_state.verification_file_mtime = (
                    None
                )


                st.success(
                    "✅ AI extraction and compliance "
                    "screening completed using all "
                    f"{len(uploaded_files)} package view(s)."
                )

                st.rerun()


            except Exception as error:

                st.error(
                    "❌ PackCheck analysis failed."
                )

                st.exception(
                    error
                )


    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    result = st.session_state.result


    if result:

        extraction = result.get(
            "extraction",
            {}
        )

        compliance = result.get(
            "compliance",
            {}
        )

        st.divider()


        # ====================================================
        # AI EXTRACTION DASHBOARD
        # ====================================================

        st.header(
            t("ai_extraction")
        )


        def display_value(value):

            if (
                value is None
                or value == ""
                or value == []
            ):

                return "Not detected"

            if isinstance(
                value,
                list
            ):

                if not value:
                    return "Not detected"

                return ", ".join(
                    str(x)
                    for x in value
                )

            return str(value)


        def is_missing(value):

            return (
                value is None
                or value == ""
                or value == []
            )


        # ----------------------------------------------------
        # PRODUCT SUMMARY
        # ----------------------------------------------------

        product_name = display_value(
            extraction.get(
                "product_name"
            )
        )

        manufacturer = display_value(
            extraction.get(
                "manufacturer"
            )
        )

        category = display_value(
            extraction.get(
                "category"
            )
        )

        country = display_value(
            extraction.get(
                "country_of_origin"
            )
        )


        st.markdown(
            f"""
<div style="
    padding: 24px;
    border-radius: 16px;
    border: 1px solid rgba(128,128,128,0.25);
    margin: 10px 0 25px 0;
">

<div style="
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    opacity: 0.65;
">
DETECTED PRODUCT
</div>

<div style="
    font-size: 2rem;
    font-weight: 750;
    margin-top: 5px;
">
{product_name}
</div>

<div style="
    font-size: 1.05rem;
    margin-top: 8px;
">
🏭 {manufacturer}
</div>

<div style="
    margin-top: 12px;
    opacity: 0.75;
">
📦 {category}
&nbsp;&nbsp; • &nbsp;&nbsp;
🌍 {country}
</div>

</div>
""",
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # IDENTITY & REGISTRATION
        # ----------------------------------------------------

        st.subheader(
            t("product_manufacturer")
        )

        col1, col2 = st.columns(2)


        with col1:

            with st.container(
                border=True
            ):

                st.markdown(
                    "**" + t("product_name") + "**"
                )

                st.write(
                    product_name
                )

                st.markdown(
                    "**Manufacturer**"
                )

                st.write(
                    manufacturer
                )

                flags = category_flags(
                    extraction.get(
                        "category"
                    )
                )


                if flags["food"]:

                    st.markdown(
                        "**" + t("fssai_number") + "**"
                    )

                    fssai = extraction.get(
                        "fssai_number"
                    )

                    if is_missing(
                        fssai
                    ):

                        st.warning(
                            "Not detected"
                        )

                    else:

                        st.code(
                            str(fssai),
                            language=None
                        )


                elif (
                    extraction.get(
                        "bis_applicable"
                    )
                    or extraction.get(
                        "is_number"
                    )
                    or extraction.get(
                        "bis_license_number"
                    )
                ):

                    st.markdown(
                        "**" + t("bis_evidence") + "**"
                    )

                    st.write(
                        t("is_standard")
                    )

                    st.code(
                        display_value(
                            extraction.get(
                                "is_number"
                            )
                        ),
                        language=None
                    )

                    st.write(
                        t("bis_license")
                    )

                    st.code(
                        display_value(
                            extraction.get(
                                "bis_license_number"
                            )
                        ),
                        language=None
                    )

                else:

                    st.markdown(
                        "**" + t("regulatory_identifier") + "**"
                    )

                    st.write(
                        "No FSSAI/BIS identifier detected."
                    )


        with col2:

            with st.container(
                border=True
            ):

                st.markdown(
                    "**" + t("manufacturer_address") + "**"
                )

                st.write(
                    display_value(
                        extraction.get(
                            "manufacturer_address"
                        )
                    )
                )

                st.markdown(
                    "**" + t("category") + "**"
                )

                st.write(
                    category
                )

                st.markdown(
                    "**" + t("country_origin") + "**"
                )

                st.write(
                    country
                )


        # ----------------------------------------------------
        # PACKAGE INFORMATION
        # ----------------------------------------------------

        st.subheader(
            t("package_information")
        )

        p1, p2, p3, p4 = st.columns(4)


        with p1:

            st.metric(
                t("mrp"),
                display_value(
                    extraction.get(
                        "mrp"
                    )
                )
            )


        with p2:

            st.metric(
                t("net_quantity"),
                display_value(
                    extraction.get(
                        "net_quantity"
                    )
                )
            )


        with p3:

            st.metric(
                t("batch_lot"),
                display_value(
                    extraction.get(
                        "batch_number"
                    )
                )
            )


        with p4:

            st.metric(
                t("barcode"),
                display_value(
                    extraction.get(
                        "barcode_or_gtin"
                    )
                )
            )


        # ----------------------------------------------------
        # DATES & SHELF LIFE
        # ----------------------------------------------------

        flags = category_flags(
            extraction.get(
                "category"
            )
        )

        show_dates = (
            flags["food"]
            or flags["cosmetic"]
        )


        if show_dates:

            st.subheader(
                t("dates_shelf")
            )

            d1, d2, d3 = st.columns(3)


            with d1:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        "**" + t("manufacturing_date") + "**"
                    )

                    value = extraction.get(
                        "manufacturing_date"
                    )

                    if is_missing(value):

                        st.warning(
                            "⚠️ Not detected"
                        )

                    else:

                        st.success(
                            f"✅ {value}"
                        )


            with d2:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        "**" + t("expiry_date") + "**"
                    )

                    value = extraction.get(
                        "expiry_date"
                    )

                    if is_missing(value):

                        st.warning(
                            "⚠️ Not detected"
                        )

                    else:

                        st.success(
                            f"✅ {value}"
                        )


            with d3:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        "**" + t("best_before") + "**"
                    )

                    value = extraction.get(
                        "best_before"
                    )

                    if is_missing(value):

                        st.warning(
                            "⚠️ Not detected"
                        )

                    else:

                        st.success(
                            "✅ Detected"
                        )

                        st.write(
                            value
                        )


        # ----------------------------------------------------
        # INGREDIENTS
        # ----------------------------------------------------

        if (
            flags["food"]
            or flags["cosmetic"]
        ):

            st.subheader(
                t("ingredients")
            )

            with st.container(
                border=True
            ):

                ingredients = extraction.get(
                    "ingredients"
                )

                if is_missing(
                    ingredients
                ):

                    st.warning(
                        "⚠️ Ingredients not detected."
                    )

                else:

                    st.write(
                        ingredients
                    )


        # ----------------------------------------------------
        # SAFETY INFORMATION
        # ----------------------------------------------------

        st.subheader(
            t("safety")
        )

        s1, s2, s3 = st.columns(3)


        with s1:

            with st.container(
                border=True
            ):

                st.markdown(
                    "### " + t("allergens")
                )

                allergens = (
                    extraction.get(
                        "allergens"
                    )
                    or []
                )

                if allergens:

                    for item in allergens:

                        st.write(
                            f"• {item}"
                        )

                else:

                    st.write(
                        "No allergen information detected."
                    )


        with s2:

            with st.container(
                border=True
            ):

                st.markdown(
                    "### " + t("warnings")
                )

                warnings = (
                    extraction.get(
                        "warnings"
                    )
                    or []
                )

                if warnings:

                    for item in warnings:

                        st.write(
                            f"• {item}"
                        )

                else:

                    st.write(
                        "No warnings detected."
                    )


        with s3:

            with st.container(
                border=True
            ):

                st.markdown(
                    "### " + t("storage")
                )

                storage = (
                    extraction.get(
                        "storage_conditions"
                    )
                    or []
                )

                if storage:

                    for item in storage:

                        st.write(
                            f"• {item}"
                        )

                else:

                    st.write(
                        "No storage conditions detected."
                    )


        # ----------------------------------------------------
        # ADDITIONAL DECLARATIONS
        # ----------------------------------------------------

        declarations = (
            extraction.get(
                "additional_declarations"
            )
            or []
        )


        if declarations:

            with st.expander(
                t("additional_declarations")
            ):

                for item in declarations:

                    if isinstance(
                        item,
                        dict
                    ):

                        declaration = item.get(
                            "declaration",
                            "Declaration"
                        )

                        value = item.get(
                            "value",
                            ""
                        )

                        st.markdown(
                            f"**{declaration}**"
                        )

                        st.write(
                            value
                        )

                    else:

                        st.write(
                            f"• {item}"
                        )


        # ----------------------------------------------------
        # AI NOTES
        # ----------------------------------------------------

        notes = (
            extraction.get(
                "extraction_notes"
            )
            or []
        )


        if notes:

            with st.expander(
                t("ai_notes")
            ):

                for note in notes:

                    st.write(
                        f"• {note}"
                    )


        # ====================================================
        # COMPLIANCE
        # ====================================================

        st.divider()

        st.header(
            t("compliance")
        )


        overall_status = compliance.get(
            "overall_status",
            "REVIEW"
        )

        summary = compliance.get(
            "summary",
            {}
        )


        # ----------------------------------------------------
        # AUTOMATED COMPLIANCE INSIGHT
        # ----------------------------------------------------

        passed_count = summary.get(
            "pass",
            summary.get("passed", 0)
        )
        missing_count = summary.get("missing", 0)
        review_count = summary.get("review", 0)
        mismatch_count = summary.get("mismatch", 0)

        attention_count = (
            int(missing_count or 0)
            + int(review_count or 0)
            + int(mismatch_count or 0)
        )

        st.subheader(t("automated_insight_title"))

        if attention_count > 0:

            st.warning(
                f"**{t('issues_detected')}**  \n"
                f"\n\n**{t('items_require_review').format(count=attention_count)}**"
            )

            st.info(
                f"**{t('ai_insight')}**\n\n"
                f"{t('insight_attention').format(count=attention_count)}"
            )

        else:

            st.success(
                f"**{t('no_issues_detected')}**"
            )

            st.info(
                f"**{t('ai_insight')}**\n\n"
                f"{t('insight_pass')}"
            )

        st.warning(
            f"🔒 **{t('regulatory_disclaimer')}**\n\n"
            f"{t('inspection_notice')}"
        )

        if overall_status == "PASS":

            st.success(
                t("overall_pass")
            )

        elif overall_status == "MISMATCH":

            st.error(
                t("overall_mismatch")
            )

        else:

            st.warning(
                t("overall_review")
            )


        m1, m2, m3, m4 = st.columns(4)


        with m1:

            st.metric(
                "Passed",
                summary.get(
                    "pass",
                    summary.get(
                        "passed",
                        0
                    )
                )
            )


        with m2:

            st.metric(
                t("missing"),
                summary.get(
                    "missing",
                    0
                )
            )


        with m3:

            st.metric(
                t("review"),
                summary.get(
                    "review",
                    0
                )
            )


        with m4:

            st.metric(
                t("mismatch"),
                summary.get(
                    "mismatch",
                    0
                )
            )


        st.markdown(
            t("field_checks")
        )


        for check in compliance.get(
            "checks",
            []
        ):

            status = check.get(
                "status",
                "REVIEW"
            )

            field = check.get(
                "field",
                "Unknown"
            )

            message = check.get(
                "message",
                ""
            )

            text = (
                f"{status_icon(status)} "
                f"**{field}** — {message}"
            )


            if status == "PASS":

                st.success(
                    text
                )

            elif status == "MISMATCH":

                st.error(
                    text
                )

            else:

                st.warning(
                    text
                )


        st.caption(
            compliance.get(
                "disclaimer",
                ""
            )
        )


        # ====================================================
        # FOSCOS — FOOD ONLY
        # ====================================================

        fssai_number = extraction.get(
            "fssai_number"
        )

        flags = category_flags(
            extraction.get(
                "category"
            )
        )


        if flags["food"]:

            st.divider()

            st.header(
                t("fssai_verification")
            )


            if fssai_number:

                st.success(
                    f"FSSAI Number Detected: "
                    f"**{fssai_number}**"
                )

                st.markdown(
                    """
### FoSCoS Workflow

1. Keep the **PackCheck Chrome extension** enabled.
2. PackCheck opens FoSCoS automatically.
3. The extension fills the detected FSSAI number.
4. **Enter the CAPTCHA manually.**
5. Click Search.
6. PackCheck reads the official result.
7. Packet details are compared with the official record.
"""
                )


                @st.fragment(
                    run_every="1s"
                )
                def foscos_live_status():

                    current = (
                        load_verification_result()
                    )


                    if current:

                        try:

                            current_mtime = (
                                API_VERIFICATION_FILE
                                .stat()
                                .st_mtime
                            )

                        except Exception:

                            current_mtime = None


                        previous_mtime = (
                            st.session_state
                            .get(
                                "verification_file_mtime"
                            )
                        )


                        if (
                            previous_mtime is None
                            or current_mtime is None
                            or current_mtime > previous_mtime
                        ):

                            st.session_state.verification = (
                                current
                            )

                            st.session_state.verification_file_mtime = (
                                current_mtime
                            )

                            st.session_state.verification_start_time = (
                                None
                            )

                            st.success(
                                "✅ Official verification received."
                            )

                            st.rerun()

                            return


                    start_time = (
                        st.session_state
                        .get(
                            "verification_start_time"
                        )
                    )


                    if start_time:

                        remaining = max(
                            0,
                            int(
                                start_time
                                - time.time()
                                + 0.999
                            )
                        )

                        if remaining > 0:

                            elapsed = max(
                                0,
                                10 - remaining
                            )

                            st.info(
                                "⏳ Verifying through "
                                "Official FoSCoS — "
                                f"opening in **{remaining} "
                                "seconds**…"
                            )

                            st.progress(
                                min(
                                    elapsed / 10,
                                    1.0
                                ),
                                text=(
                                    "Preparing official "
                                    "verification"
                                )
                            )

                        else:

                            st.success(
                                "🚀 Opening Official "
                                "FoSCoS now…"
                            )

                            st.caption(
                                "Enter the CAPTCHA manually "
                                "and click Search. PackCheck "
                                "will detect the official result."
                            )

                    else:

                        st.info(
                            "⏳ Waiting for the official "
                            "FoSCoS verification result…"
                        )


                foscos_live_status()


            else:

                st.warning(
                    "No FSSAI number was confidently detected."
                )


        # ====================================================
        # BIS OFFICIAL VERIFICATION
        # ====================================================

        bis_applicable = bool(
            extraction.get(
                "bis_applicable"
            )
            or extraction.get(
                "is_number"
            )
            or extraction.get(
                "bis_license_number"
            )
        )


        if bis_applicable:

            st.divider()

            st.header(
                t("bis_verification")
            )

            st.success(
                "BIS evidence detected: "
                f"**{display_value(extraction.get('is_number'))}**"
            )


            if extraction.get(
                "bis_license_number"
            ):

                st.info(
                    "Detected BIS licence/registration: "
                    f"**{extraction.get('bis_license_number')}**"
                )


            st.markdown(
                """
### BIS Workflow

1. Keep the **PackCheck Chrome extension** enabled.
2. PackCheck opens the official BIS Know Your Standards page.
3. The extension fills the detected IS number and starts the search.
4. If multiple standards appear, **the inspector selects the correct result**.
5. The Licence tab is opened when available.
6. If multiple licences appear, **the inspector selects the correct licence**.
7. PackCheck compares the official record with the extracted package evidence.
8. No CAPTCHA/security mechanism is bypassed.

> **BIS Verified** means the official record was found and matched the extracted evidence. It does not by itself mean every legal requirement is satisfied.
"""
            )


        # ====================================================
        # BIS LIVE STATUS
        # ====================================================

        if (
            bis_applicable
            and not flags["food"]
        ):


            @st.fragment(
                run_every="1s"
            )
            def bis_live_status():

                current = (
                    load_verification_result()
                )


                if current:

                    try:

                        current_mtime = (
                            API_VERIFICATION_FILE
                            .stat()
                            .st_mtime
                        )

                    except Exception:

                        current_mtime = None


                    previous_mtime = (
                        st.session_state
                        .get(
                            "verification_file_mtime"
                        )
                    )


                    if (
                        previous_mtime is None
                        or current_mtime is None
                        or current_mtime > previous_mtime
                    ):

                        st.session_state.verification = (
                            current
                        )

                        st.session_state.verification_file_mtime = (
                            current_mtime
                        )

                        st.session_state.verification_start_time = (
                            None
                        )

                        st.success(
                            "✅ Official BIS verification received."
                        )

                        st.rerun()

                        return


                start_time = (
                    st.session_state
                    .get(
                        "verification_start_time"
                    )
                )


                if start_time:

                    remaining = max(
                        0,
                        int(
                            start_time
                            - time.time()
                            + 0.999
                        )
                    )


                    if remaining > 0:

                        st.info(
                            "⏳ Verifying through "
                            "Official BIS — opening in "
                            f"**{remaining} seconds**…"
                        )

                    else:

                        st.info(
                            "🚀 Official BIS verification "
                            "should now be open in the browser."
                        )

                else:

                    st.info(
                        "⏳ Waiting for the official "
                        "BIS verification result…"
                    )


            bis_live_status()


        # ====================================================
        # VERIFICATION DISPLAY
        # ====================================================

        verification = (
            st.session_state.verification
        )


        if verification:

            st.divider()

            verification_data = (
                verification.get(
                    "verification",
                    {}
                )
            )

            verification_type = str(
                verification_data.get(
                    "type",
                    "FOSCOS"
                )
            ).upper()

            portal_name = (
                "BIS"
                if verification_type == "BIS"
                else "FoSCoS"
            )


            st.header(
                f"🏛️ {portal_name} Verification Result"
            )


            official = (
                verification.get(
                    "officialData",
                    {}
                )
            )

            results = (
                verification_data.get(
                    "results",
                    {}
                )
            )

            overall = (
                verification_data.get(
                    "overallStatus",
                    "UNKNOWN"
                )
            )


            if overall == "VERIFIED":

                st.success(
                    "🟢 Overall Verification: VERIFIED"
                )

            elif "REVIEW" in overall:

                st.warning(
                    f"🔎 Overall Verification: "
                    f"{overall}"
                )

            else:

                st.error(
                    f"🔴 Overall Verification: "
                    f"{overall}"
                )


            a, b, c = st.columns(3)


            with a:

                st.markdown(
                    "**" + t("official_company") + "**"
                )

                st.write(
                    safe_value(
                        official.get(
                            "companyName"
                        )
                    )
                )


            with b:

                st.markdown(
                    "**" + t("license_type") + "**"
                )

                st.write(
                    safe_value(
                        official.get(
                            "licenseType"
                        )
                    )
                )


            with c:

                st.markdown(
                    "**" + t("official_status") + "**"
                )

                st.write(
                    safe_value(
                        official.get(
                            "status"
                        )
                    )
                )


            st.markdown(
                "### Packet vs Official"
            )


            comparison_rows = [
                (
                    "FSSAI License",
                    results.get(
                        "licenseNo",
                        {}
                    )
                ),

                (
                    "Company Name",
                    results.get(
                        "companyName",
                        {}
                    )
                ),

                (
                    "Address",
                    results.get(
                        "address",
                        {}
                    )
                ),
            ]


            for label, row in comparison_rows:

                status = row.get(
                    "status",
                    "UNKNOWN"
                )

                c1, c2, c3 = st.columns(
                    [1.5, 3, 3]
                )


                with c1:

                    st.markdown(
                        f"{status_icon(status)} "
                        f"**{label}**"
                    )


                with c2:

                    st.caption(
                        "Packet"
                    )

                    st.write(
                        safe_value(
                            row.get(
                                "packet"
                            )
                        )
                    )


                with c3:

                    st.caption(
                        "Official"
                    )

                    st.write(
                        safe_value(
                            row.get(
                                "official"
                            )
                        )
                    )


                similarity = row.get(
                    "similarity"
                )


                if similarity is not None:

                    st.progress(
                        min(
                            max(
                                float(
                                    similarity
                                ) / 100,
                                0.0
                            ),
                            1.0
                        ),
                        text=(
                            f"Similarity: "
                            f"{similarity}%"
                        )
                    )


                st.divider()


            # =================================================
            # PDF REPORT
            # =================================================

            st.header(
                t("inspection_report")
            )


            if st.button(
                t("generate_pdf"),
                type="primary",
                use_container_width=True
            ):

                try:

                    copy_verification_to_root()


                    report_path = generate_report(
                        image_path=(
                            st.session_state.image_path
                        ),

                        result_path=str(
                            RESULT_FILE
                        ),

                        verification_path=str(
                            VERIFICATION_FILE
                        )
                    )


                    st.session_state.report_path = (
                        str(report_path)
                    )


                    report_record = (
                        add_report_record(
                            report_path,
                            result,
                            verification
                        )
                    )


                    st.session_state.last_report_id = (
                        report_record[
                            "report_id"
                        ]
                    )


                    st.success(
                        "✅ PDF inspection report "
                        "generated — "
                        f"{report_record['report_id']}"
                    )


                except Exception as error:

                    st.error(
                        "❌ Report generation failed."
                    )

                    st.exception(
                        error
                    )


            report_path = (
                st.session_state.report_path
            )


            if (
                report_path
                and Path(
                    report_path
                ).exists()
            ):

                report_bytes = (
                    Path(
                        report_path
                    ).read_bytes()
                )


                st.download_button(
                    t("download_inspection"),
                    data=report_bytes,
                    file_name=Path(
                        report_path
                    ).name,
                    mime="application/pdf",
                    use_container_width=True
                )


        else:

            if (
                flags["food"]
                or bis_applicable
            ):

                st.info(
                    "⏳ Complete the official "
                    "verification workflow. PackCheck "
                    "will automatically load the official "
                    "result after the portal search is completed."
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(t("prototype"))
