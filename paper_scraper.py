import os
import utilities
from bs4 import BeautifulSoup

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
    utilities.set_directory ("lrt")
    i = 1
    page = utilities.import_json (f"https://www.lrt.lt/api/search?page={i}&q={query}&count=44&dfrom={from_date}&dto={to_date}&order=desc")

    while len (page ["items"]) > 0:
        paths = []
        date_times = []

        for j in page ["items"]:
            paths.append (f"https://www.lrt.lt/{j ['url']}")
            date_times (filter (lambda c: c not in ". :", j ["item_date"]))

        utilities.download_page (paths, date_times)
        i += 1
        page = utilities.import_json (f"https://www.lrt.lt/api/search?page={i}&q={query}&count=44&dfrom={from_date}&dto={to_date}&order=desc")

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
    # "https://www.kurier.lt/?s&doing_wp_cron=1694110472.8329210281372070312500#" with no query, not sure what this means
    utilities.set_directory ("kurier")

    i = 1
    page = utilities.import_file (f"https://www.kurier.lt/?s={query}")

    while page is not None:
        page = BeautifulSoup (page.text, "html.parser")
        links = page.css.select ("div.post-item a.plain")
        # TODO: Kurier requires accessing webpage to get dates
        dates = page.css.select ("time.entry-date")
        paths = []
        date_times = []

        for j in range (len (dates)):
            date = dates [j] ["datetime"]

            if from_date <= date [: 10] <= to_date:
                paths.append (links [j] ["href"])
                date_times.append ("".join (filter (lambda c: c not in "-T:", date [: 16])))
            elif date [: 10] < from_date:
                break

        utilities.download_page (paths, date_times)
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
    utilities.set_directory ("kw")
    i = 1
    page = utilities.import_file (f"https://kurierwilenski.lt/?s={query}")

    while page is not None:
        page = BeautifulSoup (page.text, "html.parser")
        links = page.css.select ("div.tdb_module_loop h3.entry-title a")
        dates = page.css.select ("time.entry-date")
        paths = []
        date_times = []

        for j in range (len (dates)):
            date = dates [j] ["datetime"]

            if from_date <= date [: 10] <= to_date:
                paths.append (links [j] ["href"])
                date_times.append ("".join (filter (lambda c: c not in "-T:", date [: 16])))
            elif date [: 10] < from_date:
                break

        utilities.download_page (paths, date_times)
        i += 1
        page = utilities.import_file (f"https://kurierwilenski.lt/page/{i}/?s={query}")

if __name__ == "__main__":
    utilities.set_directory ("articles")
    directory = os.getcwd ()
    # Download tests
    # download_all_lrt ("Belarus", "2021-01-01", "2023-01-01") # I seem to have been blocked by LRT
    # download_all_kurier ("Belarus", "2021-01-01", "2023-01-01")
    download_all_kw ("Belarus", "2021-01-01", "2023-01-01")
