
import pdfplumber
import spacy

# Load the SpaCy English model once for NLP tasks
nlp = spacy.load("en_core_web_sm")


skills_list = [
    "python", "java", "machine learning", "deep learning",
    "django", "flask", "html", "css", "javascript",
    "sql", "data analysis", "tensorflow", "pandas",
    "numpy", "nlp", "git", "linux", "api", "react",
    "artificial intelligence"
]

def extract_text_from_pdf(pdf_path):
    """Reads and concatenates text content from all pages in a PDF file."""
    full_text = ''
    with pdfplumber.open(pdf_path) as pdf_file:
        for page in pdf_file.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + '\n'
    return full_text

def extract_skills(text):
    """Identifies known skills mentioned in the given text."""
    text_lower = text.lower()
    found_skills = [skill for skill in skills_list if skill in text_lower]
    # Remove duplicates if any and return
    return list(set(found_skills))

def detect_profile_type(text):
    
    text_lower = text.lower()
    if any(keyword in text_lower for keyword in ["intern", "fresher", "no experience"]):
        return "Fresher"
    elif any(keyword in text_lower for keyword in ["experience", "worked at", "years"]):
        return "Experienced"
    else:
        return "Unknown"
