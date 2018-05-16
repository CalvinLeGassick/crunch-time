from datetime import datetime
import psycopg2
from . import api
import urllib.parse as parse

ai_category_to_uuid = ({
    "Artificial Intelligence": "c4d8caf35fe7359bf9f22d708378e4ee",
    "Autonomous Vehicles": "897af4838963a2ab16ff2b3489106f0e",
    "Machine Learning": "5ea0cdb7c9a647fc50f8c9b0fac04863",
    "Predictive Analytics": "ca8390d722c65bb5f87022f52f364b1b",
    "Intelligent Systems": "186d333a99df4a4a6a0f69bd2c0d0bba",
    "Natural Language Processing": "789bbbefc46e1532a68df17da87090ea",
    "Computer Vision": "a69e7c2b5a12d999e85ea0da5f05b3d3",
    "Big Data": "c33728a5de33d0da7bce0e3c4383bc99",
    "Bioinformatics": "ac057a31756a62be16770fee94b6aeca",
    "Business Intelligence": "2e3b8104b12e468a65b80989208f0b16",
    "Facial Recognition": "0b8c790f03bcb2aba02e4be855952d6d",
    "Image Recognition": "af9307c9641372aeaac74391df240dd2",
    "Semantic Search": "bb1777e525f3b9f2922b0d5defe0d5bb",
    "Semantic Web": "ac34c4c6e430f66f44aeef8ca45b52bb",
    "Speech Recognition": "24dad27e6a49ccc1ec31854b73d60d16",
    "Text Analytics": "e7acbc9932c74c8809ed8fae63eb2559",
    "Virtual Assistant": "2eb0b56b6896e0f0545fc747a9ba6751",
    "Visual Search": "ad8f33a8c5d0b7d786f389aa2954c119",
    })

err = False
try:
    conn = psycopg2.connect("dbname='crunchy' host='localhost'")# user='dbuser' host='localhost' password='dbpass'")
except Exception as e:
    err = True
    print (e)
curr = conn.cursor()

def insert_company(conn, curr, company_uuid, company):
    keys = (["company_uuid", "company_name", "short_description", "company_url",
        "company_permalink", "company_crunchbase_creation",
        "company_city", "company_region", "company_country",
        "company_web_path", "company_api_path"])
    url = company["homepage_url"]
    if url is not None and url != "":
        parsed_url = parse.urlparse(url)
        url = parsed_url.scheme + "://" + parsed_url.netloc

    company_dict = ({
            "company_uuid": company_uuid,
            "company_name": company["name"],
            "short_description" : company["short_description"],
            "company_url" : url,
            "company_permalink" : company["permalink"],
            "company_crunchbase_creation" : datetime.utcfromtimestamp(int(company["created_at"])),
            "company_city": company["city_name"],
            "company_region": company["region_name"],
            "company_country": company["country_code"],
            "company_web_path": company["web_path"],
            "company_api_path": company["api_path"]
        })

    update_str = ",".join(["%s=excluded.%s" % (k, k) for k in keys[1:]])
    insert_str = ("INSERT INTO company ("
        + ",".join(keys) + ") VALUES ("
        + ",".join("%s" for _ in range(len(keys))) + ")"
        + " ON CONFLICT (company_uuid) DO UPDATE SET " +  update_str + ";")
    curr.execute(insert_str, tuple(company_dict[k] for k in keys))
    conn.commit()

def insert_category(conn, curr, category_uuid, category_name):
    keys = ["category_uuid", "category_name"]
    category_dict = {"category_uuid": category_uuid, "category_name": category_name}
    insert_str = ('INSERT INTO category ('
        + ",".join(keys) + ") VALUES ("
        + ",".join("%s" for _ in range(len(keys))) + ")"
        + " ON CONFLICT (category_uuid) DO UPDATE SET category_name = excluded.category_name;"
        )
    curr.execute(insert_str, tuple(category_dict[k] for k in keys))
    conn.commit()

def insert_company_category(conn, curr, company_uuid, category_uuid):
    keys = ["company_uuid", "category_uuid"]
    company_category_dict = ({
        "company_uuid": company_uuid,
        "category_uuid": category_uuid
        })
    insert_str = ('INSERT INTO company_category ('
        + ",".join(keys) + ") VALUES ("
        + ",".join("%s" for _ in range(len(keys))) + ")"
        + " ON CONFLICT (company_uuid, category_uuid) DO NOTHING;"
        )
    curr.execute(insert_str, tuple(company_category_dict[k] for k in keys))
    conn.commit()

