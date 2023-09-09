import os
import utilities
from bs4 import BeautifulSoup

'''
Collects data for JSON-search websites

args: dict = arguments for collector
    path: string = path to website
    query: string = search query
    page_number: int = page number
    from_date: string = from date in YYYY-MM-DD format
    to_date: string = to date in YYYY-MM-DD format
    category: string = search catgory

Pre: None
Post: None
Return: tuple = (paths, date_times) for download_page
'''
def collector_json (args):
    file = utilities.import_json (f"{args ['path']}/api/search?page={args ['page_number']}&q={args ['query']}&count=44&dfrom={args ['from_date']}&dto={args ['to_date']}&{args ['category']}")

    if len (file ["items"]) > 0:
        paths = []
        date_times = []

        for i in file ["items"]:
            paths.append (f"{args ['path']}/{i ['url']}")
            date_times.append ("".join (filter (lambda c: c not in ". :", i ["item_date"])))

        return (paths, date_times)
    else:
        return None

'''
Collects data for HTML-search websites

args: dict = arguments for collector
    path: string = path to website
    query: string = search query
    page_number: int = page number
    from_date: string = from date in YYYY-MM-DD format
    to_date: string = to date in YYYY-MM-DD format
    a_selector: string = CSS selector for <a>
    time_selector: string = CSS selector for <time>

Pre: None
Post: None
Return: tuple = (paths, date_times) for download_page
'''
def collector_html (args):
    file = utilities.import_file (f"{args ['path']}/page/{args ['page_number']}/?s={args ['query']}" if args ["page_number"] > 1 else f"{args ['path']}/?s={args ['query']}")

    if file is None:
        return None
    else:
        file = BeautifulSoup (file.text, "html.parser")
        links = page.css.select (args ["a_selector"])
        dates = page.css.select (args ["time_selector"])
        paths = []
        date_times = []

        for i in range (len (dates)):
            date = dates [i] ["datetime"]

            if args ["from_date"] <= date [: 10] <= args ["to_date"] :
                paths.append (links [i] ["href"])
                date_times.append ("".join (filter (lambda c: c not in "-T:", date [: 16])))
            # Stop looking when remaining articles are too old
            elif date [: 10] < args ["from_date"] :
                break

        return (paths, date_times)

'''
Downloads all LRT pages in a date range

query: string = search query
from_date: string = from date in YYYY-MM-DD format
to_date: string = to date in YYYY-MM-DD format

Pre: None
Post: Changes current working directory
Return: None
'''
def download_all_lrt (query, from_date, to_date):
    args = {
        "query": query,
        "from_date": from_date,
        "to_date": to_date
    }
    utilities.download_range ("lrt", collector_json, args)

'''
Downloads all Kurier pages in a date range

query: string = search query
from_date: string = from date in YYYY-MM-DD format
to_date: string = to date in YYYY-MM-DD format

Pre: None
Post: Changes current working directory
Return: None
'''
def download_all_kurier (query, from_date, to_date):
    args = {
        "query": query,
        "from_date": from_date,
        "to_date": to_date
    }
    utilities.download_range ("kurier", collector_html, args)

'''
Downloads all KW pages in a date range

query: string = search query
from_date: string = from date in YYYY-MM-DD format
to_date: string = to date in YYYY-MM-DD format

Pre: None
Post: Changes current working directory
Return: None
'''
def download_all_kw (query, from_date, to_date):
    args = {
        "query": query,
        "from_date": from_date,
        "to_date": to_date
    }
    utilities.download_range ("kw", collector_html, args)

if __name__ == "__main__":
    utilities.set_directory ("articles")
    # Download tests
    # download_all_lrt ("Belarus", "2021-01-01", "2023-01-01") # I seem to have been blocked by LRT
    download_all_kurier ("Belarus", "2021-01-01", "2023-01-01")
    download_all_kw ("Belarus", "2021-01-01", "2023-01-01")
