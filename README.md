# AI Document Intelligence & Workflow Platform

**Enterprise-Grade Document Understanding, Controlled State Machine, Validation Engine & Human-in-the-Loop Workflow Automation**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.35+-FF4B4B.svg)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/SQLite-WAL%20Mode-003B57.svg)](https://www.sqlite.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4+-F7931E.svg)](https://scikit-learn.org/)
[![PyMuPDF](https://img.shields.io/badge/PyMuPDF-1.24+-green.svg)](https://pymupdf.readthedocs.io/)
[![Tests](https://img.shields.io/badge/tests-78%20passed-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Live Demo (Cloudflare)](https://img.shields.io/badge/Live%20Demo-Cloudflare%20Edge-orange.svg?style=for-the-badge&logo=cloudflare)](https://incorporated-attempted-lucy-trusts.trycloudflare.com)
[![Streamlit Cloud](https://img.shields.io/badge/Streamlit%20Cloud-Deployed-FF4B4B.svg?style=for-the-badge&logo=streamlit)](https://mgb56neehcvkyzsiukg2qh.streamlit.app/)

**🌐 Public Live URL (Cloudflare Edge):** **[https://incorporated-attempted-lucy-trusts.trycloudflare.com](https://incorporated-attempted-lucy-trusts.trycloudflare.com)**  
**🌐 Public Live URL (Streamlit Cloud):** **[https://mgb56neehcvkyzsiukg2qh.streamlit.app/](https://mgb56neehcvkyzsiukg2qh.streamlit.app/)**  
**📂 Primary Codebase:** [evilswordboy-bot/ai-document-intelligence](https://github.com/evilswordboy-bot/ai-document-intelligence)  
**📂 Internship Portfolio:** [evilswordboy-bot/zyro-aiml-internship](https://github.com/evilswordboy-bot/zyro-aiml-internship) (Week 5 active)

---

## 📌 Executive Summary (Week 5 Upgrade)

**AI Document Intelligence & Workflow Platform** is an enterprise-grade document intelligence system built for the **ZYROO AI/ML Internship (Week 5)**. Building on Week 4's persistent repository and deduplication, Week 5 transforms stored documents into a **fully automated, controlled document workflow platform**:

$$\text{UPLOAD} \longrightarrow \text{PROCESS} \longrightarrow \text{CLASSIFY} \longrightarrow \text{EXTRACT} \longrightarrow \text{VALIDATE} \longrightarrow \text{APPLY RULES} \longrightarrow \text{REVIEW / APPROVE / REJECT} \longrightarrow \text{COMPLETE} \longrightarrow \text{AUDIT HISTORY}$$

The platform guarantees data integrity through:
1. **Controlled Workflow States**: Strict state machine enforcing allowed lifecycle jumps (`New` $\rightarrow$ `Processing` $\rightarrow$ `Needs Review` $\rightarrow$ `Approved` $\rightarrow$ `Completed`, etc.) while blocking invalid transitions.
2. **Advanced Document Validation**: Deep structural and format validation (invoice currency parsing, invoice numbers, RFC 5322 email regex, phone formatting, skills extraction).
3. **Decoupled Rule-Based Workflow Engine**: Evaluates document categories, validation flags, missing fields, and honest machine learning confidence (threshold ~0.70). Uncalibrated models (SVM/Rule baseline) honestly report "Not Available" without inventing fake confidence scores.
4. **Human Review Queue**: Dedicated review workspace for documents flagged for review, supporting reviewer notes, one-click approvals, and **strictly mandatory** rejection explanations.
5. **Fault-Tolerant Batch Processing**: High-throughput multi-document intake with isolated transaction boundaries where corrupt or unreadable files never halt or crash batch execution.
6. **Immutable Audit Trail**: SQLite `audit_logs` table recording every single automated transition and manual reviewer interaction with timestamps, state deltas, and notes.

---

## 🏛️ End-to-End Workflow & State Machine Architecture

```
                    ┌────────────────────────┐
                    │  User Document Upload  │
                    │  (PDF, JPG, JPEG, PNG) │
                    └───────────┬────────────┘
                                │ State: New (Recorded in SQLite)
                                ▼
                    ┌────────────────────────┐
                    │ File Validation Layer  │
                    │ Format & Size (<20MB)  │
                    └───────────┬────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │ Cryptographic SHA-256  │
                    │ Digest Computation     │
                    └───────────┬────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │ Duplicate Detection    │
                    │ (data/documents.db)    │
                    └───────────┬────────────┘
                                │
         ┌──────────────────────┴──────────────────────┐
 [Duplicate Hash Exists]                      [Brand New Document]
         │                                             │
         ▼                                             ▼
┌───────────────────┐                        ┌───────────────────┐
│ Suppress Storage  │                        │ State: Processing │
│ Render Vault Doc  │                        │ PyMuPDF / OCR     │
└───────────────────┘                        └─────────┬─────────┘
                                                       │
                                                       ▼
                                             ┌───────────────────┐
                                             │ Text Cleaning &   │
                                             │ Normalization     │
                                             └─────────┬─────────┘
                                                       │
                                                       ▼
                                             ┌───────────────────┐
                                             │ ML Classification │
                                             │ (TF-IDF + Models) │
                                             └─────────┬─────────┘
                                                       │
                                                       ▼
                                             ┌───────────────────┐
                                             │ Entity Extraction │
                                             │ (Regex + NLP)     │
                                             └─────────┬─────────┘
                                                       │
                                                       ▼
                                             ┌───────────────────┐
                                             │ Document Validator│
                                             │ (Invoice/Resume)  │
                                             └─────────┬─────────┘
                                                       │
                                                       ▼
                                             ┌───────────────────┐
                                             │  Workflow Engine  │
                                             │ (Rules Evaluation)│
                                             └─────────┬─────────┘
                                                       │
                           ┌───────────────────────────┴───────────────────────────┐
                           │                                                       │
              [Passed All Rules & Conf >= 70%]                       [Validation Failed or Conf < 70%]
                           │                                                       │
                           ▼                                                       ▼
                 ┌───────────────────┐                                   ┌───────────────────┐
                 │ State: Completed  │                                   │State: Needs Review│
                 │ Straight-Through  │                                   │Human Review Queue │
                 └───────────────────┘                                   └─────────┬─────────┘
                                                                                   │
                                                          ┌────────────────────────┴────────────────────────┐
                                                          │                                                 │
                                                   [Reviewer Approve]                              [Reviewer Reject]
                                                          │                                                 │
                                                          ▼                                                 ▼
                                                ┌───────────────────┐                             ┌───────────────────┐
                                                │  State: Approved  │                             │  State: Rejected  │
                                                │         │         │                             │ (Mandatory Note)  │
                                                │         ▼         │                             └───────────────────┘
                                                │ State: Completed  │
                                                └───────────────────┘
                                                          │
                                                          ▼
                                             ┌─────────────────────────┐
                                             │  SQLite Audit Logging   │
                                             │ (audit_logs table)      │
                                             └─────────────────────────┘
```

---

## 🔄 Controlled Workflow States & Transition Guard

The platform enforces a deterministic finite state machine (`services/workflow.py`). Unauthorized jumps are strictly blocked and audited:

| State | Role | Permitted Next States | Guard Logic |
| :--- | :--- | :--- | :--- |
| **`New`** | Initial intake state upon upload | `Processing`, `Failed` | Intake registered |
| **`Processing`** | OCR, classification, and extraction in progress | `Needs Review`, `Completed`, `Failed` | Transition locked during processing |
| **`Needs Review`** | Flagged by validation issues or low confidence | `Approved`, `Rejected`, `Processing` | Enters Human Review Queue |
| **`Approved`** | Human reviewer verified document | `Completed` | Automatically finalized to Completed |
| **`Rejected`** | Human reviewer rejected document | `Processing` (retry) | **Strictly requires mandatory note** |
| **`Completed`** | Successfully processed and validated | `Processing` (re-process) | Final terminal state |
| **`Failed`** | Unreadable, corrupt, or missing content | `Processing` (retry) | Exception boundary handled |

---

## ⚙️ Core Architecture & Module Bridges (Section 13)

```
ai-document-intelligence/
├── app.py                      # Streamlit application UI & navigation router
├── database.py                 # Top-level database interface bridge
├── storage.py                  # Top-level storage interface bridge
├── processor.py                # Top-level document processor bridge
├── validator.py                # Top-level document validation bridge
├── workflow.py                 # Top-level rule-based workflow engine bridge
├── audit.py                    # Top-level audit logging bridge
├── batch.py                    # Top-level fault-tolerant batch processor bridge
├── requirements.txt            # Production dependencies
├── database/
│   ├── __init__.py
│   └── db.py                   # SQLite DatabaseManager, migrations & audit_logs queries
├── models/
│   ├── __init__.py
│   └── document.py             # DocumentRecord dataclass & workflow status constants
├── services/
│   ├── __init__.py
│   ├── audit.py                # AuditService: Event recording & chronological history
│   ├── batch.py                # BatchProcessor: Isolated per-document error boundary
│   ├── classifier.py           # ML classifier service wrapper
│   ├── document_processor.py   # Full pipeline intake, routing & audit orchestrator
│   ├── file_storage.py         # FileStorageManager: SHA-256 partitioned vault
│   ├── hashing.py              # SHA-256 cryptographic digest calculation
│   ├── ocr.py                  # OCR computer vision service
│   ├── validation.py           # FileValidator & DocumentValidator (Invoices/Resumes)
│   └── workflow.py             # WorkflowEngine: State transitions & rule routing
├── src/
│   ├── classifier.py           # TF-IDF Vectorizer + LR, SVM, NB, Rule Baseline
│   ├── document_reader.py      # PyMuPDF direct PDF text extractor
│   ├── evaluator.py            # Precision, Recall, F1, Accuracy benchmarks
│   ├── extractor.py            # Regex & pattern entity extraction
│   ├── ocr_processor.py        # Tesseract OCR engine with fallback
│   ├── text_cleaner.py         # Whitespace, unicode & artifact normalization
│   ├── train_models.py         # Model training script
│   └── utils.py                # Sample generator (12 rich PDFs) & dataset loader
├── data/
│   ├── documents.db            # SQLite persistent repository (WAL mode enabled)
│   ├── train/                  # Labeled training dataset (22 domain text samples)
│   └── test/                   # Unseen testing dataset (9 test evaluation samples)
├── samples/                    # 12 authentic multi-category test PDFs
└── tests/
    ├── conftest.py             # Pytest fixtures
    ├── test_audit.py           # Audit logging & timeline integrity tests
    ├── test_batch.py           # Batch processing & fault isolation tests
    ├── test_classifier.py      # Model training & prediction unit tests
    ├── test_database.py        # SQLite migrations, CRUD & indexing tests
    ├── test_extraction.py      # Field extraction & missing-field tests
    ├── test_pipeline_e2e.py    # Pipeline end-to-end integration tests
    ├── test_processor_e2e.py   # DocumentProcessor workflow tests
    ├── test_storage.py         # SHA-256 & storage lifecycle tests
    ├── test_text_cleaning.py   # Text cleaner normalization tests
    ├── test_validation.py      # DocumentValidator format & currency tests
    ├── test_week4_acceptance.py# Week 4 backward compatibility test matrix
    ├── test_week5_acceptance.py# Week 5 15-document workflow acceptance matrix
    └── test_workflow.py        # State transitions & reviewer action tests
```

---

## 🧪 Comprehensive Test Suite (78 / 78 Passed — 100%)

All 78 unit, integration, and acceptance tests pass with 100% success rate:

```powershell
pytest -v
```

```
============================= test session starts =============================
platform win32 -- Python 3.13.15, pytest-9.1.1, pluggy-1.6.0
collected 78 items

tests/test_audit.py::test_log_and_retrieve_document_history PASSED       [  1%]
tests/test_audit.py::test_recent_timeline_joined_data PASSED             [  2%]
tests/test_batch.py::test_batch_processing_success PASSED                [  3%]
tests/test_batch.py::test_batch_isolated_error_fault_tolerance PASSED    [  5%]
tests/test_classifier.py::test_classifier_invoice_prediction PASSED      [  6%]
tests/test_classifier.py::test_classifier_resume_prediction PASSED       [  7%]
tests/test_classifier.py::test_classifier_other_prediction PASSED        [  8%]
tests/test_classifier.py::test_rule_based_baseline PASSED                [ 10%]
tests/test_classifier.py::test_model_persistence PASSED                  [ 11%]
tests/test_database.py::test_add_and_get_document PASSED                 [ 12%]
tests/test_database.py::test_duplicate_lookup_by_hash PASSED             [ 14%]
tests/test_database.py::test_multi_field_search PASSED                   [ 15%]
tests/test_database.py::test_kpi_statistics PASSED                       [ 16%]
tests/test_extraction.py::test_invoice_field_extraction_complete PASSED  [ 17%]
tests/test_extraction.py::test_invoice_missing_total_handling PASSED     [ 19%]
tests/test_extraction.py::test_resume_field_extraction_complete PASSED   [ 20%]
tests/test_extraction.py::test_resume_missing_phone_handling PASSED      [ 21%]
tests/test_extraction.py::test_document_reader_empty_pdf PASSED          [ 23%]
tests/test_extraction.py::test_document_reader_corrupt_pdf PASSED        [ 24%]
tests/test_pipeline_e2e.py::test_pipeline_normal_invoice PASSED          [ 25%]
tests/test_pipeline_e2e.py::test_pipeline_invoice_missing_total PASSED   [ 26%]
tests/test_pipeline_e2e.py::test_pipeline_normal_resume PASSED           [ 28%]
tests/test_pipeline_e2e.py::test_pipeline_resume_missing_phone PASSED    [ 29%]
tests/test_pipeline_e2e.py::test_pipeline_other_meeting_minutes PASSED   [ 30%]
tests/test_processor_e2e.py::test_e2e_invoice_workflow_and_persistence PASSED [ 32%]
tests/test_processor_e2e.py::test_e2e_missing_field_needs_review PASSED  [ 33%]
tests/test_storage.py::test_sha256_calculation PASSED                    [ 34%]
tests/test_storage.py::test_file_storage_lifecycle PASSED                [ 35%]
tests/test_storage.py::test_path_traversal_prevention PASSED             [ 37%]
tests/test_storage.py::test_file_validation PASSED                       [ 38%]
tests/test_text_cleaning.py::test_clean_normal_text PASSED               [ 39%]
tests/test_text_cleaning.py::test_clean_empty_text PASSED                [ 41%]
tests/test_text_cleaning.py::test_clean_extremely_short_text PASSED      [ 42%]
tests/test_text_cleaning.py::test_clean_unicode_and_control_chars PASSED [ 43%]
tests/test_validation.py::test_validate_invoice_valid_complete PASSED    [ 44%]
tests/test_validation.py::test_validate_invoice_missing_number PASSED    [ 46%]
tests/test_validation.py::test_validate_invoice_invalid_amount PASSED    [ 47%]
tests/test_validation.py::test_validate_invoice_currency_parsing PASSED  [ 48%]
tests/test_validation.py::test_validate_resume_valid_complete PASSED     [ 50%]
tests/test_validation.py::test_validate_resume_invalid_email PASSED      [ 51%]
tests/test_validation.py::test_validate_resume_missing_phone PASSED      [ 52%]
tests/test_validation.py::test_validate_resume_missing_skills PASSED     [ 53%]
tests/test_validation.py::test_validate_other_document PASSED            [ 55%]
tests/test_week4_acceptance.py::test_01_invoice_upload PASSED            [ 56%]
tests/test_week4_acceptance.py::test_02_invoice_with_currency PASSED     [ 57%]
tests/test_week4_acceptance.py::test_03_resume_upload PASSED             [ 58%]
tests/test_week4_acceptance.py::test_04_other_document_upload PASSED     [ 60%]
tests/test_week4_acceptance.py::test_05_duplicate_suppression PASSED     [ 61%]
tests/test_week4_acceptance.py::test_06_missing_invoice_field_needs_review PASSED [ 62%]
tests/test_week4_acceptance.py::test_07_missing_resume_field_needs_review PASSED [ 64%]
tests/test_week4_acceptance.py::test_08_scanned_image_processing PASSED  [ 65%]
tests/test_week4_acceptance.py::test_09_invalid_file_rejection PASSED    [ 66%]
tests/test_week4_acceptance.py::test_10_oversized_file_rejection PASSED  [ 67%]
tests/test_week4_acceptance.py::test_11_multi_field_search PASSED        [ 69%]
tests/test_week4_acceptance.py::test_12_sorting_and_filtering PASSED     [ 70%]
tests/test_week4_acceptance.py::test_13_restart_persistence PASSED       [ 71%]
tests/test_week5_acceptance.py::test_01_valid_invoice_completed PASSED   [ 73%]
tests/test_week5_acceptance.py::test_02_invoice_with_currency_completed PASSED [ 74%]
tests/test_week5_acceptance.py::test_03_invoice_missing_total_needs_review PASSED [ 75%]
tests/test_week5_acceptance.py::test_04_invoice_missing_number_needs_review PASSED [ 76%]
tests/test_week5_acceptance.py::test_05_invoice_freelance_completed PASSED [ 78%]
tests/test_week5_acceptance.py::test_06_valid_resume_completed PASSED    [ 79%]
tests/test_week5_acceptance.py::test_07_resume_missing_phone_needs_review PASSED [ 80%]
tests/test_week5_acceptance.py::test_08_resume_invalid_email_needs_review PASSED [ 82%]
tests/test_week5_acceptance.py::test_09_resume_senior_dev_completed PASSED [ 83%]
tests/test_week5_acceptance.py::test_10_meeting_minutes_completed PASSED [ 84%]
tests/test_week5_acceptance.py::test_11_project_proposal_completed PASSED [ 85%]
tests/test_week5_acceptance.py::test_12_nda_agreement_completed PASSED   [ 87%]
tests/test_week5_acceptance.py::test_13_scanned_receipt_image PASSED     [ 88%]
tests/test_week5_acceptance.py::test_14_duplicate_suppression PASSED     [ 89%]
tests/test_week5_acceptance.py::test_15_human_review_approval PASSED     [ 91%]
tests/test_week5_acceptance.py::test_16_human_review_rejection_mandatory_note PASSED [ 92%]
tests/test_week5_acceptance.py::test_17_batch_processing_fault_isolation PASSED [ 93%]
tests/test_week5_acceptance.py::test_18_audit_history_timeline_integrity PASSED [ 94%]
tests/test_workflow.py::test_state_transition_validation PASSED          [ 96%]
tests/test_workflow.py::test_evaluate_rules_decision_logic PASSED        [ 97%]
tests/test_workflow.py::test_approve_document_flow PASSED                [ 98%]
tests/test_workflow.py::test_reject_document_mandatory_note PASSED       [100%]
======================= 78 passed in 9.81s =======================
```

---

## 🚀 Quickstart & Local Installation

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13
- Git

### Installation Steps
```bash
# Clone the primary repository
git clone https://github.com/evilswordboy-bot/ai-document-intelligence.git
cd ai-document-intelligence

# Create and activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run model training and sample document generation
python src/train_models.py

# Launch the interactive Streamlit application
streamlit run app.py
```

Application will be available at: `http://localhost:8501`.

---

## 👥 Authors & Internship Submission

- **Student / Developer:** Sakthibalan S
- **Program:** ZYROO AI/ML Internship
- **Milestone:** Week 5 Masterpiece Submission
- **Primary Repository:** [ai-document-intelligence](https://github.com/evilswordboy-bot/ai-document-intelligence)
- **Portfolio Repository:** [zyro-aiml-internship](https://github.com/evilswordboy-bot/zyro-aiml-internship)
