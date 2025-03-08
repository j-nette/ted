from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key='KEY')

# This is the user input we're getting from somewhere else
user_speech = "" # Change to test


# Update the contents variable into a usable string
prompt_modifier = ""

response = client.models.generate_content(
    model="gemini-2.0-flash", contents=prompt_modifier+user_speech)

print(response.text)