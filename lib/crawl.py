import urllib.request
import urllib.parse
import re
import time

from bs4 import BeautifulSoup

# Get HTML of a webpage
def getSource(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
       the_page = response.read()
    return the_page

# Takes in a url and returns:
# - the text content of a url
# - the links to other pages in the same domain
def linksAndText(url, base):
    html = getSource(url)
    soup = BeautifulSoup(html, "lxml")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()

    # break into lines and remove leading and trailing space on each
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines() if len(line.strip()))

    # get links
    links = set()
    base_netloc = urllib.parse.urlparse(base).netloc
    for link in soup.findAll('a', attrs={'href': re.compile("^https+://")}):
        # Only add link if it is within the same sight
        href = link.get('href')
        link_netloc = urllib.parse.urlparse(href).netloc
        if link_netloc == base_netloc:
            links.add(href)

    return lines, links

# Given a base url, crawls links within the website, returns map:
# - key:    url within website
# - value:  plain-text on that url
def website_plaintext(base_url, max_depth=5, sleeptime=0):
    url_to_text = {}
    queue = [(base_url, 0)]
    explored = set()
    while len(queue):
        # Get next node, explore if untraversed
        url, depth = queue.pop(0)
        if (url) in explored:
            continue

        # Get text and children for node.
        print("Exploring: %s" % url)
        text, links = linksAndText(url, base_url)
        url_to_text[url] = text
        explored.add(url)

        # Add children to queue
        if depth > max_depth:
            continue
        for url in links:
            queue.append((url, depth + 1))

        # Timeout to prevent rate limiting
        time.sleep(sleeptime)

    return url_to_text
