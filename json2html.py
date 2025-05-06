#!/usr/bin/env python3
import json
import pandas as pd
from pathlib import Path

def json_to_html_with_prompt():
    # Step 1: Prompt for paths
    try:
        input_path = Path(input("Enter path to your JSON file: ").strip())
        output_path = Path(input("Enter desired path for the output HTML file: ").strip())
    except Exception as e:
        print(f"❌ Invalid input: {e}")
        return

    # Step 2: Check that the JSON file exists
    if not input_path.is_file():
        print(f"❌ File not found: {input_path}")
        return

    # Step 3: Load the JSON
    try:
        with input_path.open(encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to read/parse JSON: {e}")
        return

    # Step 4: Normalize and write out HTML
    try:
        df = pd.json_normalize(data)
        df.to_html(
            output_path,
            index=False,
            border=1,
            classes=["table", "table-striped"]
        )
    except Exception as e:
        print(f"❌ Error converting to HTML: {e}")
        return

    print(f"✅ Successfully wrote HTML to: {output_path}")

if __name__ == "__main__":
    json_to_html_with_prompt()
