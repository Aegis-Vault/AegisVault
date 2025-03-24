from pathlib import Path

OUTPUT_DIR = "./output"
SUMMARY_FILE = "./output/summary_report.md"
severities = ["[Critical]", "[High]"]

def extract_issues(file_path):
    issues = []
    with open(file_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            if any(sev in line for sev in severities):
                issues.append((file_path.name, line.strip()))
    return issues

def main():
    report = []
    output_path = Path(OUTPUT_DIR)
    for file in output_path.glob("*.md"):
        issues = extract_issues(file)
        if issues:
            report.append(f"### {file.name}")
            report += [f"- {issue[1]}" for issue in issues]
            report.append("")  # newline for spacing

    with open(SUMMARY_FILE, "w") as out:
        out.write("# 🔍 Audit Summary Report\n\n")
        out.write("\n".join(report))
    print(f"✅ Summary saved: {SUMMARY_FILE}")

if __name__ == "__main__":
    main()

[
    {
        "issue_description": "Example issue description"
    }
]