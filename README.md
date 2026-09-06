# AI Document Intelligence

**Zyroo AI/ML Internship — Week 2 Task**  
An end-to-end Document Intelligence MVP that automates document ingestion, text extraction, type classification, and structured field extraction with an intuitive Streamlit interface.

---

## Overview

**AI Document Intelligence** is an automated document processing system designed to eliminate manual reading and data entry from common business and recruitment documents. Users simply upload a document (PDF or image), and the application automatically extracts its textual content, determines whether it is an **Invoice**, a **Resume**, or **Other**, and extracts key structured fields (such as invoice numbers, amounts, candidate contact details, and technical skills).

The project is built as a transparent, dependable, and explainable MVP using Python, PyMuPDF, regular expressions, and Streamlit, featuring an OCR fallback mechanism for scanned files and an optional machine learning classification mode.

---

## Problem

Manual document processing is slow, labor-intensive, repetitive, and prone to human error. Organizations handle hundreds of invoices, vendor bills, and candidate resumes daily. Reading each file manually to extract metadata such as payment amounts, due dates, candidate emails, and skills creates administrative bottlenecks and delays decision-making.

---

## Solution

This application provides an automated, zero-friction pipeline:
1. Accepts multi-format document uploads (PDF, JPG, JPEG, PNG).
2. Validates file integrity and rejects unsupported formats gracefully.
3. Extracts clean text using **PyMuPDF** for digital PDFs and falls back to **Tesseract OCR** for scanned files or images.
4. Identifies the document type (**Invoice**, **Resume**, or **Other**) using transparent keyword scoring or an optional ML classifier.
5. Extracts structured domain-specific fields using specialized regular expressions and layout heuristics.
6. Displays the extracted metadata on an interactive dashboard with instant JSON and raw text export options.

---

## Features

- **Multi-Format Ingestion**: Supports `.pdf`, `.jpg`, `.jpeg`, and `.png`.
- **High-Performance PDF Extraction**: Direct, lightning-fast extraction of native selectable text via **PyMuPDF**.
- **Automated OCR Fallback**: Renders pages to images and invokes **Tesseract OCR** when native text is absent.
- **Transparent Document Classification**: Fast, rule-based keyword matching that never masquerades as a black-box model.
- **Optional ML Enhancement**: Integrated TF-IDF + Logistic Regression toggle for classification comparison.
- **Structured Field Extraction**:
  - **Invoice**: Invoice Number, Date, Company Name, Total Amount.
  - **Resume**: Candidate Name, Email, Phone Number, Skills.
- **Truthful Output ("Not found")**: Missing fields display `"Not found"` instead of hallucinating values.
- **Interactive Streamlit UI/UX**: Includes live system health indicators, file metadata cards, status progress chips, and downloadable JSON/TXT results.
- **Resilient Error Handling**: Never crashes on corrupted files, zero-byte uploads, or unsupported formats.

---

## Technology Stack

| Technology | Purpose |
| :--- | :--- |
| **Python 3.10+** | Core programming language |
| **Streamlit** | Interactive web dashboard and UI |
| **PyMuPDF (`fitz`)** | PDF parsing and high-resolution rasterization |
| **pytesseract** | Python wrapper for Tesseract OCR engine |
| **Pillow (PIL)** | Image manipulation and preprocessing |
| **Regular Expressions (`re`)** | Deterministic, pattern-based field extraction |
| **Scikit-Learn** | TF-IDF vectorization and Logistic Regression (Optional ML) |
| **Git & GitHub** | Version control and collaborative deployment |

---

## Architecture & Workflow

```
 USER
  ↓
 UPLOAD DOCUMENT (PDF / JPG / JPEG / PNG)
  ↓
 VALIDATE FILE TYPE
  ↓
 TEXT EXTRACTION (PyMuPDF)
  ↓
 [Has Selectable Text?]
     ├── Yes ──> EXTRACTED TEXT
     └── No  ──> TRIGGER OCR FALLBACK (Pillow + pytesseract)
                     ↓
             CLASSIFY DOCUMENT TYPE
             (Rule-Based Keyword Scoring / Optional ML)
                     ↓
             EXTRACT STRUCTURED FIELDS
             ├── Invoice: Invoice No, Date, Company, Total
             ├── Resume: Name, Email, Phone, Skills
             └── Other: General Text & Notice
                     ↓
             DISPLAY RESULTS DASHBOARD
                     ↓
             EXPORT / DOWNLOAD (JSON / TXT)
```

---

## Installation

Follow these exact steps to set up the project on Windows:

### 1. Clone or Open the Repository
```powershell
cd ai-document-intelligence
```

### 2. Create and Activate a Virtual Environment
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## Run the Application

Launch the Streamlit web interface:
```powershell
streamlit run app.py
```

The application will open automatically in your default browser at:
```
http://localhost:8501
```

*(If port 8501 is occupied, Streamlit will automatically assign the next available port, e.g., 8502 or 8504).*

---

## OCR Setup (Tesseract OCR)

For digital PDFs with selectable text, PyMuPDF works out-of-the-box without extra installations.

However, to enable **OCR for scanned PDFs and image files (`.jpg`, `.png`)**, Tesseract OCR must be installed on your Windows machine:

