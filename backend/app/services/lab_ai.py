import re
from dataclasses import dataclass, field, asdict
from typing import Optional

REFERENCE_BOOKS = {
    "cheesbrough": "Cheesbrough M. District Laboratory Practice in Tropical Countries. 2nd ed. Cambridge University Press; 2005.",
    "who_afro": "WHO AFRO. Integrated Disease Surveillance and Response (IDSR) Technical Guidelines. 3rd ed; 2019.",
    "malawi_sop": "Malawi Ministry of Health. Malawi Standard Treatment Guidelines (MSTG). 7th ed; 2022.",
    "harrison": "Jameson JL et al. Harrison's Principles of Internal Medicine. 21st ed. McGraw Hill; 2022.",
    "henry": "McPherson RA, Pincus MR. Henry's Clinical Diagnosis and Management by Laboratory Methods. 24th ed. Elsevier; 2021.",
    "who_ebm": "WHO. WHO Guidelines on Use of Medically Important Antimicrobials. 2023.",
    "malawi_lab": "Malawi Ministry of Health. National Laboratory Policy & Standard Operating Procedures. 2nd ed; 2021.",
}

@dataclass
class LabTestDef:
    name: str
    dept: str
    unit: str
    male_low: float = None
    male_high: float = None
    female_low: float = None
    female_high: float = None
    child_low: float = None
    child_high: float = None
    critical_low: float = None
    critical_high: float = None
    text_interpret: dict = field(default_factory=dict)
    pregnancy_affects: bool = False
    references: list = field(default_factory=list)
    sop_ref: str = ""

def default_refs():
    return ["cheesbrough", "malawi_sop", "malawi_lab"]

LAB_TESTS: dict[str, LabTestDef] = {}

def _def(n, dept, unit, ml=None, mh=None, fl=None, fh=None, cl=None, ch=None, crl=None, crh=None, text_interpret=None, preg=False, refs=None, sop=""):
    LAB_TESTS[n] = LabTestDef(name=n, dept=dept, unit=unit, male_low=ml, male_high=mh, female_low=fl, female_high=fh,
                              child_low=cl, child_high=ch, critical_low=crl, critical_high=crh, text_interpret=text_interpret or {},
                              pregnancy_affects=preg, references=refs or default_refs(), sop_ref=sop)

# ===================== MICROBIOLOGY =====================
_dept = "Microbiology"
_def("Gram Stain", _dept, "", text_interpret={
    "gram positive cocci in clusters": "Suggestive of Staphylococcus spp. Perform catalase and coagulase for species identification. Consider MRSA screening per Malawi SOP.",
    "gram positive cocci in chains": "Suggestive of Streptococcus spp. Perform catalase (negative), optochin and bile solubility for differentiation.",
    "gram positive cocci in pairs": "Suggestive of Streptococcus pneumoniae. Perform optochin sensitivity and bile solubility.",
    "gram positive bacilli": "May indicate Bacillus spp., Clostridium spp., or Listeria spp. Correlation with clinical presentation required.",
    "gram negative cocci": "Likely Neisseria spp. (N. gonorrhoeae or N. meningitidis). Culture on Thayer-Martin media per Malawi SOP.",
    "gram negative bacilli": "Suggestive of Enterobacteriaceae (E. coli, Klebsiella, Salmonella, etc.). Perform oxidase, TSI, and biochemical tests.",
    "yeast cells": "Suggestive of Candida spp. Perform germ tube test for C. albicans identification.",
    "gram positive branching filaments": "Suggestive of Nocardia or Actinomyces spp. Notify clinician — may require prolonged incubation.",
    "no organisms seen": "No organisms observed on Gram stain. Culture results may still yield growth — correlate.",
})
_def("Culture & Sensitivity", _dept, "", text_interpret={
    "no growth": "No bacterial growth after 48h. Consider viral, fungal, or atypical pathogens if clinically indicated.",
    "scanty growth": "Minimal growth. Clinical correlation advised — may represent colonisation vs true infection.",
    "moderate growth": "Moderate growth. Likely clinically significant — correlate with Gram stain and clinical presentation.",
    "heavy growth": "Heavy pure growth — highly suggestive of significant infection. Start targeted antibiotics based on sensitivity.",
    "mixed growth": "Mixed growth of >2 organisms. Likely contamination or colonisation. Recommend repeat collection with proper aseptic technique.",
})
_def("AFB Smear (ZN Stain)", _dept, "", text_interpret={
    "negative": "No acid-fast bacilli seen per 100 fields. If clinical suspicion high, request GeneXpert or TB culture (LJ medium).",
    "scanty": "1-9 AFB per 100 fields. Report exact count. Request GeneXpert for confirmation and rifampicin resistance testing.",
    "1+": "10-99 AFB per 100 fields. Positive. Notify clinician. Initiate TB treatment per Malawi National TB Control guidelines.",
    "2+": "1-10 AFB per field in ≥50 fields. Strong positive. Urgent clinical referral required.",
    "3+": ">10 AFB per field in ≥20 fields. Very high burden. Urgent initiation of anti-TB therapy per MSTG.",
})
_def("India Ink Preparation", _dept, "", text_interpret={
    "negative": "No encapsulated yeasts seen. If cryptococcal meningitis suspected, request CrAg (cryptococcal antigen) test.",
    "positive": "Encapsulated yeasts consistent with Cryptococcus neoformans. Start antifungal therapy per Malawi HIV guidelines.",
})
_def("Wet Mount (Vaginal)", _dept, "", text_interpret={
    "trichomonas vaginalis seen": "Motile trichomonads seen. Treat with metronidazole per MSTG. Partner treatment required.",
    "clue cells seen": "Clue cells with fishy odour — consistent with Bacterial Vaginosis. Treat with metronidazole per Malawi SOP.",
    "candida hyphae seen": "Pseudohyphae consistent with Candida vulvovaginitis. Treat with clotrimazole or fluconazole.",
    "normal": "No abnormal findings. Normal vaginal flora (predominantly Lactobacillus spp.).",
})
_def("KOH Mount", _dept, "", text_interpret={
    "negative": "No fungal elements seen. Consider other aetiologies if dermatophyte infection suspected.",
    "positive": "Fungal hyphae and/or spores seen. Consistent with dermatophyte infection. Start topical/systemic antifungal.",
})
_def("Blood Culture", _dept, "", text_interpret={
    "no growth 48h": "No growth after 48 hours. Incubate for 5-7 days before reporting negative. Consider subculture on day 2 and 5.",
    "no growth 5d": "No growth after 5 days. Report as negative. If still clinically indicated, repeat blood cultures.",
    "positive": "Bacterial growth detected. Gram stain and subculture in progress. Notify clinician immediately.",
    "contaminant": "Likely skin contaminant (coagulase-negative Staphylococcus, diphtheroids, Bacillus spp.). Clinical correlation advised.",
})
_def("Widal Test", _dept, "titre", text_interpret={
    "<1:40": "Non-significant. No evidence of Salmonella typhi/paratyphi infection.",
    "1:40": "Borderline — may be residual from past infection or early disease. Repeat in 7-10 days if clinically indicated.",
    "1:80": "Suggestive of active infection — correlate with clinical presentation and blood culture.",
    "1:160": "Significant titre — highly suggestive of enteric fever. Start treatment per MSTG guidelines.",
    ">=1:320": "Very high titre — consistent with active enteric fever. Notify clinician urgently.",
})
_def("RDT Malaria", _dept, "", text_interpret={
    "negative": "No malaria antigen detected. If strong clinical suspicion, perform blood film (thick + thin smear).",
    "pf positive": "P. falciparum antigen detected. Start artemisinin-based combination therapy (ACT) per Malawi Malaria guidelines.",
    "pan positive": "Pan-malarial antigen detected (non-P. falciparum species). Treat appropriately per species.",
    "pf + pan positive": "Mixed species infection detected (P. falciparum + non-P. falciparum). Treat with ACT per MSTG.",
})
_def("Malaria Blood Film", _dept, "/uL", ml=0, mh=0, fl=0, fh=0, cl=0, ch=0, sop="MOH-Malaria-2022",
    text_interpret={"0": "No malaria parasites seen on thick and thin films. If high suspicion, repeat in 12-24 hours."},
    refs=["cheesbrough", "malawi_sop"])
_def("Cryptococcal Antigen (CrAg)", _dept, "", text_interpret={
    "negative": "No cryptococcal antigen detected. Low likelihood of cryptococcal meningitis.",
    "positive": "Cryptococcal antigen detected. Start fluconazole or amphotericin-based therapy per Malawi HIV guidelines.",
})
_def("GeneXpert MTB/RIF", _dept, "", text_interpret={
    "mtb not detected": "M. tuberculosis complex not detected. If high clinical suspicion, consider retesting or culture.",
    "mtb detected rif resistant": "M. tuberculosis detected with rifampicin resistance. Refer for MDR-TB treatment per Malawi NTP.",
    "mtb detected rif indeterminate": "M. tuberculosis detected but RIF resistance indeterminate. Repeat Xpert or perform DST.",
    "mtb detected rif sensitive": "M. tuberculosis detected, sensitive to rifampicin. Start first-line anti-TB therapy.",
})
_def("Lactophenol Cotton Blue Mount", _dept, "", text_interpret={
    "no fungal elements": "No fungal structures identified. Consider repeat sampling if suspicion remains.",
    "fungal hyphae septate": "Septate hyphae — consistent with Aspergillus spp. or other hyalohyphomycetes. Culture for definitive ID.",
    "fungal hyphae non-septate": "Broad, non-septate hyphae — suggestive of Mucorales (zygomycosis). Urgent clinical notification required.",
    "yeast cells with capsules": "Encapsulated yeast — consistent with Cryptococcus neoformans.",
})

# ===================== CLINICAL CHEMISTRY =====================
_dept = "Clinical Chemistry"
_def("Glucose (Fasting)", _dept, "mmol/L", ml=3.9, mh=6.1, fl=3.9, fh=6.1, cl=3.3, ch=5.6, crl=2.2, crh=25.0, sop="MOH-DM-2022",
    refs=["harrison", "malawi_sop"])
_def("Glucose (Random)", _dept, "mmol/L", ml=3.9, mh=11.1, fl=3.9, fh=11.1, cl=3.3, ch=11.1, crl=2.2, crh=25.0)
_def("HbA1c", _dept, "%", ml=4.0, mh=6.0, fl=4.0, fh=6.0, cl=4.0, ch=6.0, preg=True,
    sop="MOH-DM-2022", refs=["harrison", "malawi_sop"])
_def("Urea", _dept, "mmol/L", ml=2.5, mh=7.1, fl=2.5, fh=7.1, cl=1.8, ch=6.4, crh=35.0)
_def("Creatinine", _dept, "umol/L", ml=62, mh=106, fl=44, fh=80, cl=27, ch=62, crh=450)
_def("Sodium (Na+)", _dept, "mmol/L", ml=136, mh=145, fl=136, fh=145, cl=136, ch=145, crl=120, crh=160)
_def("Potassium (K+)", _dept, "mmol/L", ml=3.5, mh=5.1, fl=3.5, fh=5.1, cl=3.5, ch=5.1, crl=2.5, crh=6.5)
_def("Chloride (Cl-)", _dept, "mmol/L", ml=98, mh=107, fl=98, fh=107, cl=98, ch=107)
_def("Bicarbonate (HCO3-)", _dept, "mmol/L", ml=22, mh=29, fl=22, fh=29, cl=20, ch=28, crl=10, crh=40)
_def("Calcium (Total)", _dept, "mmol/L", ml=2.15, mh=2.55, fl=2.15, fh=2.55, cl=2.1, ch=2.55, crl=1.75, crh=3.5, sop="MOH-Ca-2022")
_def("Phosphate", _dept, "mmol/L", ml=0.81, mh=1.45, fl=0.81, fh=1.45, cl=1.2, ch=1.8)
_def("Uric Acid", _dept, "mmol/L", ml=0.20, mh=0.42, fl=0.14, fh=0.36, cl=0.12, ch=0.32)
_def("Total Protein", _dept, "g/L", ml=60, mh=80, fl=60, fh=80, cl=60, ch=80)
_def("Albumin", _dept, "g/L", ml=35, mh=50, fl=35, fh=50, cl=35, ch=50)
_def("Globulin", _dept, "g/L", ml=20, mh=35, fl=20, fh=35, cl=20, ch=35)
_def("A/G Ratio", _dept, "", ml=1.0, mh=2.0, fl=1.0, fh=2.0, cl=1.0, ch=2.0)
_def("Bilirubin (Total)", _dept, "umol/L", ml=0, mh=21, fl=0, fh=21, cl=0, ch=21, crh=340)
_def("Bilirubin (Direct)", _dept, "umol/L", ml=0, mh=5.1, fl=0, fh=5.1, cl=0, ch=5.1)
_def("Bilirubin (Indirect)", _dept, "umol/L", ml=0, mh=17, fl=0, fh=17, cl=0, ch=17)
_def("ALT (SGPT)", _dept, "U/L", ml=10, mh=40, fl=10, fh=40, cl=10, ch=40, crh=300, sop="MOH-LFT-2022")
_def("AST (SGOT)", _dept, "U/L", ml=10, mh=40, fl=10, fh=40, cl=10, ch=40, crh=300)
_def("ALP", _dept, "U/L", ml=44, mh=147, fl=44, fh=147, cl=100, ch=350, preg=True)
_def("GGT", _dept, "U/L", ml=8, mh=61, fl=5, fh=36, cl=5, ch=35)
_def("LDH", _dept, "U/L", ml=140, mh=280, fl=140, fh=280, cl=140, ch=280)
_def("Amylase", _dept, "U/L", ml=30, mh=110, fl=30, fh=110, cl=30, ch=110)
_def("Lipase", _dept, "U/L", ml=0, mh=60, fl=0, fh=60, cl=0, ch=60)
_def("Cholesterol (Total)", _dept, "mmol/L", ml=3.6, mh=5.2, fl=3.6, fh=5.2, cl=3.0, ch=4.5, sop="MOH-CVD-2022",
    refs=["harrison", "malawi_sop"])
_def("HDL Cholesterol", _dept, "mmol/L", ml=0.9, mh=2.5, fl=1.0, fh=2.5, cl=0.9, ch=2.5)
_def("LDL Cholesterol", _dept, "mmol/L", ml=0, mh=3.4, fl=0, fh=3.4, cl=0, ch=3.0, crh=4.9)
_def("Triglycerides", _dept, "mmol/L", ml=0, mh=1.7, fl=0, fh=1.7, cl=0, ch=1.5, crh=5.0)
_def("CRP (Quantitative)", _dept, "mg/L", ml=0, mh=5, fl=0, fh=5, cl=0, ch=5, crh=100)
_def("ESR (Westergren)", _dept, "mm/hr", ml=0, mh=15, fl=0, fh=20, cl=0, ch=10, preg=True)
_def("Ferritin", _dept, "ug/L", ml=20, mh=250, fl=15, fh=150, cl=15, ch=100)
_def("Iron (Serum)", _dept, "umol/L", ml=11, mh=32, fl=9, fh=27, cl=9, ch=27)
_def("TIBC", _dept, "umol/L", ml=45, mh=77, fl=45, fh=77, cl=45, ch=77)
_def("Transferrin Saturation", _dept, "%", ml=16, mh=50, fl=15, fh=50, cl=15, ch=50)
_def("Vitamin B12", _dept, "pmol/L", ml=145, mh=569, fl=145, fh=569, cl=145, ch=569)
_def("Folate", _dept, "nmol/L", ml=7, mh=45, fl=7, fh=45, cl=7, ch=45)
_def("PSA (Total)", _dept, "ug/L", ml=0, mh=4.0, fl=None, fh=None, cl=None, ch=None, sop="MOH-CaP-2022")

# ===================== HAEMATOLOGY =====================
_dept = "Haematology"
_def("Haemoglobin (Hb)", _dept, "g/dL", ml=13.5, mh=17.5, fl=11.5, fh=15.5, cl=10.5, ch=14.0, crl=6.0, preg=True,
    sop="MOH-ANC-2022", refs=["henry", "malawi_sop"])
