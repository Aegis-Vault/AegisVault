from openai import OpenAI
import os
import json
import logging
import re
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm

# Load API key from .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Paths
SUMMARY_FILE = "./output/summary_report.md"
FINDINGS_FILE = "./output/findings.json"
CLARIFICATION_PROMPT = "./prompts/clarification_prompt.txt"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_clarification_prompt():
    """Load the clarification prompt from a file."""
    try:
        with open(CLARIFICATION_PROMPT, "r") as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"Prompt file not found: {CLARIFICATION_PROMPT}")
        raise

def extract_findings(summary_path):
    """Extract findings from the summary report."""
    if not summary_path.exists():
        logging.error(f"❌ Summary report not found at {summary_path}")
        return []

    findings = []
    current_contract = None
    with open(summary_path, "r") as f:
        for i, line in enumerate(f):
            if line.startswith("## "):
                current_contract = line.strip("# \n")
            elif any(sev in line for sev in ["[Critical]", "[High]"]):
                severity_match = re.search(r"\[(.*?)\]", line)
                severity = severity_match.group(1) if severity_match else "Unknown"
                findings.append({
                    "contract": current_contract,
                    "severity": severity,
                    "issue": line.strip(),
                    "source_line": i + 1  # Add this for traceability
                })

    return findings

def clarify_finding(finding, prompt_template):
    """Clarify the severity and feasibility of a finding using the OpenAI API."""
    prompt = prompt_template.replace("{{issue_description}}", finding["issue"])
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        clarification = response.choices[0].message.content
        clarification_lc = clarification.lower()
        finding["clarification"] = clarification
        finding["confirmed"] = any(kw in clarification_lc for kw in [
            "yes, this is feasible", 
            "clearly exploitable", 
            "can lead to"
        ])
        finding["confidence"] = "High" if "high confidence" in clarification_lc else "Medium"
    except Exception as e:
        logging.error(f"OpenAI error on {finding['issue']}: {e}")
        finding["clarification"] = "ERROR"
        finding["confirmed"] = False
        finding["confidence"] = "Unknown"

    return finding

def main():
    """Main function to extract findings, clarify them, and save to JSON."""
    summary_path = Path(SUMMARY_FILE)
    findings = extract_findings(summary_path)
    if not findings:
        logging.warning("⚠️ No findings extracted.")
        return

    prompt_template = load_clarification_prompt()
    clarified_findings = [clarify_finding(finding, prompt_template) for finding in tqdm(findings, desc="Clarifying")]

    # Attempt to attach matching contract filename
    for finding in clarified_findings:
        if not finding.get("contract"):
            continue
        filename_guess = finding["contract"].lower().replace(" ", "-") + ".clar"
        file_path = Path("../contracts") / filename_guess
        if file_path.exists():
            finding["contract_file"] = str(file_path)
        else:
            finding["contract_file"] = "NOT_FOUND"

    with open(FINDINGS_FILE, "w") as f:
        json.dump(clarified_findings, f, indent=4)
    logging.info(f"✅ Clarified findings saved: {FINDINGS_FILE}")

if __name__ == "__main__":
    main()