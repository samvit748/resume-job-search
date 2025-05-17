import csv
from resumeMatcher.extract_resume import extract_text_from_pdf, extract_skills, detect_profile_type
from resumeMatcher.jobSearch import search_jobs_on_google  
from sentence_transformers import SentenceTransformer, util

# --- Load the semantic embedding model ---
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')


resume_file = "Resume.pdf"
text_from_resume = extract_text_from_pdf(resume_file)
extracted_skills = extract_skills(text_from_resume)
profile_category = detect_profile_type(text_from_resume)

print("\n Extracted Skills:", ", ".join(extracted_skills))
print(f"🔍 Profile identified as: {profile_category}")


resume_vector = embedding_model.encode(text_from_resume, convert_to_tensor=True)


skills_input = input("Enter skills (comma-separated) to tailor your job search:\n> ")

# Normalize skills for comparison (lowercase)
extracted_skills_lower = [skill.lower() for skill in extracted_skills]
input_skills = [skill.strip().lower() for skill in skills_input.split(",")]

# Determine the skills to focus on by intersecting user input and resume skills
target_skills = [skill for skill in extracted_skills_lower if skill in input_skills]

if not target_skills:
    print("The skills you entered weren't found in your resume. Displaying general matches instead.")
    target_skills = extracted_skills_lower[:3]  # default to top 3 skills
else:
    print("Concentrating job search on:", ", ".join(target_skills))

 
if profile_category == "Fresher":
    keywords = target_skills + ["fresher", "entry level"]
else:
    keywords = target_skills + ["experienced", "senior"]

print(f"Searching jobs using keywords: {', '.join(keywords)}")


api_key = input("\n Please provide your SerpAPI key: ")
job_location = input("Enter preferred job location: ")
jobs_found = search_jobs_on_google(keywords, api_key, job_location)

if not jobs_found:
    print("No jobs were found matching your criteria.")
    exit()

print("\n Here are a few sample job links for your reference:")
for job in jobs_found[:3]:
    print(f"{job['title']} ➡ {job['link']}")

# --- Rank jobs based on semantic similarity to resume ---
def get_jobs_ranked_by_similarity(job_list, resume_vec):
    ranked_jobs = []
    for job in job_list:
        combined_text = f"{job.get('title', '')} {job.get('company', '')} {job.get('location', '')}"
        job_vec = embedding_model.encode(combined_text, convert_to_tensor=True)
        sim_score = util.cos_sim(resume_vec, job_vec).item()
        ranked_jobs.append((job, sim_score))
    ranked_jobs.sort(key=lambda x: x[1], reverse=True)
    return ranked_jobs

sorted_jobs = get_jobs_ranked_by_similarity(jobs_found, resume_vector)

# --- Output top matches and save to CSV ---
print("\n Top job matches based on semantic similarity:\n")

with open("job_results.csv", "w", newline="", encoding="utf-8") as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["Job Title", "Company", "Location", "Application Link", "Matched Skills", "Profile Type", "Similarity Score"])

    for idx, (job, similarity) in enumerate(sorted_jobs[:10], 1):
        job_title = job.get('title', 'N/A')
        company_name = job.get('company', 'N/A')
        job_loc = job.get('location', 'N/A')
        apply_url = job.get('link', 'N/A')

        print(f"{idx}. {job_title} at {company_name} ({job_loc}) — Similarity: {similarity:.3f}")
        print(f"   Apply here: {apply_url}\n")

        csv_writer.writerow([job_title, company_name, job_loc, apply_url, ", ".join(target_skills), profile_category, f"{similarity:.3f}"])

print("Job search results have been saved to job_results.csv")