_def("RBC Count", _dept, "x10^12/L", ml=4.5, mh=5.5, fl=3.8, fh=4.8, cl=3.5, ch=4.5, preg=True)
_def("Haematocrit (HCT)", _dept, "%", ml=40, mh=50, fl=35, fh=45, cl=32, ch=42, crl=20, preg=True)
_def("MCV", _dept, "fL", ml=80, mh=96, fl=80, fh=96, cl=75, ch=95)
_def("MCH", _dept, "pg", ml=27, mh=32, fl=27, fh=32, cl=25, ch=32)
_def("MCHC", _dept, "g/dL", ml=320, mh=360, fl=320, fh=360, cl=320, ch=360)
_def("RDW", _dept, "%", ml=11.5, mh=14.5, fl=11.5, fh=14.5, cl=11.5, ch=14.5)
_def("WBC Count", _dept, "x10^9/L", ml=4.0, mh=10.0, fl=4.0, fh=10.0, cl=5.0, ch=15.0, crl=1.0, crh=30.0, preg=True)
_def("Neutrophils", _dept, "%", ml=40, mh=70, fl=40, fh=70, cl=40, ch=70)
_def("Neutrophils (Absolute)", _dept, "x10^9/L", ml=1.5, mh=7.5, fl=1.5, fh=7.5, cl=1.5, ch=7.5, crl=0.5)
_def("Lymphocytes", _dept, "%", ml=20, mh=45, fl=20, fh=45, cl=20, ch=45)
_def("Lymphocytes (Absolute)", _dept, "x10^9/L", ml=1.0, mh=4.0, fl=1.0, fh=4.0, cl=1.5, ch=6.5)
_def("Monocytes", _dept, "%", ml=2, mh=10, fl=2, fh=10, cl=2, ch=10)
_def("Eosinophils", _dept, "%", ml=1, mh=6, fl=1, fh=6, cl=1, ch=6, refs=["henry", "malawi_sop"])
_def("Basophils", _dept, "%", ml=0, mh=2, fl=0, fh=2, cl=0, ch=2)
_def("Platelet Count", _dept, "x10^9/L", ml=150, mh=400, fl=150, fh=400, cl=150, ch=400, crl=20, crh=800, preg=True)
_def("Reticulocyte Count", _dept, "%", ml=0.5, mh=2.5, fl=0.5, fh=2.5, cl=0.5, ch=2.5)
_def("Blood Group", _dept, "", text_interpret={
    "a+": "Blood group A Rh-positive. Can receive A+, A-, O+, O-. Can donate to A+, AB+.",
    "a-": "Blood group A Rh-negative. Can receive A-, O-. Can donate to A-, A+, AB-, AB+.",
    "b+": "Blood group B Rh-positive. Can receive B+, B-, O+, O-. Can donate to B+, AB+.",
    "b-": "Blood group B Rh-negative. Can receive B-, O-. Can donate to B-, B+, AB-, AB+.",
    "ab+": "Blood group AB Rh-positive (universal recipient). Can receive all types. Can donate to AB+.",
    "ab-": "Blood group AB Rh-negative. Can receive A-, B-, AB-, O-. Can donate to AB+, AB-.",
    "o+": "Blood group O Rh-positive. Can receive O+, O-. Can donate to all Rh+ types.",
    "o-": "Blood group O Rh-negative (universal donor). Can receive O-. Can donate to all types.",
})
_def("Blood Film Comment", _dept, "", text_interpret={
    "normocytic normochromic": "Normal red cell morphology. No significant abnormalities detected.",
    "microcytic hypochromic": "Consistent with iron deficiency anaemia or thalassaemia trait. Check ferritin, iron studies, Hb electrophoresis.",
    "macrocytic": "Macrocytic red cells. Check B12, folate levels. Consider causes: B12/folate deficiency, alcohol, MDS, hypothyroidism.",
    "dimorphic": "Dual red cell populations. Consider sideroblastic anaemia, post-transfusion, or combined deficiency states.",
    "sickle cells": "Sickle-shaped RBCs seen. Consistent with sickle cell disease (HbSS or HbSC). Perform Hb electrophoresis.",
    "target cells": "Target cells present. Consider HbC disease, thalassaemia, liver disease, or post-splenectomy.",
    "spherocytes": "Spherocytes seen. Consider hereditary spherocytosis, autoimmune haemolytic anaemia, or recent transfusion.",
    "blasts seen": "Blast cells identified. Urgent haematology referral required. Perform bone marrow aspirate and flow cytometry.",
    "malaria parasites": "Plasmodium spp. identified on film. Quantify parasitaemia. Treat per Malawi Malaria guidelines.",
    "microfilaria seen": "Microfilaria of Wuchereria bancrofti seen. Treat with ivermectin/albendazole per Malawi NTD programme.",
})
_def("Hb Electrophoresis", _dept, "", text_interpret={
    "aa": "HbAA — normal adult haemoglobin pattern. No haemoglobinopathy detected.",
    "as": "HbAS — sickle cell trait. Generally asymptomatic. Genetic counselling recommended.",
    "ss": "HbSS — sickle cell disease. Start folic acid, pneumococcal prophylaxis. Refer to specialist clinic per Malawi SOP.",
    "ac": "HbAC — HbC trait. Usually asymptomatic. Genetic counselling recommended.",
    "cc": "HbCC — HbC disease. Mild haemolytic anaemia. Monitor Hb and reticulocyte count.",
    "sc": "HbSC — sickle cell disease (compound heterozygote). Clinical severity variable. Refer to specialist.",
    "a2 elevated": "Elevated HbA2 (>3.5%) — consistent with beta-thalassaemia trait. Check ferritin to exclude IDA.",
    "f升高": "Elevated HbF — consider beta-thalassaemia major/intermedia, hereditary persistence of HbF, or juvenile myelomonocytic leukaemia.",
})

# ===================== URINALYSIS =====================
_dept = "Urinalysis"
_def("Urine Colour", _dept, "", text_interpret={
    "straw": "Normal urine colour.",
    "yellow": "Normal — concentrated urine. Adequate hydration recommended.",
    "dark yellow": "Concentrated urine. Increase fluid intake.",
    "amber": "May indicate dehydration or elevated urobilinogen.",
    "red/pink": "Possible haematuria, haemoglobinuria, myoglobinuria, or dietary causes (beetroot, rifampicin). Perform microscopy.",
    "brown": "May indicate bilirubinuria, porphyria, or methemoglobinuria. Check LFTs and urine bilirubin.",
    "cloudy": "May indicate pyuria, bacteriuria, phosphaturia, or chyluria. Perform microscopy and dipstick.",
    "cola coloured": "Suggests glomerulonephritis or rhabdomyolysis. Check urine protein, creatinine kinase, and renal function.",
})
_def("Urine Appearance", _dept, "", text_interpret={
    "clear": "Normal — no visible turbidity.",
    "slightly cloudy": "Minimal turbidity. May be normal or early UTI. Correlate with dipstick and microscopy.",
    "cloudy": "Turbid urine. Likely pyuria/bacteriuria. Perform microscopy and culture.",
    "blood stained": "Visible blood. Perform microscopy for RBC count and morphology. Rule out UTI, stones, glomerulonephritis.",
})
_def("Urine pH", _dept, "", ml=4.5, mh=8.0, fl=4.5, fh=8.0, cl=4.5, ch=8.0, sop="MOH-Urine-2022",
    text_interpret={
        "<5.5": "Acidic urine. Consider: high-protein diet, metabolic acidosis, UTI (E. coli), or medications (vitamin C).",
        ">7.5": "Alkaline urine. Consider: UTI (Proteus, Pseudomonas), vegetarian diet, renal tubular acidosis, or stale specimen.",
    })
_def("Urine Specific Gravity", _dept, "", ml=1.005, mh=1.030, fl=1.005, fh=1.030, cl=1.005, ch=1.030)
_def("Urine Glucose", _dept, "", text_interpret={
    "negative": "Normal — no glucose detected.",
    "1+": "Trace glucose. Check blood glucose. May be renal glycosuria if blood glucose normal.",
    "2+": "Moderate glucose. Likely diabetes mellitus. Check fasting glucose and HbA1c.",
    "3+": "Significant glucosuria. Start diabetes workup per Malawi SOP.",
    "4+": "Heavy glucosuria. Urgent blood glucose and ketone check. Rule out DKA.",
})
_def("Urine Protein", _dept, "", text_interpret={
    "negative": "Normal — no protein detected.",
    "trace": "Trace protein. May be normal or early renal disease. Repeat with first morning specimen.",
    "1+": "Mild proteinuria (approx 0.3 g/L). Correlate with microscopy. Consider 24h urine protein if persistent.",
    "2+": "Moderate proteinuria (approx 1.0 g/L). Investigate renal function, ACR/PCR. Refer if persistent.",
    "3+": "Significant proteinuria (approx 3.0 g/L). Likely glomerular disease. Urgent nephrology referral.",
    "4+": "Nephrotic-range proteinuria. 24h urine protein, renal function, and nephrology referral required.",
})
_def("Urine Blood", _dept, "", text_interpret={
    "negative": "Normal — no blood detected.",
    "trace": "Trace haemoglobin. Menstrual contamination in females. Repeat mid-stream specimen.",
    "1+": "Mild haematuria. Perform microscopy for RBC count. Consider UTI, stones, or glomerular disease.",
    "2+": "Moderate haematuria. Microscopy, culture, and imaging (ultrasound) recommended.",
    "3+": "Significant haematuria. Urgent evaluation — consider infection, stones, glomerulonephritis, or malignancy.",
})
_def("Urine Ketones", _dept, "", text_interpret={
    "negative": "Normal — no ketones detected.",
    "1+": "Trace ketones. May be due to fasting, diet, or early DKA. Check blood glucose and beta-hydroxybutyrate.",
    "2+": "Moderate ketonuria. Likely DKA or starvation ketosis. Check blood glucose, electrolytes, and ABG.",
    "3+": "Significant ketonuria. Urgent medical assessment. Likely DKA — start IV fluids and insulin per Malawi protocol.",
})
_def("Urine Urobilinogen", _dept, "umol/L", ml=0, mh=17, fl=0, fh=17, cl=0, ch=17)
_def("Urine Bilirubin", _dept, "", text_interpret={
    "negative": "Normal — no bilirubin detected.",
    "positive": "Conjugated bilirubin detected. Suggests obstructive jaundice or hepatocellular injury. Check LFTs.",
})
_def("Urine Nitrite", _dept, "", text_interpret={
    "negative": "UTI not excluded (some organisms do not reduce nitrate). Correlate with WBC and clinical signs.",
    "positive": "Suggests nitrate-reducing bacteria (Enterobacteriaceae). Likely UTI. Perform microscopy and culture.",
})
_def("Urine Leucocyte Esterase", _dept, "", text_interpret={
    "negative": "No significant pyuria. UTI less likely but not excluded.",
    "trace": "Minimal WBC activity. May be early infection or contamination. Repeat with clean-catch specimen.",
    "1+": "Mild pyuria. Possible UTI. Correlate with nitrite, microscopy, and clinical symptoms.",
    "2+": "Moderate pyuria. Likely UTI. Perform microscopy and culture. Start empirical antibiotics per Malawi SOP.",
    "3+": "Marked pyuria. Urinary tract infection highly likely. Urgent microscopy, culture, and treatment.",
})
_def("Urine Microscopy — WBC", _dept, "/HPF", ml=0, mh=5, fl=0, fh=5, cl=0, ch=5)
_def("Urine Microscopy — RBC", _dept, "/HPF", ml=0, mh=3, fl=0, fh=3, cl=0, ch=3, crh=50)
_def("Urine Microscopy — Casts", _dept, "/LPF", text_interpret={
    "none seen": "Normal — no casts identified.",
    "hyaline casts": "Hyaline casts — may be normal (exercise, dehydration) or early renal disease.",
    "granular casts": "Granular casts — suggest renal tubular injury or glomerulonephritis. Correlate with proteinuria and renal function.",
    "red cell casts": "RBC casts — diagnostic of glomerulonephritis. Urgent nephrology referral required.",
    "white cell casts": "WBC casts — suggest pyelonephritis or tubulointerstitial nephritis.",
    "waxy casts": "Waxy casts — indicate advanced chronic kidney disease.",
})
_def("Urine Microscopy — Crystals", _dept, "", text_interpret={
    "none seen": "No crystals identified.",
    "calcium oxalate": "Calcium oxalate crystals. Common — may be dietary or early stone formation. Hydrate and repeat.",
    "uric acid": "Uric acid crystals. Associated with acidic urine, gout, or high-purine diet.",
    "triple phosphate": "Struvite crystals — associated with UTI (urease-producing organisms).",
    "cystine": "Cystine crystals — diagnostic of cystinuria. Refer for metabolic workup.",
})
_def("Urine hCG (Pregnancy)", _dept, "", text_interpret={
    "negative": "No hCG detected. Pregnancy unlikely if amenorrhoea is <7 days or test performed too early.",
    "positive": "hCG detected — pregnancy confirmed. Refer for antenatal care per Malawi ANC guidelines.",
})
_def("Urine Culture", _dept, "CFU/mL", text_interpret={
    "<10^3": "Insignificant growth. Likely contamination. Repeat if clinically indicated.",
    "10^3-10^4": "Borderline. Clinical correlation required. Repeat with clean-catch specimen if symptomatic.",
    ">=10^5": "Significant bacteriuria — consistent with UTI. Start antibiotics per culture sensitivity and Malawi SOP.",
    ">=10^2 (catheter)": "Significant in catheter specimen. Treat per sensitivity results.",
})

# ===================== PARASITOLOGY =====================
_dept = "Parasitology"
_def("Stool Microscopy — Ova & Cysts", _dept, "", text_interpret={
    "no ova/cysts seen": "No intestinal parasites detected on direct smear. If clinical suspicion high, perform concentration technique (formol-ether).",
    "hookworm ova": "Hookworm ova detected (Ancylostoma duodenale or Necator americanus). Treat with albendazole per Malawi SOP.",
    "ascaris lumbricoides": "Ascaris ova detected. Treat with albendazole or mebendazole. Health education on hygiene.",
    "trichuris trichiura": "Whipworm ova detected. Treat with albendazole for 3 days.",
    "schistosoma mansoni": "S. mansoni ova detected. Treat with praziquantel per Malawi Schistosomiasis Control Programme.",
    "schistosoma haematobium": "S. haematobium ova detected. Treat with praziquantel. Urine microscopy recommended.",
    "giardia lamblia (trophozoite)": "Giardia intestinalis trophozoites seen. Treat with metronidazole or tinidazole per MSTG.",
    "giardia lamblia (cyst)": "Giardia intestinalis cysts seen. Treat with metronidazole. Family screening recommended.",
    "entamoeba histolytica": "E. histolytica trophozoites/cysts (with ingested RBCs) seen. Treat with metronidazole + diloxanide.",
    "taenia spp": "Taenia ova detected. Treat with praziquantel or niclosamide.",
    "hymenolepis nana": "Dwarf tapeworm ova detected. Treat with praziquantel.",
    "strongyloides stercoralis": "Strongyloides larvae detected (may indicate hyperinfection in immunocompromised). Treat with ivermectin.",
    "cryptosporidium spp": "Cryptosporidium oocysts detected. Supportive care. In HIV patients, initiate ART and consider nitazoxanide.",
})
_def("Stool Occult Blood", _dept, "", text_interpret={
    "negative": "No occult blood detected.",
    "positive": "Occult blood detected. Consider: hookworm infection, peptic ulcer, IBD, colorectal pathology. Colonoscopy if persistent.",
})
_def("Kato-Katz (Stool Egg Count)", _dept, "eggs/g", sop="MOH-NTD-2022",
    text_interpret={
        "<100": "Light intensity infection (S. mansoni). Treat with praziquantel per Malawi NTD guidelines.",
        "100-399": "Moderate intensity infection. Treat with praziquantel. Follow-up stool exam recommended.",
        ">=400": "Heavy intensity infection. Treat with praziquantel. Repeat stool exam after 4 weeks.",
    })
_def("Blood Film — Trypanosomes", _dept, "", text_interpret={
    "negative": "No trypanosomes seen on thick and thin films. If suspected, repeat at night (coinciding with fever peaks).",
    "positive": "Trypanosoma brucei spp. detected. Urgent referral to district hospital for staging and treatment.",
})
_def("Blood Film — Borrelia", _dept, "", text_interpret={
    "negative": "No Borrelia spirochetes seen. If relapsing fever suspected, repeat during febrile episode.",
    "positive": "Borrelia duttonii detected. Treat with doxycycline or erythromycin per Malawi SOP.",
})

# ===================== MOLECULAR BIOLOGY =====================
_dept = "Molecular Biology"
_def("HIV-1 Viral Load", _dept, "copies/mL", ml=0, mh=40, fl=0, fh=40, cl=0, ch=40,
    sop="MOH-HIV-2022", refs=["malawi_sop", "who_afro"],
    text_interpret={
        "<40": "Suppressed (<40 copies/mL). Continue current ART regimen. Repeat VL in 6-12 months per Malawi HIV guidelines.",
        "40-999": "Low-level viraemia. Repeat VL in 3 months. Reinforce adherence.",
        "1000-9999": "Moderate viraemia. Assess adherence. Consider resistance testing if persistent.",
        ">=10000": "High-level viraemia. Likely treatment failure. Request HIV drug resistance testing and switch regimen per Malawi protocol.",
    })
_def("HIV-1 DNA PCR (Infant)", _dept, "", text_interpret={
    "negative": "HIV-1 DNA not detected. Continue prophylaxis. Repeat at 6 weeks post-exposure per Malawi EID guidelines.",
    "positive": "HIV-1 DNA detected. Infant likely HIV-infected. Start ART immediately per Malawi paediatric HIV guidelines.",
})
_def("CD4 Count", _dept, "cells/uL", ml=500, mh=1500, fl=500, fh=1500, cl=500, ch=2000,
    sop="MOH-HIV-2022", refs=["malawi_sop"])
_def("HBsAg (Hepatitis B)", _dept, "", text_interpret={
    "negative": "HBsAg not detected. No current HBV infection. Vaccinate if at risk per Malawi EPI schedule.",
    "positive": "HBsAg detected — indicates current HBV infection. Check HBeAg, HBV DNA, LFTs. Refer for management per Malawi guidelines.",
})
_def("HCV Antibody", _dept, "", text_interpret={
    "negative": "Anti-HCV not detected. No evidence of HCV infection.",
    "positive": "Anti-HCV detected. Perform HCV RNA to confirm active infection. Refer for treatment per Malawi HCV guidelines.",
})
_def("Syphilis Serology (RPR/VDRL)", _dept, "titre", text_interpret={
    "negative": "Non-reactive. No serological evidence of syphilis.",
    "1:2": "Low-titre reactive. May be old treated infection or early disease. Correlate with TPHA/TPPA.",
    "1:4-1:8": "Moderate titre. Likely active infection. Confirm with treponemal test. Treat with benzathine penicillin per MSTG.",
    ">=1:16": "High titre — active syphilis. Urgent treatment with benzathine penicillin. Contact tracing required.",
})
_def("TPHA/TPPA (Confirmatory)", _dept, "", text_interpret={
    "negative": "No treponemal antibodies. RPR/VDRL likely false positive.",
    "positive": "Treponemal antibodies confirmed. Syphilis diagnosis established. Stage and treat accordingly.",
})
_def("SARS-CoV-2 PCR", _dept, "", text_interpret={
    "negative": "SARS-CoV-2 RNA not detected. COVID-19 unlikely. If high suspicion, repeat in 3-5 days.",
    "positive": "SARS-CoV-2 RNA detected. Patient is COVID-19 positive. Isolate and manage per Malawi COVID-19 guidelines.",
})
_def("GeneXpert CT/NG", _dept, "", text_interpret={
    "ct negative ng negative": "Chlamydia trachomatis and Neisseria gonorrhoeae not detected.",
    "ct positive ng negative": "C. trachomatis detected. Treat with doxycycline or azithromycin per MSTG. Partner treatment required.",
    "ct negative ng positive": "N. gonorrhoeae detected. Treat with ceftriaxone + azithromycin per Malawi STI guidelines.",
    "ct positive ng positive": "Dual infection detected. Treat both with appropriate antibiotics.",
})

# ===================== SEMEN ANALYSIS =====================
_dept = "Semen Analysis"
_def("Semen Volume", _dept, "mL", ml=1.5, mh=5.0, fl=1.5, fh=5.0, sop="WHO-Semen-2021",
    refs=["who_afro", "henry"])
_def("Sperm Concentration", _dept, "x10^6/mL", ml=15, mh=200, fl=15, fh=200, sop="WHO-Semen-2021")
_def("Total Motility", _dept, "%", ml=40, mh=100, fl=40, fh=100)
_def("Progressive Motility", _dept, "%", ml=32, mh=100, fl=32, fh=100)
_def("Sperm Morphology (Normal)", _dept, "%", ml=4, mh=100, fl=4, fh=100)
_def("pH (Semen)", _dept, "", ml=7.2, mh=8.0, fl=7.2, fh=8.0)
_def("WBC in Semen", _dept, "x10^6/mL", ml=0, mh=1.0, fl=0, fh=1.0)
_def("Semen Fructose", _dept, "", text_interpret={
    "present": "Fructose detected — suggests patent seminal vesicles and ejaculatory ducts.",
    "absent": "Fructose not detected — possible ejaculatory duct obstruction or seminal vesicle aplasia.",
})

