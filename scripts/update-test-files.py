import os

# Directory containing the TypeScript test files
TEST_DIR = "./tests"

# Import statement to add
IMPORT_STATEMENT = "import { describe, it, expect, beforeEach } from 'vitest';\n"

def update_test_files():
    for root, _, files in os.walk(TEST_DIR):
        for file in files:
            if file.endswith(".test.ts"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    content = f.read()
                if IMPORT_STATEMENT not in content:
                    with open(file_path, "w") as f:
                        f.write(IMPORT_STATEMENT + content)
                    print(f"Updated {file_path}")

if __name__ == "__main__":
    update_test_files()