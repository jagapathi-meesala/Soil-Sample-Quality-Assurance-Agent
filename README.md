# Soil Sample Quality Assurance Agent

A small, explainable Python tool that screens soil sample metadata and lab-result records for completeness and consistency. It is designed to support QA review, not to certify soil safety or regulatory compliance.

## Checks
- Missing sample ID, collection date, location, sampler, container, preservation, or chain-of-custody reference
- Duplicate sample identifiers and unparseable collection dates
- Results referencing unknown samples, duplicate analytes, missing/non-numeric values, missing units, and optional user-configured min/max bounds
- JSON report with evidence-backed findings and summary counts

## Run
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python verification/readiness_audit.py
python -m core.cli examples/soil_case.json --output report.json
```

## Input
See `examples/soil_case.json`. Bounds are illustrative and must be configured for the relevant analytical method and project. The agent does not infer regulatory limits, authenticate chain-of-custody documents, or make sample disposition decisions.
