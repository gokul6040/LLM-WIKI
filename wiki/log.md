# Wiki Change Log

> This file is **append-only**. Never delete or edit past entries. Each entry must include a date, action type, and summary.

---

## Entry Format

```
### [YYYY-MM-DD] — [Action Type]
**By:** [agent or human]
**Summary:** ...
**Details:**
- ...
```

Action types: `SETUP` | `INGEST` | `EDIT` | `LINT` | `QUERY` | `REFACTOR`

---

## Entries

### [2026-06-02] — SETUP
**By:** Cursor Agent (setup run)
**Summary:** Initial wiki scaffold created. No ingestion has been run yet.
**Details:**
- Created `wiki/` directory
- Created `wiki/index.md` — empty navigation stub, awaiting first ingestion
- Created `wiki/log.md` — this file
- Created `AGENTS.md` — full agent instruction set
- Source file confirmed present: `raw/hospital_disease.md`
- No wiki content pages exist yet. Run the Ingestion Workflow (AGENTS.md §5) to populate the wiki.

---

---

### [2026-06-02] — INGEST
**By:** Cursor Agent (first ingestion run)
**Summary:** Full ingestion of `raw/hospital_disease.md` completed. 121 wiki pages created across 7 folders.
**Details:**

**Folders created (7):**
- `wiki/groups/` — 9 disease group overview pages
- `wiki/diseases/` — 47 individual disease profile pages
- `wiki/symptoms/` — 15 symptom pages
- `wiki/warning-signs/` — 8 emergency warning sign cluster pages
- `wiki/investigations/` — 20 investigation pages
- `wiki/departments/` — 14 department pages
- `wiki/overlaps/` — 8 cross-disease reasoning pages

**Pages created (121 total):**

*Disease Groups (9):* Cardiovascular Diseases, Respiratory Diseases, Infectious Diseases, Endocrine and Metabolic Diseases, Kidney and Urinary Diseases, Gastrointestinal and Liver Diseases, Cancer, Blood and Immune Diseases, Mental Health and Cognitive Conditions

*Disease Profiles (47):* Heart Attack, Angina, Stroke, Atrial Fibrillation, Heart Failure, Hypertension, Pneumonia, Asthma, COPD, Tuberculosis, Pulmonary Embolism, Sepsis, Influenza, Dengue, Malaria, Meningitis, Epileptic Seizure, Migraine, Type 2 Diabetes, Diabetic Ketoacidosis, Hypoglycemia, Chronic Kidney Disease, Acute Kidney Injury, Urinary Tract Infection, Appendicitis, Pancreatitis, Gallstones/Cholecystitis, Peptic Ulcer Disease, GERD, Inflammatory Bowel Disease, Liver Cirrhosis, Hepatitis B, Cancer General, Breast Cancer, Lung Cancer, Colorectal Cancer, Anemia, Leukemia, Lymphoma, Rheumatoid Arthritis, Lupus, Anaphylaxis, Depression, Anxiety/Panic Attack, Dementia/Alzheimer, Ectopic Pregnancy, Preeclampsia

*Symptoms (15):* Chest Pain, Shortness of Breath, Fever, Cough, Headache, Abdominal Pain, Confusion, Weight Loss, Rash, Vomiting, Swelling, Bleeding, Palpitations, Seizure, Joint Pain

*Warning Signs (8):* Chest Pain Warning Signs, Stroke Warning Signs, Breathing Warning Signs, Infection Warning Signs, Abdominal Warning Signs, Neurological Warning Signs, Allergy Warning Signs, Pregnancy Warning Signs

*Investigations (20):* ECG, Troponin, Complete Blood Count, Blood Glucose, Chest X-ray, CT Brain, MRI Brain, Urinalysis, Creatinine/eGFR, Liver Function Tests, Ultrasound Abdomen, Pregnancy Test, Lumbar Puncture, Blood Cultures, Platelet Count, Sputum Test, Biopsy, Colonoscopy, Spirometry, Echocardiogram

*Departments (14):* Emergency Medicine, Cardiology, Neurology, Pulmonology, Infectious Disease, Nephrology, Endocrinology, Gastroenterology, General Surgery, Oncology, Hematology, Rheumatology, Obstetrics and Gynecology, Psychiatry

