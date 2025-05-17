import pdfplumber
import spacy

# Load the English NLP model from SpaCy
nlp = spacy.load("en_core_web_sm")

# Predefined list of common technical skills
skills_list = [
    "python", "java", "machine learning", "deep learning",
    "django", "flask", "html", "css", "javascript",
    "sql", "data analysis", "tensorflow", "pandas",
    "numpy", "nlp", "git", "linux", "api", "react",
    "artificial intelligence"
]

def extract_text_from_pdf(pdf_path):
    
    full_text = ''
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + '\n'
    return full_text

def extract_skills(resume_text):
    
    resume_text = resume_text.lower()
    found = []
    for skill in skills_list:
        if skill in resume_text:
            found.append(skill)
    return list(set(found))  # Removing duplicates

def detect_profile_type(resume_text):
    
    resume_text = resume_text.lower()

    if "fresher" in resume_text or "intern" in resume_text or "no experience" in resume_text:
        return "Fresher"
    elif "experience" in resume_text or "worked at" in resume_text or "years" in resume_text:
        return "Experienced"
    else:
        return "Unknown"
