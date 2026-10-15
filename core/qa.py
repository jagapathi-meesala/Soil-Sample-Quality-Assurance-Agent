from __future__ import annotations
from datetime import date
from typing import Any

REQUIRED_SAMPLE_FIELDS = ("sample_id", "collection_date", "location", "sampler", "container", "preservation", "chain_of_custody")

def _finding(severity: str, code: str, message: str, **evidence: Any) -> dict[str, Any]:
    return {"severity": severity, "code": code, "message": message, "evidence": evidence}

def validate_samples(samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    seen: set[str] = set()
    for i, sample in enumerate(samples):
        if not isinstance(sample, dict):
            findings.append(_finding("high", "INVALID_SAMPLE_RECORD", "Sample record must be an object.", row=i))
            continue
        sid = str(sample.get("sample_id", "")).strip()
        if not sid:
            findings.append(_finding("high", "MISSING_SAMPLE_ID", "Sample identifier is missing.", row=i))
        elif sid in seen:
            findings.append(_finding("high", "DUPLICATE_SAMPLE_ID", "Sample identifier is duplicated.", sample_id=sid, row=i))
        else:
            seen.add(sid)
        for field in REQUIRED_SAMPLE_FIELDS:
            if not str(sample.get(field, "")).strip():
                findings.append(_finding("medium", "MISSING_SAMPLE_METADATA", f"Required metadata field '{field}' is missing.", sample_id=sid or None, field=field, row=i))
        raw_date = str(sample.get("collection_date", "")).strip()
        if raw_date:
            try:
                date.fromisoformat(raw_date)
            except ValueError:
                findings.append(_finding("medium", "INVALID_COLLECTION_DATE", "Collection date must use ISO format YYYY-MM-DD.", sample_id=sid or None, value=raw_date, row=i))
    return findings

def validate_results(results: list[dict[str, Any]], samples: list[dict[str, Any]], bounds: dict[str, dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    known = {str(s.get("sample_id", "")).strip() for s in samples if isinstance(s, dict) and str(s.get("sample_id", "")).strip()}
    seen: set[tuple[str, str]] = set()
    bounds = bounds or {}
    for i, result in enumerate(results):
        if not isinstance(result, dict):
            findings.append(_finding("high", "INVALID_RESULT_RECORD", "Lab result must be an object.", row=i))
            continue
        sid, analyte = str(result.get("sample_id", "")).strip(), str(result.get("analyte", "")).strip()
        if not sid or sid not in known:
            findings.append(_finding("high", "UNKNOWN_SAMPLE_REFERENCE", "Result references a missing or unknown sample ID.", sample_id=sid or None, analyte=analyte or None, row=i))
        if not analyte:
            findings.append(_finding("medium", "MISSING_ANALYTE", "Analyte name is missing.", sample_id=sid or None, row=i))
        key = (sid, analyte.casefold())
        if sid and analyte and key in seen:
            findings.append(_finding("medium", "DUPLICATE_ANALYTE_RESULT", "Multiple result rows exist for the same sample and analyte.", sample_id=sid, analyte=analyte, row=i))
        seen.add(key)
        if result.get("value") is None or str(result.get("value", "")).strip() == "":
            findings.append(_finding("medium", "MISSING_RESULT_VALUE", "Laboratory result value is missing.", sample_id=sid or None, analyte=analyte or None, row=i))
            continue
        try:
            value = float(result["value"])
        except (TypeError, ValueError):
            findings.append(_finding("medium", "NON_NUMERIC_RESULT", "Result value is not numeric.", sample_id=sid or None, analyte=analyte or None, value=result.get("value"), row=i))
            continue
        if not str(result.get("unit", "")).strip():
            findings.append(_finding("medium", "MISSING_RESULT_UNIT", "Result unit is missing.", sample_id=sid or None, analyte=analyte or None, row=i))
        rule = bounds.get(analyte, {})
        if isinstance(rule, dict):
            if rule.get("min") is not None and value < float(rule["min"]):
                findings.append(_finding("medium", "BELOW_CONFIGURED_BOUND", "Result is below the user-configured minimum; verify applicability.", sample_id=sid, analyte=analyte, value=value, minimum=rule["min"], unit=result.get("unit")))
            if rule.get("max") is not None and value > float(rule["max"]):
                findings.append(_finding("medium", "ABOVE_CONFIGURED_BOUND", "Result exceeds the user-configured maximum; verify applicability.", sample_id=sid, analyte=analyte, value=value, maximum=rule["max"], unit=result.get("unit")))
    return findings

def build_report(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("Input must be a JSON object.")
    samples = data.get("samples", [])
    results = data.get("results", [])
    if not isinstance(samples, list) or not isinstance(results, list):
        raise ValueError("'samples' and 'results' must be lists.")
    findings = validate_samples(samples) + validate_results(results, samples, data.get("bounds", {}))
    counts = {level: sum(1 for f in findings if f["severity"] == level) for level in ("high", "medium", "low")}
    return {"agent": "soil-sample-quality-assurance-agent", "status": "REVIEW_REQUIRED" if findings else "NO_FLAGS_FROM_CONFIGURED_CHECKS", "sample_count": len(samples), "result_count": len(results), "finding_count": len(findings), "severity_counts": counts, "findings": findings, "limitations": ["Checks are limited to programmed metadata and consistency rules.", "Configured bounds are not regulatory determinations.", "A qualified reviewer must decide sample acceptance and follow-up."]}