1. Download the Windows installer from:  
   **[UB-Mannheim Tesseract OCR Wiki](https://github.com/UB-Mannheim/tesseract/wiki)**  
   *(Recommended version: `tesseract-ocr-w64-setup-5.x.exe`)*
2. Run the installer and install to the default path:  
   `C:\Program Files\Tesseract-OCR`
3. Add `C:\Program Files\Tesseract-OCR` to your System `PATH` environment variable.
4. Restart your terminal or command prompt.

> **Note on App Behavior**: If Tesseract is not installed, the application **will not crash**. It displays a clear, helpful status indicator in the sidebar and an informational alert when scanned images are uploaded, explaining that digital PDF extraction remains fully operational.

---

## Testing & Sample Verification

The repository includes three verified sample documents in the `samples/` directory:

| Filename | Expected Type | Detected Type | Fields Found | Fields Not Found |
| :--- | :--- | :--- | :--- | :--- |
| **`samples/invoice_1.pdf`** | `Invoice` | `Invoice` | **Invoice Number**: `INV-2026-001`<br>**Date**: `15/03/2026`<br>**Company Name**: `TechCorp Solutions Inc.`<br>**Total Amount**: `$ 1,450.00` | *None (All 4 found)* |
| **`samples/invoice_2.pdf`** | `Invoice` | `Invoice` | **Invoice Number**: `INV-8832`<br>**Date**: `2026-04-10`<br>**Company Name**: `Apex Retailers Pvt Ltd`<br>**Total Amount**: `Rs. 78,500` | *None (All 4 found)* |
| **`samples/resume_1.pdf`** | `Resume` | `Resume` | **Candidate Name**: `Alex Smith`<br>**Email**: `alex.smith@email.com`<br>**Phone**: `+91 98765 43210`<br>**Skills**: `Python, SQL, JavaScript, C++, Streamlit, PyMuPDF, Scikit-learn, PyTorch, Docker, FastAPI, Pandas, Git` | *None (All 4 found)* |

You can test these files in 1 click using the **Quick Test Samples** selector in the Streamlit sidebar!

---

## Screenshots

Demo screenshots can be viewed or captured into the `screenshots/` directory:

| Screen | Description | File Location |
| :--- | :--- | :--- |
| **1. Upload Screen** | Main interface with sidebar system status indicators and drag-and-drop uploader. | `screenshots/01_upload_screen.png` |
| **2. Invoice Result** | Analysis cards showing Invoice Number, Date, Company, and Total Amount. | `screenshots/02_invoice_result.png` |
| **3. Resume Result** | Analysis cards showing Candidate Name, Email, Phone, and Skills badges. | `screenshots/03_resume_result.png` |
| **4. Extracted Text** | Expandable text view with character/word counts and JSON/TXT download options. | `screenshots/04_extracted_text.png` |

---

## Limitations

- **Rule-Based Classification**: Classification relies on domain keyword density. Highly unconventional documents with mixed terminology may be categorized as `Other`.
- **Pattern-Based Field Extraction**: Field extraction uses flexible regular expressions and layout heuristics. Non-standard date formats or heavily skewed tables may require custom regex patterns.
- **OCR System Dependency**: OCR requires the Tesseract binary to be installed on the host operating system.
- **Complex Multi-Column Layouts**: PyMuPDF extracts text in reading order; complex multi-column layouts without clear line breaks can occasionally interleave text.

---

## Future Improvements

- **Layout-Aware AI Models**: Integrate LayoutLM or Donut for vision-and-layout-based document understanding.
- **Expanded Document Classes**: Add support for Medical Prescriptions, Contracts, Bank Statements, and ID Cards.
- **Table Structure Extraction**: Implement Camelot / pdfplumber for tabular line-item extraction.
- **RESTful API Endpoint**: Add a FastAPI microservice alongside the Streamlit UI for enterprise system integration.
- **Persistent Database Storage**: Store processed document metadata and audit trails in PostgreSQL or SQLite.

---

## Deployment (Streamlit Community Cloud)

To deploy this application to Streamlit Community Cloud:

1. Push your repository to GitHub (ensure `app.py` and `requirements.txt` are at the repository root).
2. Go to **[share.streamlit.io](https://share.streamlit.io)** and log in with GitHub.
3. Click **New app**, select repository `ai-document-intelligence`, branch `main`, and main file path `app.py`.
4. (Optional for OCR) Add a `packages.txt` file containing `tesseract-ocr` if you want Tesseract OCR enabled on the cloud Linux container.
5. Click **Deploy!**

---

## GitHub Setup Commands

Use these exact commands to initialize and push your project to GitHub:

```bash
# 1. Initialize Git repository
git init

# 2. Stage all files
git add .

# 3. Commit your changes
git commit -m "Build AI Document Intelligence MVP"

# 4. Set main branch
git branch -M main

# 5. Add remote GitHub repository (replace with your repo URL)
git remote add origin https://github.com/<YOUR_USERNAME>/ai-document-intelligence.git

# 6. Push to GitHub
git push -u origin main
```

---

## Evaluation Guide (For Zyroo AI/ML Evaluator)

When presenting this project during your internship evaluation:
1. **Explain the Architecture**: Highlight the separation between file ingestion, extraction (PyMuPDF with OCR fallback), classification, and field parsing.
2. **Demonstrate Both Invoice & Resume**: Use the sidebar sample loader to demonstrate `invoice_1.pdf`, `invoice_2.pdf`, and `resume_1.pdf` live.
3. **Showcase Truthfulness**: Point out that when a field cannot be matched with confidence, it cleanly outputs `"Not found"` rather than hallucinating fake data.
4. **Highlight Resilience**: Demonstrate error handling by attempting to upload a text file or image when OCR is unavailable—showing that the app never crashes.
5. **Discuss Rule-based vs. ML**: Explain why rule-based extraction was prioritized for high transparency and speed, and showcase the optional TF-IDF ML toggle.