def insert_funding(conn, curr, company_uuid, funding):
    keys = ([
        "funding_uuid",
        "company_uuid",
        "funding_round_type",
        "series",
        "announced_on",
        "announced_on_trust_code",
        "closed_on",
        "closed_on_trust_code",
        "money_raised_usd",
        "target_money_raised_usd",
        "created_at",
        ])
    funding_dict = dict(funding)
    funding_dict["created_at"] = datetime.utcfromtimestamp(int(funding["created_at"]))
    funding_dict.update({"company_uuid": company_uuid})

    insert_str = ('INSERT INTO funding_round ('
        + ",".join(keys) + ") VALUES ("
        + ",".join("%s" for _ in range(len(keys))) + ")"
        + " ON CONFLICT (funding_uuid) DO UPDATE SET funding_uuid = excluded.funding_uuid;"
        )
    curr.execute(insert_str, tuple(funding_dict[k] for k in keys))
    conn.commit()

def injest_companies(conn, curr):
    current = 1
    batch_size = 10
    max_batches = 100
    while current * batch_size <= max_batches:
        companies = api.fetch_companies(start_page=current * batch_size, max_pages=(current + 1) * batch_size - 1)
        for c in companies:
            company_uuid = c["uuid"]
            company = c["properties"]
            insert_company(conn, curr, company_uuid, company)
        if not len(companies):
            break
        current += 1

def injest_categories(conn, curr):
    categories = api.fetch_categories()
    for category_uuid, category_name in categories:
        insert_category(conn, curr, category_uuid, category_name)

def get_category_uuids(category_name_list):
    query = (
        "SELECT category_name, category_uuid"
        + " FROM category"
        + " WHERE category_name IN ("
        + ",".join(["'%s'" % n for n in category_name_list]) + ");"
        )

    conn, curr, err = open_connection()
    if err:
        return None

    curr.execute(query)
    category_tuples = curr.fetchall()

    # Close connection
    conn.commit()
    curr.close()
    conn.close()

    category_dict = dict(category_tuples)
    return category_dict

def injest_ai_companies(conn, curr):
    for category_name, category_uuid in ai_category_to_uuid.items():
        injest_companies_for_category(conn, curr, category_uuid)

def injest_companies_for_category(conn, curr, category_uuid):
    filters = ({
            "locations": "United States", # "London" "Germany" "France"
            "category_uuids": ",".join([category_uuid])
            })
    companies = api.fetch_companies(filters=filters)
    for c in companies:
        company_uuid = c["uuid"]
        company = c["properties"]
        insert_company(conn, curr, company_uuid, company)
        insert_company_category(conn, curr, company_uuid, category_uuid)

def open_connection():
    err = False
    try:
        conn = psycopg2.connect("dbname='crunchy' host='localhost'")# user='dbuser' host='localhost' password='dbpass'")
    except Exception as e:
        err = True
        return None, None, err
    curr = conn.cursor()
    return conn, curr, err

def select_companies(keys=["company_uuid", "company_permalink"]):
    conn, curr, err = open_connection()
    if err:
        return None

    curr.execute("SELECT " + ",".join(keys) + " FROM company")
    company_tuples = curr.fetchall()

    # Close connection
    conn.commit()
    curr.close()
    conn.close()

    companies = []
    for c in company_tuples:
        company = {}
        for i, k in enumerate(keys):
            company[k] = c[i]
        companies.append(company)

    return companies

def select_companies_with_funding():
    conn, curr, err = open_connection()
    if err:
        return None
    curr.execute("SELECT DISTINCT(company_uuid) FROM FUNDING_ROUND;")
    company_tuples = curr.fetchall()

    # Close connection
    conn.commit()
    curr.close()
    conn.close()

    return [c[0] for c in company_tuples]

def valid_companies():
    keys = ["company_name", "short_description", "comapny_url", "company_permalink", "company_crunchbase_creation"]
    conn, curr, err = open_connection()
    if err:
        return None

    curr.execute("SELECT " + ",".join(keys) + " FROM company WHERE url IS NOT NULL;")
    company_tuples = curr.fetchall()

    # Close connection
    conn.commit()
    curr.close()
    conn.close()

    companies = []
    for c in company_tuples:
        company = {}
        for i, k in enumerate(keys):
            company[k] = c[i]
        companies.append(company)

    return companies

if __name__ == "__main__":
    if not err:
        injest_companies(curr)
        curr.close()
        conn.close()
