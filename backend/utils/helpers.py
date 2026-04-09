import json
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from utils.logger_config import get_logger
import shutil
import re
from utils.exceptions import LLMError

logger = get_logger(__name__)

def raw_script_maker(script_file, event, celebrant_image, base_celebrant_source="slides/base_celebrant.png"):
	"""
	Update the script JSON with the new celebrant, organized by generation (eldest → youngest).
	"""
	try:
		script_file = Path(script_file)
		celebrant_image = Path(celebrant_image)
		pics_dir = celebrant_image.parent  

		# Step 2: Parse image filename to extract day, generation, name
		base = celebrant_image.stem
		gen, day, month, *name_parts = base.split("_")
		generation = gen.replace("gen", "")
		name = " ".join(name_parts)
		day = int(day)
		suffix = "th" if 11 <= day <= 13 else {1:"st",2:"nd",3:"rd"}.get(day % 10, "th")
		entry = f"{day}{suffix} - {name}"

		# Step 3: Load JSON
		if script_file.exists():
			data = json.loads(script_file.read_text(encoding="utf-8"))
		else:
			data = {}

		# Step 4: Organize by generation for birthdays
		if event.lower().startswith("birth"):
			birthdays = data.setdefault("Birthdays", {})
			lst = birthdays.setdefault(generation, [])
		else:
			lst = data.setdefault(event, [])

		# Step 5: Add entry if missing
		if entry not in lst:
			lst.append(entry)

		# Step 6: Sort each generation's list by day
		lst_sorted = sorted(lst, key=lambda x: int(re.findall(r"\d+", x)[0]))
		if event.lower().startswith("birth"):
			birthdays[generation] = lst_sorted
		else:
			data[event] = lst_sorted

		# Step 7: Sort generations (eldest → youngest)
		if event.lower().startswith("birth"):
			sorted_birthdays = dict(sorted(birthdays.items(), key=lambda x: int(x[0])))
			data["Birthdays"] = sorted_birthdays

		# Step 8: Save JSON
		script_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
		return {"message": f"script updated successfully in {script_file}"}

	except Exception as e:
		logger.exception("Error updating script: %s", str(e))
		raise Exception("Failed to update script") from e
		
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
		logger.exception("Error converting JSON to text:%s", str(e))
		raise Exception("Failed to convert JSON to text") from e

def validate_cend_count(ai_text, celebrants_no):
	cend_no = len(re.findall("<cend>", ai_text))
	logger.debug(f"<cend> markers = {cend_no}")
	return cend_no == celebrants_no

def generate_ai_script(month, retries=10):

	from pathlib import Path

	load_dotenv()
	api_key = os.getenv("GEMINI_API_KEY")

	if not api_key:
		return {"error": "Missing AI API key"}

	client = genai.Client(api_key=api_key)

	try:
		# Paths
		script_json = Path("./data") / month / "script.json"
		with open(script_json, "r") as f:
			script_txt = json.load(f)

		# Convert JSON → plain text
		# text_data = json_to_script_txt(script_json, script_txt)
		# if isinstance(text_data, dict) and "Error" in text_data:
		# 	return text_data
		celebrants_file = Path("./data") / month / "script.json"
		with open(celebrants_file, "r") as f:
			celebrants = json.load(f)
		for v in celebrants.values():
			celebrants_no = sum((len(g))for g in v.values())
		logger.debug(f"Number of celebrants for {month} is {celebrants_no}")
		# Prompt for structured narration with markers
		prompt = f"""
		You are a family celebration narrator. Create a warm, conversational script announcing birthdays and anniversaries for {month}.

		CRITICAL RULES:
		1. End each celebrant line with <cend>.
		2. Use the actual names and dates from the data provided—never use placeholders like "our dear family member".
		3. Every person must be announced with their full name, exact date, and generation context where available (e.g., "daughter of", "grandson of").
		4. Format each birthday line as: "On [Day], we celebrate [Full Name]".
		5. Format each anniversary/wedding line as: "On [Month] [Day], we celebrate [Full Name] and [Partner Name]".

		STRUCTURE:
		- Opening: One warm sentence welcoming the month and the celebrations ahead.
		- For each generation present in the data:
			* Include a brief sentence introducing the generation in quotes.
			* List each person with their date, full name, and relationship context.
			* Use natural variety in phrasing: "we celebrate", "best wishes go to", "we honor", "birthday cheers go to", "we cheer for".
		- Closing: Include a section celebrating anniversaries/weddings with the couple's names and date.
		- 

		STYLE REQUIREMENTS:
		- Write in flowing paragraphs, not bullet points.
		- Use conversational, spoken-word friendly language.
		- Include emotional warmth while keeping it natural.
		- Do NOT include stage directions or instructions.
		- Do NOT use generic placeholders—mention every actual name and date from the data.

		DATA TO PROCESS:
		the layout is:
		{{
			"Birthdays": {{
				"generation": [
					"date - name"
				]
			}},
			"Weddings": {{
				"generation": [
					"date - couple names"
				]
			}}
		}}
		A MUST RULE! the number of <cend> texts  must equal to the number of  celebrants, so in this case, the text should have a total of {celebrants_no} <cend>
		{script_txt}

		Generate the script now, ensuring every single person and couple in the data is mentioned with their exact date and generation context.
		"""

		# Generate AI script
		response = client.models.generate_content(
			model="gemini-2.5-flash-lite", #gemini-2.5-flash-lite-preview-09-2025",
			contents=prompt
		)



		# retry atleast 3 times if <cend> markers are not same number as participants
		if validate_cend_count(response.text, celebrants_no=celebrants_no):
			# Save AI narration
			ai_script_path = Path("./data") / month / "ai_script.txt"
			ai_script_path.write_text(response.text, encoding="utf-8")

			return {
			"is_successful": True,
			"message": "AI script created successfully",
			"script_path": str(ai_script_path),
			"ai_response": response.text
		}
		
		if retries <= 0:
			logger.info("Max LLM retries reached")
			return {"is_successful": False, "ai_text": None}

		return generate_ai_script(month, retries - 1)

	except Exception as e:
		logger.error("Error creating AI script: %s", str(e), exc_info=True)
		if isinstance(e, LLMError):
			raise
		raise LLMError(f"Failed to create AI script: {str(e)}") from e