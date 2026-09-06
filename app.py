"""
AI Document Intelligence MVP
Zyroo AI/ML Internship - Week 2 Task

An end-to-end document processing application built with Streamlit, PyMuPDF,
Pillow, pytesseract, and regular expressions. It ingests PDFs and images,
extracts text with OCR fallback, classifies documents as Invoice, Resume, or Other,
and extracts domain-specific structured fields.
"""

import os
import io
import re
import json
import shutil
from typing import Tuple, Dict, Any, Optional

import streamlit as st
import pymupdf
from PIL import Image
import pytesseract

# Optional Machine Learning Classifier imports
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


# =====================================================================
# SYSTEM CONFIGURATION & TESSERACT OCR DISCOVERY
# =====================================================================

def configure_tesseract() -> bool:
    """
    Checks if Tesseract OCR is available on the host machine.
    Checks standard Windows installation paths if not on system PATH.
    Returns True if Tesseract is detected and configured, False otherwise.
    """
    # 1. Check if already in PATH
    if shutil.which("tesseract"):
        return True

    # 2. Check standard Windows default paths
    windows_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
    ]

    for path in windows_paths:
        if os.path.isfile(path):
            pytesseract.pytesseract.tesseract_cmd = path
            return True

    return False


TESSERACT_AVAILABLE = configure_tesseract()


# =====================================================================
# 1. TEXT EXTRACTION ENGINES (PyMuPDF & OCR FALLBACK)
# =====================================================================

def extract_text_from_pdf(pdf_bytes: bytes) -> Tuple[str, bool, str]:
    """
    Extracts text from an uploaded PDF file using PyMuPDF.
    If selectable text is missing or negligible (scanned document),
    automatically triggers OCR fallback using PyMuPDF page rendering and pytesseract.

    Returns:
        (extracted_text, used_ocr, status_message)
    """
    try:
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    except Exception as e:
        return "", False, f"Failed to open PDF document: {str(e)}"

    if doc.page_count == 0:
        return "", False, "The uploaded PDF document contains no pages."

    page_texts = []
    for page_num in range(doc.page_count):
        try:
            page = doc.load_page(page_num)
            text = page.get_text("text")
            if text:
                page_texts.append(text.strip())
        except Exception:
            continue

    combined_text = "\n\n".join(page_texts).strip()

    # If selectable text is sufficient (at least 20 alphanumeric characters)
    alphanumeric_count = len(re.findall(r"\w", combined_text))
    if alphanumeric_count >= 20:
        doc.close()
        return combined_text, False, "Text extraction successful (Native PDF selectable text)"

    # Fallback to OCR if selectable text is insufficient
    ocr_text, ocr_success, ocr_msg = ocr_pdf(doc)
    doc.close()

    if ocr_success and len(re.findall(r"\w", ocr_text)) > 0:
        return ocr_text, True, "No selectable text detected — successfully extracted using OCR fallback."
    elif not TESSERACT_AVAILABLE:
        return (
            combined_text,
            False,
            "No selectable text detected. OCR fallback is unavailable because Tesseract OCR is not installed or configured."
        )
    else:
        return ocr_text, True, f"OCR completed with message: {ocr_msg}"


def ocr_pdf(doc: pymupdf.Document) -> Tuple[str, bool, str]:
    """
    Renders PDF pages to high-resolution images and extracts text via pytesseract.
    """
    if not TESSERACT_AVAILABLE:
        return "", False, "Tesseract OCR executable not found on host."

    extracted_pages = []
    try:
        for page_num in range(min(doc.page_count, 10)):  # Safeguard: first 10 pages
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=200)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            page_text = pytesseract.image_to_string(img)
            if page_text.strip():
                extracted_pages.append(page_text.strip())

        full_text = "\n\n".join(extracted_pages).strip()
        return full_text, True, "OCR extraction completed successfully."
    except Exception as e:
        return "", False, f"Error occurred during PDF OCR: {str(e)}"


def extract_text_from_image(image_bytes: bytes) -> Tuple[str, bool, str]:
    """
    Extracts text from an image (JPG, JPEG, PNG) using Pillow and pytesseract.
    """
    if not TESSERACT_AVAILABLE:
        return (
            "",
            False,
            "Tesseract OCR is not installed or configured. Please install Tesseract to extract text from images."
        )

    try:
        img = Image.open(io.BytesIO(image_bytes))
        # Basic preprocessing: convert palette or RGBA to RGB
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        text = pytesseract.image_to_string(img)
        cleaned_text = text.strip()

        if not cleaned_text:
            return "", True, "OCR completed, but no legible text was detected in the image."

        return cleaned_text, True, "Text extracted successfully using Tesseract OCR."
    except Exception as e:
        return "", False, f"Image processing error: {str(e)}"


