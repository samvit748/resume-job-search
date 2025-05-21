import csv
import time
from sentence_transformers import SentenceTransformer, util
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import concurrent.futures

# --- Basic list of common skills to look for ---
skills_list = [
    "python", "java", "machine learning", "deep learning",
    "django", "flask", "html", "css", "javascript",
    "sql", "data analysis", "tensorflow", "pandas",
    "numpy", "nlp", "git", "linux", "api", "react",
    "artificial intelligence"
]

# Extract text from PDF resume
def extract_text_from_pdf(pdf_path):
    import pdfplumber
    text = ''
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + '\n'
    return text

# Find which skills appear in the resume
def extract_skills(resume_text):
    resume_text = resume_text.lower()
    found_skills = {skill for skill in skills_list if skill in resume_text}
    return list(found_skills)

# Guess if the candidate is a fresher or experienced based on keywords
def detect_profile_type(resume_text):
    resume_text = resume_text.lower()
    if any(word in resume_text for word in ("fresher", "intern", "no experience")):
        return "Fresher"
    elif any(word in resume_text for word in ("experience", "worked at", "years")):
        return "Experienced"
    else:
        return "Unknown"

# Setup Selenium Chrome driver with headless mode
def get_chrome_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=options)

# Safely get text from an element or return a default string
def safe_find_text(element, by, selector):
    try:
        return element.find_element(by, selector).text.strip()
    except Exception:
        return "Not specified"

# Search jobs on Naukri using Selenium
def search_jobs_on_naukri(skills, location, max_results=10):
    query = "-".join(skills)
    loc = location.replace(" ", "-")
    url = f"https://www.naukri.com/{query}-jobs-in-{loc}"
    driver = get_chrome_driver()
    driver.get(url)

    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "cust-job-tuple"))
    )
    job_cards = driver.find_elements(By.CLASS_NAME, "cust-job-tuple")
    jobs = []
    count = 0
    for job in job_cards:
        if count >= max_results:
            break
        try:
            title = job.find_element(By.CSS_SELECTOR, "a.title").text
            link = job.find_element(By.CSS_SELECTOR, "a.title").get_attribute("href")
            company = safe_find_text(job, By.CSS_SELECTOR, "a.comp-name")
            location = safe_find_text(job, By.CSS_SELECTOR, ".locWdth")
            jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "link": link,
                "source": "Naukri"
            })
            count += 1
        except Exception:
            continue
    driver.quit()
    return jobs

# Search jobs on Shine using Selenium
def search_jobs_on_shine(skills, location, max_results=10):
    query = "+".join(skills)
    loc = location.replace(" ", "+")
    url = f"https://www.shine.com/job-search/{query}-jobs-in-{loc}"
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    jobs = []
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "jobCardNova_bigCard__W2xn3"))
        )
        job_cards = driver.find_elements(By.CLASS_NAME, "jobCardNova_bigCard__W2xn3")

        collected = 0
        for job in job_cards:
            if collected >= max_results:
                break
            try:
                title_elem = job.find_element(By.CLASS_NAME, "jobCardNova_bigCardTopTitleHeading__Rj2sC")
                title = title_elem.text.strip()
                link = title_elem.get_attribute("href")
                if not link:
                    meta = job.find_element(By.CSS_SELECTOR, 'meta[itemprop="url"]')
                    link = meta.get_attribute("content")

                company = safe_find_text(job, By.CSS_SELECTOR, "span.jobCardNova_bigCardTopTitleName__M_W_m.jdTruncationCompany")

                loc_elems = job.find_elements(By.CLASS_NAME, "jobCardNova_bigCardCenterListLoc__usiPB")
                location = ", ".join([loc.text.strip() for loc in loc_elems if loc.text.strip()]) if loc_elems else "Not specified"

                jobs.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "link": link,
                    "source": "Shine"
                })
                collected += 1
            except Exception:
                continue
    except TimeoutException:
        print("No Shine jobs found or took too long to load.")
    finally:
        driver.quit()

    return jobs

