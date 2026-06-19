from groq import Groq
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_scenes(story, genre="thriller"):
    prompt = f"""Analyze this story and return ONLY a JSON object, no markdown, no explanation:
Story: "{story}"
Genre: {genre}
Return this exact structure:
{{
  "title": "movie title",
  "characters": ["name1", "name2"],
  "scenes": [
    {{
      "num": 1,
      "title": "scene title",
      "description": "2 sentence vivid description",
      "location": "location name",
      "type": "EXTERIOR or INTERIOR",
      "image_prompt": "detailed prompt for image generation, no text in image",
      "narration": "20 word voiceover line for this scene"
    }}
  ]
}}
Generate exactly 4 scenes. Return ONLY the JSON, nothing else. Never use double-quote characters inside any text value - use single quotes instead if quoting speech."""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    text = response.choices[0].message.content
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = _repair_and_parse(text)

    data["screenplay"] = _generate_screenplay(data)
    return data


def _generate_screenplay(data):
    scene_summaries = "\n".join(
        f"Scene {s['num']} ({s['type']}, {s['location']}): {s['description']}"
        for s in data["scenes"][:2]
    )
    screenplay_prompt = f"""Write the first 2 scenes of "{data['title']}" in proper screenplay format (INT./EXT., action lines, dialogue). Base it on:

{scene_summaries}

Return ONLY the screenplay text, nothing else - no JSON, no markdown."""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": screenplay_prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()


def _repair_and_parse(text):
    """
    Repairs common small-model JSON mistakes:
    - raw newlines/tabs/control chars inside string values
    - stray literal double-quotes inside string values
    """
    repaired_chars = []
    inside_string = False
    escape_next = False
    chars = list(text)
    i = 0
    n = len(chars)

    while i < n:
        char = chars[i]

        if escape_next:
            repaired_chars.append(char)
            escape_next = False
            i += 1
            continue

        if char == '\\':
            repaired_chars.append(char)
            escape_next = True
            i += 1
            continue

        if char == '"':
            if not inside_string:
                inside_string = True
                repaired_chars.append(char)
                i += 1
                continue
            else:
                j = i + 1
                while j < n and chars[j] in ' \t\n\r':
                    j += 1
                if j < n and chars[j] in ',:}]':
                    inside_string = False
                    repaired_chars.append(char)
                    i += 1
                    continue
                elif j >= n:
                    inside_string = False
                    repaired_chars.append(char)
                    i += 1
                    continue
                else:
                    repaired_chars.append('\\"')
                    i += 1
                    continue

        if inside_string and char == '\n':
            repaired_chars.append('\\n')
        elif inside_string and char == '\t':
            repaired_chars.append('\\t')
        elif inside_string and char == '\r':
            repaired_chars.append('\\r')
        elif inside_string and ord(char) < 0x20:
            pass
        else:
            repaired_chars.append(char)

        i += 1

    repaired_text = ''.join(repaired_chars)

    try:
        return json.loads(repaired_text)
    except json.JSONDecodeError as e:
        print("RAW RESPONSE FROM AI:")
        print(text)
        print("\nREPAIR ATTEMPT FAILED:", e)
        raise