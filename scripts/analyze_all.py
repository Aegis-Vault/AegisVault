import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI

# Load API key from .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Paths
CONTRACT_DIR = "../contracts"
PROMPT_TEMPLATE = "./prompts/clarity_audit.txt"
OUTPUT_DIR = "./output"
Path(OUTPUT_DIR).mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_prompt_template():
    """Load the prompt template from a file."""
    try:
        with open(PROMPT_TEMPLATE, "r") as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"Prompt template file not found: {PROMPT_TEMPLATE}")
        raise

def analyze_contract(file_path, template):
    """Analyze a contract using the OpenAI API."""
    try:
        with open(file_path, "r") as f:
            code = f.read()
        prompt = template.replace("{{code}}", code)

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error analyzing contract {file_path}: {e}")
        return None

def save_result(file_name, result):
    """Save the analysis result to a file."""
    out_path = Path(OUTPUT_DIR) / (file_name + ".md")
    try:
        with open(out_path, "w") as f:
            f.write(result)
        logging.info(f"✅ Saved: {out_path}")
    except Exception as e:
        logging.error(f"Error saving result for {file_name}: {e}")

def main():
    """Main function to load the template and analyze all contracts."""
    template = load_prompt_template()
    contract_files = list(Path(CONTRACT_DIR).glob("*.clar"))

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(analyze_contract, file, template): file for file in contract_files}
        for future in as_completed(futures):
            file = futures[future]
            try:
                result = future.result()
                if result:
                    save_result(file.stem, result)
            except Exception as e:
                logging.error(f"Error processing file {file}: {e}")

if __name__ == "__main__":
    main()