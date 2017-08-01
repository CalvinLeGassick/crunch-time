import requests
from .config import config 
api_key = config.api_key
base_url = "https://api.crunchbase.com/v/3/"

def fetch_companies(start_page=1, max_pages=10):
    url_ext = "odm-organizations"
    query = {"user_key":api_key, "locations": "United States", "organization_types": "company", "page": str(start_page)}
    companies = []
    while int(query["page"]) <= max_pages:
        response = requests.get(base_url + url_ext, params=query)
        data = response.json()
        for idx, item in enumerate(data["data"]["items"]):
            if item["properties"]["primary_role"] != "company":
                print ("Not a company: %s" % item["properties"]["name"])
                continue
            if item["properties"]["country_code"] != "United States":
                print ("Not in US: %s" % item["properties"]["name"])
                continue
            companies.append(item)
        print ("Page %s processed" % query["page"])
        query["page"] = str(int(query["page"]) + 1)
    print ("%s companies retreived from API" % len(companies))
    return companies
