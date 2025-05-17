# utils/extract_resume.py

import pdfplumber
import spacy

# Load SpaCy NLP model
nlp = spacy.load("en_core_web_sm")

# A basic skills database (you can expand this)
SKILLS_DB = [
    "python", "java", "machine learning", "deep learning",
    "django", "flask", "html", "css", "javascript",
    "sql", "data analysis", "tensorflow", "pandas",
    "numpy", "nlp", "git", "linux", "api", "react", 
    "artificial intelligence"
]

# Function to read text from resume
def extract_text_from_pdf(pdf_path):
    text = ''
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + '\n'
    return text

# Function to extract skills using SpaCy and matching
def extract_skills(text):
    text = text.lower()
    skills_found = []

    for skill in SKILLS_DB:
        if skill in text:
            skills_found.append(skill)

    return list(set(skills_found))

# utils/extract_resume.py (add this function)

def detect_profile_type(text):
    text = text.lower()
    if "intern" in text or "fresher" in text or "no experience" in text:
        return "Fresher"
    elif "experience" in text or "worked at" in text or "years" in text:
        return "Experienced"
    else:
        return "Unknown"
