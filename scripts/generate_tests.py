from openai import OpenAI
import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm

# Load API key from .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Paths
FINDINGS_FILE = "./scripts/output/findings.json"
TESTS_DIR = "./tests/auto"
TESTGEN_PROMPT = "./scripts/prompts/testgen_prompt.txt"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_testgen_prompt():
    """Load the test generation prompt from a file."""
    try:
        with open(TESTGEN_PROMPT, "r") as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"Prompt file not found: {TESTGEN_PROMPT}")
        raise

def generate_test(finding, prompt_template):
    """Generate a Clarinet test for a finding using the OpenAI API."""
    issue_description = finding.get("issue", "No issue description provided")
    contract_name = finding.get("contract", "unnamed") or "unnamed"
    prompt = prompt_template.replace("{{issue_description}}", issue_description)
    prompt = prompt.replace("{{contract_name}}", contract_name)

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        test_code = response.choices[0].message.content
        return test_code
    except Exception as e:
        logging.error(f"OpenAI error on {finding['issue']}: {e}")
        return None

def save_test(contract, test_code):
    """Save the generated test code to a file."""
    contract_name = (contract or "unnamed").replace("/", "_")
    issue_hash = abs(hash(test_code)) % 100000
    test_path = Path(TESTS_DIR) / f"test-{contract_name}-{issue_hash}.ts"
    try:
        with open(test_path, "w") as f:
            f.write(test_code)
        logging.info(f"✅ Test saved: {test_path}")
    except Exception as e:
        logging.error(f"Error saving test for {contract_name}: {e}")

def main():
    """Main function to generate tests for confirmed critical findings."""
    findings_path = Path(FINDINGS_FILE)
    if not findings_path.exists():
        logging.error(f"❌ Findings file not found at {findings_path}")
        return

    with open(findings_path, "r") as f:
        findings = json.load(f)

    prompt_template = load_testgen_prompt()
    confirmed_criticals = [f for f in findings if f["confirmed"] and f["severity"] == "Critical"]

    if not confirmed_criticals:
        logging.warning("⚠️ No confirmed critical findings.")
        return

    Path(TESTS_DIR).mkdir(parents=True, exist_ok=True)
    for finding in tqdm(confirmed_criticals):
        test_code = generate_test(finding, prompt_template)
        if test_code:
            save_test(finding.get("contract"), test_code)

if __name__ == "__main__":
    main()