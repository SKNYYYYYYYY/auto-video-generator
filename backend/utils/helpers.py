import json
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from elevenlabs.client import ElevenLabs
import os
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

    from pathlib import Path

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {"error": "Missing AI API key"}

    client = genai.Client(api_key=api_key)

    try:
        # Paths
        script_json = Path("./data") / month / "script.json"
        script_txt = script_json.with_suffix(".txt")

        # Convert JSON → plain text
        text_data = json_to_script_txt(script_json, script_txt)
        if isinstance(text_data, dict) and "Error" in text_data:
            return text_data

        # Prompt for structured narration with markers
        prompt = f"""
        You are a family celebration narrator. Create a warm, conversational script announcing birthdays and anniversaries for {month}.

        CRITICAL RULES:
        1. Use ACTUAL NAMES AND DATES from the data provided - never use placeholders like "our dear family member" or "our precious little one"
        2. Every person must be announced with their full name and exact date
        3. Format each birthday as: "On [Month] [Day], we celebrate [Full Name]"
        4. Add generation context where provided (e.g., "daughter of", "son of", "grandson of")
        5. End each celebrant line with <cend>

        STRUCTURE:
        - Opening: One warm sentence welcoming the month and the celebrations ahead
        - For each generation present in the data:
        * Brief transitional sentence introducing the generation in quotes
        * List each person with their date, full name, and relationship context
        * Use natural variety: "we celebrate", "best wishes go to", "we honor", "birthday cheers go to", "we cheer for"
        - Closing: If anniversaries/weddings exist, add a final section celebrating couples with date and both names

        STYLE REQUIREMENTS:
        - Write in flowing paragraphs, NOT bullet points
        - Use conversational, spoken-word friendly language
        - Include emotional warmth but keep it natural
        - NO stage directions or instructions
        - NO generic placeholders - use every actual name provided

        DATA TO PROCESS:
        {text_data}

        Generate the script now, ensuring every single person in the data is mentioned by name with their specific date.
        """

        # Generate AI script
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-09-2025",
            contents=prompt
        )

        # Save AI narration
        ai_script_path = Path("./data") / month / "ai_script.txt"
        ai_script_path.write_text(response.text, encoding="utf-8")

        return {
            "message": "AI script created successfully",
            "script_path": str(ai_script_path),
            "ai_response": response.text
        }

    except Exception as e:
        return {"Error creating AI script": str(e)}

def extract_anchors_and_clean_text(text, window=3):
    anchors = []
    def replacer(match):
        before = match.group(1)
        words = before.split()
        anchor = " ".join(words[-window:])
        anchors.append(anchor)
        return before
    clean_text = re.sub(
        r"(.*?)(<cend>)",
        replacer,
        text,
        flags = re.DOTALL
    )
    return clean_text, anchors

def text_to_speech(cleaned_voiceover):
    client = ElevenLabs(
        api_key=os.getenv("ELEVENLABS_API_KEY")
    )
    try:
        audio  = client.text_to_speech.convert(
            text=cleaned_voiceover,
            voice_id="kPzsL2i3teMYv0FxEYQ6",
            model_id="eleven_flash_v2_5",
            output_format="mp3_44100_128",
        )

        with open("output.mp3", "wb") as f:
            for chunk in audio:
                f.write(chunk)

        return {"message": "Audio saved to output.mp3"}
    except Exception as e:
        return {"Error generating TTS audio": str(e)}