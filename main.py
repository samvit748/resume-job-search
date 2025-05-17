import csv
from resumeMatcher.extract_resume import extract_text_from_pdf, extract_skills, detect_profile_type
from resumeMatcher.jobSearch import search_jobs_on_google  
from sentence_transformers import SentenceTransformer, util

# Load the model that helps in comparing text meanings
model = SentenceTransformer('all-MiniLM-L6-v2')

# Step 1: Read and extract info from the resume
resume_path = "Resume.pdf"
resume_text = extract_text_from_pdf(resume_path)
skills_from_resume = extract_skills(resume_text)
profile_type = detect_profile_type(resume_text)

print("\nSkills found in resume:", ", ".join(skills_from_resume))
print(f"Profile Type: {profile_type}")

# Convert resume text into a form that can be compared
resume_embedding = model.encode(resume_text, convert_to_tensor=True)

# Step 2: Ask user for skills to search jobs for
user_input = input("Enter some skills (comma-separated) to focus your job search:\n> ")
user_skills = [skill.strip().lower() for skill in user_input.split(",")]
resume_skills_lower = [skill.lower() for skill in skills_from_resume]

# Match skills from user input with skills in resume
common_skills = [skill for skill in resume_skills_lower if skill in user_skills]

if not common_skills:
    print("No matching skills found in resume. Showing general job results.")
    common_skills = resume_skills_lower[:3]
else:
    print("Searching jobs based on skills:", ", ".join(common_skills))

# Add extra keywords based on profile type
if profile_type == "Fresher":
    search_keywords = common_skills + ["fresher", "entry level"]
else:
    search_keywords = common_skills + ["experienced", "senior"]

print(f"Searching jobs using: {', '.join(search_keywords)}")

# Step 3: Get jobs from Google using SerpAPI
api_key = input("\nEnter your SerpAPI key: ")
location = input("Preferred job location: ")

job_results = search_jobs_on_google(search_keywords, api_key, location)

if not job_results:
    print("Sorry, no jobs found.")
    exit()

print("\nSample job results:")
for job in job_results[:3]:
    print(f"{job['title']} ➡ {job['link']}")

# Step 4: Rank jobs based on how well they match the resume
def rank_jobs_by_similarity(jobs, resume_embedding):
    results = []
    for job in jobs:
        job_text = f"{job.get('title', '')} {job.get('company', '')} {job.get('location', '')}"
        job_embedding = model.encode(job_text, convert_to_tensor=True)
        similarity = util.cos_sim(resume_embedding, job_embedding).item()
        results.append((job, similarity))
    results.sort(key=lambda x: x[1], reverse=True)
    return results

sorted_job_results = rank_jobs_by_similarity(job_results, resume_embedding)

# Step 5: Show and save top matching jobs
print("\nTop job matches:\n")

with open("job_results.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Job Title", "Company", "Location", "Link", "Skills Used", "Profile Type", "Match Score"])

    for i, (job, score) in enumerate(sorted_job_results[:10], start=1):
        title = job.get('title', 'N/A')
        company = job.get('company', 'N/A')
        loc = job.get('location', 'N/A')
        link = job.get('link', 'N/A')

        print(f"{i}. {title} at {company} ({loc}) — Match Score: {score:.3f}")
        print(f"   Apply here: {link}\n")

        writer.writerow([title, company, loc, link, ", ".join(common_skills), profile_type, f"{score:.3f}"])

print("Done! Job results saved in job_results.csv")
