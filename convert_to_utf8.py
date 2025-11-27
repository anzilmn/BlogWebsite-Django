import json
import os

# File paths
script_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(script_dir, "backup.json")      # your original file
output_file = os.path.join(script_dir, "backup_clean.json")  # cleaned output

# Try reading JSON safely with utf-8-sig (handles BOM) and ignores errors
try:
    with open(input_file, "r", encoding="utf-8-sig", errors="ignore") as f:
        data = json.load(f)
except Exception as e:
    print(f"❌ Failed to read {input_file}: {e}")
    exit(1)

# Keep only objects that are NOT users.customuser
clean_data = [obj for obj in data if obj.get("model") != "users.customuser"]

# Save cleaned JSON in UTF-8
try:
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, indent=4, ensure_ascii=False)
    print(f"✅ Cleaned JSON saved as {output_file}")
except Exception as e:
    print(f"❌ Failed to save {output_file}: {e}")
    