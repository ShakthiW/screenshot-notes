from openai import OpenAI

client = OpenAI()

prompt_template = """
You are a helpful assistant that summarizes notes from a screenshot.

Here are the notes:
{notes}
"""

system_prompt = """
    You are a helpful assistant that summarizes notes from a screenshot. 
    Screenshots are taken by the user and they have something related to the screenshot as the note. 
    So, please refactor and summarize the note and the Screenshot content for better clarity when searching for it later.
"""

def summarize_notes(notes, image_url):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_template.format(notes=notes)},
            {
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                },
            },
        ],
        max_completion_tokens=100
    )
    return response.choices[0].message.content
