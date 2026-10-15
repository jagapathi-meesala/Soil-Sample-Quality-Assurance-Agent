from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ["agent.yaml","SOUL.md","RULES.md","DUTIES.md","AGENTS.md","EXPLAINABILITY.md","README.md","requirements.txt","pytest.ini","core/__init__.py","core/qa.py","core/cli.py","tools/validate-sample-records.yaml","tools/check-lab-results.yaml","tools/generate-qa-report.yaml","skills/sample-intake/SKILL.md","skills/lab-result-validation/SKILL.md","skills/qa-reporting/SKILL.md","tests/test_qa.py","examples/soil_case.json"]
missing = [p for p in REQUIRED if not (ROOT / p).is_file()]
manifest = yaml.safe_load((ROOT / "agent.yaml").read_text())
assert manifest["name"] == "soil-sample-quality-assurance-agent"
assert not missing, f"Missing required files: {missing}"
print(f"PASS: all {len(REQUIRED)}/{len(REQUIRED)} required files present")
print("PASS: manifest name and structure checked")
