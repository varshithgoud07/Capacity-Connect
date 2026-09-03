import io
import requests
import os
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