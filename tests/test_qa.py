import json
from pathlib import Path
from core.qa import build_report, validate_samples, validate_results

EXAMPLE = Path(__file__).parents[1] / "examples" / "soil_case.json"

def test_example_flags_review_items():
    report = build_report(json.loads(EXAMPLE.read_text()))
    assert report["status"] == "REVIEW_REQUIRED"
    assert report["finding_count"] > 0

def test_complete_sample_has_no_sample_findings():
    sample = {"sample_id":"S1","collection_date":"2026-01-01","location":"A","sampler":"X","container":"jar","preservation":"cool","chain_of_custody":"C1"}
    assert validate_samples([sample]) == []

def test_duplicate_sample_id_flagged():
    s = {"sample_id":"S1","collection_date":"2026-01-01","location":"A","sampler":"X","container":"jar","preservation":"cool","chain_of_custody":"C1"}
    assert "DUPLICATE_SAMPLE_ID" in {f["code"] for f in validate_samples([s, s])}

def test_invalid_date_flagged():
    s = {"sample_id":"S1","collection_date":"yesterday","location":"A","sampler":"X","container":"jar","preservation":"cool","chain_of_custody":"C1"}
    assert "INVALID_COLLECTION_DATE" in {f["code"] for f in validate_samples([s])}

def test_unknown_result_reference_flagged():
    fs = validate_results([{"sample_id":"X","analyte":"pH","value":7,"unit":"pH"}], [], {})
    assert "UNKNOWN_SAMPLE_REFERENCE" in {f["code"] for f in fs}

def test_configured_bound_flagged():
    s = {"sample_id":"S1"}
    fs = validate_results([{"sample_id":"S1","analyte":"Lead","value":20,"unit":"mg/kg"}], [s], {"Lead":{"max":10}})
    assert "ABOVE_CONFIGURED_BOUND" in {f["code"] for f in fs}

def test_duplicate_analyte_flagged():
    s = {"sample_id":"S1"}
    row = {"sample_id":"S1","analyte":"pH","value":7,"unit":"pH"}
    fs = validate_results([row, row], [s])
    assert "DUPLICATE_ANALYTE_RESULT" in {f["code"] for f in fs}

def test_bad_top_level_rejected():
    try:
        build_report([])
    except ValueError:
        pass
    else:
        assert False, "Expected ValueError"