DEPARTMENTS = [
    "Microbiology", "Clinical Chemistry", "Haematology",
    "Urinalysis", "Parasitology", "Molecular Biology", "Semen Analysis"
]

DEPARTMENT_TESTS = {dept: [t for t in LAB_TESTS.values() if t.dept == dept] for dept in DEPARTMENTS}


@dataclass
class InterpretationResult:
    test_name: str
    result_value: str
    flag: str  # normal, high, low, critical_high, critical_low, interpret
    interpretation: str
    recommendation: str
    references: list
    department: str


def interpret_result(test_name: str, result_value: str,
                     gender: str = "male", age: Optional[float] = None,
                     pregnant: bool = False,
                     metadata: Optional[dict] = None) -> InterpretationResult:
    td = LAB_TESTS.get(test_name)
    if not td:
        # fuzzy match
        for n, t in LAB_TESTS.items():
            if test_name.lower() in n.lower():
                td = t
                break
    if not td:
        return InterpretationResult(
            test_name=test_name, result_value=result_value,
            flag="unknown", interpretation="Test not found in knowledge base.",
            recommendation="Consult laboratory reference manual.",
            references=["malawi_lab"], department="Unknown"
        )

    is_child = age is not None and age < 15
    rv_low = result_value.strip().lower()

    # text-based interpretation
    if td.text_interpret:
        for key, interp in td.text_interpret.items():
            if rv_low == key:
                rec = _recommend(td, rv_low, gender, age, pregnant, metadata)
                return InterpretationResult(
                    test_name=td.name, result_value=result_value,
                    flag="interpret", interpretation=interp,
                    recommendation=rec,
                    references=td.references, department=td.dept
                )

    # numeric interpretation
    try:
        val = _parse_numeric(result_value)
    except ValueError:
        return InterpretationResult(
            test_name=td.name, result_value=result_value,
            flag="unknown", interpretation="Unable to parse numeric value for reference range comparison.",
            recommendation="Verify result format and re-enter.",
            references=td.references, department=td.dept
        )

    low, high = _get_ranges(td, gender, is_child)
    cl, ch = td.critical_low, td.critical_high

    notes = []
    if pregnant and td.pregnancy_affects:
        notes.append("Pregnancy may affect reference ranges — interpret with caution.")

    flag = "normal"
    interp = f"{td.name}: {result_value} {td.unit}. "

    if cl is not None and val < cl:
        flag = "critical_low"
        interp += f"CRITICALLY LOW (reference: {low}-{high}). Urgent clinical attention required."
    elif ch is not None and val > ch:
        flag = "critical_high"
        interp += f"CRITICALLY HIGH (reference: {low}-{high}). Urgent clinical attention required."
    elif low is not None and val < low:
        flag = "low"
        interp += f"Low (reference: {low}-{high} {td.unit}). "
    elif high is not None and val > high:
        flag = "high"
        interp += f"High (reference: {low}-{high} {td.unit}). "
    else:
        interp += f"Within normal reference range ({low}-{high} {td.unit})."

    if notes:
        interp += " " + " ".join(notes)

    rec = _recommend(td, result_value, gender, age, pregnant, metadata, flag=flag)

    return InterpretationResult(
        test_name=td.name, result_value=result_value,
        flag=flag, interpretation=interp.strip(),
        recommendation=rec,
        references=td.references, department=td.dept
    )


def interpret_batch(results: list, gender: str = "male", age: float = None,
                    pregnant: bool = False, patient_name: str = "",
                    metadata: dict = None) -> dict:
    interpretations = []
    flags = []
    for r in results:
        ir = interpret_result(r.get("test"), r.get("result"), gender, age, pregnant, metadata)
        interpretations.append(asdict(ir))
        flags.append(ir.flag)

    summary = _batch_summary(flags, patient_name)
    return {
        "patient": patient_name or "Unknown",
        "gender": gender,
        "age": age,
        "pregnant": pregnant,
        "results": interpretations,
        "summary": summary,
        "total_tests": len(results),
        "abnormal_count": sum(1 for f in flags if f != "normal" and f != "interpret"),
    }


def _get_ranges(td: LabTestDef, gender: str, is_child: bool):
    if is_child:
        return td.child_low, td.child_high
    if gender == "female":
        return td.female_low or td.male_low, td.female_high or td.male_high
    return td.male_low, td.male_high


def _parse_numeric(val: str) -> float:
    val = re.sub(r'[^\d.,]', '', val).strip()
    if not val:
        raise ValueError
    if ',' in val and '.' in val:
        if val.rindex(',') > val.rindex('.'):
            val = val.replace('.', '').replace(',', '.')
        else:
            val = val.replace(',', '')
    elif ',' in val:
        val = val.replace(',', '.')
    return float(val)


def _recommend(td: LabTestDef, val, gender, age, pregnant, metadata, flag="normal") -> str:
    if flag == "critical_low":
        return "CRITICAL: Immediate clinician notification required. Repeat test urgently and verify with new specimen."
    if flag == "critical_high":
        return "CRITICAL: Immediate clinician notification required. Repeat test urgently and verify with new specimen."
    if flag == "high":
        if td.name == "Glucose (Fasting)":
            return "Repeat fasting glucose. If ≥7.0 mmol/L on two occasions, diagnose diabetes per Malawi SOP. Consider HbA1c."
        if td.name == "HbA1c":
            return "Repeat HbA1c in 3 months. If ≥6.5%, diagnose diabetes. Start lifestyle counselling."
        if "ALT" in td.name or "AST" in td.name:
            return "Evaluate for causes of liver injury (viral hepatitis, alcohol, drugs, NAFLD). Repeat LFTs in 2 weeks."
        if td.name == "Creatinine":
            return "Check eGFR. Repeat creatinine. If persistently elevated, refer for renal assessment."
        if td.name == "Potassium (K+)" and flag == "high":
            return "Repeat with haemolysis-free specimen. If confirmed, check ECG and treat per Malawi protocol."
        return "Result is above reference range. Correlate clinically. Repeat if unexpected."
    if flag == "low":
        if td.name == "Haemoglobin (Hb)":
            anc = " In pregnancy, start iron and folic acid per ANC guidelines." if pregnant else ""
            return f"Anaemia detected. Check MCV, ferritin, blood film. Treat underlying cause.{anc}"
        if td.name == "CD4 Count":
            return "Immunosuppression. Ensure patient is on ART. Start co-trimoxazole prophylaxis if CD4 <200 per Malawi guidelines."
        return "Result is below reference range. Correlate clinically. Consider repeat testing."
    return "Result within normal range. No further action required."


def _batch_summary(flags, patient_name):
    n = len(flags)
    norm = flags.count("normal") + flags.count("interpret")
    abn = n - norm
    crit = flags.count("critical_low") + flags.count("critical_high")
    if crit > 0:
        return f"{'Patient' if not patient_name else patient_name} has {crit} critical result(s) requiring immediate action. {abn} abnormal result(s) out of {n} tests."
    if abn == 0:
        return f"All {n} result(s) within normal limits."
    return f"{abn} abnormal result(s) out of {n} tests. Clinical correlation recommended."


# =====================================================================
# TEST PROCEDURE KNOWLEDGE BASE (Pre-analytical → Analytical → Post-analytical)
# =====================================================================

APA_REFERENCES = {
    "cheesbrough": "Cheesbrough, M. (2005). District laboratory practice in tropical countries (2nd ed.). Cambridge University Press.",
    "who_afro": "World Health Organization Regional Office for Africa. (2019). Integrated disease surveillance and response (IDSR) technical guidelines (3rd ed.). WHO AFRO.",
    "malawi_sop": "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi.",
    "harrison": "Jameson, J. L., Kasper, D. L., Longo, D. L., Fauci, A. S., Hauser, S. L., & Loscalzo, J. (2022). Harrison's principles of internal medicine (21st ed.). McGraw Hill.",
    "henry": "McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
    "who_ebm": "World Health Organization. (2023). WHO guidelines on use of medically important antimicrobials. WHO.",
    "malawi_lab": "Malawi Ministry of Health. (2021). National laboratory policy and standard operating procedures (2nd ed.). Government of Malawi.",
    "who_malaria": "World Health Organization. (2022). WHO guidelines for malaria. WHO.",
    "who_hiv": "World Health Organization. (2022). Consolidated guidelines on HIV prevention, testing, treatment, service delivery and monitoring. WHO.",
    "who_tb": "World Health Organization. (2022). WHO consolidated guidelines on tuberculosis. WHO.",
    "cdc_antibiotic": "Centers for Disease Control and Prevention. (2023). Antibiotic resistance threats in the United States. U.S. Department of Health and Human Services.",
    "who_semen": "World Health Organization. (2021). WHO laboratory manual for the examination and processing of human semen (6th ed.). WHO.",
    "clsi": "Clinical and Laboratory Standards Institute. (2022). Performance standards for antimicrobial susceptibility testing (32nd ed., CLSI supplement M100). CLSI.",
}

@dataclass
class TestProcedure:
    name: str
    department: str
    specimen_type: str
    container: str
    volume: str
    storage: str
    transport: str
    patient_prep: str
    methodology: str
    equipment: str
    quality_control: str
    turnaround: str
    interpretation: str
    clinical_significance: str
    limitations: str
    references_apa: list
    references_keys: list


TEST_PROCEDURES: dict[str, TestProcedure] = {}


def _proc(name, dept, spec, container, volume, storage, transport, patient_prep,
          methodology, equipment, qc, tat, interpretation, clinical_sig, limitations,
          refs_apa, ref_keys):
    TEST_PROCEDURES[name] = TestProcedure(
        name=name, department=dept, specimen_type=spec, container=container,
        volume=volume, storage=storage, transport=transport, patient_prep=patient_prep,
        methodology=methodology, equipment=equipment, quality_control=qc,
        turnaround=tat, interpretation=interpretation, clinical_significance=clinical_sig,
        limitations=limitations, references_apa=refs_apa, references_keys=ref_keys,
    )


# --------------------- MICROBIOLOGY ---------------------
_d = "Microbiology"
_proc("Gram Stain", _d, "Clinical specimen (sputum, pus, CSF, urine, swab, tissue)", "Sterile container / swab in transport medium",
      "As per specimen", "Room temp: 2 h; Refrigerate: 24 h if delay",
      "Triple-packed in leak-proof container; transport within 2 h",
      "Collect before antimicrobial therapy where possible; clean site with 70% alcohol for invasive procedures",
      "Heat-fixed smear stained with crystal violet (1 min) → Gram's iodine (1 min) → acetone-alcohol decolouriser (10–15 s) → safranin counterstain (30 s). Examine under oil immersion (×1000).",
      "Microscope (×1000 oil immersion), staining rack, timer, glass slides, inoculating loop, Bunsen burner",
      "Positive control: S. aureus (ATCC 25923) — gram-positive cocci; E. coli (ATCC 25922) — gram-negative rods. Negative: reagent sterility check with sterile saline. Daily QC before patient runs.",
      "Within 1 h of specimen receipt (STAT: 30 min)",
      "Report organisms, morphology, Gram reaction, and semi-quantitative abundance. Correlation with culture required. Gram stain guides empiric antibiotic therapy pending culture.",
      "Directs initial empiric antimicrobial therapy; essential for meningitis (CSF), pneumonia (sputum), UTI (urine), wound infections, and bacteraemia screening.",
      "Decolourisation may be inconsistent in thick smears; some organisms (e.g., Mycoplasma, Chlamydia) are not visualised; prior antibiotics may reduce organism yield.",
      ["Cheesbrough, M. (2005). District laboratory practice in tropical countries (2nd ed.). Cambridge University Press.",
       "Clinical and Laboratory Standards Institute. (2022). Performance standards for antimicrobial susceptibility testing (32nd ed., CLSI supplement M100). CLSI.",
       "Malawi Ministry of Health. (2021). National laboratory policy and standard operating procedures (2nd ed.). Government of Malawi."],
      ["cheesbrough", "clsi", "malawi_lab"])

_proc("Culture & Sensitivity", _d, "Clinical specimen (urine, blood, swab, sputum, pus, fluid)", "Sterile container; blood: blood culture bottles",
      "Urine: 10 mL; Blood: 8–10 mL per bottle (adult), 1–5 mL (paediatric)", "Blood cultures: room temp; Others: 2–8°C if delay >2 h",
      "Triple-packed; inoculate blood culture bottles at bedside; transport within 2 h (blood: 30 min)",
      "Collect before antibiotics; clean site with 70% alcohol then 2% chlorhexidine for blood culture; mid-stream clean-catch for urine",
      "Specimen inoculated on BA, MAC, CA (5% CO2 at 35±2°C for 18–24 h). Identification by colony morphology, Gram stain, biochemical tests (API, VITEK or manual). AST by Kirby-Bauer disc diffusion (MHA, 0.5 McFarland, 35°C, 16–18 h) per CLSI.",
      "Incubator (35–37°C, ±CO2), biosafety cabinet, autoclave, McFarland densitometer, disc dispenser, zone calliper or ruler",
      "Media QC: BA supports haemolysis, MAC selects Gram-negatives. Organism QC: S. aureus ATCC 25923, E. coli ATCC 25922, P. aeruginosa ATCC 27853. Disc potency checked with ATCC strains weekly.",
      "Preliminary: 18–24 h; Final: 48–72 h (blood: up to 5 days); AST: additional 24 h",
      "Report organism(s) identified and semi-quantitative growth (scanty/moderate/heavy). AST reported as Sensitive (S), Intermediate (I), or Resistant (R) per CLSI breakpoints. Interpret in context of specimen source and clinical presentation.",
      "Gold standard for confirming infection and guiding targeted antibiotic therapy. Essential for antimicrobial stewardship.",
      "Slow-growing or fastidious organisms may be missed; prior antibiotics reduce yield; contamination possible if aseptic technique not followed; culture-negative infections occur.",
      ["Cheesbrough, M. (2005). District laboratory practice in tropical countries (2nd ed.). Cambridge University Press.",
       "Clinical and Laboratory Standards Institute. (2022). Performance standards for antimicrobial susceptibility testing (32nd ed., CLSI supplement M100). CLSI.",
       "World Health Organization. (2023). WHO guidelines on use of medically important antimicrobials. WHO."],
      ["cheesbrough", "clsi", "who_ebm"])

