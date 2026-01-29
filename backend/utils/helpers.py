import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import re

def raw_script_maker(script_file, event, celebrant_image):
    try:
        script_file = Path(script_file)
        
        #  Parse filename 
        base = Path(celebrant_image).stem
        gen, day, month, *name_parts = base.split("_")
        generation = gen.replace("gen", "")
        name = " ".join(name_parts)

        # Ordinal date
        day = int(day)
        suffix = "th" if 11 <= day <= 13 else {1:"st",2:"nd",3:"rd"}.get(day % 10, "th")
        entry = f"{day}{suffix} - {name}"

        #  Load existing JSON 
        if script_file.exists():
            data = json.loads(script_file.read_text(encoding="utf-8"))
        else:
            data = {}

        #  Insert entry 
        if event.lower() == "birthdays":
            if "Birthdays" not in data:
                data["Birthdays"] = {}
            if generation not in data["Birthdays"]:
                data["Birthdays"][generation] = []
            if entry not in data["Birthdays"][generation]:
                data["Birthdays"][generation].append(entry)
                # Sort by day
                data["Birthdays"][generation].sort(key=lambda x: int(re.findall(r"\d+", x)[0]))
        else:
            # Wedding or any other flat event
            if event not in data:
                data[event] = []
            if entry not in data[event]:
                data[event].append(entry)
                data[event].sort(key=lambda x: int(re.findall(r"\d+", x)[0]))

        #  Save JSON 
        script_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return {"message": f"script updated successfully in {script_file}"}
    except Exception as e:
        return {"Error updating script": str(e)}

import json
from pathlib import Path

def json_to_script_txt(json_file, txt_file):
    try:
        json_file = Path(json_file)
        txt_file = Path(txt_file)

        if not json_file.exists():
            raise FileNotFoundError(f"{json_file} does not exist")

        data = json.loads(json_file.read_text(encoding="utf-8"))
        lines = []

        # Handle Birthdays
        birthdays = data.get("Birthdays", {})
        if birthdays:
            for gen in sorted(birthdays.keys(), key=lambda x: int(re.findall(r"\d+", x)[0])):
                lines.append("Birthdays")
                lines.append(f"{gen} generation")
                for entry in birthdays[gen]:
                    lines.append(entry)
                lines.append("") 

        # Handle other events (e.g., Wedding)
        for event, entries in data.items():
            if event == "Birthdays":
                continue
            if entries:
                lines.append(event.capitalize())
                for entry in entries:
                    lines.append(entry)
                lines.append("") 

        # Save to script.txt
        text_content = "\n".join(lines)
        txt_file.write_text(text_content, encoding="utf-8")
        return text_content

    except Exception as e:
        
        return {"Error converting JSON to text": str(e)}

def ai_script_maker(month):
    from dotenv import load_dotenv
    import os

    load_dotenv() 
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    try:

        script_json = Path("./data") / month / "script.json"
        script_txt =  script_json.with_suffix(".txt")
        data = json_to_script_txt(script_json, script_txt)
        
        prompt = f"Create a heartfelt video script for the following events in {month}:\n\n"

        ai_response = client.responses.create(
            model="gpt-4",
            prompt=prompt + data,
            # max_tokens=1500,
            temperature=0.7
        )
        print(ai_response)
    except Exception as e:
        return {"Error creating AI script": str(e)}