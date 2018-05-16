import pickle
import os
import time

from lib import crawl, db, api

# RATE LIMITING - 200 HITS PER MINUTE ACCORDING TO TIM

text_db_filename = "db.p"

# def get_company_text(company):
def save_db(text_db):
    with open(text_db_filename, "wb") as f:
        pickle.dump(text_db, f)
def load_db():
    return pickle.load(open(text_db_filename, "rb"))

# Load text db
if not os.path.isfile(text_db_filename):
    save_db({})
text_db = pickle.load(open(text_db_filename, "rb"))

def init_text_db():
    companies = db.valid_companies()
    company = companies[0]
    company_url = company["url"]
    company_name = company["name"]
    if company_name not in text_db:
        url_to_text = crawl.website_plaintext(company_url)
        text_db[company_name] = url_to_text
        save_db(text_db)
    else:
        url_to_text = text_db[company_name]
    text = " ".join(list(url_to_text.values()))

def print_dict(d):
    print("\n".join(["%s: %s" % (k, v) for (k, v) in sorted(d.items())]))

def download_funding_info():
    conn, curr, err = db.open_connection()
    companies = db.select_companies()

    company_funding_info = db.select_companies_with_funding()
    companies = [c for c in companies if c["company_uuid"] not in company_funding_info]
    for company in companies:
        permalink = company["company_permalink"]
        company_uuid = company["company_uuid"]
        try:
            funding_rounds = api.fetch_company_funding_details(permalink)
            for round_ in funding_rounds:
                db.insert_funding(conn, curr, company_uuid, round_)
        except Exception as e:
            print("ERROR WITH COMPANY %s" % company_uuid)
            print(e)
            print("------")
            curr.close()
            conn.close()
            conn, curr, _ = db.open_connection()
            time.sleep(10)

def print_locations():
    locations = api.fetch_locations()
    cities = list(sorted(list(locations["city"])))
    countries = list(sorted(list(locations["country"])))
    continents = list(sorted(list(locations["continent"])))
     
    print("Cities")
    print("\n".join(cities))
    print("---")
    print("Countries")
    print("\n".join(countries))
    print("---")
    print("Continents")
    print("\n".join(continents))
    print("---")

if __name__ == "__main__":
    pass
    # conn, curr, err = db.open_connection()
    # db.injest_ai_companies(conn, curr)
    # category_dict = db.get_category_uuids(db.ai_category_to_uuid)
    # for name, uuid in sorted(category_dict.items()):
    #     print("Injesting '%s' companies" % name)
    #     db.injest_companies_for_category(conn, curr, uuid)

    # db.injest_filtered_companies(conn, curr)
    # db.injest_companies(conn, curr)
    # db.injest_categories(conn, curr)
