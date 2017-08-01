from lib import crawl, db

if __name__ == "__main__":
    companies = db.valid_companies()
    company_urls = [c[2] for c in companies]

    company_url = company_urls[1]
    url_to_text = crawl.website_plaintext(company_url)
    for key, value in url_to_text.items():
        print (key)
        for text in value:
            print ("\t%s" % text)
