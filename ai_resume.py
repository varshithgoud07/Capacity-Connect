import io
import requests
import os
import json
from google import genai
from pypdf import PdfReader
from dotenv import load_dotenv
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def extract_resume_text(resume_url):
    """
    Downloads a PDF resume from Cloudinary
    and extracts all text from it.
    """

    response = requests.get(resume_url)

    if response.status_code != 200:
        return None

    pdf_file = io.BytesIO(response.content)

    reader = PdfReader(pdf_file)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text

from google.genai.errors import ClientError
import json

def analyze_resume(resume_text):
    prompt = f"""
    ...
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return json.loads(response.text)

    except ClientError:
        return {
            "score": 0,
            "ats_score": 0,
            "strengths": [],
            "missing_skills": [],
            "recommended_roles": [],
            "suggestions": [
                "Gemini API quota exceeded. Please try again later."
            ]
        }