import urllib.parse
import requests
import time
from .config import config 
api_key = config.api_key
base_url = "https://api.crunchbase.com/v/3/"

def request_all_pages(url, query_args, extractor, max_pages=None):
    results = []
    page_size = None
    while True:
        # Make request and add response to result set 
        try:
            response = requests.get(url, params=query_args)
            data = response.json()
            results.extend(extractor(data))
        except Exception as e:
            import pdb; pdb.set_trace()
            time.sleep(10)

        # If we have paged through all the results, exit
        current = int(data["data"]["paging"]["current_page"])

        this_page_size = len(data["data"]["items"])
        if page_size is None and this_page_size == 0:
            print("No results on first page of request for url: %s" % url)
            raise Exception()

        page_size = page_size if page_size is not None else this_page_size
        total_items = int(data["data"]["paging"]["total_items"])
        if current * page_size >= total_items:
            break

        if max_pages is not None and current >= max_pages:
            break

        query_args["page"] = str(current + 1)

    return results

def fetch_companies(start_page=1, max_pages=None, filters={}):
    if not len(filters):
        filters = {"locations": "United States"}

    full_url = urllib.parse.urljoin(base_url, "organizations")
    query_args = {"user_key": api_key, "page": str(start_page)}
    query_args.update(filters)
    def company_extractor(data):
        results = []
        for idx, item in enumerate(data["data"]["items"]):
            if item["properties"]["primary_role"] != "company":
                print ("Not a company: %s" % item["properties"]["name"])
                continue
            results.append(item)
        # print("\n".join(item["properties"]["name"] for item in results))
        return results

    results = request_all_pages(full_url, query_args, company_extractor, max_pages)
    return results

def fetch_categories(start_page=1, max_pages=None):
    full_url = urllib.parse.urljoin(base_url, "categories")
    query_args = {"user_key": api_key, "page": str(start_page)}
    def category_extractor(data):
        items = data["data"]["items"]
        # print("\n".join(i["properties"]["name"] for i in items))
        return [(i["uuid"], i["properties"]["name"]) for i in items]

    # Page through results
    results = request_all_pages(full_url, query_args, category_extractor, max_pages)
    return results

def fetch_company_details(permalink):
    full_url = urllib.parse.urljoin(base_url, "organizations/" + permalink)
    query_args = {"user_key": api_key}
    response = requests.get(full_url, params=query_args)
    data = response.json()
    return data

def fetch_company_funding_details(permalink):
    data = fetch_company_details(permalink)
    keys = (
        "series",
        "announced_on",
        "announced_on_trust_code",
        "closed_on",
        "closed_on_trust_code",
        "money_raised_usd",
        "target_money_raised_usd",
        "created_at",
        )

    funding_rounds = []
    round_details = data["data"]["relationships"]["funding_rounds"]["items"]
    for round_ in round_details:
        round_dict = {}
        round_dict.update({"funding_uuid": round_["uuid"]})
        round_dict.update({"funding_round_type": round_["type"]})
        round_dict.update({k: round_["properties"][k] for k in keys})
        funding_rounds.append(round_dict)
        # funding_rounds.append(
        #     {"funding_uuid": round_["uuid"]}
        #     + {"funding_round_type": round_["type"]}
        #     + {k: round_["properties"][k] for k in keys})

    return funding_rounds

#     "properties": {
#         "description",
#         "primary_role",
#         "role_company",
#         "role_investor",
#         "role_group",
#         "role_school",
#         "founded_on",
#         "founded_on_trust_code",
#         "is_closed",
#         "closed_on",
#         "closed_on_trust_code",
#         "num_employees_min",
#         "num_employees_max",
#         "stock_symbol",
#         "total_funding_usd",
#     }
#     "relationships": {
#         "offices": {
#             # Type Address
#             "items": {
#                 "properties": {
#                     "city":
#                     "country"
#                 }
#             }
#         }
#         "headquarters": {
#             # Type Address        
#             "item": {

#             }
#         }
#         "categories": {
#             "items": {
#                 "uuid":
#                 "properties": {
#                     "name"
#                 }
#             }
#         }
#         "aquired_by": {
#         }
#         "funding_rounds": {
#         }
#     }

def fetch_locations():
    location_dict = {
        "city": set(),
        "country": set(),
        "continent": set()
    }
    def location_extractor(data, location_dict=location_dict):
        items = data["data"]["items"]
        for i in items:
            for k in location_dict:
                if k in i["properties"]:
                    if i["properties"][k] is not None:
                        location_dict[k].add(i["properties"][k])
        return []

    full_url = urllib.parse.urljoin(base_url, "locations/")
    query_args = {"user_key": api_key}
    request_all_pages(full_url, query_args, location_extractor, 5)
    return location_dict
