from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key='KEY')




response = client.models.generate_content(
    model="gemini-2.0-flash", contents="Explain how AI works"
)
print(response.text)