# =====================================================================
# 2. DOCUMENT CLASSIFICATION (RULE-BASED & OPTIONAL ML)
# =====================================================================

INVOICE_KEYWORDS = [
    "invoice", "invoice number", "invoice no", "inv-", "inv #", "inv no",
    "bill to", "billed to", "tax invoice", "amount due", "balance due",
    "total amount", "subtotal", "gstin", "payment terms", "due date",
    "item particulars", "description", "qty", "quantity", "unit price"
]

RESUME_KEYWORDS = [
    "resume", "curriculum vitae", "cv", "experience", "work experience",
    "education", "skills", "technical expertise", "projects", "summary",
    "professional summary", "employment", "certifications", "bachelor",
    "master", "university", "github", "linkedin", "competencies"
]


def classify_rule_based(text: str) -> Tuple[str, str, Dict[str, Any]]:
    """
    Classifies the document as 'Invoice', 'Resume', or 'Other' based on keyword occurrence counts.
    Returns: (document_type, method_name, details_dict)
    """
    lower_text = text.lower()

    # Compute matches for invoices
    invoice_score = 0
    matched_invoice_kws = []
    for kw in INVOICE_KEYWORDS:
        count = lower_text.count(kw)
        if count > 0:
            invoice_score += count
            matched_invoice_kws.append(f"{kw} ({count})")

    # Compute matches for resumes
    resume_score = 0
    matched_resume_kws = []
    for kw in RESUME_KEYWORDS:
        count = lower_text.count(kw)
        if count > 0:
            resume_score += count
            matched_resume_kws.append(f"{kw} ({count})")

    # Classification decision
    if invoice_score > resume_score and invoice_score >= 2:
        doc_type = "Invoice"
    elif resume_score > invoice_score and resume_score >= 2:
        doc_type = "Resume"
    else:
        doc_type = "Other"

    details = {
        "invoice_score": invoice_score,
        "resume_score": resume_score,
        "matched_invoice_keywords": matched_invoice_kws[:6],
        "matched_resume_keywords": matched_resume_kws[:6],
    }

    return doc_type, "Rule-based classification", details


# Optional ML Enhancement (TF-IDF + Logistic Regression)
@st.cache_resource
def train_optional_ml_classifier():
    """
    Trains a lightweight in-memory TF-IDF + Logistic Regression classifier
    on representative sample texts as an optional enhancement.
    """
    if not SKLEARN_AVAILABLE:
        return None, None

    training_docs = [
        # Invoices
        "Tax Invoice Invoice No: INV-1002 Date: 2026-01-10 Bill To Acme Corp Total Amount: $450.00 Subtotal Payment Terms Due Date",
        "INVOICE TechCorp Solutions Invoice Number: INV-9921 Total Amount Due: $1,250.00 Description Qty Unit Price",
        "Commercial Invoice Bill To Client Ltd Amount Due: ₹45,000 GSTIN Tax Description Total Hours Rate",
        "Invoice receipt for hardware items item particulars qty balance due total: $890.00",
        "Tax invoice Apex Retailers Private Limited Billed to Sharma Electronics Total Amount: ₹78,500",

        # Resumes
        "Alex Smith Software Engineer Resume Email: alex@test.com Phone: 9876543210 Skills: Python Streamlit PyTorch Experience Education",
        "Curriculum Vitae John Doe Data Scientist Technical Expertise: Machine Learning SQL Docker Work Experience Projects",
        "Jane Developer Professional Summary 4 years experience in Full Stack Development Education Bachelor of Technology Skills Java React",
        "Resume Jane Smith AI Engineer Employment History Nexa Systems GitHub LinkedIn Education Master of Science",
        "Curriculum Vitae Alex Smith Skills & Technical Expertise: Python PyMuPDF Scikit-learn FastAPI Education VTU",

        # Other
        "Meeting Minutes Project update discussion regarding Q3 roadmap. Attendees agreed to review timelines next week.",
        "Terms and Conditions Agreement. This agreement is entered between party A and party B for general service guidelines.",
        "A brief overview of renewable energy systems and recent solar cell efficiencies published in scientific journals.",
        "Company picnic notice. All employees are invited to attend the annual gathering this Saturday at Central Park."
    ]

    training_labels = [
        "Invoice", "Invoice", "Invoice", "Invoice", "Invoice",
        "Resume", "Resume", "Resume", "Resume", "Resume",
        "Other", "Other", "Other", "Other"
    ]

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
    X = vectorizer.fit_transform(training_docs)
    clf = LogisticRegression(random_state=42)
    clf.fit(X, training_labels)

    return vectorizer, clf


