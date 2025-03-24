import csv
import re
import os
import logging
from pathlib import Path
import argparse

# Constants
SEVERITY_LEVELS = ["[Critical]", "[High]", "[Medium]", "[Low]", "[Info]"]

# Paths
SUMMARY_DIR = "./output"
SUMMARY_FILE = "summary_report.md"
CSV_OUTPUT = "summary_report.csv"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_findings(summary_path):
    """Extract findings from the summary report."""
    if not summary_path.exists():
        logging.error(f"❌ Summary report not found at {summary_path}")
        return []

    findings = []
    current_contract = None
    with open(summary_path, "r") as f:
        for line in f:
            if line.startswith("## "):
                current_contract = line.strip("# \n")
            elif any(sev in line for sev in SEVERITY_LEVELS):
                severity_match = re.search(r"\[(.*?)\]", line)
                severity = severity_match.group(1) if severity_match else "Unknown"
                findings.append((current_contract, severity, line.strip()))

    return findings

def write_csv(findings, csv_path):
    """Write findings to a CSV file."""
    try:
        with open(csv_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Contract", "Severity", "Issue"])
            for contract, severity, issue in findings:
                writer.writerow([contract, severity, issue])
        logging.info(f"✅ CSV saved: {csv_path}")
    except Exception as e:
        logging.error(f"Error writing CSV: {e}")

def main(summary_dir, summary_file, csv_output):
    """Main function to extract findings and write to CSV."""
    summary_path = Path(summary_dir) / summary_file
    findings = extract_findings(summary_path)
    if findings:
        csv_path = Path(summary_dir) / csv_output
        write_csv(findings, csv_path)
    else:
        logging.warning("⚠️ No findings extracted.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate CSV summary from audit findings.")
    parser.add_argument("--summary-dir", type=str, default=SUMMARY_DIR, help="Directory containing the summary report.")
    parser.add_argument("--summary-file", type=str, default=SUMMARY_FILE, help="Summary report file name.")
    parser.add_argument("--csv-output", type=str, default=CSV_OUTPUT, help="CSV output file name.")
    args = parser.parse_args()

    main(args.summary_dir, args.summary_file, args.csv_output)