# 📦 PackCheck AI

### AI-Powered Product Compliance & Smart Automation

**Scan • Analyze • Verify • Report**

PackCheck AI is an **AI-assisted smart automation and product compliance intelligence system** designed to help users extract information from product package labels, perform automated rule-based analysis, identify areas requiring further review, assist with official verification workflows, and generate structured inspection reports.

The system combines **AI-powered information extraction, automated data processing, rule-based compliance analysis, verification assistance, and structured reporting** into a unified inspection workflow.

> **Note:** PackCheck AI is an inspection-assistance and decision-support system. Final verification and regulatory decisions remain under the control of the authorized authority.

---

# 🎯 Problem

Modern product and regulatory inspection workflows often involve collecting information from multiple sources, checking large amounts of structured and unstructured data, and performing repetitive verification tasks manually.

This creates challenges such as:

* Time-consuming information collection
* Repetitive manual verification
* Difficulty consolidating information from different sources
* Increased possibility of human error
* Limited automation in preliminary inspection and analysis
* Difficulty converting extracted information into actionable insights

There is a need for a **smart, AI-assisted software solution** that can automate information extraction, intelligently analyze the collected data, identify areas requiring attention, and assist users in making informed decisions.

PackCheck AI addresses this challenge by combining **AI-powered information extraction, automated rule-based analysis, product compliance intelligence, official verification workflows, and structured reporting** into a unified inspection-assistance system.

---

# 💡 Solution

PackCheck AI is a **smart automation and product compliance intelligence platform** designed to reduce repetitive manual work involved in product inspection and preliminary compliance analysis.

The system follows an intelligent workflow:

```text
Product Image / PDF
        ↓
AI-Powered Information Extraction
        ↓
Structured Product Data
        ↓
Automated Analysis & Rule-Based Processing
        ↓
Compliance Intelligence & Insights
        ↓
Official Verification Assistance
        ↓
Structured Inspection Report
```

The system:

1. Accepts a product package image or PDF.
2. Uses AI-powered vision processing to extract relevant information.
3. Converts unstructured package information into structured data.
4. Automatically evaluates the extracted information against applicable rules and requirements.
5. Identifies missing, inconsistent, or potentially problematic information.
6. Generates actionable compliance insights for review.
7. Assists users with relevant official verification workflows.
8. Generates structured inspection reports.
9. Maintains inspection history through the dashboard.

PackCheck AI is designed as a **decision-support and automation system**. It assists users by reducing repetitive work and organizing relevant information, while final verification and regulatory decisions remain under the control of the authorized authority.

---

# 🤖 Smart Automation

PackCheck AI demonstrates **Smart Automation** by combining artificial intelligence, structured data processing, deterministic rule-based analysis, and automated reporting into a single workflow.

Instead of requiring the user to manually collect and evaluate every piece of product information, the system automatically:

* Extracts relevant information from product labels using AI-powered vision.
* Converts unstructured information into structured product data.
* Determines applicable compliance requirements.
* Performs automated rule-based checks.
* Identifies missing or potentially inconsistent information.
* Generates automated compliance insights.
* Provides recommended areas for further review.
* Assists with official verification workflows.
* Generates structured inspection reports.
* Maintains historical inspection records.

This approach reduces repetitive manual effort and allows users to focus their attention on cases that require human judgment or official verification.

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

PackCheck AI is designed so that additional regulatory verification workflows can be added for other categories of products and regulated items.

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

Reports provide users with a consolidated view of the analysis performed by the system.

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
                    │ Product Image / PDF │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   AI Vision Engine  │
                    │ Information         │
                    │ Extraction          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Structured Product  │
                    │       Data          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Smart Automation &  │
                    │ Rule-Based Analysis │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Product Compliance │
                    │    Intelligence     │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
       ┌──────────────────┐        ┌──────────────────┐
       │ Official         │        │ Additional       │
       │ Verification     │        │ Verification     │
       │ Workflows        │        │ Sources          │
       └────────┬─────────┘        └────────┬─────────┘
                │                           │
                └─────────────┬─────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │ Reports, Insights   │
                    │ & Inspection History│
                    └─────────────────────┘
```

---

# 🛠️ Tech Stack

| **Technology**           | **Purpose**                            |
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
git clone https://github.com/PackCheck-AI/PackCheck-AI.git
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
1. Upload Product
       ↓
2. AI Information Extraction
       ↓
3. Structure Extracted Data
       ↓
4. Automated Analysis
       ↓
5. Generate Compliance Intelligence
       ↓
6. Review Identified Findings
       ↓
7. Perform Official Verification
       ↓
8. Generate Inspection Report
       ↓
9. Store Inspection History
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

PackCheck AI is currently developed as a prototype for the **Smart India Hackathon – Student Innovation** track under the **Smart Automation** theme.

The current prototype demonstrates how AI and automated data processing can be applied to a real-world inspection and compliance workflow.

Current capabilities include:

* AI-powered product information extraction
* Automated rule-based analysis
* Product compliance intelligence
* Automated compliance insights
* FSSAI / FoSCoS verification assistance
* BIS verification workflow
* Automated inspection reports
* Inspection history
* Streamlit-based inspector dashboard

The architecture is designed to be extensible, allowing additional product categories, regulatory requirements, data sources, and verification workflows to be integrated as the system evolves.

---

# 🎯 Smart India Hackathon – Student Innovation

**Category:** Student Innovation
**Theme:** Smart Automation
**Project:** PackCheck AI

PackCheck AI demonstrates how **artificial intelligence, automated data processing, and rule-based intelligence** can be combined to address repetitive and information-intensive inspection workflows.

The project focuses on transforming unstructured product information into **structured data, automated analysis, actionable insights, and verification assistance** through a unified software platform.

By automating repetitive information extraction and preliminary analysis, PackCheck AI aims to improve workflow efficiency while keeping human judgment and official verification at the appropriate stages.

The solution is designed around the principles of:

* **AI-assisted automation**
* **Intelligent information extraction**
* **Automated data analysis**
* **Actionable intelligence**
* **Human-in-the-loop verification**
* **Extensible software architecture**
* **Structured reporting and traceability**

---

# 👥 Team

Developed as part of the **Smart India Hackathon – Student Innovation** initiative.

---

# 📌 Disclaimer

PackCheck AI is a prototype **AI-assisted smart automation and decision-support system**.

AI-generated information extraction and automated analysis are intended to assist users by reducing repetitive work and identifying areas requiring further review. They should not replace official verification, regulatory authorities, or the judgment of an authorized authority.

Official portals, regulatory databases, and authorized authorities remain the source of final verification and compliance decisions.