def classify_with_ml(text: str) -> Tuple[str, str, Dict[str, Any]]:
    """
    Classifies document using the optional TF-IDF + Logistic Regression model.
    Falls back to rule-based if scikit-learn is unavailable.
    """
    vectorizer, clf = train_optional_ml_classifier()
    if vectorizer is None or clf is None:
        return classify_rule_based(text)

    X_test = vectorizer.transform([text])
    predicted_type = clf.predict(X_test)[0]
    probabilities = clf.predict_proba(X_test)[0]
    classes = clf.classes_

    prob_dict = {cls: round(float(prob), 3) for cls, prob in zip(classes, probabilities)}

    return predicted_type, "TF-IDF + Logistic Regression (Optional ML)", prob_dict


# =====================================================================
# 3. FIELD EXTRACTION ENGINES
# =====================================================================

def extract_invoice_fields(text: str) -> Dict[str, str]:
    """
    Extracts key fields for invoices using regex and heuristic rules:
    - Invoice Number
    - Date
    - Company Name
    - Total Amount
    """
    fields = {
        "Invoice Number": "Not found",
        "Date": "Not found",
        "Company Name": "Not found",
        "Total Amount": "Not found"
    }

    # 1. Invoice Number Extraction
    inv_num_patterns = [
        r"(?i)\b(?:invoice\s*(?:no\.?|number|#|id)|inv\s*(?:no\.?|number|#)|bill\s*(?:no\.?|number|#))\s*[:#\-]?\s*([A-Za-z0-9\-_/]+)",
        r"(?i)\binvoice\s*[:#]\s*([A-Za-z0-9\-_/]+)",
        r"(?i)\b(INV-[A-Za-z0-9\-_/]+)\b",
    ]
    for pattern in inv_num_patterns:
        match = re.search(pattern, text)
        if match:
            candidate = match.group(1).strip().strip(":,")
            if len(candidate) >= 3 and candidate.lower() not in ["invoice", "tax", "date", "bill", "due"]:
                fields["Invoice Number"] = candidate
                break

    # 2. Date Extraction
    date_patterns = [
        r"(?i)\b(?:date|invoice\s*date|dated|issue\s*date)\s*[:#\-]?\s*([0-9]{1,4}[-/.][0-9]{1,2}[-/.][0-9]{1,4})",
        r"(?i)\b(?:date|invoice\s*date|dated)\s*[:#\-]?\s*([A-Za-z]{3,9}\s+[0-9]{1,2},?\s+[0-9]{4})",
        r"(?i)\b(?:date|invoice\s*date|dated)\s*[:#\-]?\s*([0-9]{1,2}\s+[A-Za-z]{3,9},?\s+[0-9]{4})",
        r"\b([0-9]{4}[-/][0-9]{1,2}[-/][0-9]{1,2})\b",
        r"\b([0-9]{1,2}[-/][0-9]{1,2}[-/][0-9]{2,4})\b"
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            candidate = match.group(1).strip()
            if any(c.isdigit() for c in candidate):
                fields["Date"] = candidate
                break

    # 3. Company Name Extraction (Heuristic inspection of top lines)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    stop_terms = ["invoice", "tax invoice", "commercial invoice", "bill to", "billed to", "date", "due date", "page", "phone", "email", "gstin"]

    company_candidate = None
    for line in lines[:8]:  # inspect first 8 lines
        lower_line = line.lower()
        if any(lower_line.startswith(term) for term in stop_terms):
            continue

        corp_indicators = ["inc", "ltd", "pvt", "corp", "corporation", "solutions", "retailers", "technologies", "systems", "services", "company", "enterprises"]
        if any(re.search(rf"\b{ind}\b", lower_line) for ind in corp_indicators):
            company_candidate = line
            break

    if not company_candidate and lines:
        for line in lines[:5]:
            if line.lower() not in ["invoice", "tax invoice", "commercial invoice"] and len(line) > 3:
                company_candidate = line
                break

    if company_candidate:
        fields["Company Name"] = company_candidate.strip()

    # 4. Total Amount Extraction
    amount_patterns = [
        r"(?i)(?:total\s*amount|grand\s*total|amount\s*due|balance\s*due|total)\s*[:#\-]?\s*([₹$€£]|USD|INR|Rs\.?)?\s*([0-9,]+(?:\.[0-9]{2})?)",
        r"(?i)([₹$€£]|USD|INR|Rs\.?)\s*([0-9,]+(?:\.[0-9]{2})?)",
        r"(?i)(?:total|due)\s*[:#\-]?\s*([0-9,]+(?:\.[0-9]{2})?)"
    ]
    for pattern in amount_patterns:
        matches = re.findall(pattern, text)
        if matches:
            for m in reversed(matches):
                if isinstance(m, tuple):
                    curr = m[0].strip() if len(m) > 1 and m[0] else ""
                    val = m[1].strip() if len(m) > 1 else m[0].strip()
                else:
                    curr = ""
                    val = m.strip()

                if val and any(c.isdigit() for c in val):
                    fields["Total Amount"] = f"{curr} {val}".strip() if curr else val
                    break
            if fields["Total Amount"] != "Not found":
                break

    return fields


def extract_resume_fields(text: str) -> Dict[str, str]:
    """
    Extracts key fields for resumes using regex and heuristic rules:
    - Name
    - Email
    - Phone
    - Skills
    """
    fields = {
        "Name": "Not found",
        "Email": "Not found",
        "Phone": "Not found",
        "Skills": "Not found"
    }

    # 1. Email Extraction
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    email_match = re.search(email_pattern, text)
    if email_match:
        fields["Email"] = email_match.group(0).strip()

    # 2. Phone Extraction (Supports Indian, international, and US formats)
    phone_pattern = r"(?:(?:\+|00)\d{1,3}[\s-]?)?(?:\(?\d{2,5}\)?[\s-]?)?\d{3,5}[\s-]?\d{3,5}"
    phone_matches = re.findall(phone_pattern, text)
    for p in phone_matches:
        digits = re.sub(r"\D", "", p)
        if 10 <= len(digits) <= 14:
            fields["Phone"] = p.strip()
            break

    # 3. Name Extraction (Heuristic based on candidate header lines)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    invalid_name_terms = [
        "resume", "curriculum", "vitae", "cv", "email", "phone", "profile",
        "summary", "experience", "education", "skills", "page", "http", "www", "github", "linkedin"
    ]

    for line in lines[:5]:
        lower_line = line.lower()
        if any(term in lower_line for term in invalid_name_terms):
            continue
        if "@" in line or any(c.isdigit() for c in line):
            continue

        words = line.split()
        if 1 <= len(words) <= 4:
            fields["Name"] = line.strip()
            break

    # 4. Skills Extraction
    # Strategy A: Look for a dedicated Skills block/section
    skills_pattern = r"(?i)(?:skills\s*(?:&|and)?\s*technical\s*expertise|technical\s*skills|core\s*competencies|skills)\s*[:\-\n]([\s\S]*?)(?=\n\s*(?:work\s*experience|experience|education|projects|certifications|employment)|$)"
    skills_match = re.search(skills_pattern, text)

    extracted_skills = []
    if skills_match:
        skills_block = skills_match.group(1).strip()
        # Clean lines and split on commas or bullets
        raw_skills = re.split(r"[,•|\n;]", skills_block)
        for s in raw_skills:
            clean_s = re.sub(r"^(?:languages|frameworks\s*&\s*tools|frameworks|tools|technologies|competencies|core\s*competencies)\s*[:\-]", "", s, flags=re.IGNORECASE).strip()
            if clean_s and len(clean_s) <= 40 and not any(clean_s.lower().startswith(b) for b in ["experience", "education"]):
                extracted_skills.append(clean_s)

    # Strategy B: Fallback keyword dictionary matching if section parse is sparse
    common_skills = [
        "Python", "SQL", "Java", "C++", "JavaScript", "TypeScript", "HTML", "CSS",
        "Streamlit", "PyMuPDF", "FastAPI", "Flask", "Django", "Docker", "Kubernetes",
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "PyTorch",
        "TensorFlow", "Scikit-learn", "Pandas", "NumPy", "Git", "PostgreSQL", "MongoDB",
        "AWS", "Azure", "GCP", "Linux", "REST APIs", "CI/CD"
    ]

    if not extracted_skills or len(extracted_skills) < 2:
        for skill in common_skills:
            if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE):
                if skill not in extracted_skills:
                    extracted_skills.append(skill)

    if extracted_skills:
        # Deduplicate while preserving order
        unique_skills = []
        for s in extracted_skills:
            if s and s not in unique_skills:
                unique_skills.append(s)
        fields["Skills"] = ", ".join(unique_skills[:12])

    return fields


