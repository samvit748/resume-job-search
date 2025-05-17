from serpapi import GoogleSearch

def search_jobs_on_google(skills, api_key, location):
    # Combine skills into a single search phrase
    search_query = " ".join(skills) + " jobs"
    print(f"Initiating Google Jobs search for: {search_query}")

    params = {
        "engine": "google_jobs",
        "q": search_query,
        "location": location,
        "api_key": api_key
    }

    search = GoogleSearch(params)
    response = search.get_dict()

    print("Received keys from SerpAPI response:", response.keys())

    if "error" in response:
        print(f"Error from SerpAPI: {response['error']}")
        return []

    job_results = response.get("jobs_results", [])
    if not job_results:
        print("No job listings found in the response.")
        return []

    processed_jobs = []
    for job in job_results:
        apply_url = None

        
        if "job_apply_link" in job:
            apply_url = job["job_apply_link"]
        
        elif "related_links" in job:
            for link_info in job["related_links"]:
                if "apply" in link_info.get("text", "").lower():
                    apply_url = link_info.get("link")
                    break
        
        if not apply_url:
            title_terms = "+".join(job.get("title", "").split())
            company_terms = "+".join(job.get("company_name", "").split())
            apply_url = f"https://www.google.com/search?q={title_terms}+{company_terms}+job+apply"

        processed_jobs.append({
            "title": job.get("title", "N/A"),
            "company": job.get("company_name", "N/A"),
            "location": job.get("location", "N/A"),
            "link": apply_url
        })

    return processed_jobs
