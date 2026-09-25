# 📦 PackCheck AI

### AI-Powered Automated Package Compliance Checking

**Scan • Analyze • Verify • Report**

PackCheck AI is an AI-powered inspection assistance system designed to help inspectors extract mandatory declarations from packaged commodity labels, perform automated rule-based compliance checks, assist with official verification workflows, and generate structured inspection reports.

The latest prototype also presents automated compliance insights, helping convert extracted package information into useful findings that can be reviewed by an authorized inspector.

---

## 🎯 Problem

Inspecting packaged commodities manually requires checking multiple declarations on product labels and verifying them against applicable regulatory requirements.

Important information such as:

* Product name
* MRP
* Net quantity
* Manufacturer / Packer / Importer
* Address
* Date of manufacture / packing
* Country of origin
* Consumer care information
* FSSAI licence / registration details
* BIS / IS information

may need to be checked individually.

This can make the inspection process time-consuming and repetitive, while increasing the possibility of manual errors.

PackCheck AI brings these steps together into a single inspection-assistance workflow using AI-powered extraction, automated compliance analysis, official verification workflows, and automated reporting.

---

## 💡 Solution

PackCheck AI follows the workflow:

```text
Package Image / PDF
        ↓
Gemini Vision Extraction
        ↓
Structured Product Information
        ↓
Automated Compliance Engine
        ↓
Compliance Insights
        ↓
Official Verification Workflows
        ↓
Inspection Report
```

The system:

1. Accepts a package image or PDF.
2. Extracts relevant label information using Gemini Vision.
3. Identifies mandatory and applicable declarations.
4. Performs automated rule-based compliance checks.
5. Identifies potential issues and generates actionable compliance insights.
6. Assists with official verification workflows such as FSSAI/FoSCoS and BIS.
7. Generates a structured inspection report.
8. Maintains inspection history through the dashboard.

> **Note:** PackCheck AI is an inspection-assistance system. Final verification and regulatory decisions remain under the control of the authorized inspector.

---

# 🤖 Smart Automation

PackCheck AI demonstrates smart automation by combining artificial intelligence, information extraction, and automated rule-based analysis.

The system automatically:

* Extracts package information using AI-powered vision processing.
* Converts extracted label information into structured product data.
* Evaluates the information against applicable compliance requirements.
* Identifies missing or potentially incorrect declarations.
* Generates automated compliance insights and recommended actions.
* Produces structured inspection reports.

This reduces repetitive manual checking and allows inspectors to focus on information that requires further review.

---

# ✨ Key Features

## 🔍 AI-Powered Label Extraction

PackCheck AI uses **Google Gemini Vision** to extract information from package labels.

The extraction workflow can identify:

* Product name
* Brand
* Manufacturer / Packer / Importer
* Address
* MRP
* Net quantity
* Batch / Lot number
* Manufacturing / Packing date
* Expiry / Best-before information
* Country of origin
* Consumer care information
* Ingredients
* FSSAI information
* BIS / IS information

The extraction process is designed to avoid inventing information that is not present on the package.

---

## ⚖️ Automated Rule-Based Compliance Engine

The extracted information is evaluated using an applicability-aware rule-based compliance engine.

Checks can include:

* MRP declaration
* Net quantity
* Manufacturer / Packer / Importer details
* Address
* Country of origin
* Date declarations
* Consumer care information
* Ingredients where applicable
* FSSAI details where applicable
* BIS / Indian Standard information where applicable
* Additional product-specific declarations

The compliance engine keeps regulatory rules separate from AI-generated extraction so that extracted information is not treated as the final compliance decision.

---

## 💡 Automated Compliance Insights

After the compliance checks are completed, PackCheck AI provides a clear automated summary of the analysis.

Depending on the result, the system can display:

* **Potential Compliance Issues Detected**
* Number of items requiring review
* Information that was successfully detected
* Missing or potentially incorrect declarations
* An automated insight explaining the areas requiring attention
* Recommended actions for further review

For example:

```text
⚠️ Potential Compliance Issues Detected

3 items require review.

AI Insight:
The automated screening identified declarations that may require
further verification. Review the highlighted requirements before
making a final regulatory decision.
```

If no potential issues are identified, the system provides a corresponding successful compliance summary.

> 🔒 **Final regulatory decisions remain with the authorized inspector.** PackCheck AI provides automated preliminary screening and decision-support assistance and does not replace official regulatory judgment.

---

# 🏛️ Official Verification Workflows

## FSSAI / FoSCoS

For applicable food products, PackCheck AI assists inspectors with the **FSSAI/FoSCoS verification workflow**.

The system can assist with:

* Identifying the FSSAI licence / registration number from the package
* Opening the FoSCoS verification page
* Filling relevant product information
* Assisting with state and district selection
* Allowing the inspector to manually enter CAPTCHA
* Continuing the verification using the official FoSCoS portal

CAPTCHA remains a manual step to keep the verification under the inspector's control.

---

## BIS Verification

For products associated with BIS standards or licences, PackCheck AI provides a BIS verification workflow.

The workflow can assist the inspector in:

1. Identifying an IS standard number from the extracted information.
2. Opening the BIS **Know Your Standards** page.
3. Entering the relevant IS number.
4. Opening the relevant licence information.
5. Entering or checking licence-related information.
6. Performing the final verification on the official BIS portal.

The official portal remains the source for the final verification.

---

## 🔗 Extensible Verification Architecture

