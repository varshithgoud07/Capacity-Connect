import io
import requests
import os
import json
from google import genai
from pypdf import PdfReader

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

def analyze_resume(resume_text):

    prompt = f"""
You are an expert ATS Resume Analyzer.

Analyze the following resume.

Return ONLY valid JSON.

Do NOT add markdown.
Do NOT add explanation.
Do NOT use ```json.
Return only the JSON object.

The JSON format must be:

{{
    "score": 0,
    "ats_score": 0,
    "strengths": [],
    "missing_skills": [],
    "recommended_roles": [],
    "suggestions": []
}}

Resume:

{resume_text}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return json.loads(response.text)