# =====================================================================
# 4. PIPELINE CONTROLLER & DATA MODEL
# =====================================================================

def process_document(file_bytes: bytes, filename: str, file_extension: str, classification_mode: str = "Rule-based") -> Dict[str, Any]:
    """
    Coordinates file validation, text extraction, document classification,
    and field extraction into a standardized result dictionary.
    """
    ext = file_extension.lower()

    # 1. Text Extraction
    if ext == "pdf":
        text, used_ocr, status_msg = extract_text_from_pdf(file_bytes)
    elif ext in ("jpg", "jpeg", "png"):
        text, used_ocr, status_msg = extract_text_from_image(file_bytes)
    else:
        return {
            "filename": filename,
            "file_type": ext,
            "document_type": "Unsupported",
            "classification_method": "None",
            "fields": {},
            "text": "",
            "error": "Unsupported file format. Please upload a PDF, JPG, JPEG, or PNG."
        }

    # 2. Document Classification
    if not text.strip():
        return {
            "filename": filename,
            "file_type": ext,
            "document_type": "Other",
            "classification_method": "None (Empty Text)",
            "classification_details": {},
            "fields": {},
            "text": "",
            "ocr_used": used_ocr,
            "status_message": status_msg,
            "error": "No text could be extracted from this document."
        }

    if classification_mode == "Optional ML (TF-IDF)" and SKLEARN_AVAILABLE:
        doc_type, method_name, details = classify_with_ml(text)
    else:
        doc_type, method_name, details = classify_rule_based(text)

    # 3. Field Extraction based on Identified Type
    if doc_type == "Invoice":
        fields = extract_invoice_fields(text)
    elif doc_type == "Resume":
        fields = extract_resume_fields(text)
    else:
        fields = {
            "Notice": "Document classified as 'Other'. Field extraction is tailored for Invoices and Resumes."
        }

    # 4. Return Normalized Data Model
    return {
        "filename": filename,
        "file_type": ext.upper(),
        "document_type": doc_type,
        "classification_method": method_name,
        "classification_details": details,
        "fields": fields,
        "text": text,
        "text_length": len(text),
        "word_count": len(text.split()),
        "ocr_used": used_ocr,
        "status_message": status_msg,
        "error": None
    }