PackCheck AI is designed so that additional regulatory verification workflows can be added for other categories of packaged commodities and regulated products.

This allows the system to expand beyond a single regulatory database or product category.

---

# 📄 Automated Inspection Reports

After analysis, PackCheck AI generates a structured inspection report containing information such as:

* Analysis / Inspection ID
* Product information
* Extracted label information
* Compliance checks
* Applicable rule / evidence information
* Verification information
* Inspection outcome
* Timestamp

Reports provide inspectors with a consolidated view of the analysis performed by the system.

---

# 📊 Inspector Dashboard

The Streamlit dashboard provides an interface for inspectors to:

* Upload package images or PDFs
* View extracted product information
* Review automated compliance insights
* Review detailed compliance checks
* Access verification workflows
* View previous inspection records
* Generate inspection reports

The dashboard is intended to keep the complete inspection workflow in one place.

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │   Package Image /   │
                    │        PDF          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Gemini Vision    │
                    │  Label Extraction   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Extracted Product   │
                    │      Details        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Automated Compliance│
                    │       Engine        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Compliance Insights │
                    │ & Review Findings   │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
       ┌──────────────────┐        ┌──────────────────┐
       │ FSSAI / FoSCoS  │        │       BIS        │
       │   Verification  │        │   Verification   │
       └────────┬─────────┘        └────────┬─────────┘
                │                           │
                └─────────────┬─────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │ Inspection Report   │
                    │    & Dashboard      │
                    └─────────────────────┘
```

---

# 🛠️ Tech Stack

| Technology               | Purpose                                |
| ------------------------ | -------------------------------------- |
| **Python**               | Core application and compliance logic  |
| **Streamlit**            | Inspector dashboard                    |
| **Google Gemini Vision** | Package label extraction               |
| **OpenCV**               | Image processing                       |
| **JavaScript**           | Browser verification workflows         |
| **HTML / CSS**           | Verification extension interface       |
| **JSON**                 | Structured data and inspection history |
| **ReportLab**            | Inspection report generation           |
| **Git / GitHub**         | Version control and collaboration      |

---

# 📁 Project Structure

```text
PackCheck-AI/
│
├── API/
│   ├── server.py
│   └── packcheck_result.json
│
├── Extraction/
│   └── extractor.py
│
├── Extension/
│   └── FoSCoS-Autofill/
│
├── Reports/
│   └── report_generator.py
│
├── Verification/
│   └── compliance_engine.py
│
├── data/
│   └── report_history.json
│
├── app.py
├── report_server.py
├── verification.js
├── requirements.txt
├── start_packcheck.bat
├── packcheck_result.json
├── .gitignore
└── README.md
```

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/Moulya-k-m/PackCheck-AI.git
cd PackCheck-AI
```

## 2. Create a virtual environment

### Windows

```bash
python -m venv sih_env
```

Activate it:

```bash
sih_env\Scripts\activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 API Configuration

PackCheck AI requires a Gemini API key for AI-powered label extraction.

Create a local `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

**Never commit your real API key to GitHub.**

The `.env` file should be included in `.gitignore`.

Example:

```gitignore
.env
*.env
__pycache__/
.venv/
sih_env/
```

> Each developer using the project should create their own local `.env` file with their own API key.

---

# ▶️ Running the Application

After activating the virtual environment:

```bash
streamlit run app.py
```

The Streamlit application will open in your browser.

If required by the verification workflow, start the report server separately:

```bash
python report_server.py
```

---

# 🔄 Inspection Workflow

```text
1. Upload Package
       ↓
2. AI Label Extraction
       ↓
3. Review Extracted Details
       ↓
4. Automated Compliance Analysis
       ↓
5. Review Compliance Insights
       ↓
6. Perform Official Verification
       ↓
7. Generate Inspection Report
       ↓
8. Store Inspection History
```

---

# 🔐 Security

PackCheck AI uses API credentials through environment variables.

Sensitive information such as:

* API keys
* `.env` files
* Authentication credentials

should **not** be committed to the repository.

Official verification workflows are designed to keep actions such as CAPTCHA entry and final verification under the inspector's control.

---

# 🚧 Project Status

PackCheck AI is currently developed as a prototype for **Smart India Hackathon (SIH) Student Innovation – Smart Automation**.

Current prototype capabilities include:

* AI-based package label extraction
* Automated rule-based compliance checking
* Automated compliance insights
* FSSAI / FoSCoS verification assistance
* BIS verification workflow
* Automated inspection reports
* Inspection history
* Streamlit-based inspector dashboard

Additional regulatory categories and verification workflows can be integrated as the system evolves.

---

# 🎯 Smart India Hackathon – Student Innovation

**Category:** Student Innovation
**Theme:** Smart Automation
**Project:** PackCheck AI

PackCheck AI demonstrates the intelligent use of artificial intelligence and automated rule-based analysis to transform package-label information into useful compliance insights.

The project focuses on reducing repetitive manual work during packaged commodity inspections by combining AI-assisted information extraction, deterministic compliance rules, official verification workflows, and structured reporting.

---

# 👥 Team

Developed as part of the **Smart India Hackathon**.

---

## 📌 Disclaimer

PackCheck AI is a prototype inspection-assistance and decision-support system.

AI-generated extraction and automated rule checks are intended to assist inspectors and identify areas requiring further review. They should not replace official regulatory verification or the judgment of an authorized authority.

Official portals and regulatory authorities remain the source of final verification and compliance decisions.
