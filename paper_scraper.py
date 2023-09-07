from bs4 import BeautifulSoup
import utilities

'''
Downloads all LRT pages in a date range

query: string = search query
from_date: string = from date in YYYY-MM-DD format
to_date: string = to date in YYYY-MM-DD format

Pre: None
Post: None
Return: None
'''
def download_all_lrt (query, from_date, to_date):
    i = 1
    page = utilities.import_json (f"https://www.lrt.lt/api/search?page={i}&q={query}&count=44&dfrom={from_date}&dto={to_date}&order=desc")

    while len (page ["items"]) > 0:
        paths = []
        date_times = []

        for j in page ["items"]:
            paths.append (f"https://www.lrt.lt/{j ['url']}")
            date_times (filter (lambda c: c not in ". :", j ["item_date"]))

        download_page (paths, date_times)
        i += 1
        page = utilities.import_json (f"https://www.lrt.lt/api/search?page={i}&q={query}&count=44&dfrom={from_date}&dto={to_date}&order=desc")

'''
Downloads all Kurier pages in a date range

query: string = search query
from_date: string = from date in YYYY-MM-DD format
to_date: string = to date in YYYY-MM-DD format

Pre: None
Post: None
Return: None
'''
def download_all_kurier (query, from_date, to_date):
    # "https://www.kurier.lt/?s&doing_wp_cron=1694110472.8329210281372070312500#" with no query, not sure what this means
    i = 1
    page = utilities.import_file (f"https://www.kurier.lt/?s={query}")
    page = BeautifulSoup (page.text, "html.parser")

    while page is not None:
        links = page.css.select ("div.post-item a.plain")
        dates = page.css.select ("time.entry-date")
        paths = []
        date_times = []

        for j in range (len (dates)):
            date = dates [j] ["datetime"]

            if from_date <= date [: 10] <= to_date:
                paths.append (links [j])
                date_times.append (filter (lambda c: c not in "-T:", date [: 16]))

        download_page (paths, date_times)
        i += 1
        page = utilities.import_file (f"https://www.kurier.lt/page/{i}/?s={query}")

'''
Downloads all KW pages in a date range

query: string = search query
from_date: string = from date in YYYY-MM-DD format
to_date: string = to date in YYYY-MM-DD format

Pre: None
Post: None
Return: None
'''
def download_all_kw (query, from_date, to_date):
    i = 1
    page = utilities.import_file (f"https://kurierwilenski.lt/?s={query}")
    page = BeautifulSoup (page.text, "html.parser")

    while page is not None:
        links = page.css.select ("div.tdb_module_loop h3.entry-title a")
        dates = page.css.select ("time.entry-date")
        paths = []
        date_times = []

        for j in range (len (dates)):
            date = dates [j] ["datetime"]

            if from_date <= date [: 10] <= to_date:
                paths.append (links [j])
                date_times.append (filter (lambda c: c not in "-T:", date [: 16]))

        download_page (paths, date_times)
        i += 1
        page = utilities.import_file (f"https://kurierwilenski.lt/page/{i}/?s={query}")

if __name__ == "__main__":
    # utilities.set_directory ("articles")
    print ("Paper Scraper")