# =====================================================================
# 5. STREAMLIT USER INTERFACE
# =====================================================================

def render_ui():
    st.set_page_config(
        page_title="AI Document Intelligence",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom styling
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.3rem;
            font-weight: 700;
            color: #1E293B;
            margin-bottom: 0.2rem;
        }
        .sub-header {
            font-size: 1.05rem;
            color: #64748B;
            margin-bottom: 1.5rem;
        }
        .badge-mvp {
            background-color: #EEF2FF;
            color: #4F46E5;
            padding: 0.25rem 0.6rem;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 0.5rem;
        }
        .metric-card {
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.75rem;
        }
        .metric-label {
            font-size: 0.8rem;
            color: #64748B;
            font-weight: 600;
            text-transform: uppercase;
        }
        .metric-value {
            font-size: 1.15rem;
            color: #0F172A;
            font-weight: 600;
            margin-top: 0.25rem;
            word-break: break-word;
        }
        .status-chip {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.85rem;
            font-weight: 500;
            margin-right: 0.5rem;
            margin-bottom: 0.5rem;
        }
        .status-success {
            background-color: #DCFCE7;
            color: #166534;
        }
        .status-info {
            background-color: #E0F2FE;
            color: #0369A1;
        }
        </style>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # SIDEBAR
    # -------------------------------------------------------------
    with st.sidebar:
        st.title("📄 AI Doc Intelligence")
        st.caption("Zyroo AI/ML Internship — Week 2")

        st.markdown("---")
        st.subheader("Application")
        st.markdown("**Upload Document**")
        st.markdown("Supported Formats: `PDF`, `JPG`, `JPEG`, `PNG`")

        st.markdown("---")
        st.subheader("System Status")

        # Status 1: PDF Extraction
        st.markdown("🔹 **PDF Extraction**: `PyMuPDF (Active)`")

        # Status 2: OCR Engine
        if TESSERACT_AVAILABLE:
            st.markdown("🔹 **OCR Engine**: `Tesseract (Ready)`")
        else:
            st.markdown("🔸 **OCR Engine**: `Config Required`")
            with st.expander("Install Tesseract on Windows"):
                st.caption(
                    "To enable OCR for scanned images:\n"
                    "1. Download installer from GitHub: `UB-Mannheim/tesseract/wiki`\n"
                    "2. Install to default path (`C:\\Program Files\\Tesseract-OCR`)\n"
                    "3. Restart the Streamlit app."
                )

        # Status 3: Document Classification
        st.markdown("🔹 **Classification**: `Keyword Rule-Based`")

        # Status 4: Field Extraction
        st.markdown("🔹 **Field Extraction**: `Active (Regex Rules)`")

        st.markdown("---")
        st.subheader("Classification Settings")
        classifier_mode = st.radio(
            "Classification Engine:",
            options=["Rule-based", "Optional ML (TF-IDF)"],
            index=0,
            help="Rule-based is transparent and fast. Optional ML uses a lightweight TF-IDF + Logistic Regression model."
        )

        st.markdown("---")
        st.subheader("Quick Test Samples")
        st.caption("Load an included test document instantly:")

        samples_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")
        sample_options = ["None (Upload my own)"]
        sample_files = ["invoice_1.pdf", "invoice_2.pdf", "resume_1.pdf"]

        for sf in sample_files:
            if os.path.isfile(os.path.join(samples_dir, sf)):
                sample_options.append(sf)

        selected_sample = st.selectbox("Select sample file:", sample_options)

    # -------------------------------------------------------------
    # HEADER
    # -------------------------------------------------------------
    st.markdown('<span class="badge-mvp">DOCUMENT ANALYSIS MVP</span>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">AI Document Intelligence</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Upload a document. Extract its text. Understand its type. Get useful information instantly.</p>',
        unsafe_allow_html=True
    )

    # -------------------------------------------------------------
    # MAIN AREA: FILE UPLOADER & SAMPLE RESOLUTION
    # -------------------------------------------------------------
    file_bytes: Optional[bytes] = None
    filename: str = ""
    file_type: str = ""
    file_size_bytes: int = 0

    uploaded_file = st.file_uploader(
        "Upload a document (PDF, JPG, JPEG, PNG)",
        type=["pdf", "jpg", "jpeg", "png"],
        help="Upload an invoice, resume, or other document."
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        filename = uploaded_file.name
        file_type = filename.split(".")[-1].lower()
        file_size_bytes = len(file_bytes)
    elif selected_sample != "None (Upload my own)":
        sample_path = os.path.join(samples_dir, selected_sample)
        if os.path.isfile(sample_path):
            with open(sample_path, "rb") as f:
                file_bytes = f.read()
            filename = selected_sample
            file_type = filename.split(".")[-1].lower()
            file_size_bytes = len(file_bytes)
            st.info(f"Loaded sample file from repository: `{filename}`")

    # -------------------------------------------------------------
    # PROCESSING PIPELINE & RESULTS
    # -------------------------------------------------------------
    if file_bytes is not None:
        # File Validation
        allowed_extensions = ["pdf", "jpg", "jpeg", "png"]
        if file_type not in allowed_extensions:
            st.error("Unsupported file type. Please upload a PDF, JPG, JPEG, or PNG.")
            return

        # Display File Metadata
        size_kb = file_size_bytes / 1024
        size_display = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"

        meta_col1, meta_col2, meta_col3 = st.columns(3)
        with meta_col1:
            st.metric("Filename", filename)
        with meta_col2:
            st.metric("File Type", file_type.upper())
        with meta_col3:
            st.metric("File Size", size_display)

        # Run Document Processing
        with st.spinner("Processing document..."):
            result = process_document(file_bytes, filename, file_type, classification_mode=classifier_mode)

        if result.get("error"):
            st.error(f"Error: {result['error']}")
            if result.get("status_message"):
                st.info(result["status_message"])
            return

        # Clear status messages
        st.markdown("---")
        st.markdown("### Processing Status")
        status_html = """
        <span class="status-chip status-success">✓ File accepted</span>
        <span class="status-chip status-success">✓ Text extracted</span>
        <span class="status-chip status-success">✓ Document identified</span>
        <span class="status-chip status-success">✓ Fields extracted</span>
        """
        st.markdown(status_html, unsafe_allow_html=True)
        st.caption(f"Extraction details: {result['status_message']}")

        # ---------------------------------------------------------
        # RESULT SECTION
        # ---------------------------------------------------------
        st.markdown("---")
        st.subheader("Document Analysis Results")

        res_col1, res_col2 = st.columns([1, 1])

        with res_col1:
            st.markdown(f"### Detected Type: **{result['document_type']}**")
            st.markdown(f"**Classification Method**: {result['classification_method']}")

        with res_col2:
            if result["classification_method"].startswith("Rule-based"):
                scores = result.get("classification_details", {})
                st.caption(f"Keyword score balance — Invoice: {scores.get('invoice_score', 0)} | Resume: {scores.get('resume_score', 0)}")
            else:
                prob = result.get("classification_details", {})
                st.caption(f"Class probabilities: {prob}")

        # Extracted Information Cards
        st.markdown("#### Extracted Information")
        fields = result.get("fields", {})

        if result["document_type"] == "Invoice":
            col_a, col_b = st.columns(2)
            col_c, col_d = st.columns(2)

            with col_a:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Invoice Number</div>
                    <div class="metric-value">{fields.get("Invoice Number", "Not found")}</div>
                </div>
                """, unsafe_allow_html=True)

            with col_b:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Date</div>
                    <div class="metric-value">{fields.get("Date", "Not found")}</div>
                </div>
                """, unsafe_allow_html=True)

            with col_c:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Company Name</div>
                    <div class="metric-value">{fields.get("Company Name", "Not found")}</div>
                </div>
                """, unsafe_allow_html=True)

            with col_d:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total Amount</div>
                    <div class="metric-value">{fields.get("Total Amount", "Not found")}</div>
                </div>
                """, unsafe_allow_html=True)

        elif result["document_type"] == "Resume":
            col_a, col_b = st.columns(2)
            col_c, col_d = st.columns(2)

            with col_a:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Candidate Name</div>
                    <div class="metric-value">{fields.get("Name", "Not found")}</div>
                </div>
                """, unsafe_allow_html=True)

            with col_b:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Email Address</div>
                    <div class="metric-value">{fields.get("Email", "Not found")}</div>
                </div>
                """, unsafe_allow_html=True)

            with col_c:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Phone Number</div>
                    <div class="metric-value">{fields.get("Phone", "Not found")}</div>
                </div>
                """, unsafe_allow_html=True)

            with col_d:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Skills</div>
                    <div class="metric-value">{fields.get("Skills", "Not found")}</div>
                </div>
                """, unsafe_allow_html=True)

        else:
            st.info(
                "The document is categorized as **Other**. General text was extracted successfully, "
                "but specific field extraction schemas are currently tailored for Invoices and Resumes."
            )

        # ---------------------------------------------------------
        # EXTRACTED TEXT SECTION
        # ---------------------------------------------------------
        st.markdown("---")
        with st.expander("📄 View Extracted Document Text", expanded=False):
            st.caption(f"Total Characters: {result['text_length']} | Words: {result['word_count']}")
            st.text_area(
                label="Extracted Text Content",
                value=result["text"],
                height=260,
                disabled=True
            )

        # ---------------------------------------------------------
        # EXPORT / DOWNLOAD OPTIONS
        # ---------------------------------------------------------
        st.markdown("#### Export Results")
        d_col1, d_col2 = st.columns(2)

        # Download JSON
        json_output = json.dumps(result, indent=2)
        with d_col1:
            st.download_button(
                label="⬇️ Download Results (JSON)",
                data=json_output,
                file_name=f"{filename}_analysis.json",
                mime="application/json",
                use_container_width=True
            )

        # Download Extracted Text
        with d_col2:
            st.download_button(
                label="⬇️ Download Raw Text (.txt)",
                data=result["text"],
                file_name=f"{filename}_extracted_text.txt",
                mime="text/plain",
                use_container_width=True
            )


if __name__ == "__main__":
    render_ui()
