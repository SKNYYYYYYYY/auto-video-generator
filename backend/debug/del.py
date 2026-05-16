from google import genai

def llm(prompt):
    client = genai.Client(api_key="AIzaSyCLiKtm7_Exc-iFIFzFrlCijMk2E37oNjM")
    response = client.models.generate_content(
      model="gemini-2.5-pro", #gemini-2.5-flash-lite-preview-09-2025
      contents=prompt
    )

    # print("List of models that support generateContent:\n")
    # for m in client.models.list():
    #     for action in m.supported_actions:
    #         if action == "generateContent":
    #             print(m.name)
    return response

response = llm("")
print(response)
month = "April"
celebrants_no = 5
script_txt = {
  "Birthdays": {
    "2": [
      "20th - Gertrude Katunge Marisin",
      "23rd - Richard Marisin "
    ],
    "3": [
      "8th - Caren Chepkemoi Mackenzie"
    ],
    "4": [
      "0th - Jayson Kiprop",
      "14th - Ryan Kiplangat"
    ]
  }
}
global prompt 
prompt = f"""
		You are a family celebration narrator. Create a warm, conversational script announcing birthdays and anniversaries for {month}.

		CRITICAL RULES:
		1. End each celebrant line with <cend>.
		2. Use the actual names and dates from the data provided—never use placeholders like "our dear family member".
		3. Every person must be announced with their full name, exact date, and relation context where available (e.g., "daughter of", "grandson of").
		4. Format each birthday line as: "On [Day], we celebrate [Full Name]".
		5. Format each anniversary/wedding line as: "On [Day], we celebrate [Full Name] and [Partner Name]".

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

		"""

# ======================= Background image layout =======================================


# from PIL import Image, ImageDraw, ImageFont

# def debug_text(font_path, details):
#     # Create blank canvas (like your video frame)
#     img = Image.new("RGB", (1920, 1080), "black")
#     draw = ImageDraw.Draw(img)

#     # Fonts
#     name_font = ImageFont.truetype(font_path, 85)
#     rel_font = ImageFont.truetype(font_path, 40)

#     # Name
#     name = details["celebrant"][1]
#     name_pos = (1100, 380)

#     draw.text(name_pos, name, font=name_font, fill="#9b8a7c")

#     # Get name height (like name_text.h)
#     name_bbox = name_font.getbbox(name)
#     name_height = name_bbox[3] - name_bbox[1]

#     # Relation
#     relation = details["celebrant"][2] if len(details["celebrant"]) > 2 else None

#     if relation:
#         rel_pos = (1100, 380 + name_height + 20)  # spacing instead of 100 guess
#         draw.text(rel_pos, relation, font=rel_font, fill="#9b8a7c")

#     img.show()  # instant preview

# debug_text(font_path="DejaVuSerif.ttf", details= {'celebrant': ['2', 'Newton Kiprono', 's/o Paul']})