# Search jobs on TimesJobs using Selenium
def search_jobs_on_timesjobs(skills, location, max_results=10):
    query = "+".join(skills)
    loc = location.replace(" ", "+")
    url = (
        "https://www.timesjobs.com/candidate/job-search.html"
        f"?searchType=personalizedSearch&from=submit"
        f"&txtKeywords={query}&txtLocation={loc}"
    )
    driver = get_chrome_driver()
    driver.get(url)

    WebDriverWait(driver, 25).until(
        EC.presence_of_element_located((By.XPATH, "//li[contains(@class,'job-bx')]"))
    )
    time.sleep(5)

    for i in range(1, 5):
        driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {i/4});")
        time.sleep(1)

    job_cards = driver.find_elements(By.XPATH, "//li[contains(@class,'job-bx')]")
    jobs = []
    count = 0
    for job in job_cards:
        if count >= max_results:
            break
        try:
            title_elem = job.find_element(By.CSS_SELECTOR, "h2 a")
            title = title_elem.text.strip()
            link = title_elem.get_attribute("href")
            company = safe_find_text(job, By.CSS_SELECTOR, "h3.joblist-comp-name")
            jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "link": link,
                "source": "TimesJobs"
            })
            count += 1
        except Exception:
            continue
    driver.quit()
    return jobs

# Check if job has an application link
def has_link(job):
    return bool(job.get("link") and job["link"].strip())

# Rank jobs based on how similar they are to the resume content
def rank_jobs_by_similarity(jobs, resume_embedding, model):
    scored_jobs = []
    for job in jobs:
        combined_text = f"{job['title']} {job['company']} {job['location']}"
        score = util.cos_sim(resume_embedding, model.encode(combined_text, convert_to_tensor=True)).item()
        scored_jobs.append((job, score))
    return sorted(scored_jobs, key=lambda x: x[1], reverse=True)

def main():
    print("Loading model and your resume...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    resume_text = extract_text_from_pdf("Resume.pdf")
    skills_found = extract_skills(resume_text)
    profile_type = detect_profile_type(resume_text)

    print(f"Skills found in your resume: {', '.join(skills_found)}")
    print(f"Profile type detected: {profile_type}\n")

    resume_embedding = model.encode(resume_text, convert_to_tensor=True)

    user_input = input("Enter the skills you want to focus on (comma separated):\n> ")
    focus_skills = [s.strip().lower() for s in user_input.split(",") if s.strip()]
    # Use common skills found or top 3 if none match
    common_skills = [skill for skill in skills_found if skill in focus_skills] or skills_found[:3]

    location = input("Where do you want to search jobs? (Location): ").title()

    print("\nSearching jobs from multiple websites... Please wait.")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_naukri = executor.submit(search_jobs_on_naukri, common_skills, location)
        future_shine = executor.submit(search_jobs_on_shine, common_skills, location)
        future_times = executor.submit(search_jobs_on_timesjobs, common_skills, location)

        jobs_naukri = future_naukri.result()
        jobs_shine = future_shine.result()
        jobs_times = future_times.result()

    print(f"Jobs found on Naukri: {len(jobs_naukri)}")
    print(f"Jobs found on Shine: {len(jobs_shine)}")
    print(f"Jobs found on TimesJobs: {len(jobs_times)}")

    all_jobs = jobs_naukri + jobs_shine + jobs_times
    jobs_with_links = [job for job in all_jobs if has_link(job)]
    print(f"\nTotal jobs with application links: {len(jobs_with_links)}")

    ranked_jobs = rank_jobs_by_similarity(jobs_with_links, resume_embedding, model)
    top_10 = ranked_jobs[:10]

    # Save all jobs to a CSV file
    with open("job_results.csv", "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "Job Title", "Company", "Location", "Link", "Source",
            "Skills Used", "Profile Type", "Similarity Score"
        ])
        for job, score in ranked_jobs:
            writer.writerow([
                job["title"], job["company"], job["location"],
                job["link"], job["source"],
                ", ".join(common_skills), profile_type, f"{score:.3f}"
            ])

    print("\nTop 10 jobs that match your resume:")
    for i, (job, score) in enumerate(top_10, 1):
        print(f"{i}. {job['title']} at {job['company']} ({job['location']})")
        print(f"   Apply here: {job['link']}")
        print(f"   Similarity Score: {score:.3f}\n")

    print("Job details saved to 'job_results.csv'.")

if __name__ == "__main__":
    main()
