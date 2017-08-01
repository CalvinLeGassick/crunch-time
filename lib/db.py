from datetime import datetime
import psycopg2
import time
from . import api
import urllib.parse as parse

err = False
try:
    conn = psycopg2.connect("dbname='crunchy' host='localhost'")# user='dbuser' host='localhost' password='dbpass'")
except Exception as e:
    err = True
    print (e)
curr = conn.cursor()

def insert_company(curr, company):
    keys = ["name", "short_description", "url", "perma", "created"]
    url = company["homepage_url"]
    if url is not None and url != "":
        parsed_url = parse.urlparse(url)
        url = parsed_url.scheme + "://" + parsed_url.netloc

    company_dict = ({
            "name": company["name"],
            "short_description" : company["short_description"],
            "url" : url,
            "perma" : company["permalink"],
            "created" : datetime.utcfromtimestamp(time.time())
        })

    insert_str = ("INSERT INTO company ("
        + ",".join(keys) + ") VALUES ("
        + "%s, %s, %s, %s, %s" + ")"
        + " ON CONFLICT (perma) DO UPDATE SET url = excluded.url;")
    curr.execute(insert_str, tuple([company_dict[k] for k in keys]))
    conn.commit()

def injest_companies(curr):
    companies = api.fetch_companies()
    # print ("\n".join([c["properties"]["name"] for c in companies]))
    for c in companies:
        company = c["properties"]
        insert_company(curr, company)

def open_connection():
    err = False
    try:
        conn = psycopg2.connect("dbname='crunchy' host='localhost'")# user='dbuser' host='localhost' password='dbpass'")
    except Exception as e:
        err = True
        return None, None, err
    curr = conn.cursor()
    return conn, curr, err

def valid_companies():
    conn, curr, err = open_connection()
    if err:
        return None

    curr.execute("SELECT * FROM company WHERE url IS NOT NULL;")
    companies = curr.fetchall()

    # Close connection
    conn.commit()
    curr.close()
    conn.close()

    return companies

if __name__ == "__main__":
    if not err:
        injest_companies(curr)
        curr.close()
        conn.close()
