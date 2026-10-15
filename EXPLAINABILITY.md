# Explainability

## Inputs
Sample metadata (`sample_id`, `collection_date`, `location`, `sampler`, `container`, `preservation`, `chain_of_custody`) and result fields (`sample_id`, `analyte`, `value`, `unit`). Optional per-analyte `min` and `max` bounds are user-supplied screening thresholds.

## Decision
The validator checks required metadata, duplicate sample IDs, parseable dates, result references, duplicate analytes per sample, numeric values, units, and optional configured bounds. It does not determine whether a soil result is environmentally safe.

## Limits
No regulatory standard, analytical method, sampling plan, holding-time table, or lab accreditation status is inferred. A range flag means only that a user-configured bound was crossed. Date checks do not establish sample preservation or holding-time compliance.

## Tool: validate-sample-records
### Inputs and Data Sources
A list of sample records supplied by the user.
### Decision and Reasoning
Check required metadata, duplicate IDs, and date format.
### Outputs and Evidence
Record-level findings identify sample ID, field, reason, and severity.
### Limits and Constraints
No geospatial validation or custody-document authentication.
### Failure Handling
Malformed records produce explicit findings rather than being silently dropped.
### Human Review
Confirm missing metadata against field sheets and custody records.

## Tool: check-lab-results
### Inputs and Data Sources
Laboratory result rows and optional configured bounds.
### Decision and Reasoning
Check references, analyte uniqueness, numeric values, units, and supplied bounds.
### Outputs and Evidence
Each flag includes the result row context and the check that failed.
### Limits and Constraints
No analytical-method validation or regulatory interpretation.
### Failure Handling
Missing or nonnumeric values are flagged.
### Human Review
Compare flagged rows with signed laboratory reports and method-specific QA/QC.

## Tool: generate-qa-report
### Inputs and Data Sources
Sample records, result rows, and generated findings.
### Decision and Reasoning
Aggregate finding counts and overall review status.
### Outputs and Evidence
JSON report containing findings, counts, and limitations.
### Limits and Constraints
A clean report means only that these programmed checks found no issue.
### Failure Handling
Invalid top-level input returns a clear error.
### Human Review
QA lead determines acceptance, resampling, reanalysis, or corrective action.
