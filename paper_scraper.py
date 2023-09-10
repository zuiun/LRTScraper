import os
import utilities
from bs4 import BeautifulSoup

'''
Downloads all LRT pages in a date range

query: string = search query
from_date: string = from date in YYYY-MM-DD format
to_date: string = to date in YYYY-MM-DD format
category: string = search category
    LT = "order=desc"
    EN = "category_id=19"
    RU = "category_id=17"
    PL = "category_id=1261"

Pre: None
Post: Changes current working directory
Return: None
'''
def download_all_lrt (query, from_date, to_date, category):
    i = 1
    page = utilities.import_json (f"https://www.lrt.lt/api/search?page={i}&q={query}&count=44&dfrom={from_date}&dto={to_date}&{category}")

    while len (page ["items"]) > 0:
        paths = []
        date_times = []

        for j in page ["items"]:
            paths.append (f"https://www.lrt.lt/{j ['url']}")
            date_times.append (filter (lambda c: c not in ". :", j ["item_date"]))

        utilities.download_page (paths, date_times)
        i += 1
        page = utilities.import_json (f"https://www.lrt.lt/api/search?page={i}&q={query}&count=44&dfrom={from_date}&dto={to_date}&{category}")

'''
Downloads all Kurier pages in a date range
Runs abominably slowly due to connection times

query: string = search query
from_date: string = from date in YYYY-MM-DD format
to_date: string = to date in YYYY-MM-DD format

Pre: None
Post: Changes current working directory
Return: None
'''
def download_all_kurier (query, from_date, to_date):
    # "https://www.kurier.lt/?s&doing_wp_cron=1694110472.8329210281372070312500#" with no query, not sure what this means
    i = 1
    page = utilities.import_file (f"https://www.kurier.lt/?s={query}")

    while page is not None:
        page = BeautifulSoup (page.text, "html.parser")
        links = page.css.select ("div.post-item a.plain")
        paths = []
        date_times = []
        finished = False

        for j in range (len (links)):
            date = utilities.import_file (links [j] ["href"])
            date = BeautifulSoup (date.text, "html.parser")
            date = date.css.select ("time.entry-date") [0] ["datetime"]

            if from_date <= date [: 10] <= to_date:
                paths.append (links [j] ["href"])
                date_times.append ("".join (filter (lambda c: c not in "-T:", date [: 16])))
            elif date [: 10] < from_date:
                finished = True
                break

        utilities.download_page (paths, date_times)

        if finished:
            break

        i += 1
        page = utilities.import_file (f"https://www.kurier.lt/page/{i}/?s={query}")

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
    i = 1
    page = utilities.import_file (f"https://kurierwilenski.lt/?s={query}")

    while page is not None:
        page = BeautifulSoup (page.text, "html.parser")
        links = page.css.select ("div.tdb_module_loop h3.entry-title a")
        dates = page.css.select ("time.entry-date")
        paths = []
        date_times = []
        finished = False

        for j in range (len (dates)):
            date = dates [j] ["datetime"]

            if from_date <= date [: 10] <= to_date:
                paths.append (links [j] ["href"])
                date_times.append ("".join (filter (lambda c: c not in "-T:", date [: 16])))
            elif date [: 10] < from_date:
                finished = True
                break

        utilities.download_page (paths, date_times)

        if finished:
            break

        i += 1
        page = utilities.import_file (f"https://kurierwilenski.lt/page/{i}/?s={query}")

if __name__ == "__main__":
    path = utilities.set_directory (os.path.join (os.getcwd (), "articles"))
    # Download tests
    utilities.set_directory (os.path.join (path, "lrt"))
    download_all_lrt ("Belarus", "2021-01-01", "2023-01-01", "order=desc") # I seem to have been blocked by LRT
    # utilities.set_directory (os.path.join (path, "kurier"))
    # download_all_kurier ("Belarus", "2021-01-01", "2023-01-01")
    # utilities.set_directory (os.path.join (path, "kw"))
    # download_all_kw ("Belarus", "2021-01-01", "2023-01-01")