_proc("AFB Smear (ZN Stain)", _d, "Sputum (spot, early morning), BAL, gastric lavage, tissue, CSF", "Sterile, wide-mouth, leak-proof container; 50 mL Falcon tube",
      "Sputum: 2–5 mL; minimum 1 mL", "Room temp: up to 3 d; Refrigerate: up to 7 d; Do NOT heat-inactivate",
      "Triple-packed; Category B UN3373; transport within 24 h; if >24 h, store at 2–8°C",
      "Early morning specimen preferred (3 specimens: spot-morning-spot); avoid saliva; instruct patient to cough deeply from chest; N95 mask for staff",
      "Concentrated (NaOH-NALC 3% decontamination, centrifuge 3000×g for 15 min) or direct smear. Smear heat-fixed, stained with carbol fuchsin (10 min, steam), decolourised with 3% HCl in 70% ethanol, counterstained with methylene blue (30 s). Examine under ×1000 (oil). Report as per IUATLD/WHO scale.",
      "Microscope (×1000 oil immersion), heating rack, centrifuge, biosafety cabinet, glass slides, staining rack",
      "Positive control: known AFB-positive smear; Negative control: known negative smear. Staining reagents changed after 100 smears or monthly. Blind recheck of 10% of slides for QA.",
      "Same day (concentrated method: 3–4 h; direct: 1–2 h)",
      "Negative: No AFB per 100 fields; Scanty: 1–9/100 fields (report exact count); 1+: 10–99/100 fields; 2+: 1–10/field in ≥50 fields; 3+: >10/field in ≥20 fields. Positive: Notify clinician; start TB treatment per NTP; request GeneXpert for RIF resistance testing.",
      "Primary screening tool for pulmonary TB in resource-limited settings. Cheap, rapid, moderately sensitive (50–70% culture-positive). High specificity in high-burden settings.",
      "Low sensitivity in HIV co-infection (paucibacillary), children, and extrapulmonary TB; cannot distinguish live from dead bacilli; NTM may give false-positive.",
      ["Cheesbrough, M. (2005). District laboratory practice in tropical countries (2nd ed.). Cambridge University Press.",
       "World Health Organization. (2022). WHO consolidated guidelines on tuberculosis. WHO.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["cheesbrough", "who_tb", "malawi_sop"])

_proc("GeneXpert MTB/RIF", _d, "Sputum, BAL, gastric lavage, CSF, lymph node aspirate, tissue", "Sterile container; GeneXpert cartridge",
      "Sputum: 1–2 mL; CSF: ≥1 mL", "Room temp: 24 h; 2–8°C: up to 72 h",
      "Triple-packed UN3373; transport at 2–8°C if delay >24 h",
      "Early morning specimen preferred; N95 for staff; no special patient preparation",
      "Sample treated with SR buffer (2:1 ratio), vortexed, incubated 15 min at room temp. 2 mL transferred to cartridge. Cartridge loaded into GeneXpert instrument. Automated DNA extraction, amplification (real-time PCR targeting rpoB gene), and detection (~112 min).",
      "GeneXpert IV/VI/XVI instrument, laptop/software, vortex mixer, pipettes (P100, P1000), cartridge rack",
      "Positive control: included in each cartridge (internal control). External QC: known MTB-positive and negative samples weekly. Instrument calibration annually.",
      "2 h (walk-away; hands-on ~10 min)",
      "MTB NOT DETECTED: No M. tuberculosis complex DNA detected. If high suspicion, repeat or perform culture.\nMTB DETECTED, RIF SENSITIVE: TB confirmed; start first-line therapy.\nMTB DETECTED, RIF RESISTANT: MDR-TB; refer for second-line therapy.\nMTB DETECTED, RIF INDETERMINATE: repeat Xpert or perform DST.",
      "WHO-recommended initial diagnostic test for TB and rifampicin resistance. High sensitivity (~90% smear-positive, ~70% smear-negative). Rapid detection of multidrug resistance.",
      "Cannot distinguish live from dead bacilli (may remain positive after treatment); does not provide full DST for other drugs; requires stable power supply; cartridge cost is a barrier.",
      ["World Health Organization. (2022). WHO consolidated guidelines on tuberculosis. WHO.",
       "Clinical and Laboratory Standards Institute. (2022). Performance standards for antimicrobial susceptibility testing (32nd ed., CLSI supplement M100). CLSI.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["who_tb", "clsi", "malawi_sop"])

_proc("RDT Malaria", _d, "Capillary blood (finger-prick) or venous blood", "EDTA microtainer or capillary tube",
      "5–10 µL (capillary); 1 mL (venous EDTA)", "Room temp: 1 h; EDTA: 4°C up to 24 h",
      "Room temp within 1 h of collection; do NOT freeze",
      "No special preparation; explain procedure to patient; warm hands if capillary flow poor",
      "Add 5 µL blood to sample well, add 3–4 drops of buffer to buffer well. Read at 15–20 min (not after 30 min). Bands appear: Control (C), Pan (P), Pf (P. falciparum-specific HRP2).",
      "RDT test kit (e.g., SD Bioline, Paracheck, CareStart), timer, lancet, capillary pipette, gloves",
      "Kit internal control: control line must appear. Lot-to-lot QC with known positive/negative specimens. Store kits at 2–30°C (do not freeze). Check expiry before use.",
      "15–20 min",
      "Negative: No bands (C only) — malaria unlikely; if high suspicion, do blood film.\nPf positive: P. falciparum — treat with ACT.\nPan positive: Non-P. falciparum — treat per species.\nPf + Pan positive: Mixed infection — treat with ACT.",
      "Rapid, simple, no equipment needed. Highly sensitive for P. falciparum (HRP2). Recommended by WHO for fever case management in endemic areas.",
      "HRP2 may persist 2–4 weeks after treatment (false-positive); low sensitivity for non-falciparum species; prozone effect in high parasitaemia; HRP2-negative parasites (pfhrp2 deletion) cause false-negatives.",
      ["World Health Organization. (2022). WHO guidelines for malaria. WHO.",
       "Cheesbrough, M. (2005). District laboratory practice in tropical countries (2nd ed.). Cambridge University Press.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["who_malaria", "cheesbrough", "malawi_sop"])

_proc("Cryptococcal Antigen (CrAg)", _d, "Serum (or plasma, CSF)", "Serum separator tube (SST) or plain tube; CSF: sterile container",
      "Serum: 3–5 mL; CSF: ≥1 mL", "Serum: 2–8°C for 72 h; CSF: 2–8°C for 48 h",
      "Triple-packed; transport at 2–8°C if delay >2 h",
      "No special preparation; aseptic venipuncture for serum; lumbar puncture by clinician for CSF",
      "Lateral flow assay (LFA): 1 drop of serum added to sample pad, insert strip into buffer well. Read at 10 min. Two lines (control + test) = positive. Qualitative or semi-quantitative (titre by serial dilution).",
      "CrAg LFA kit (IMMY, or equivalent), timer, pipette, serum/CSF specimen",
      "Kit internal control: control line must appear. Positive and negative controls run with each new lot. Store at 2–30°C.",
      "10–15 min",
      "Negative: No CrAg detected — cryptococcal meningitis unlikely.\nPositive: CrAg detected — patient at high risk for or has cryptococcal meningitis. Start fluconazole or amphotericin B per Malawi HIV guidelines. In HIV patients with CD4 <100, CrAg screening recommended at ART initiation.",
      "Essential screening test for HIV patients with low CD4. High sensitivity/specificity for Cryptococcus neoformans. Rapid, point-of-care, no equipment needed.",
      "Cannot differentiate active vs past infection; CSF CrAg more specific for meningitis; false-positive rare but may occur with rheumatoid factor.",
      ["World Health Organization. (2022). Consolidated guidelines on HIV prevention, testing, treatment, service delivery and monitoring. WHO.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi.",
       "Cheesbrough, M. (2005). District laboratory practice in tropical countries (2nd ed.). Cambridge University Press."],
      ["who_hiv", "malawi_sop", "cheesbrough"])

_proc("Blood Culture", _d, "Venous blood (two sets from separate sites recommended)", "Blood culture bottles (aerobic + anaerobic); paediatric bottles",
      "Adult: 8–10 mL per bottle; Child: 1–5 mL per bottle", "Room temp; do NOT refrigerate",
      "Transport to lab within 30 min; incubate immediately at 35–37°C",
      "Disinfect skin with 70% alcohol then 2% chlorhexidine; allow to dry; disinfect bottle septum with 70% alcohol; collect two sets from different peripheral sites before antibiotics",
      "Bottles placed in automated blood culture system (e.g., BACTEC, BacT/ALERT) or manually subbed at 24 h, 48 h, 72 h, 5 d. Positive bottles Gram stained, subcultured to BA, CA, MAC. Identification and AST per CLSI.",
      "Blood culture system (automated or manual), incubator, biosafety cabinet, Gram stain reagents, culture media",
      "Automated system: internal sensors flag growth. Manual: blind subculture day 1, 2, 3, 5. Bottle sterility checked with each lot. Skin antisepsis is critical QC step.",
      "Preliminary (positive): 12–48 h; Final negative: 5 days (routine); 7 days (endocarditis, Brucella suspected)",
      "Positive: organism identified + AST; interpret significance based on organism type (true pathogen vs contaminant). Negative at 5 days: no growth — report as 'No growth after 5 days'.",
      "Gold standard for diagnosing bloodstream infections and sepsis. Guides targeted antibiotic therapy in critically ill patients.",
      "Prior antibiotics sharply reduce yield; contaminants (CoNS, diphtheroids, Bacillus) common; single set insufficient (two sets increase yield 15–30%); intermittent bacteraemia may be missed.",
      ["Cheesbrough, M. (2005). District laboratory practice in tropical countries (2nd ed.). Cambridge University Press.",
       "Clinical and Laboratory Standards Institute. (2022). Performance standards for antimicrobial susceptibility testing (32nd ed., CLSI supplement M100). CLSI.",
       "World Health Organization. (2023). WHO guidelines on use of medically important antimicrobials. WHO."],
      ["cheesbrough", "clsi", "who_ebm"])


# --------------------- CLINICAL CHEMISTRY ---------------------
_d = "Clinical Chemistry"
_proc("Glucose (Fasting)", _d, "Plasma (fluoride oxalate tube preferred) or serum", "Fluoride oxalate (grey-top) or SST",
      "2–3 mL", "Room temp: 30 min (glycolysis); centrifuge within 30 min; plasma stable 2–8°C for 8 h",
      "Centrifuge within 30 min; transport on ice if delay >30 min",
      "Strict 8–12 h fast (water only); no smoking, tea, coffee; patient should be seated and rested for 5 min before collection; morning specimen preferred",
      "Enzymatic (hexokinase/GOD-POD) method. Plasma incubated with glucose oxidase/peroxidase + chromogen (4-aminophenazone + phenol). Absorbance read at 505 nm, proportional to glucose concentration. Automated analyser (e.g., Cobas c311, AU480).",
      "Chemistry analyser, cuvettes, pipettes, glucose reagent (GOD-POD or hexokinase), calibrator, controls",
      "Two-level QC (normal + abnormal) run daily before patient samples. Calibration every 7 days or after reagent lot change. Internal controls within 2SD. External QA (NEQAS) monthly.",
      "1 h (automated); STAT: 30 min",
      "Fasting glucose ≥7.0 mmol/L on two occasions = diabetes. 6.1–6.9 mmol/L = impaired fasting glucose (pre-diabetes). 3.9–6.1 mmol/L = normal. <2.2 mmol/L = critical hypoglycaemia. <3.3 mmol/L = hypoglycaemia (McMahon et al., 2022).",
      "Essential for diagnosing and monitoring diabetes mellitus, hypoglycaemia, and metabolic disorders. Most widely ordered chemistry test.",
      "Glycolysis in non-fluoride tubes decreases glucose by 5–7% per hour; haemolysis may cause false-low; stress, illness, medications may elevate glucose (non-fasting).",
      ["Jameson, J. L., Kasper, D. L., Longo, D. L., Fauci, A. S., Hauser, S. L., & Loscalzo, J. (2022). Harrison's principles of internal medicine (21st ed.). McGraw Hill.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi.",
       "McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier."],
      ["harrison", "malawi_sop", "henry"])

_proc("HbA1c", _d, "Whole blood (EDTA)", "EDTA (lavender-top) tube",
      "2–3 mL", "Room temp: 8 h; 2–8°C: 7 days; stable 1 month at –20°C",
      "Room temp; stable 8 h without processing",
      "No fasting required; can be done at any time; note: Hb variants, anaemia, transfusions affect results",
      "Turbidimetric inhibition immunoassay (TINIA) or HPLC. HbA1c separated from total Hb by specific antibody binding or charge-based separation. Measured photometrically at 340/700 nm. Result expressed as % of total Hb or mmol/mol (IFCC).",
      "Chemistry analyser with HbA1c module or dedicated HbA1c analyser (e.g., D-10, Cobas c513), reagents, calibrator, controls",
      "Two-level QC daily. NGSP certification required annually. Calibration with IFCC/NGSP traceable standards. Inter-laboratory comparison quarterly. Ensure Hb variant interference is noted.",
      "1–2 h",
      "<5.7% (<39 mmol/mol): Normal; 5.7–6.4% (39–47 mmol/mol): Pre-diabetes; ≥6.5% (≥48 mmol/mol): Diabetes. Reflects average glycaemia over 8–12 weeks. Every 1% reduction = 37% decrease in microvascular complications.",
      "Gold standard for monitoring glycaemic control in diabetes. Predicts microvascular complications (retinopathy, nephropathy, neuropathy). No fasting required.",
      "Falsely low: haemolytic anaemia, recent transfusion, CKD (anaemia), HbS/C trait (some methods). Falsely high: iron deficiency, renal failure (carbamylated Hb). Not reliable in pregnancy (use fructosamine).",
      ["Jameson, J. L., Kasper, D. L., Longo, D. L., Fauci, A. S., Hauser, S. L., & Loscalzo, J. (2022). Harrison's principles of internal medicine (21st ed.). McGraw Hill.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi.",
       "McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier."],
      ["harrison", "malawi_sop", "henry"])

_proc("ALT (SGPT)", _d, "Serum (SST or plain tube)", "SST (gold-top) or plain (red-top) tube",
      "3–5 mL", "Room temp: 8 h; 2–8°C: 48 h; separate serum within 1 h",
      "Centrifuge within 1 h; transport on cold pack if delay >4 h",
      "Overnight fast preferred (but not essential); note strenuous exercise elevates ALT; stop hepatotoxic medications if clinically safe",
      "Enzymatic UV method (IFCC). ALT catalyses: alanine + α-ketoglutarate → pyruvate + glutamate. Pyruvate + NADH + H+ → lactate + NAD+, measured at 340 nm (decrease in absorbance proportional to ALT activity).",
      "Chemistry analyser, ALT reagent, calibrator, controls (normal + abnormal), cuvettes",
      "Two-level QC daily. Calibration every 7 days or lot change. Internal QC within 2SD. External QA programme participation. Reagent blank and linearity verification monthly.",
      "1 h (automated); STAT: 30 min",
      "Normal: 10–40 U/L (adults). Mild elevation: 40–100 U/L (steatosis, medication, viral hepatitis). Moderate: 100–300 U/L (acute hepatitis). Severe: >300 U/L (massive hepatocyte necrosis). ALT >1000 U/L: ischaemic/toxic injury. ALT > AST = hepatocellular pattern.",
      "Primary screening test for hepatocellular injury. More specific for liver than AST. Used to monitor hepatitis, drug-induced liver injury, fatty liver disease.",
      "Not specific to aetiology (elevated in many conditions); haemolysis interferes; normal ALT does not exclude cirrhosis; muscle injury may elevate ALT mildly.",
      ["Jameson, J. L., Kasper, D. L., Longo, D. L., Fauci, A. S., Hauser, S. L., & Loscalzo, J. (2022). Harrison's principles of internal medicine (21st ed.). McGraw Hill.",
       "McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["harrison", "henry", "malawi_sop"])

_proc("Creatinine", _d, "Serum (SST or plain tube) or plasma (heparin)", "SST (gold-top) or lithium heparin (green-top)",
      "3–5 mL", "Room temp: 8 h; 2–8°C: 48 h",
      "Centrifuge within 2 h; stable at room temp up to 8 h",
      "Overnight fast preferred; avoid strenuous exercise (elevates creatinine); note: high meat intake may elevate",
      "Jaffé kinetic method (alkaline picrate) or enzymatic. Creatinine + picrate in alkaline medium forms orange-red chromogen measured at 505 nm. Enzymatic method more specific (creatininase → creatine → sarcosine → H2O2 + chromogen).",
      "Chemistry analyser, creatinine reagent (Jaffé or enzymatic), calibrator traceable to IDMS, controls",
      "Two-level QC daily. Calibration with IDMS-traceable standard. Bilirubin, lipaemia, haemolysis interference checks. eGFR automatically calculated using CKD-EPI or MDRD equation (report with result).",
      "1 h (automated); STAT: 30 min",
      "Male: 62–106 µmol/L; Female: 44–80 µmol/L; Child: 27–62 µmol/L. Elevated: pre-renal, renal, or post-renal AKI. eGFR <60 mL/min/1.73m² for ≥3 months = CKD. Rapid rise >26.5 µmol/L in 48 h = AKI. Critically high: >450 µmol/L.",
      "Measures renal function; used to diagnose and stage AKI and CKD, guide drug dosing, monitor dialysis, calculate eGFR.",
      "Affected by muscle mass, age, gender, diet; Jaffé method affected by bilirubin, ketones, cephalosporins (pseudo-elevation); enzymatic method preferred but costlier.",
      ["Jameson, J. L., Kasper, D. L., Longo, D. L., Fauci, A. S., Hauser, S. L., & Loscalzo, J. (2022). Harrison's principles of internal medicine (21st ed.). McGraw Hill.",
       "McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["harrison", "henry", "malawi_sop"])

_proc("Urea", _d, "Serum (SST or plain tube) or plasma (heparin)", "SST (gold-top) or lithium heparin (green-top)",
      "3–5 mL", "Room temp: 8 h; 2–8°C: 72 h",
      "Centrifuge within 2 h; stable at room temp up to 8 h",
      "Overnight fast preferred; avoid high-protein meal before test; note hydration status",
      "Urease/GLDH enzymatic method. Urea hydrolysed by urease to NH₃ + CO₂. NH₃ combines with α-ketoglutarate (catalysed by GLDH) with simultaneous NADH → NAD⁺ oxidation measured at 340 nm. Rate of absorbance decrease proportional to urea concentration.",
      "Chemistry analyser, urea reagent (urease/GLDH), calibrator, controls (normal + abnormal)",
      "Two-level QC daily. Calibration every 7 days or lot change. Internal QC within 2SD. External QA programme participation monthly.",
      "1 h (automated); STAT: 30 min",
      "Normal: 2.5–7.1 mmol/L. Child: 1.8–6.4 mmol/L. Elevated (>7.1): pre-renal (dehydration, CHF, shock), renal (AKI, CKD), or post-renal (obstruction). BUN:Creatinine ratio >20:1 suggests pre-renal cause. Critically high: >35 mmol/L.",
      "Measures renal function and nitrogen balance. Used with creatinine to differentiate pre-renal vs renal AKI. Elevated in high-protein states, GI bleeding, catabolism.",
      "Affected by diet (high protein), hydration, GI bleeding, steroids; not as specific as creatinine for renal function; rises with age.",
      ["Jameson, J. L., Kasper, D. L., Longo, D. L., Fauci, A. S., Hauser, S. L., & Loscalzo, J. (2022). Harrison's principles of internal medicine (21st ed.). McGraw Hill.",
       "McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["harrison", "henry", "malawi_sop"])

_proc("Sodium (Na+)", _d, "Serum (SST) or plasma (lithium heparin)", "SST (gold-top) or lithium heparin (green-top)",
      "3–5 mL", "Room temp: 4 h; 2–8°C: 72 h; separate serum within 1 h",
      "Centrifuge within 1 h; do NOT use gel barrier tubes for long storage (leaching)",
      "No special preparation; note posture (standing increases Na slightly); avoid tourniquet application >1 min (haemoconcentration)",
      "Ion-selective electrode (ISE) direct potentiometry. Sample diluted with buffer and passed over Na⁺-selective membrane. Potential difference measured against reference electrode, logarithmically proportional to Na⁺ activity. Automated on chemistry analysers (e.g., Cobas, AU480).",
      "Chemistry analyser with ISE module, Na⁺ reagent/ISE buffer, calibrator, controls, electrodes (replaced per manufacturer schedule)",
      "Two-level QC daily. Electrode slope checked weekly. ISE membrane replaced per schedule. External QA monthly. Check for lipaemia/icterus interference.",
      "1 h (automated); STAT: 15 min (ISE direct)",
      "Normal: 136–145 mmol/L. Hyponatraemia (<136): hypervolaemic (CHF, cirrhosis), euvolemic (SIADH, psychogenic polydipsia), hypovolaemic (diuretics, diarrhoea). Hypernatraemia (>145): water deficit (DI, insensible loss), Na overload. Critical: <120 or >160 mmol/L.",
      "Critical electrolyte for maintaining osmotic pressure, nerve conduction, and fluid balance. Most common electrolyte disorder in hospitalised patients.",
      "Pseudohyponatraemia: hyperlipidaemia, hyperproteinaemia (use ISE direct to avoid). Hyperglycaemia: Na drops 1.6 mmol/L per 5.5 mmol/L glucose rise. Haemolysis: minimal effect. Icteric/lipaemic samples may interfere with indirect ISE.",
      ["Jameson, J. L., Kasper, D. L., Longo, D. L., Fauci, A. S., Hauser, S. L., & Loscalzo, J. (2022). Harrison's principles of internal medicine (21st ed.). McGraw Hill.",
       "McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["harrison", "henry", "malawi_sop"])

_proc("Potassium (K+)", _d, "Serum (SST) or plasma (lithium heparin)", "SST (gold-top) or lithium heparin (green-top)",
      "3–5 mL", "Room temp: 2 h (serum); 2–8°C: 72 h (plasma); separate within 1 h",
      "Centrifuge within 1 h; do NOT refrigerate whole blood (K+ leaks from cells); transport at room temp",
      "No special preparation; avoid fist clenching (K+ release from muscle); avoid haemolysis; note: delayed separation falsely elevates K+",
      "Ion-selective electrode (ISE) direct potentiometry. Sample diluted with buffer, passed over K⁺-selective membrane (valinomycin-based). Potential difference measured against reference, logarithmically proportional to K⁺ activity. Automated on chemistry analysers.",
      "Chemistry analyser with ISE module, K⁺ reagent/ISE buffer, calibrator, controls, ISE electrodes",
      "Two-level QC daily. Electrode slope checked weekly. External QA monthly. Critical: haemolysis index monitoring (Hb >50 mg/dL = reject for K+). Check for pseudohyperkalaemia (thrombocytosis, WBC >50×10⁹/L — use plasma instead of serum).",
      "1 h (automated); STAT: 15 min",
      "Normal: 3.5–5.1 mmol/L. Hypokalaemia (<3.5): diuretics, diarrhoea, vomiting, hyperaldosteronism, alkalosis. Hyperkalaemia (>5.1): renal failure, K⁺-sparing diuretics, ACEi, acidosis, haemolysis. Critical: <2.5 (arrhythmia risk) or >6.5 (immediate ECG + treatment per Malawi protocol).",
      "Essential for cardiac conduction, muscle contraction, acid-base balance. Most dangerous electrolyte abnormality (cardiac arrest risk at extremes).",
      "Pseudohyperkalaemia: haemolysis, thrombocytosis, delayed separation, fist clenching. Refrigerated whole blood: K+ rises 0.5–1.0 mmol/L per 24 h. IV contamination (draw from opposite arm).",
      ["Jameson, J. L., Kasper, D. L., Longo, D. L., Fauci, A. S., Hauser, S. L., & Loscalzo, J. (2022). Harrison's principles of internal medicine (21st ed.). McGraw Hill.",
       "McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["harrison", "henry", "malawi_sop"])

_proc("Calcium (Total)", _d, "Serum (SST or plain tube)", "SST (gold-top) or plain (red-top) tube",
      "3–5 mL", "Room temp: 4 h; 2–8°C: 48 h",
      "Centrifuge within 2 h; avoid prolonged stasis during venipuncture",
      "Fasting preferred (10–12 h); avoid alcohol; patient seated and rested 5 min before draw",
      "Arsenazo III or o-cresolphthalein complexone (OCPC) colorimetric method. Calcium binds with arsenazo III at pH 6.5 to form a blue-purple complex measured at 650 nm. OCPC method: Ca²⁺ + OCPC in alkaline medium → purple chromogen read at 570 nm.",
      "Chemistry analyser, calcium reagent (arsenazo III or OCPC), calibrator, controls (normal + abnormal)",
      "Two-level QC daily. Calibration every 7 days or lot change. Corrected Ca²⁺ calculated when albumin abnormal: Corrected Ca = Measured Ca + [0.02 × (40 − Albumin in g/L)]. Ionised Ca preferred for critical patients.",
      "1 h (automated); STAT: 30 min",
      "Normal: 2.15–2.55 mmol/L (adults); 2.1–2.55 mmol/L (children). Hypercalcaemia (>2.55): hyperparathyroidism, malignancy, sarcoidosis, vitamin D excess, immobility. Hypocalcaemia (<2.15): CKD, vitamin D deficiency, hypoparathyroidism, pancreatitis. Critical: <1.75 or >3.5 mmol/L.",
      "Essential for bone metabolism, nerve conduction, muscle contraction, blood coagulation. Screen for parathyroid disorders, bone disease, malignancy, and CKD.",
      "Total Ca affected by albumin (corrected Ca needed). Haemolysis falsely elevates (RBC Ca release). Stasis/tourniquet falsely elevates (haemoconcentration). Fasting required (postprandial Ca rises 0.1–0.2 mmol/L).",
      ["Jameson, J. L., Kasper, D. L., Longo, D. L., Fauci, A. S., Hauser, S. L., & Loscalzo, J. (2022). Harrison's principles of internal medicine (21st ed.). McGraw Hill.",
       "McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["harrison", "henry", "malawi_sop"])

_proc("Bilirubin (Total)", _d, "Serum (SST or plain tube), protect from light", "SST (gold-top) or plain (red-top) tube wrapped in foil",
      "3–5 mL", "Room temp: 2 h (photodegradation); 2–8°C: 24 h protected from light",
      "Protect from light (wrap in aluminium foil); centrifuge within 1 h; transport on cold pack",
      "Fasting preferred (lipaemia interferes); avoid prolonged tourniquet",
      "Diazo (Jendrassik-Gróf) colorimetric method. Bilirubin reacts with diazotised sulphanilic acid to form azobilirubin (pink chromogen). Total bilirubin: with accelerator (DMSO/ caffeine). Direct bilirubin: without accelerator (aqueous phase). Measured at 540 nm (main) and 630 nm (blank).",
      "Chemistry analyser, total/direct bilirubin reagent, calibrator, controls, foil-wrapped tubes",
      "Two-level QC daily. Calibration every 7 days. Protect reagents from light. Linearity verified monthly. Bilirubin standards light-sensitive — use fresh. External QA monthly.",
      "1 h (automated); STAT: 30 min",
      "Total: 0–21 µmol/L; Direct: 0–5.1 µmol/L; Indirect: 0–17 µmol/L. Pre-hepatic (indirect ↑): haemolysis, ineffective erythropoiesis. Hepatic (both ↑): hepatitis, cirrhosis, drug-induced. Post-hepatic (direct ↑): obstruction (gallstones, stricture, tumour). Critical: >340 µmol/L (kernicterus risk in neonates).",
      "Evaluates jaundice, differentiates causes of hyperbilirubinaemia, monitors liver function and haemolytic disease. Essential neonatal screening to prevent kernicterus.",
      "Photodegradation (light destroys bilirubin) — protect from light at all times. Lipaemia interferes (blank correction needed). Haemolysis falsely decreases (Hb oxidises bilirubin). Direct bilirubin may overestimate in renal failure.",
      ["Jameson, J. L., Kasper, D. L., Longo, D. L., Fauci, A. S., Hauser, S. L., & Loscalzo, J. (2022). Harrison's principles of internal medicine (21st ed.). McGraw Hill.",
       "McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["harrison", "henry", "malawi_sop"])

_proc("AST (SGOT)", _d, "Serum (SST or plain tube)", "SST (gold-top) or plain (red-top) tube",
      "3–5 mL", "Room temp: 8 h; 2–8°C: 48 h; separate within 1 h",
      "Centrifuge within 1 h; stable at room temp up to 8 h",
      "Overnight fast preferred; avoid strenuous exercise (elevates AST from muscle); note: haemolysis falsely elevates",
      "Enzymatic UV method (IFCC). AST catalyses: aspartate + α-ketoglutarate → oxaloacetate + glutamate. Oxaloacetate + NADH + H+ → malate + NAD⁺ (catalysed by MDH). Rate of NADH oxidation measured at 340 nm (decrease in absorbance).",
      "Chemistry analyser, AST reagent, calibrator, controls, cuvettes",
      "Two-level QC daily. Calibration every 7 days or lot change. Internal QC within 2SD. Haemolysis index monitoring (AST from RBCs falsely elevates). External QA monthly.",
      "1 h (automated); STAT: 30 min",
      "Normal: 10–40 U/L (adults). Mild: 40–100 U/L. Moderate: 100–300 U/L. Severe: >300 U/L. AST > ALT = alcoholic hepatitis, cirrhosis, metastatic liver disease. ALT > AST = viral hepatitis, NAFLD. Markedly elevated >1000 U/L: ischaemic/toxic injury. Also elevated in muscle injury, MI, haemolysis.",
      "Screens for hepatocellular injury, used with ALT to calculate AST:ALT ratio (De Ritis ratio). Less liver-specific than ALT (also in heart, muscle, kidney, brain).",
      "Not specific to liver; haemolysis significantly elevates; exercise elevates transiently; normal AST does not exclude cirrhosis; macro-AST (rare) causes isolated AST elevation.",
      ["Jameson, J. L., Kasper, D. L., Longo, D. L., Fauci, A. S., Hauser, S. L., & Loscalzo, J. (2022). Harrison's principles of internal medicine (21st ed.). McGraw Hill.",
       "McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["harrison", "henry", "malawi_sop"])

_proc("ALP", _d, "Serum (SST or plain tube)", "SST (gold-top) or plain (red-top) tube",
      "3–5 mL", "Room temp: 8 h; 2–8°C: 7 days; stable frozen 1 month",
      "Centrifuge within 2 h; stable at room temp",
      "Fasting preferred (postprandial ALP rises from intestinal isoenzyme); note: pregnancy increases (placental isoenzyme), children have higher ALP (bone growth)",
      "Enzymatic (pNPP) colorimetric method. ALP hydrolyses p-nitrophenyl phosphate (pNPP) to p-nitrophenol + phosphate. p-Nitrophenol in alkaline medium (2-amino-2-methyl-1-propanol buffer pH 10.4) forms yellow chromogen measured at 405 nm. Rate of absorbance increase proportional to ALP activity.",
      "Chemistry analyser, ALP reagent (pNPP + AMP buffer), calibrator, controls (normal + abnormal), cuvettes",
      "Two-level QC daily. Calibration every 7 days or lot change. Enzyme controls within 2SD. Verify linearity monthly. External QA monthly.",
      "1 h (automated); STAT: 30 min",
      "Adults: 44–147 U/L; Children: 100–350 U/L (higher during growth spurts). Elevated: liver (cholestasis, hepatitis, mass), bone (Paget's, metastases, fracture healing, hyperparathyroidism), placental (pregnancy). Mild: 1–3× ULN; Moderate: 3–10×; Marked: >10× (suggests cholestasis). Low: hypophosphatasaemia (rare).",
      "Marker for hepatobiliary disease (cholestasis) and bone turnover. GGT differentiates liver vs bone origin. Useful in monitoring metabolic bone disease.",
      "Elevated in children (bone growth), pregnancy (placental), post-fracture. Falsely low: Zn/Mg deficiency. Many drugs (anticonvulsants, rifampicin) induce ALP. Not specific to liver (confirm with GGT).",
      ["Jameson, J. L., Kasper, D. L., Longo, D. L., Fauci, A. S., Hauser, S. L., & Loscalzo, J. (2022). Harrison's principles of internal medicine (21st ed.). McGraw Hill.",
       "McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["harrison", "henry", "malawi_sop"])

_proc("GGT", _d, "Serum (SST or plain tube)", "SST (gold-top) or plain (red-top) tube",
      "3–5 mL", "Room temp: 8 h; 2–8°C: 7 days; stable frozen 1 month",
      "Centrifuge within 2 h; stable at room temp",
      "Fasting preferred; avoid alcohol 24 h before test (alcohol induces GGT); note: many drugs induce GGT (anticonvulsants, warfarin, NSAIDs)",
      "Enzymatic colorimetric method (Szasz/IFCC). GGT transfers glutamyl group from L-γ-glutamyl-3-carboxy-4-nitroanilide to glycylglycine acceptor. Released 5-amino-2-nitrobenzoate measured at 405 nm. Rate of absorbance increase proportional to GGT activity.",
      "Chemistry analyser, GGT reagent, calibrator, controls (normal + abnormal), cuvettes",
      "Two-level QC daily. Calibration every 7 days. Enzyme controls within 2SD. External QA monthly. Haemolysis acceptable (RBCs low GGT).",
      "1 h (automated); STAT: 30 min",
      "Male: 8–61 U/L; Female: 5–36 U/L; Child: 5–35 U/L. Elevated: hepatobiliary disease (cholestasis, hepatitis, mass), alcohol use (especially ALT:GGT ratio <1), enzyme-inducing drugs. Most sensitive marker for hepatobiliary obstruction. ALP + GGT both elevated = liver origin.",
      "Confirms hepatobiliary origin of elevated ALP (ALP + GGT both elevated = liver source). Sensitive marker for alcohol-induced liver disease. Monitors cholestasis and drug-induced liver injury.",
      "Induced by alcohol, anticonvulsants, rifampicin, warfarin (not specific to acute injury). Not elevated in bone disease (unlike ALP). Normal GGT does not exclude cirrhosis.",
      ["Jameson, J. L., Kasper, D. L., Longo, D. L., Fauci, A. S., Hauser, S. L., & Loscalzo, J. (2022). Harrison's principles of internal medicine (21st ed.). McGraw Hill.",
       "McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["harrison", "henry", "malawi_sop"])

_proc("Cholesterol (Total)", _d, "Serum (SST or plain tube) or plasma (EDTA/heparin)", "SST (gold-top) or EDTA (lavender-top)",
      "3–5 mL", "Room temp: 4 h; 2–8°C: 7 days; separate within 2 h",
      "Centrifuge within 2 h; protect from light; stable at 2–8°C up to 7 days",
      "Strict 12 h fast (water only); no alcohol 24 h; seated 5 min before draw; avoid tourniquet >1 min",
      "Enzymatic colorimetric (CHOD-PAP) method. Cholesterol esterase (CHE) hydrolyses cholesterol esters → free cholesterol. Cholesterol oxidase (CHOD) oxidises cholesterol → cholest-4-en-3-one + H₂O₂. H₂O₂ + 4-aminophenazone + phenol → quinoneimine (red chromogen) measured at 505 nm.",
      "Chemistry analyser, cholesterol reagent (CHOD-PAP), calibrator (traceable to Abell-Kendall reference method), controls (normal + abnormal)",
      "Two-level QC daily (targets within 3% CV). Calibrator traceable to CDC reference method. External QA (NEQAS, CDC Lipid Standardisation) quarterly. Verify linearity monthly. Fasting status recorded for risk assessment.",
      "1 h (automated); STAT: 30 min",
      "Desirable: <5.2 mmol/L; Borderline: 5.2–6.2 mmol/L; High: ≥6.2 mmol/L. Elevated: familial hypercholesterolaemia, diet, hypothyroidism, nephrotic syndrome, cholestasis, diabetes. Low (<3.6): malnutrition, hyperthyroidism, liver disease, malabsorption. Part of total CVD risk assessment (not standalone).",
      "Major modifiable risk factor for atherosclerotic cardiovascular disease. Used in CVD risk calculators (WHO/ISH, Framingham). National cholesterol screening per Malawi CVD guidelines.",
      "Fasting status critical (postprandial TC drops 5–10%); acute illness/MI lowers TC (measure after 8 weeks); pregnancy elevates TC. Cannot interpret without HDL, LDL, and TG for full lipid profile. Non-fasting non-HDL useful alternative.",
      ["Jameson, J. L., Kasper, D. L., Longo, D. L., Fauci, A. S., Hauser, S. L., & Loscalzo, J. (2022). Harrison's principles of internal medicine (21st ed.). McGraw Hill.",
       "McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["harrison", "henry", "malawi_sop"])

_proc("CRP (Quantitative)", _d, "Serum (SST or plain tube) or plasma (heparin)", "SST (gold-top) or lithium heparin (green-top)",
      "3–5 mL", "Room temp: 8 h; 2–8°C: 72 h; –20°C: 1 month",
      "Centrifuge within 2 h; stable at room temp up to 8 h",
      "No special preparation; note: CRP is acute-phase reactant — interpret in context of clinical presentation and timing from symptom onset",
      "Immunoturbidimetric or immunonephelometric method. Sample mixed with latex particles coated with anti-CRP antibodies. CRP antigen-antibody binding forms aggregates. Turbidity measured at 540/700 nm (turbidimetric) or light scatter at 90° (nephelometric). Concentration proportional to aggregate formation.",
      "Chemistry analyser or nephelometer, CRP reagent (latex-enhanced), calibrator (WHO International Standard IFCC/CRM 470), controls (normal + elevated)",
      "Two-level QC (normal + elevated) daily. Calibration curve every 7 days or per lot. High-sensitivity CRP (hs-CRP) for cardiovascular risk requires separate standardisation. External QA monthly. Prozone check for very high values (dilute if result > upper limit).",
      "1 h (automated); STAT: 30 min",
      "Normal: <5 mg/L (usually <3 mg/L in healthy). Mild elevation 5–40 mg/L: mild inflammation (viral, autoimmune, smoking). Moderate 40–100 mg/L: significant inflammation (bacterial infection, active autoimmune). Marked >100 mg/L: severe bacterial infection, sepsis, major trauma. Critical: >100 mg/L suggests serious bacterial infection. hs-CRP: <1 mg/L low CVD risk, 1–3 mg/L moderate, >3 mg/L high.",
      "Acute-phase reactant used to diagnose and monitor infection, inflammation, and tissue injury. Differentiates bacterial from viral infection (CRP typically higher in bacterial). Monitors treatment response.",
      "Not specific — elevated in any inflammatory state. Delayed rise (24–48 h post-stimulus). Not useful for viral vs bacterial absolute cut-off (overlap). Immunosuppressed patients may have blunted response.",
      ["Jameson, J. L., Kasper, D. L., Longo, D. L., Fauci, A. S., Hauser, S. L., & Loscalzo, J. (2022). Harrison's principles of internal medicine (21st ed.). McGraw Hill.",
       "McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["harrison", "henry", "malawi_sop"])

_proc("ESR (Westergren)", _d, "Whole blood (tri-sodium citrate 3.2% or EDTA)", "EDTA (lavender-top) or citrate (black-top) tube",
      "EDTA: 2–3 mL; Citrate: 1.6 mL (exact 4:1 ratio blood:citrate)", "Room temp: 4 h; 2–8°C: 12 h (mix well before testing)",
      "Room temp; upright; test within 4 h of collection; do NOT refrigerate for prolonged storage",
      "No special preparation; note: posture, pregnancy, age, gender, and drugs (NSAIDs, steroids, statins) affect ESR",
      "Westergren method. Whole blood (4:1 ratio with trisodium citrate) drawn into Westergren pipette (200 mm, 2.5 mm bore) mounted vertically on Westergren stand. ESR read at exactly 60 min (mm fall of RBCs). Automated ESR analysers (e.g., Ves-Matic, Streck ESR-Auto) use closed-tube technology with optical sensors.",
      "Westergren pipettes, Westergren stand/vacuum device, timer, citrate tubes, EDTA tubes, automated ESR analyser (if available)",
      "QC: known control weekly. Wintrobe or ICSH reference method comparison quarterly. Temperature correction: 1 mm/h per °C above 20°C. Ensure tube vertical (tilt >2° increases ESR 30%). Avoid bubbles in pipette.",
      "60 min (manual); 30 min (automated)",
      "Male: 0–15 mm/h; Female: 0–20 mm/h; Child: 0–10 mm/h. Elevated: infection, inflammation (temporal arteritis, PMR), autoimmune (SLE, RA), malignancy (myeloma, lymphoma), anaemia, pregnancy, CKD. Marked elevation >100 mm/h: myeloma, TB, autoimmune, occult malignancy. Low: polycythaemia, spherocytosis, hypofibrinogenaemia.",
      "Non-specific screening test for inflammation. Used to monitor temporal arteritis/PMR, assess TB treatment response, detect occult disease (very high ESR). Still widely used in resource-limited settings.",
      "Non-specific — many conditions elevate ESR. Affected by age (0.5 mm/h per year >50), gender, anaemia, pregnancy. CRP has faster rise/fall kinetics. Falsely low in high WBC, high viscosity, spherocytosis. Falsely high in obesity, female, age.",
      ["McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
       "Cheesbrough, M. (2005). District laboratory practice in tropical countries (2nd ed.). Cambridge University Press.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["henry", "cheesbrough", "malawi_sop"])

_proc("Ferritin", _d, "Serum (SST or plain tube)", "SST (gold-top) or plain (red-top) tube",
      "3–5 mL", "Room temp: 8 h; 2–8°C: 7 days; –20°C: 3 months",
      "Centrifuge within 2 h; stable at 2–8°C up to 7 days",
      "Fasting preferred (optional); note: ferritin is acute-phase reactant — elevated in inflammation irrespective of iron stores",
      "Immunoturbidimetric or immunochemiluminescent (CLIA) method. Anti-ferritin antibody-coated latex particles agglutinate with ferritin in sample. Turbidity measured at 570/800 nm (immunoturbidimetric) or chemiluminescence (CLIA). Calibrated against WHO International Standard (IS 94/578).",
      "Chemistry analyser or immunoassay analyser, ferritin reagent/kit, calibrator, controls (low, normal, high), cuvettes",
      "Three-level QC (low, normal, high) daily. Calibration every 14 days or lot change. External QA monthly. CRP measured concurrently to interpret ferritin in inflammatory states (ferritin is acute-phase reactant). Prozone check for high values.",
      "1–2 h (automated)",
      "Male: 20–250 µg/L; Female: 15–150 µg/L; Child: 15–100 µg/L. Low (<15): iron deficiency anaemia (most sensitive and specific marker). High: iron overload (haemochromatosis, transfusion), infection/inflammation (acute-phase), chronic disease, liver disease, malignancy. Very high >1000 µg/L: haemochromatosis, Still's disease, macrophage activation syndrome.",
      "Gold standard for assessing body iron stores. Differentiates iron deficiency anaemia from anaemia of chronic disease. Screening for iron overload. Acute-phase reactant — interpret with CRP.",
      "Acute-phase reactant (elevated in inflammation regardless of iron stores) — measure with CRP for accurate interpretation. Elevated in liver disease (damaged hepatocytes release ferritin). Falsely normal in iron deficiency with concurrent inflammation.",
      ["McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
       "Jameson, J. L., Kasper, D. L., Longo, D. L., Fauci, A. S., Hauser, S. L., & Loscalzo, J. (2022). Harrison's principles of internal medicine (21st ed.). McGraw Hill.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["henry", "harrison", "malawi_sop"])


# --------------------- HAEMATOLOGY ---------------------
_d = "Haematology"
_proc("Haemoglobin (Hb)", _d, "Whole blood (EDTA)", "EDTA (lavender-top) tube",
      "2–3 mL", "Room temp: 6 h; 2–8°C: 24 h",
      "Room temp; gently invert tube 8–10 times immediately after collection; do not refrigerate whole blood >24 h",
      "No special preparation; note posture (standing increases Hb slightly), time of day, altitude",
      "Cyanmethhaemoglobin (HiCN) method or automated haematology analyser (impedance + spectrophotometry). Blood diluted in Drabkin's reagent (KCN + K3Fe(CN)6), haemoglobin converted to cyanmethhaemoglobin, absorbance read at 540 nm. Automated analysers use SLS-Hb method (lauryl sulphate).",
      "Haematology analyser (e.g., Sysmex XN-series, Mindray BC-series) or spectrophotometer, Drabkin's reagent, pipettes, controls",
      "Two-level QC (normal + abnormal) run daily. Calibration with commercial calibrator. Internal QC within 2SD. External QA programme monthly. Analyser calibration verified every 6 months.",
      "1 min (automated); 15 min (manual HiCN method)",
      "Male: 13.5–17.5 g/dL; Female: 11.5–15.5 g/dL; Child: 10.5–14.0 g/dL. Critical: <6.0 g/dL. Anaemia graded: Mild (Hb 10–12), Moderate (Hb 8–10), Severe (Hb <8). High Hb: polycythaemia, dehydration, COPD, high altitude.",
      "First-line screening test for anaemia, polycythaemia, and blood loss. Essential for pre-operative assessment and ANC monitoring.",
      "Haemolysis, lipaemia, high WBC (>50×10⁹/L) interfere; posture, pregnancy (haemodilution), and smoking affect Hb; capillary Hb less reliable than venous.",
      ["McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi.",
       "Cheesbrough, M. (2005). District laboratory practice in tropical countries (2nd ed.). Cambridge University Press."],
      ["henry", "malawi_sop", "cheesbrough"])

_proc("WBC Count", _d, "Whole blood (EDTA)", "EDTA (lavender-top) tube",
      "2–3 mL", "Room temp: 6 h; 2–8°C: 24 h",
      "Room temp; gently invert tube; store upright",
      "No special preparation; note that exercise, stress, pregnancy, and smoking elevate WBC",
      "Impedance (Coulter principle) or flow cytometry. Blood passed through aperture; cells disrupt electrical current; pulse size proportional to cell size. Five-part differential (neutrophils, lymphocytes, monocytes, eosinophils, basophils) by laser scatter + fluorescence or VCS technology.",
      "Automated haematology analyser, EDTA blood, controls, reagents (diluent, lysate, rinse)",
      "Two-level QC daily. Calibration verified every 6 months. Differential reviewed on blood smear if abnormal flags. 200-cell manual differential if blasts, immature granulocytes, or atypical lymphocytes flagged.",
      "1 min (automated)",
      "Total: 4.0–10.0 ×10⁹/L. Leucocytosis (>10.0): infection, inflammation, leukaemia, stress, steroids. Leucopenia (<4.0): viral infection, bone marrow suppression, hypersplenism, drugs. Critical: <1.0 (sepsis risk) or >30.0 (leukaemia until proven otherwise).",
      "Screens for infection, inflammation, haematological malignancies, bone marrow function. Essential for monitoring chemotherapy and HIV.",
      "Pseudoleucopenia in clotted samples; cryoglobulins cause falsely high count; manual differential needed for blasts; cannot diagnose leukaemia alone (requires flow cytometry + bone marrow).",
      ["McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi.",
       "Cheesbrough, M. (2005). District laboratory practice in tropical countries (2nd ed.). Cambridge University Press."],
      ["henry", "malawi_sop", "cheesbrough"])

_proc("CD4 Count", _d, "Whole blood (EDTA)", "EDTA (lavender-top) tube",
      "3–5 mL", "Room temp: 48 h (do NOT refrigerate); stable in Cylex T-Cell tube: 72 h",
      "Room temp only (refrigeration destroys CD4 cells); transport within 24 h; do not vortex or freeze",
      "No special preparation; avoid extreme exercise before collection",
      "Flow cytometry (BD FACSCount, FACSCalibur, or PIMA point-of-care). CD3+ gating → CD4+ subset identified by fluorescence-labelled monoclonal antibodies (anti-CD4-PE, anti-CD3-PerCP). Absolute count by bead-based or single-platform method.",
      "Flow cytometer, monoclonal antibodies (CD4/CD3), lysis buffer, counting beads (TruCOUNT tubes), PBS, pipettes, vortex, centrifuge",
      "Daily QC: bead calibration, fluorescence compensation. Controls: Immuno-Trol or equivalent run daily. External QA: UK NEQAS or CDC programme. Instrument cleaning weekly.",
      "2–3 h (automated); 20 min (PIMA POC)",
      "Normal: 500–1500 cells/µL. Moderate immunosuppression: 200–500. Severe immunosuppression: <200 (AIDS-defining). <350: start ART per Malawi guidelines. <200: start co-trimoxazole prophylaxis. Rising CD4 on ART = good immunological response.",
      "Key monitoring tool for HIV disease progression and ART response. Guides prophylaxis decisions (co-trimoxazole, fluconazole). Independent predictor of mortality in HIV.",
      "Variation: 15–25% intra-individual (time of day, intercurrent infection). Refrigeration destroys cells. PIMA POC has higher variability. Does not measure CD4 function. Not reliable during acute infection.",
      ["World Health Organization. (2022). Consolidated guidelines on HIV prevention, testing, treatment, service delivery and monitoring. WHO.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi.",
       "McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier."],
      ["who_hiv", "malawi_sop", "henry"])

_proc("Platelet Count", _d, "Whole blood (EDTA)", "EDTA (lavender-top) tube",
      "2–3 mL", "Room temp: 6 h; 2–8°C: 24 h (do not refrigerate for impedance counting — platelet swelling)",
      "Room temp; gently invert tube 8–10 times; store upright; do not refrigerate",
      "No special preparation; note: platelets decrease in pregnancy (gestational thrombocytopenia); pseudothrombocytopenia due to EDTA-induced agglutination",
      "Impedance (Coulter) or optical (fluorescent) method on automated haematology analyser. Blood passed through aperture; platelets counted in 2–20 fL channel (impedance) or by fluorescent staining + laser scatter (optical). Fluorescent method preferred for low counts or platelet clumps. Blood smear review to confirm thrombocytopenia.",
      "Haematology analyser (e.g., Sysmex XN, Mindray BC), EDTA blood, reagents (diluent, lysate), controls, blood smear slides for manual verification",
      "Two-level QC daily. Calibration verified every 6 months. 200-cell manual differential if abnormal flag. Blood film review for platelet clumps/giant platelets if count <100 or >600. External QA monthly. Capillary versus venous discrepancy noted.",
      "1 min (automated)",
      "150–400 ×10⁹/L. Thrombocytopenia (<150): immune (ITP, SLE, drugs), consumptive (DIC, TTP), reduced production (leukaemia, marrow infiltration), sequestration (hypersplenism), gestational. Thrombocytosis (>400): reactive (infection, iron deficiency, inflammation, post-splenectomy), essential thrombocythaemia (primary). Critical: <20 (spontaneous bleeding risk) or >800 (thrombosis risk).",
      "Essential for haemostasis assessment. Screens for bleeding disorders, DIC, bone marrow failure, and pre-eclampsia. Pre-operative and chemotherapy monitoring.",
      "Pseudothrombocytopenia: EDTA-induced platelet agglutination (check smear, use citrate tube). Platelet clumps falsely lower count. Giant platelets counted as RBCs (falsely low). Pregnancy: mild decrease normal. Diurnal variation (platelets peak in afternoon).",
      ["McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
       "Cheesbrough, M. (2005). District laboratory practice in tropical countries (2nd ed.). Cambridge University Press.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["henry", "cheesbrough", "malawi_sop"])

_proc("Blood Film Comment", _d, "Whole blood (EDTA) or capillary blood", "EDTA (lavender-top) tube or glass slide (fresh smear)",
      "1 drop (smear); 2–3 mL (EDTA tube)", "Make smear within 2 h (EDTA); capillary smear immediately",
      "Room temp; fix with methanol within 1 h of making smear",
      "No special preparation; note: fingertip puncture for capillary smears; avoid alcohol contamination",
      "Thin blood film on glass slide, air-dried, fixed in methanol (3 min), stained with Giemsa or Wright's stain (15–20 min). Examined systematically at ×100 (low power for smear quality, WBC estimate, platelet clumps) and ×1000 oil immersion for cell morphology, differential WBC count (100–200 cells), RBC morphology, and platelet estimate.",
      "Microscope (×1000 oil immersion), glass slides, coverslips, methanol, Giemsa/Wright stain, staining rack, immersion oil, tally counter",
      "Stain QC: fresh stain monthly; known normal slide checked with each batch. 10% of films rechecked by senior technologist. Slide archived for 7 days (minimum). Differential verified against automated count.",
      "30–45 min (manual differential)",
      "RBC: normocytic normochromic (normal), microcytic hypochromic (IDA, thalassaemia), macrocytic (B12/folate deficiency), dimorphic (mixed deficiency), sickle cells (SCD), target cells (HbC, thalassaemia, liver disease), spherocytes (hereditary spherocytosis, AIHA), schistocytes (microangiopathic haemolytic anaemia/TTP/HUS), blasts (leukaemia), nucleated RBCs (marrow infiltration/demand). WBC: left shift (infection), toxic granulation (sepsis), atypical lymphocytes (EBV, viral), blasts (acute leukaemia).",
      "Provides essential morphological confirmation of automated results. Detects malaria parasites, abnormal cells (blasts, lymphoma), and RBC abnormalities missed by analyser. Gold standard for differential when analyser flags abnormalities.",
      "Subjective interpretation — requires trained technologist. Thick films better for malaria (thin for species identification). Drying artefact, stain precipitate, or thick smear may obscure detail. Smear made from EDTA >4 h shows degenerative changes.",
      ["McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
       "Cheesbrough, M. (2005). District laboratory practice in tropical countries (2nd ed.). Cambridge University Press.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["henry", "cheesbrough", "malawi_sop"])

_proc("Hb Electrophoresis", _d, "Whole blood (EDTA)", "EDTA (lavender-top) tube",
      "3–5 mL", "Room temp: 8 h; 2–8°C: 7 days; haemolysate stable –20°C: 6 months",
      "Room temp; EDTA whole blood stable up to 7 days at 2–8°C",
      "No special preparation; note: recent transfusion (<12 weeks) may mask patient's Hb pattern; family studies often required for definitive diagnosis",
      "Alkaline electrophoresis (cellulose acetate pH 8.6) or capillary electrophoresis (CE) or HPLC (Bio-Rad D-10/VARIANT II). Haemolysate applied to medium, electrophoresed, bands fixed and stained (Ponceau S). Hb fractions quantified by densitometry. HPLC: cation-exchange column, haemoglobins eluted by pH gradient, detected at 415 nm. HbA2 confirmed: >3.5% = β-thal trait; HbF elevated in β-thal major/HPFH.",
      "Electrophoresis tank + power supply, cellulose acetate plates/agarose gel, buffer (TEB pH 8.6), densitometer, HPLC system (Bio-Rad D-10/VARIANT II), controls (HbAA, HbAS, HbSS), haemoglobin lysate reagents",
      "QC: known controls (AA, AS, SS, AC, SC) run with each batch. HbA2 reference verified annually. HPLC: calibration verification weekly. External QA (UK NEQAS Haemoglobinopathies) quarterly. Southern blot/DNA analysis for definitive genotyping when needed.",
      "Electrophoresis: 2–3 h; HPLC: 6–10 min/sample",
      "HbAA: Normal adult (HbA 95–98%, HbA2 2–3.5%, HbF <1%). HbAS: Sickle cell trait (HbA ~60%, HbS ~40%). HbSS: Sickle cell disease (HbS ~80–95%, HbF 5–20%, HbA2 normal). HbAC: HbC trait. HbCC: HbC disease. HbSC: Compound heterozygote SCD. Elevated HbA2 (>3.5%): β-thalassaemia trait. Elevated HbF: β-thal major, HPFH, juvenile myelomonocytic leukaemia. HbH/Constant Spring: α-thalassaemia.",
      "Definitive diagnosis of haemoglobinopathies (sickle cell disease, thalassaemias, HbC/E/D). Essential for newborn screening, premarital counselling, and chronic anaemia investigation.",
      "Recent transfusion (<12 weeks) masks patient Hb genotype. HPLC cannot resolve some variants (requires CE or DNA analysis). HbF and HbA2 affected by age (HbF high in newborns). Some variants co-elute. DNA analysis (PCR, sequencing) required for definitive genotyping.",
      ["McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
       "Cheesbrough, M. (2005). District laboratory practice in tropical countries (2nd ed.). Cambridge University Press.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["henry", "cheesbrough", "malawi_sop"])


# --------------------- URINALYSIS ---------------------
_d = "Urinalysis"
_proc("Urine Dipstick", _d, "Fresh mid-stream urine (MSU)", "Sterile, wide-mouth, leak-proof container",
      "10–20 mL", "Room temp: 1 h; 2–8°C: 4 h (discard if >4 h old)",
      "Room temp within 1 h; refrigeration delays but does not prevent changes",
      "Mid-stream clean-catch technique: wash hands, clean urethral meatus, discard first stream, collect mid-stream. First morning specimen preferred for protein/bilirubin/nitrite.",
      "Dipstick (reagent strip) immersed in well-mixed urine for 1 s, edge drawn along rim, placed on absorbent pad. Read at 60–120 s (specific timing per parameter). Parameters: pH, SG, glucose, protein, blood, ketones, bilirubin, urobilinogen, nitrite, leucocyte esterase, ascorbate.",
      "Urine dipsticks (e.g., Combur, Multistix, Urisys), urine analyser (e.g., Urisys 1800, Cobas u 601) or manual reading, clean container",
      "QC: known positive and negative dipstick controls run daily. Check strip expiry date. Store strips at 2–30°C in original container, desiccant cap tightly closed. Do not touch reagent pads.",
      "1–2 min (manual); automated: 1 min/sample",
      "See individual parameters: glucose (diabetes), protein (renal disease), blood (UTI/stones), nitrite (bacteria), leucocyte esterase (WBCs → UTI), ketones (DKA/starvation), bilirubin (obstructive jaundice). Normal: all negative except pH 4.5–8.0, SG 1.005–1.030.",
      "Rapid, inexpensive screening for multiple conditions: UTI, diabetes, renal disease, liver disease, metabolic disorders. Essential first-line test in primary care.",
      "Coloured urine (beetroot, rifampicin, phenazopyridine) interferes with colour reactions. High ascorbate false-negative glucose/blood/nitrite. Stale urine: pH becomes alkaline, ketones evaporate, bacteria multiply. Specific gravity affected by temperature.",
      ["Cheesbrough, M. (2005). District laboratory practice in tropical countries (2nd ed.). Cambridge University Press.",
       "McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["cheesbrough", "henry", "malawi_sop"])

_proc("Urine hCG (Pregnancy)", _d, "Urine (first morning preferred) or serum", "Clean container (urine); SST (serum)",
      "10–20 mL (urine); 3–5 mL (serum)", "Room temp: 8 h; 2–8°C: 48 h",
      "Room temp; avoid freeze-thaw cycles",
      "First morning urine contains highest hCG concentration. Avoid excessive fluid intake before testing (dilutes hCG). Test from day of missed menses onwards.",
      "Lateral flow immunoassay. Urine/serum flows across nitrocellulose strip. hCG binds to anti-β-hCG antibody-colloidal gold conjugate. Complex captured by immobilised anti-α-hCG antibody → pink/purple test line. Control line confirms test validity. Read at 3–5 min.",
      "Pregnancy test kit (e.g., OneStep, Clearview), timer, urine/serum specimen, pipette if required",
      "Kit internal control: control line must appear. Check expiry date. Store at 2–30°C. Positive and negative controls with each new lot. Do not use if foil pouch damaged.",
      "3–5 min",
      "Negative: No hCG detected — pregnancy unlikely if amenorrhoea >7 days (may be too early if <7 days post-implantation). If high suspicion, repeat in 48–72 h.\nPositive: hCG detected — pregnancy confirmed. Refer for ANC. Quantitative serum hCG can estimate gestational age and rule out ectopic.",
      "Rapid, sensitive (25 mIU/mL), specific for pregnancy. Also elevated in gestational trophoblastic disease and some germ cell tumours.",
      "False-negative: very early pregnancy, dilute urine, expired kit. False-positive: recent miscarriage/abortion, molar pregnancy, hCG-producing tumours, rare assay interference (heterophilic antibodies).",
      ["Cheesbrough, M. (2005). District laboratory practice in tropical countries (2nd ed.). Cambridge University Press.",
       "McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["cheesbrough", "henry", "malawi_sop"])

_proc("Urine Microscopy", _d, "Fresh mid-stream urine (MSU)", "Sterile, wide-mouth, leak-proof container",
      "10–20 mL", "Room temp: 1 h; 2–8°C: 4 h (crystals may precipitate on refrigeration)",
      "Room temp within 1 h; delay >1 h invalidates cellular elements and casts",
      "Mid-stream clean-catch; first morning specimen preferred; avoid menstruation during collection",
      "Well-mixed urine (10 mL) centrifuged at 1500–2000 rpm × 5 min. Supernatant decanted; sediment resuspended in ~0.5 mL. One drop placed on slide, coverslipped. Examined systematically: ×100 (low power) for casts and crystals (10 fields); ×400 (high power) for WBC, RBC, epithelial cells, bacteria, yeasts (10 fields). Report per HPF or LPF as per standardised reporting scheme.",
      "Microscope (×100, ×400), centrifuge, glass slides, coverslips, pipettes, centrifuge tubes, urine sediment chart",
      "QC: known positive sediment checked weekly; 10% of negatives rechecked; centrifuge speed and time standardised. Use fresh specimen only. Staining (Sternheimer-Malbin or Sternheimer) optional for cell identification.",
      "30 min (collection to report)",
      "WBC: 0–5 /HPF (normal). >5/HPF = pyuria (UTI, STI, TB, interstitial nephritis). RBC: 0–3 /HPF (normal). >3/HPF = haematuria (UTI, stones, glomerulonephritis, trauma, tumour, schistosomiasis). Casts: hyaline (normal, dehydration), granular (tubular injury), RBC casts (pathognomonic for glomerulonephritis), WBC casts (pyelonephritis), waxy (CKD). Crystals: calcium oxalate (dietary, stones), uric acid (gout, acidic urine), triple phosphate/struvite (UTI), cystine (cystinuria).",
      "Essential to confirm dipstick findings and detect formed elements (casts, crystals, cells) not detected by dipstick. Gold standard for haematuria evaluation.",
      "Delay >1 h: WBC and RBC lyse, casts disintegrate, bacteria multiply, pH changes. Refrigeration: crystals precipitate (may confuse). Centrifugation speed too high: casts break; too low: cells not sedimented. Menstrual blood contaminates urine RBC.",
      ["Cheesbrough, M. (2005). District laboratory practice in tropical countries (2nd ed.). Cambridge University Press.",
       "McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["cheesbrough", "henry", "malawi_sop"])

_proc("Urine Culture", _d, "Fresh mid-stream urine (MSU) or catheter specimen", "Sterile, wide-mouth, leak-proof container (no preservative)",
      "10–20 mL", "Room temp: 2 h; 2–8°C: 24 h (refrigerate if >2 h delay)",
      "Transport within 2 h or refrigerate at 2–8°C; use boric acid preservative tube if delay >24 h",
      "Mid-stream clean-catch after washing; catheter specimen by sterile technique; instruct patient to separate labia/retract foreskin",
      "Calibrated loop (1 µL or 10 µL) streaked onto CLED (cysteine-lactose-electrolyte-deficient) agar and BA (blood agar). Incubate at 35–37°C aerobically for 18–24 h. CFU count: ≥10⁵ CFU/mL = significant bacteriuria (single organism). For catheter specimens: ≥10² CFU/mL significant. Identification by colony morphology, Gram stain, biochemical tests. AST per CLSI guidelines.",
      "Incubator (35–37°C), biosafety cabinet, calibrated loops (1 µL, 10 µL), CLED agar, BA, MAC agar, Gram stain reagents, biochemical test reagents/KIA/TSI, antibiotic discs, McFarland standard",
      "Media QC: sterility and growth support checked every batch. Incubator temperature logged daily. Positive control (E. coli ATCC 25922) weekly. Urine culture QC: known positive and negative controls. Disc diffusion QC per CLSI M100.",
      "18–24 h (preliminary negative); 24–48 h (final negative); AST: additional 24 h",
      "<10³ CFU/mL: Insignificant — likely contamination. 10³–10⁴ CFU/mL: Borderline — repeat if symptomatic. ≥10⁵ CFU/mL single organism: Significant bacteriuria — UTI confirmed. ≥10² CFU/mL (catheter): Significant for catheter-associated UTI. Mixed growth ≥2 organisms: Likely contamination — repeat clean-catch specimen. Report organism(s) and AST: S, I, R per CLSI breakpoints.",
      "Gold standard for diagnosing UTI. Identifies causative organism and antibiotic susceptibility pattern for targeted therapy. Essential for antimicrobial stewardship and complicated UTI.",
      "Contamination common if clean-catch not performed correctly. Prior antibiotics reduce yield. Fastidious organisms (Lactobacillus, Gardnerella) may be missed on routine media. Delayed transport: bacterial multiplication may produce false-positive. Anaerobic UTI requires specific request.",
      ["Cheesbrough, M. (2005). District laboratory practice in tropical countries (2nd ed.). Cambridge University Press.",
       "Clinical and Laboratory Standards Institute. (2022). Performance standards for antimicrobial susceptibility testing (32nd ed., CLSI supplement M100). CLSI.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["cheesbrough", "clsi", "malawi_sop"])


# --------------------- PARASITOLOGY ---------------------
_d = "Parasitology"
_proc("Stool Microscopy — Ova & Cysts", _d, "Fresh stool (formed or semi-formed)", "Clean, wide-mouth, leak-proof container; no toilet paper/urine contamination",
      "Finger-to-thumbnail sized (approx. 5–10 g)", "Room temp: 1 h (formed); 30 min (liquid); 2–8°C: 24 h in PVA or formalin fixative",
      "Transport within 1 h (unpreserved); if delay >1 h, use formalin or PVA fixative; triple-packed",
      "Explain collection technique: pass stool onto clean paper/pan, use provided scoop, avoid urine/water/soil contamination. Three specimens on alternate days recommended.",
      "Direct wet mount: pea-sized stool emulsified in saline (trophozoites) and iodine (cysts), coverslipped, examined systematically at ×100 (cysts) and ×400 (trophozoites). Formol-ether concentration: 1 g stool emulsified in 10% formalin, ether added, centrifuged at 2000 rpm × 2 min; sediment examined. Modified ZN for Cryptosporidium (if requested).",
      "Microscope (×100, ×400, ×1000 oil), centrifuge, glass slides, coverslips, saline, Lugol's iodine, 10% formalin, diethyl ether/ethyl acetate, staining rack",
      "QC: known positive slides read monthly; bench aids/charts available for identification; 10% of negative slides rechecked by senior technologist. Participate in external PT programme.",
      "Direct mount: 15–30 min; Concentration: 45 min; Modified ZN: 30 min",
      "Report organisms identified and semi-quantitative load. Common findings: Hookworm (Ancylostoma/Necator), Ascaris, Trichuris, Schistosoma (S. mansoni, S. haematobium in urine), Giardia (trophozoites/cysts), E. histolytica (with ingested RBCs = invasive), Taenia, Strongyloides, Cryptosporidium (HIV). Negative: 'No ova, cysts, or parasites seen'.",
      "Essential for diagnosing intestinal parasitic infections, a major cause of morbidity in tropical countries. Directs deworming and schistosomiasis control programmes.",
      "Sensitivity low (single stool: ~50%); three specimens increase yield to 85–90%. Some parasites (S. stercoralis, pinworm) require special techniques. Cannot speciate some hookworm eggs. Immunocompromised patients may have atypical loads.",
      ["Cheesbrough, M. (2005). District laboratory practice in tropical countries (2nd ed.). Cambridge University Press.",
       "World Health Organization Regional Office for Africa. (2019). Integrated disease surveillance and response (IDSR) technical guidelines (3rd ed.). WHO AFRO.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["cheesbrough", "who_afro", "malawi_sop"])

_proc("Kato-Katz (Stool Egg Count)", _d, "Fresh stool (formed)", "Clean, wide-mouth container; no toilet paper/urine",
      "Finger-to-thumbnail sized (~5–10 g)", "Process within 24 h (fresh); do not refrigerate (eggs hatch)",
      "Transport within 2 h; keep at room temp; process same day",
      "No special preparation; collect three specimens on alternate days for optimal sensitivity (Schistosoma mansoni egg excretion varies diurnally)",
      "Stool pressed through 212 µm mesh sieve to remove debris. ~41.7 mg sieved stool transferred to template on slide, covered with glycerin-soaked cellophane (soaked 24 h in 3% malachite green/glycerin). Slides left 24 h for clearing (S. mansoni eggs clear faster — read at 24 h; hookworm eggs overclear after 30–60 min). Total eggs counted × 24 = eggs/g.",
      "Microscope (×100 for egg count), Kato-Katz kit (template, 212 µm sieve, cellophane strips, spatula, slides), glycerin-malachite green solution, timer",
      "QC: duplicate readings on 10% of slides; positive control slide set available; participate in external QA (WHO NTD laboratory network). Template volume verified periodically (41.7 mg = 1/24th of a gram).",
      "30 min per sample (collection to clearing); reading at 24 h (S. mansoni) or within 30–60 min (hookworm — read immediately)",
      "Negative: No eggs seen after 24 h clearing. Light intensity: <100 eggs/g (S. mansoni) or <2000 eggs/g (hookworm/Trichuris). Moderate: 100–399 eggs/g (S. mansoni). Heavy: ≥400 eggs/g (S. mansoni). WHO thresholds used for MDA decision-making. S. mansoni: light <100, moderate 100–399, heavy ≥400. Soil-transmitted helminths: light <2000, moderate 2000–3999, heavy ≥4000 eggs/g.",
      "WHO-recommended quantitative method for mapping and monitoring schistosomiasis and STH control programmes. Determines infection intensity, which correlates with morbidity. Essential for MDA decision-making.",
      "Hookworm eggs overclear in glycerin (>60 min) — read quickly or use different clearing time. Sensitivity low in light infections. Cannot differentiate Schistosoma species (S. intercalatum, S. guineensis similar to S. mansoni). Malachite green is potential carcinogen — handle with care.",
      ["Cheesbrough, M. (2005). District laboratory practice in tropical countries (2nd ed.). Cambridge University Press.",
       "World Health Organization Regional Office for Africa. (2019). Integrated disease surveillance and response (IDSR) technical guidelines (3rd ed.). WHO AFRO.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["cheesbrough", "who_afro", "malawi_sop"])


# --------------------- MOLECULAR BIOLOGY ---------------------
_d = "Molecular Biology"
_proc("HIV-1 Viral Load", _d, "Plasma (EDTA or PPT)", "EDTA (lavender-top) or PPT (plasma preparation tube)",
      "4–6 mL (EDTA); 2–3 mL (PPT)", "Room temp: 6 h; 2–8°C: 72 h; –20°C: 1 month; –70°C: long-term. Do NOT freeze whole blood.",
      "Centrifuge within 6 h; separate plasma; transport on dry ice if frozen; UN3373 Category B",
      "No special preparation; avoid haemolysis (reduces RNA yield); note: do not draw from arm with IV infusion; collect before daily ART dose (trough level not required but recommended for consistency)",
      "Real-time RT-PCR (e.g., Abbott m2000, Roche COBAS AmpliPrep/TaqMan, Cepheid GeneXpert VL). RNA extracted from plasma, reverse-transcribed to cDNA, amplified with HIV-1-specific primers/probes targeting gag/pol/LTR. Quantified against internal standard. Detection range: 40–10,000,000 copies/mL.",
      "Real-time PCR instrument, nucleic acid extraction system, V/P (viral load) reagents, internal control, calibrators, controls, pipettes (dedicated PCR set)",
      "Three-level QC (negative, low positive, high positive) each run. Calibration curve with WHO International Standard. External QA: VQA, UK NEQAS. Contamination control: separate areas for extraction, amplification, detection. UV decontamination, one-way workflow.",
      "4–6 h (batched); 90 min (GeneXpert, single sample)",
      "Suppressed: <40 copies/mL — continue ART, repeat in 6 months.\nLow-level viraemia: 40–999 copies/mL — repeat VL in 3 months, reinforce adherence.\nModerate: 1000–9999 copies/mL — assess adherence, consider resistance testing if persistent.\nHigh: ≥10,000 copies/mL — likely treatment failure; request resistance testing, switch regimen per Malawi protocol.",
      "Gold standard for monitoring ART efficacy. WHO recommends VL at 6 and 12 months after ART initiation, then annually. Goal: sustained suppression <1000 copies/mL.",
      "Cannot detect HIV-2 (use separate assay); clade-dependent sensitivity (group O, N, P may under-quantify); haemolysis and long storage reduce RNA yield; requires stable power and cold chain; cost/per sample high.",
      ["World Health Organization. (2022). Consolidated guidelines on HIV prevention, testing, treatment, service delivery and monitoring. WHO.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi.",
       "McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier."],
      ["who_hiv", "malawi_sop", "henry"])

_proc("HBsAg (Hepatitis B)", _d, "Serum (SST or plain tube) or plasma (EDTA/heparin)", "SST (gold-top), plain (red-top), or EDTA (lavender-top)",
      "3–5 mL", "Room temp: 8 h; 2–8°C: 7 days; –20°C: 1 month",
      "Centrifuge within 2 h; transport at 2–8°C if delay >4 h",
      "No special preparation; consent required for HIV/HBV testing per Malawi guidelines",
      "Enzyme-linked immunoassay (ELISA) or chemiluminescent immunoassay (CLIA). Microwell plates coated with monoclonal anti-HBsAg antibodies. Patient serum added; if HBsAg present, it binds. Detection antibody (anti-HBsAg-HRP conjugate) added, followed by TMB substrate. Blue colour develops, stopped with acid (yellow). Absorbance read at 450/630 nm. Positive: OD ≥ cut-off. Confirm with neutralisation assay.",
      "ELISA/CLIA analyser or automated immunoassay platform, HBsAg kit, microwell washer, pipettes, incubator (37°C), reader (450 nm)",
      "Kit controls: negative, cut-off, positive control must meet manufacturer ranges. Internal QC: known positive and negative samples each run. External QA: NEQAS hepatitis programme quarterly. Do not use expired kits. Store kit at 2–8°C.",
      "2–3 h (ELISA); 30–45 min (rapid test/CLIA)",
      "Negative: No HBsAg detected — no current HBV infection (vaccinate if at risk). Positive: HBsAg detected — current HBV infection (acute or chronic). Acute HBV: HBsAg + HBeAg + IgM anti-HBc. Chronic HBV (>6 months): HBsAg + HBeAg or anti-HBe + IgG anti-HBc. Refer for HBV DNA, LFTs, ultrasound, and treatment assessment per Malawi guidelines.",
      "Primary screening test for HBV infection. Essential for blood donor screening, antenatal screening (prevents vertical transmission), and high-risk population testing.",
      "Window period: HBsAg negative during acute infection window (HBsAg disappeared, anti-HBs not yet detectable) — test for IgM anti-HBc. Occult HBV: HBsAg negative but HBV DNA positive (immunosuppressed, HIV co-infection). Mutant HBV may escape detection. Confirm reactive results with neutralisation test.",
      ["Jameson, J. L., Kasper, D. L., Longo, D. L., Fauci, A. S., Hauser, S. L., & Loscalzo, J. (2022). Harrison's principles of internal medicine (21st ed.). McGraw Hill.",
       "World Health Organization. (2022). Consolidated guidelines on HIV prevention, testing, treatment, service delivery and monitoring. WHO.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["harrison", "who_hiv", "malawi_sop"])

_proc("HCV Antibody", _d, "Serum (SST or plain tube) or plasma (EDTA)", "SST (gold-top), plain (red-top), or EDTA (lavender-top)",
      "3–5 mL", "Room temp: 8 h; 2–8°C: 7 days; –20°C: 3 months",
      "Centrifuge within 2 h; transport at 2–8°C if delay >4 h",
      "No special preparation; consent required; note: seroconversion may take 4–10 weeks (window period)",
      "Third/fourth-generation ELISA or CLIA. Microwell plates coated with recombinant HCV antigens (core, NS3, NS4, NS5). Patient antibodies (anti-HCV) bind. Detection with anti-human IgG-HRP conjugate + TMB substrate. Colour development stopped with acid, read at 450/630 nm. Reactive samples: repeat twice; if repeatedly reactive, confirm with HCV RNA (PCR) or RIBA (recombinant immunoblot assay).",
      "ELISA/CLIA analyser, HCV kit, microwell washer, pipettes, incubator, reader (450 nm)",
      "Kit controls (negative, cut-off, positive) must meet range. Known positive and negative controls run each plate. External QA quarterly. Confirm all positive screens with HCV RNA or RIBA. Check kit lot number, expiry, storage (2–8°C).",
      "2–3 h (ELISA); 30–45 min (rapid test/CLIA)",
      "Negative: No anti-HCV detected — no evidence of HCV infection (or window period if recent exposure). Positive: Anti-HCV detected — past or current infection. Cannot distinguish active vs resolved. Must confirm with HCV RNA PCR. If HCV RNA positive = active chronic HCV infection. If HCV RNA negative = resolved infection OR false-positive screen. Refer for genotype, LFTs, FibroScan.",
      "Screening test for HCV infection. Essential for blood donor screening, risk-based testing (IVDU, transfused before 1992, HIV co-infected).",
      "Window period 4–10 weeks (negative antibody but HCV RNA positive) — if recent exposure, test HCV RNA directly. False-positive: autoimmune disease, rheumatoid factor, post-vaccination (rare). False-negative: immunosuppression (HIV, transplant). Cannot distinguish active vs past infection (need HCV RNA).",
      ["Jameson, J. L., Kasper, D. L., Longo, D. L., Fauci, A. S., Hauser, S. L., & Loscalzo, J. (2022). Harrison's principles of internal medicine (21st ed.). McGraw Hill.",
       "World Health Organization. (2022). Consolidated guidelines on HIV prevention, testing, treatment, service delivery and monitoring. WHO.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["harrison", "who_hiv", "malawi_sop"])

_proc("Syphilis Serology (RPR/VDRL)", _d, "Serum (SST or plain tube) or plasma (EDTA)", "SST (gold-top), plain (red-top), or EDTA (lavender-top)",
      "3–5 mL", "Room temp: 8 h; 2–8°C: 72 h; –20°C: 1 month (do not heat-inactivate)",
      "Centrifuge within 2 h; transport at 2–8°C",
      "No special preparation; explain procedure; antenatal screening consent per Malawi guidelines",
      "RPR (rapid plasma reagin) flocculation test. Serum (50 µL) placed on card, one drop RPR antigen (charcoal-containing cardiolipin-lectthin-cholesterol suspension) added. Rotated at 100 rpm for 8 min. Clumping (flocculation) = reactive. VDRL: serum heated 56°C × 30 min, mixed with VDRL antigen on slide, rotated for 4 min at 180 rpm. Read microscopically at ×100. Titre: serial doubling dilutions (1:2 to 1:256+). Serofast: stable low titre after treatment.",
      "RPR card kit/VDRL antigen, rotator (100 rpm), pipettes, VDRL slides, microscope (×100), saline, heating block (56°C for VDRL)",
      "QC: known positive and negative controls each session. RPR: reactive control (16–32 titre) must be within ±1 dilution. Antigen: resuspended fresh daily; discard if contaminated. Temperature: VDRL heating exactly 56°C × 30 min. External QA quarterly.",
      "8 min (RPR); 1 h (VDRL with inactivation)",
      "Non-reactive: No serological evidence of syphilis (or very early infection — 2–4 week window). Reactive 1:2–1:8: Low titre — may be old treated infection, early primary, or false-positive (pregnancy, autoimmune, TB, malaria, leprosy, vaccination). Reactive ≥1:16: Active infection requiring treatment. Confirm with treponemal test (TPHA/TPPA). Four-fold drop in titre after treatment = adequate response. Serofast: persistent low titre after treatment — common in HIV co-infection.",
      "Non-treponemal screening test for syphilis. Quantifiable — monitors treatment response. Used for antenatal screening (Malawi recommends at first ANC visit, third trimester). Essential for congenital syphilis prevention.",
      "False-positive: pregnancy, autoimmune (SLE), TB, malaria, leprosy, recent vaccination, IVDU, elderly. False-negative: early infection (2–4 week window), prozone phenomenon (high antibody excess — dilute serum 1:2, 1:4). HIV co-infection may cause atypical titres. VDRL requires heated serum — unheated gives false-positive.",
      ["Jameson, J. L., Kasper, D. L., Longo, D. L., Fauci, A. S., Hauser, S. L., & Loscalzo, J. (2022). Harrison's principles of internal medicine (21st ed.). McGraw Hill.",
       "World Health Organization. (2022). Consolidated guidelines on HIV prevention, testing, treatment, service delivery and monitoring. WHO.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["harrison", "who_hiv", "malawi_sop"])

_proc("SARS-CoV-2 PCR", _d, "Nasopharyngeal (NP) swab, oropharyngeal (OP) swab, sputum, BAL", "Swab in viral transport medium (VTM) or sterile container (sputum)",
      "NP swab: 1–2 mL VTM; Sputum: 2–5 mL", "Room temp: 24 h; 2–8°C: 72 h; –20°C: 1 month; –70°C: long-term",
      "Triple-packed UN3373 Category B; transport on ice (2–8°C); do not freeze VTM before processing",
      "Explain procedure — NP swab: insert through nostril to nasopharynx, rotate 10 s, withdraw. OP swab: swab posterior pharynx and tonsillar pillars. Sputum: cough deeply from chest. PPE: N95 mask, face shield, gown, gloves.",
      "Real-time RT-PCR targeting SARS-CoV-2 genes (E, N, ORF1ab, RdRp). RNA extracted from VTM/sputum using magnetic bead or column-based extraction. One-step RT-PCR (reverse transcription and PCR in single reaction). Amplified target detected by hydrolysis probes (TaqMan). Ct value inversely proportional to viral load. Result: detected (positive) or not detected (negative). Internal control (e.g., RNase P) confirms specimen adequacy.",
      "Real-time PCR instrument (e.g., AB 7500, QuantStudio 5, GeneXpert), nucleic acid extraction system, RT-PCR kit (e.g., CDC/WHO primers, TaqPath, GeneXpert Xpress SARS-CoV-2), PCR tubes/plates, dedicated pipettes",
      "Per WHO: positive and negative controls each run. Extraction control to assess extraction efficiency. Internal control in every well. One-way workflow (extraction → amplification separate rooms). UV decontamination. Staff competency assessed quarterly. External QA (WHO panel, NEQAS) quarterly.",
      "4–6 h (batched); 45 min (GeneXpert rapid)",
      "NOT DETECTED: SARS-CoV-2 RNA not detected — COVID-19 unlikely (if adequate specimen). If high clinical suspicion, repeat in 3–5 days. DETECTED (Ct <40): SARS-CoV-2 RNA detected — COVID-19 confirmed. Report Ct value (lower Ct = higher viral load). Ct <25: high viral load (highly infectious). Ct 25–35: moderate viral load. Ct 35–40: low viral load (early/late infection or residual RNA).",
      "Gold standard for COVID-19 diagnosis. Highly sensitive (≥95%) and specific (≥99%) when performed correctly. Ct value correlates with infectivity.",
      "False-negative: poor swab technique, early/late disease, inadequate VTM, transport delay, freeze-thaw. False-positive: contamination (amplicon) — rare with one-way workflow. Ct value not standardised across platforms. May remain positive for weeks after recovery (RNA shedding). New variants may affect primer/probe binding.",
      ["World Health Organization. (2022). WHO guidelines on use of medically important antimicrobials. WHO.",
       "Jameson, J. L., Kasper, D. L., Longo, D. L., Fauci, A. S., Hauser, S. L., & Loscalzo, J. (2022). Harrison's principles of internal medicine (21st ed.). McGraw Hill.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["who_ebm", "harrison", "malawi_sop"])

_proc("GeneXpert CT/NG", _d, "Urine (first-void, not mid-stream), endocervical swab, urethral swab", "Urine: sterile container; Swab: swab in transport medium",
      "Urine: 10–20 mL (first 10–20 mL of stream); Swab: as per kit", "Room temp: 24 h; 2–8°C: 72 h; do not freeze",
      "Transport at 2–8°C if delay >2 h; urine stable 24 h at room temp",
      "Urine: patient should not have urinated for ≥1 h before collection; first-void urine (NOT mid-stream). Swab: endocervical (rotate 10 s in os), urethral (insert 2–3 cm, rotate, withdraw).",
      "Urine (1 mL) or swab in elution buffer, transferred to GeneXpert CT/NG cartridge. Cartridge loaded into GeneXpert instrument. Automated DNA extraction, real-time PCR targeting Chlamydia trachomatis cryptic plasmid and Neisseria gonorrhoeae genomic DNA. Includes internal control. Results in ~90 min.",
      "GeneXpert IV/VI/XVI instrument, CT/NG cartridge kit, pipettes (P1000 for urine), urine collection cups, swab collection kit",
      "Kit internal control in every cartridge. External QC: known positive and negative samples weekly. Instrument calibration annually. Cartridge storage at 2–28°C. Do not use expired cartridges. Lot-to-lot verification.",
      "90 min (walk-away)",
      "CT NEGATIVE, NG NEGATIVE: Neither C. trachomatis nor N. gonorrhoeae detected. CT POSITIVE, NG NEGATIVE: C. trachomatis detected — treat with doxycycline 100 mg BID × 7 d or azithromycin 1 g single dose per MSTG. Partner treatment essential. CT NEGATIVE, NG POSITIVE: N. gonorrhoeae detected — treat with ceftriaxone 250 mg IM + azithromycin 1 g oral per Malawi STI guidelines. CT POSITIVE, NG POSITIVE: Dual infection detected — treat both.",
      "WHO-recommended test for diagnosis of chlamydia and gonorrhoea. High sensitivity (≥96%) and specificity (≥99%). Allows same-day treatment. Essential for STI syndromic management backup.",
      "Cannot distinguish viable from non-viable organisms (may remain positive after treatment for 2–3 weeks). Does not provide antibiotic susceptibility profile for N. gonorrhoeae (culture needed for AST). Urine: first-void essential — not mid-stream. Self-collected specimens acceptable but instruction critical.",
      ["Clinical and Laboratory Standards Institute. (2022). Performance standards for antimicrobial susceptibility testing (32nd ed., CLSI supplement M100). CLSI.",
       "World Health Organization. (2023). WHO guidelines on use of medically important antimicrobials. WHO.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["clsi", "who_ebm", "malawi_sop"])


# --------------------- SEMEN ANALYSIS ---------------------
_d = "Semen Analysis"
_proc("Semen Analysis", _d, "Semen (ejaculate)", "Sterile, wide-mouth container (no lubricant)",
      "Whole ejaculate", "Room temp in incubator (37°C): liquefaction 30–60 min; analyse within 1 h of collection (60 min max)",
      "Keep at 37°C during transport; do not refrigerate or expose to extremes; transport within 30 min",
      "Sexual abstinence 2–7 days (WHO: 48 h–7 d). Record abstinence period. Collect by masturbation directly into container. Avoid lubricants (toxic to sperm). Label with name, date, time, abstinence period.",
      "Macroscopic: volume (measuring cylinder), pH (pH paper), colour, viscosity, liquefaction time. Microscopic: sperm concentration (Neubauer haemocytometer or Makler chamber), motility (WHO grades a+b+c), morphology (Papanicolaou or Diff-Quik stain ×1000 oil, strict Kruger criteria), WBC count. Optional: fructose (qualitative), MAR test (antisperm antibodies).",
      "Microscope (phase-contrast ×200, ×400), haemocytometer/Makler chamber, pH paper, measuring cylinder, warm stage/incubator (37°C), pipettes, slides, coverslips",
      "QC: replicate counts (10% difference max), participate in external QA (UK NEQAS Andrology). Temperature control critical (37°C). Counting chamber depth verified. Morphology reviewed by trained technologist.",
      "30–60 min (liquefaction 30 min + analysis 30 min)",
      "Volume: ≥1.5 mL; Concentration: ≥15 ×10⁶/mL; Total motility: ≥40%; Progressive motility: ≥32%; Normal morphology (Kruger): ≥4%; pH: ≥7.2; WBC: <1 ×10⁶/mL; Fructose: present. Abnormal: oligozoospermia, asthenozoospermia, teratozoospermia (or combinations: OAT syndrome). Azoospermia: no sperm — confirm with centrifuge pellet.",
      "First-line investigation for male infertility. Also used for post-vasectomy confirmation (azoospermia). WHO 6th edition (2021) reference values standardised for fertility assessment.",
      "High inter-laboratory variability (especially morphology and motility). Single sample may not represent true fertility. Infection, fever, medications, heat exposure affect results. Requires abstinence compliance.",
      ["World Health Organization. (2021). WHO laboratory manual for the examination and processing of human semen (6th ed.). WHO.",
       "McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["who_semen", "henry", "malawi_sop"])

_proc("Sperm Concentration", _d, "Semen (ejaculate)", "Sterile, wide-mouth container (no lubricant)",
      "Whole ejaculate", "Analyse within 1 h of collection at 37°C",
      "Keep at 37°C; transport within 30 min",
      "Sexual abstinence 2–7 days; record abstinence period; collect by masturbation; avoid lubricants",
      "Neubauer haemocytometer (improved double) or Makler counting chamber. Well-mixed semen (10 µL) loaded onto chamber. After sedimentation (3–5 min), sperm counted in 5 small squares (Neubauer) or 10 rows (Makler) at ×200–400. Count × dilution factor × chamber constant = concentration (×10⁶/mL). WHO 6th ed: at least 200 sperm counted for accuracy. Computer-assisted semen analysis (CASA) also available.",
      "Microscope (phase-contrast ×200, ×400), Neubauer haemocytometer or Makler chamber, pipettes (P10, P20), warm stage (37°C), diluent (saline, formalin, or NaHCO₃-formalin for immobilisation)",
      "QC: replicate counts (duplicate, difference <10%). Chamber depth verified periodically. Dilution accuracy checked. Participate in external QA (UK NEQAS Andrology). Temperatures monitored (37°C). Counting recommendations per WHO 6th ed.",
      "15–30 min",
      "Normal: ≥15 ×10⁶/mL (WHO 6th ed). Oligozoospermia: <15 ×10⁶/mL. Severe oligozoospermia: <5 ×10⁶/mL. Cryptozoospermia: <0.1 ×10⁶/mL. Azoospermia: no sperm (centrifuge pellet at 3000×g for 15 min; if no sperm, confirm with pellet examination on two separate occasions). Polyzoospermia: >200 ×10⁶/mL (rare, may indicate high count with poor quality).",
      "Essential parameter for male infertility investigation. Determines WHO classification (oligo/azo/normozoospermia). Key for intrauterine insemination (IUI) and IVF decision-making.",
      "High inter-laboratory variability (standardised training critical). Single sample may not reflect true concentration (repeat after 2–3 months). Abstinence period must be recorded (longer abstinence increases concentration but reduces motility). Immobilisation essential for accurate counting (motile sperm leave counting area).",
      ["World Health Organization. (2021). WHO laboratory manual for the examination and processing of human semen (6th ed.). WHO.",
       "McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["who_semen", "henry", "malawi_sop"])

_proc("Semen Fructose", _d, "Semen (ejaculate)", "Sterile, wide-mouth container (no lubricant)",
      "Whole ejaculate (from fructose analysis — part of semen analysis)", "Analyse within 1 h of collection; freeze if delayed",
      "Room temp if analysed within 1 h; –20°C if batched",
      "Sexual abstinence 2–7 days; collect by masturbation; avoid lubricants",
      "Qualitative (resorcinol/seliwanoff) or quantitative (enzymatic UV) method. Qualitative: 0.5 mL semen + 0.5 mL 1.8% resorcinol in 30% HCl, heated 60°C × 10 min; red colour = fructose present. Quantitative: Fructose phosphorylated by hexokinase to fructose-6-phosphate, converted to glucose-6-phosphate by phosphoglucose isomerase; G6P + NADP⁺ → 6-phosphogluconolactone + NADPH (absorbance at 340 nm, proportional to fructose). WHO reference: ≥13 µmol/ejaculate.",
      "Water bath (60°C), spectrophotometer (340 nm for quantitative), resorcinol/HCl (qualitative), cuvettes, pipettes, fructose standard, centrifuge",
      "QC: known positive and negative controls (qualitative); calibration curve with fructose standard (quantitative). Reagent blank with each batch. Internal controls (low, normal) run daily.",
      "30 min (qualitative); 1 h (quantitative)",
      "Present (qualitative) or ≥13 µmol/ejaculate (quantitative): Normal — patent seminal vesicles and ejaculatory ducts. Absent (qualitative) or <13 µmol/ejaculate: Suggestive of ejaculatory duct obstruction, seminal vesicle aplasia/atrophy, or incomplete ejaculation. Bilateral absence of vas deferens (CBAVD) associated with absent fructose (CFTR gene mutation).",
      "Marker of seminal vesicle function. Differentiation of obstructive azoospermia (low volume + absent fructose) from testicular causes (normal volume + normal fructose). Essential for azoospermia workup.",
      "Qualitative only detects presence/absence — does not quantify. Low fructose in androgen deficiency, incomplete ejaculation. False-negative: old sample (fructose degraded). False-positive: contamination (glucose from other sources interferes with resorcinol — use specific fructose method).",
      ["World Health Organization. (2021). WHO laboratory manual for the examination and processing of human semen (6th ed.). WHO.",
       "McPherson, R. A., & Pincus, M. R. (2021). Henry's clinical diagnosis and management by laboratory methods (24th ed.). Elsevier.",
       "Malawi Ministry of Health. (2022). Malawi standard treatment guidelines (MSTG) (7th ed.). Government of Malawi."],
      ["who_semen", "henry", "malawi_sop"])


def get_test_procedure(test_name: str) -> dict:
    """Return full procedure guide for a given test name."""
    tp = TEST_PROCEDURES.get(test_name)
    if not tp:
        for n, t in TEST_PROCEDURES.items():
            if test_name.lower() in n.lower():
                tp = t
                break
    if not tp:
        return None
    return {
        "test_name": tp.name,
        "department": tp.department,
        "specimen_type": tp.specimen_type,
        "container": tp.container,
        "volume": tp.volume,
        "storage": tp.storage,
        "transport": tp.transport,
        "patient_preparation": tp.patient_prep,
        "methodology": tp.methodology,
        "equipment": tp.equipment,
        "quality_control": tp.quality_control,
        "turnaround_time": tp.turnaround,
        "interpretation": tp.interpretation,
        "clinical_significance": tp.clinical_significance,
        "limitations": tp.limitations,
        "references": tp.references_apa,
        "reference_keys": tp.references_keys,
    }


def parse_free_text(text: str, gender: str = "male", age: float = None,
                    pregnant: bool = False, patient_name: str = "",
                    patient_id: int = None) -> dict:
    """
    Parse free-text lab results and return interpretations.
    Tries to extract test-name: result pairs from unstructured text.
    Falls back to treating the entire text as a single result if parsing fails.
    """
    text = text.strip()
    if not text:
        return {"error": "No text provided", "results": [], "summary": "No input to interpret."}

    lines = text.split("\n")
    extracted = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        for sep in [":", "=", "\t", "–", "-"]:
            if sep in line:
                parts = line.split(sep, 1)
                test_name = parts[0].strip()
                result_val = parts[1].strip()
                if test_name and result_val:
                    extracted.append({"test": test_name, "result": result_val})
                    break

    if not extracted:
        extracted.append({"test": "Free Text Result", "result": text})

    metadata = {"patient_id": patient_id} if patient_id else None
    interpretations = []
    flags = []
    for pair in extracted:
        ir = interpret_result(pair["test"], pair["result"], gender, age, pregnant, metadata)
        interpretations.append(asdict(ir))
        flags.append(ir.flag)

    summary = _batch_summary(flags, patient_name)
    return {
        "patient": patient_name or "Unknown",
        "gender": gender,
        "age": age,
        "pregnant": pregnant,
        "raw_text": text,
        "parsed_tests": extracted,
        "results": interpretations,
        "summary": summary,
        "total_tests": len(extracted),
        "abnormal_count": sum(1 for f in flags if f != "normal" and f != "interpret"),
    }