*Overlaps/Reasoning (8):* Fever Is Nonspecific, Chest Pain Requires Careful Separation, Shortness of Breath Has Many Body-System Causes, Chronic Cough Changes the Pattern, Confusion Is a Major Red Flag, Abdominal Pain Needs Context, Weight Loss — Persistent and Unexplained, Risk Factors Modify Interpretation

**Major concept types detected from raw file:**
- Sections 1–2: Disease groups and 47 disease profiles
- Section 3: 15-symptom relationship index
- Section 4: 7-category emergency warning sign index (+ pregnancy = 8 pages)
- Section 5: 20 named investigations
- Section 6: 14 named departments
- Section 7: 8 cross-disease reasoning notes
- Section 8: Compact condition-to-symptom map (used to verify disease page content)
- Section 9: 8 practical Q&A examples (used to verify query entry points in index)

**Unclear sections:** None. All sections in the raw file were well-structured and parseable.

**Safety-sensitive areas noted:**
- All disease pages with warning signs include the ⚠️ safety note and link to relevant warning sign pages
- Obstetric pages (Ectopic Pregnancy, Preeclampsia) carry explicit emergency framing
- Mental health pages (Depression, Anxiety/Panic Attack) include psychiatric safety notes
- Sepsis, Meningitis, Anaphylaxis, Diabetic Ketoacidosis pages carry the strongest emergency framing
- No diagnostic language ("you have", "this confirms") was used on any page
- No information was added beyond what appears in `raw/hospital_disease.md`

**`wiki/index.md` updated:** Yes — full rebuild with all 121 pages listed and query entry point table.

---

### [2026-06-02] — LINT v1

**By:** Cursor Agent (lint pass v1)
**Summary:** Full lint run per AGENTS.md § 7 Lint Workflow. 20 broken wikilinks fixed, 2 new department stub pages created, diagnostic language corrected, 7 symptom pages linked to their overlap counterparts. Wiki version bumped to 1.1. Total pages: 121 → 123.

**Checks run:**

| Check | Result |
|---|---|
| Broken wikilinks | 20 found → 0 remaining |
| Orphan pages | 0 found |
| Duplicate concepts | 0 found |
| Missing source references | 0 found |
| Over-copying raw text | Pass — pages are synthesized |
| Diagnostic language | 1 found in `chest-pain-separation.md` → fixed |
| Missing safety notes | 0 found |
| Disease pages missing links | 0 found |
| Symptom pages missing overlap links | 7 found → fixed |
| Department pages missing conditions | 0 found |
| Investigation pages missing disease links | 0 found |
| index.md completeness | 2 new pages added to departments section |
| log.md | This entry |

**Changes made:**
- Fixed H1 titles in 5 files: `anxiety-panic-attack.md`, `cancer-general.md`, `creatinine-egfr.md`, `dementia-alzheimer.md`, `gallstones-cholecystitis.md`
- Created `wiki/departments/primary-care.md`
- Created `wiki/departments/intensive-care-unit.md`
- Removed `[[]]` wikilink brackets from 13 non-page references across 25 file occurrences
- Fixed `[[Surgery]]` → `[[General Surgery]]` in `cancer-general.md`
- Fixed diagnostic language in `chest-pain-separation.md`
- Added overlap page cross-links to 7 symptom pages
- Updated `wiki/index.md`: departments count 14 → 16, version 1.0 → 1.1

**Report:** `reports/wiki_lint_report.md`
### [2026-06-02 14:02:32] BUILD

- Source: `raw/hospital_disease.md`
- Pages written: 686
- departments: 14
- diseases: 47
- groups: 9
- investigations: 20
- overlaps: 8
- source-sections: 565
- symptoms: 15
- warning-signs: 8

---
### [2026-06-02 14:07:51] BUILD

- Source: `raw/hospital_disease.md`
- Pages written: 686
- departments: 14
- diseases: 47
- groups: 9
- investigations: 20
- overlaps: 8
- source-sections: 565
- symptoms: 15
- warning-signs: 8

---
### [2026-06-02 14:08:41] BUILD

- Source: `raw/hospital_disease.md`
- Pages written: 686
- departments: 14
- diseases: 47
- groups: 9
- investigations: 20
- overlaps: 8
- source-sections: 565
- symptoms: 15
- warning-signs: 8

---
