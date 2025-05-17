from serpapi import GoogleSearch

def search_jobs_on_google(skills, api_key, location):
    """
    This function searches for jobs on Google using SerpAPI.
    It takes skills, API key, and location as input.
    """

    # Join all the skills to create a search query
    search_query = " ".join(skills) + " jobs"
    print(f"Searching Google Jobs for: {search_query}")

    # Set the parameters for the SerpAPI request
    params = {
        "engine": "google_jobs",
        "q": search_query,
        "location": location,
        "api_key": api_key
    }

    # Send the search request
    search = GoogleSearch(params)
    response = search.get_dict()

    print("Response keys received from SerpAPI:", response.keys())

    # Check if there was an error in the response
    if "error" in response:
        print("Error:", response["error"])
        return []

    # Get the job results from the response
    job_results = response.get("jobs_results", [])
    if not job_results:
        print("No jobs found.")
        return []

    final_jobs = []

    for job in job_results:
        # Try to find the apply link
        apply_link = None

        # Check for direct apply link
        if "job_apply_link" in job:
            apply_link = job["job_apply_link"]

        # Otherwise, look for related links with "apply" in text
        elif "related_links" in job:
            for item in job["related_links"]:
                if "apply" in item.get("text", "").lower():
                    apply_link = item.get("link")
                    break

        
        if not apply_link:
            title = "+".join(job.get("title", "").split())
            company = "+".join(job.get("company_name", "").split())
            apply_link = f"https://www.google.com/search?q={title}+{company}+job+apply"

        # Add job info to the list
        final_jobs.append({
            "title": job.get("title", "N/A"),
            "company": job.get("company_name", "N/A"),
            "location": job.get("location", "N/A"),
            "link": apply_link
        })

    return final_jobs
