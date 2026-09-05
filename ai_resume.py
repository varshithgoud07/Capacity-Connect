import io
import os
import re
import json
import requests

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ClientError
from pypdf import PdfReader

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def extract_resume_text(resume_url):
    try:
        response = requests.get(resume_url, timeout=20)

        if response.status_code != 200:
            return ""

        pdf = PdfReader(io.BytesIO(response.content))

        text = ""

        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        return text.strip()

    except Exception as e:
        print("PDF Extraction Error:", e)
        return ""
def offline_resume_analysis(text):

    text_lower = text.lower()

    skills = [
        "python","java","c","c++","javascript","html","css",
        "sql","flask","django","react","node","git","github",
        "machine learning","ai","data structures","mongodb",
        "postgresql","aws","docker"
    ]

    found_skills = []

    for skill in skills:
        if skill in text_lower:
            found_skills.append(skill.title())

    score = 40 + min(len(found_skills) * 3, 40)

    strengths = []

    if found_skills:
        strengths.append("Technical skills identified")

    if "project" in text_lower:
        strengths.append("Projects included")

    if "intern" in text_lower:
        strengths.append("Internship experience found")

    if "github" in text_lower:
        strengths.append("GitHub profile included")

    if "linkedin" in text_lower:
        strengths.append("LinkedIn profile included")

    missing = []

    if "github" not in text_lower:
        missing.append("GitHub")

    if "linkedin" not in text_lower:
        missing.append("LinkedIn")

    if "project" not in text_lower:
        missing.append("Projects")

    if "intern" not in text_lower:
        missing.append("Internships")

    roles = []

    if "python" in text_lower:
        roles.append("Python Developer")

    if "java" in text_lower:
        roles.append("Java Developer")

    if "machine learning" in text_lower or "ai" in text_lower:
        roles.append("AI Engineer")

    if "react" in text_lower:
        roles.append("Frontend Developer")

    if not roles:
        roles.append("Software Engineer")

    return {
        "analysis_type": "Offline ATS Analysis",
        "score": score,
        "ats_score": score,
        "strengths": strengths,
        "missing_skills": missing,
        "recommended_roles": roles,
        "suggestions": [
            "Add measurable project achievements.",
            "Include GitHub and LinkedIn profile links.",
            "Tailor your resume to the job description.",
            "Use ATS-friendly keywords."
        ]
    }
def gemini_resume_analysis(resume_text):

    prompt = f"""
You are an ATS Resume Expert.

Analyze this resume and return ONLY valid JSON.

Format:

{{
    "score":0,
    "ats_score":0,
    "strengths":[],
    "missing_skills":[],
    "recommended_roles":[],
    "suggestions":[]
}}

Resume:

{resume_text}
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        text = response.text.strip()

        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()

        return json.loads(text)

    except Exception as e:
        print("Gemini Error:", e)
        return None
    
def merge_analysis(offline, ai):

    if ai is None:
        offline["analysis_type"] = "Offline ATS Analysis"
        return offline

    ai["analysis_type"] = "AI + ATS Analysis"

    return {
        "analysis_type": ai["analysis_type"],
        "score": ai.get("score", offline["score"]),
        "ats_score": ai.get("ats_score", offline["ats_score"]),
        "strengths": ai.get("strengths", offline["strengths"]),
        "missing_skills": ai.get("missing_skills", offline["missing_skills"]),
        "recommended_roles": ai.get("recommended_roles", offline["recommended_roles"]),
        "suggestions": ai.get("suggestions", offline["suggestions"])
    }


def analyze_resume(resume_text):

    if not resume_text or len(resume_text.strip()) == 0:
        return {
            "score": 0,
            "ats_score": 0,
            "strengths": [],
            "missing_skills": [],
            "recommended_roles": [],
            "suggestions": [
                "Resume is empty or could not be read."
            ]
        }

    offline = offline_resume_analysis(resume_text)

    ai = gemini_resume_analysis(resume_text)

    return merge_analysis(offline, ai)