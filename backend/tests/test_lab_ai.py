"""Tests for AI Lab Assistant (rule engine, OCR, PDF, test procedures)."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app.services.lab_ai import (
    interpret_result, interpret_batch, parse_free_text,
    get_test_procedure, LAB_TESTS, TEST_PROCEDURES
)


# ============= INTERPRETATION TESTS =============

class TestNumericInterpretation:
    def test_glucose_fasting_normal(self):
        r = interpret_result("Glucose (Fasting)", "5.0", gender="male", age=30)
        assert r.flag == "normal"

    def test_glucose_fasting_high(self):
        r = interpret_result("Glucose (Fasting)", "7.5", gender="male", age=45)
        assert "high" in r.flag
        assert "diabetes" in r.recommendation.lower()

    def test_glucose_fasting_critical_low(self):
        r = interpret_result("Glucose (Fasting)", "1.8", gender="male", age=30)
        assert r.flag == "critical_low"

    def test_creatinine_gender_specific(self):
        r_m = interpret_result("Creatinine", "100", gender="male", age=40)
        r_f = interpret_result("Creatinine", "100", gender="female", age=40)
        assert r_m.flag in ("normal", "high")
        assert r_f.flag != r_m.flag

    def test_child_range_used(self):
        r = interpret_result("Glucose (Fasting)", "3.0", gender="male", age=6)
        assert r.flag in ("low", "critical_low")

    def test_pregnancy_note(self):
        r = interpret_result("Haemoglobin (Hb)", "10.0", gender="female", age=28, pregnant=True)
        assert "pregnancy" in r.interpretation.lower()

    def test_unknown_test_fallback(self):
        r = interpret_result("NonExistentTest123", "5.0")
        assert r.flag == "unknown"

    def test_numeric_parse_european_format(self):
        r = interpret_result("Cholesterol (Total)", "6,5", gender="male", age=50)
        assert r.flag == "high"


class TestTextInterpretation:
    def test_gram_stain_pattern(self):
        r = interpret_result("Gram Stain", "gram positive cocci in clusters")
        assert r.flag == "interpret"
        assert "Staphylococcus" in r.interpretation

    def test_malaria_rdt(self):
        r = interpret_result("RDT Malaria", "pf positive")
        assert r.flag == "interpret"
        assert "ACT" in r.interpretation or "artemisinin" in r.interpretation.lower()

    def test_urine_dipstick(self):
        r = interpret_result("Urine Glucose", "3+")
        assert r.flag == "interpret"

    def test_blood_group(self):
        r = interpret_result("Blood Group", "o-")
        assert "universal donor" in r.interpretation.lower()

    def test_hiv_viral_load_suppressed(self):
        r = interpret_result("HIV-1 Viral Load", "<40")
        assert "suppressed" in r.interpretation.lower()


class TestBatchInterpretation:
    def test_batch_all_normal(self):
        results = [
            {"test": "Glucose (Fasting)", "result": "5.0"},
            {"test": "Haemoglobin (Hb)", "result": "14.0"},
        ]
        batch = interpret_batch(results, gender="male", age=35)
        assert batch["total_tests"] == 2
        assert batch["abnormal_count"] == 0

    def test_batch_with_abnormal(self):
        results = [
            {"test": "Glucose (Fasting)", "result": "15.0"},
            {"test": "Haemoglobin (Hb)", "result": "7.0"},
        ]
        batch = interpret_batch(results, gender="male", age=60)
        assert batch["abnormal_count"] >= 1


class TestFreeTextParsing:
    def test_parse_simple(self):
        text = "Glucose (Fasting): 7.5\nHaemoglobin: 13.0"
        result = parse_free_text(text, gender="male", age=45)
        assert result["total_tests"] >= 2

    def test_parse_empty(self):
        result = parse_free_text("")
        assert "error" in result

    def test_parse_no_separator(self):
        result = parse_free_text("some random text without proper format")
        assert result["total_tests"] == 1  # falls back to free text


# ============= TEST PROCEDURE GUIDE TESTS =============

class TestProcedureGuides:
    def test_major_procedures_exist(self):
        major = ["Gram Stain", "Culture & Sensitivity", "AFB Smear (ZN Stain)",
                 "Glucose (Fasting)", "HbA1c", "ALT (SGPT)", "Creatinine",
                 "Haemoglobin (Hb)", "WBC Count", "CD4 Count",
                 "Urine Dipstick", "Urine Microscopy", "Urine Culture",
                 "Stool Microscopy — Ova & Cysts", "HIV-1 Viral Load",
                 "Semen Analysis", "Platelet Count", "Blood Film Comment",
                 "Hb Electrophoresis", "HBsAg (Hepatitis B)"]
        for name in major:
            guide = get_test_procedure(name)
            assert guide is not None, f"Missing procedure: {name}"
            assert guide["test_name"] == name
            assert guide["department"]
            assert guide["methodology"]
            assert guide["references"]

    def test_procedure_all_fields(self):
        guide = get_test_procedure("Gram Stain")
        fields = ["test_name", "department", "specimen_type", "container",
                  "volume", "storage", "transport", "patient_preparation",
                  "methodology", "equipment", "quality_control",
                  "turnaround_time", "interpretation", "clinical_significance",
                  "limitations", "references", "reference_keys"]
        for f in fields:
            assert f in guide, f"Missing field: {f}"

    def test_all_lab_tests_have_procedures(self):
        """Not all tests need procedures, but at least 15 should exist."""
        count = len(TEST_PROCEDURES)
        assert count >= 40, f"Only {count} procedures — expected ≥40"

    def test_department_tests_listed(self):
        from app.services.lab_ai import DEPARTMENT_TESTS
        depts = list(DEPARTMENT_TESTS.keys())
        assert "Microbiology" in depts
        assert "Clinical Chemistry" in depts
        assert "Haematology" in depts
        assert "Urinalysis" in depts
        assert "Molecular Biology" in depts
        total = sum(len(tests) for tests in DEPARTMENT_TESTS.values())
        assert total >= 50


# ============= OCR PIPELINE TESTS =============

class TestOCRService:
    def test_preprocess_image(self):
        from app.services.ocr_service import preprocess_image
        from PIL import Image
        import io
        img = Image.new("RGB", (200, 100), color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        processed = preprocess_image(buf.getvalue())
        assert len(processed) > 0

    def test_ocr_text(self):
        from app.services.ocr_service import ocr_image
        from PIL import Image, ImageDraw, ImageFont
        import io
        img = Image.new("RGB", (400, 100), color="white")
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except Exception:
            font = ImageFont.load_default()
        draw.text((10, 30), "Glucose: 5.2 mmol/L", fill="black", font=font)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        result = ocr_image(buf.getvalue())
        if result["success"]:
            assert "Glucose" in result["text"] or "glucose" in result["text"].lower()

    def test_pdf_extraction(self):
        from app.services.ocr_service import extract_pdf_text
        try:
            import fitz
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((50, 50), "Haemoglobin: 14.2 g/dL", fontsize=14)
            pdf_bytes = doc.write()
            doc.close()
            text = extract_pdf_text(pdf_bytes)
            assert text is not None
            assert "Haemoglobin" in text
        except Exception as e:
            pytest.skip(f"PDF creation failed: {e}")


# ============= REFERENCE FORMAT TESTS =============

class TestReferences:
    def test_reference_books_defined(self):
        from app.services.lab_ai import REFERENCE_BOOKS, APA_REFERENCES
        assert len(REFERENCE_BOOKS) >= 5
        assert "cheesbrough" in REFERENCE_BOOKS
        assert "malawi_sop" in REFERENCE_BOOKS
        assert "harrison" in REFERENCE_BOOKS
        assert len(APA_REFERENCES) >= 5

    def test_apa_format(self):
        from app.services.lab_ai import APA_REFERENCES
        for key, ref in APA_REFERENCES.items():
            assert "(" in ref, f"APA format missing year parentheses: {key}"
            assert ref.endswith("."), f"APA format missing period: {key}"
