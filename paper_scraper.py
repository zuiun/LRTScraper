import datetime
import os
# import argparse
import utilities
from bs4 import BeautifulSoup
from translatepy import Translate
from translatepy.translators import GoogleTranslate

'''
Downloads all LRT pages in a date range

query: string = search query
from_date: string = from date in YYYY-MM-DD format
to_date: string = to date in YYYY-MM-DD format
language: string = article language
translator: Translator = article translator

Pre: None
Post: Changes current working directory
Return: None
'''
def download_all_lrt (query, from_date, to_date, language, translator = None):
    category = None

    if language == "lit":
        category = "order=desc"
    elif language == "eng":
        category = "category_id=19"
    elif language == "rus":
        category = "category_id=17"
    elif language == "pol":
        category = "category_id=1261"

    i = 1
    page = utilities.import_json (f"https://www.lrt.lt/api/search?page={i}&q={query}&count=44&dfrom={from_date}&dto={to_date}&{category}")

    while len (page ["items"]) > 0:
        paths = []
        date_times = []

        for j in page ["items"]:
            if j ["is_video"] == 0 and j ["is_audio"] == 0:
                paths.append (f"https://www.lrt.lt/{j ['url']}")
                date_times.append ("".join (filter (lambda c: c not in ". :", j ["item_date"])))

        utilities.download_page (paths, date_times, translator, language)
        i += 1
        page = utilities.import_json (f"https://www.lrt.lt/api/search?page={i}&q={query}&count=44&dfrom={from_date}&dto={to_date}&{category}")

'''
Downloads all Kurier pages in a date range
Runs abominably slowly due to connection times

query: string = search query
from_date: string = from date in YYYY-MM-DD format
to_date: string = to date in YYYY-MM-DD format
translator: Translator = article translator

Pre: None
Post: Changes current working directory
Return: None
'''
def download_all_kurier (query, from_date, to_date, translator):
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

        utilities.download_page (paths, date_times, translator)

        if finished:
            break

        i += 1
        page = utilities.import_file (f"https://www.kurier.lt/page/{i}/?s={query}")

'''
Downloads all KW pages in a date range

query: string = search query
from_date: string = from date in YYYY-MM-DD format
to_date: string = to date in YYYY-MM-DD format
translator: Translator = article translator

Pre: None
Post: Changes current working directory
Return: None
'''
def download_all_kw (query, from_date, to_date, translator):
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

        utilities.download_page (paths, date_times, translator, "pol")

        if finished:
            break

        i += 1
        page = utilities.import_file (f"https://kurierwilenski.lt/page/{i}/?s={query}")

if __name__ == "__main__":
    paper = input ("Choose a paper (lrt = LRT [LT], le = LRT [EN], lr = LRT [RU], lp = LRT [PL], ku = Kurier, kw = Kurier Wileński): ")

    while paper != "lrt" and paper != "le" and paper != "lr" and paper != "lp" and paper != "ku" and paper != "kw":
        paper = input ("Invalid choice. Choose a paper: ")

    query = input ("Enter your query (blank queries are accepted): ")
    from_date = input ("Enter a from date (YYYY-MM-DD): ")

    while True:
        try:
            datetime.date.fromisoformat (from_date)
        except ValueError as exception:
            from_date = input ("Invalid date. Enter a from date: ")
        else:
            break

    to_date = input ("Enter a to date (YYYY-MM-DD): ")

    while True:
        try:
            datetime.date.fromisoformat (to_date)
        except ValueError as exception:
            to_date = input ("Invalid date. Enter a to date: ")
        else:
            break

    translator = Translate ([GoogleTranslate])

    if paper == "lrt":
        utilities.set_directory (os.path.join (os.getcwd (), "articles", "lrt", "lit"))
        download_all_lrt (query, from_date, to_date, "lit", translator)
    elif paper == "le":
        utilities.set_directory (os.path.join (os.getcwd (), "articles", "lrt", "eng"))
        download_all_lrt (query, from_date, to_date, "eng")
    elif paper == "lr":
        utilities.set_directory (os.path.join (os.getcwd (), "articles", "lrt", "rus"))
        download_all_lrt (query, from_date, to_date, "rus", translator)
    elif paper == "lp":
        utilities.set_directory (os.path.join (os.getcwd (), "articles", "lrt", "pol"))
        download_all_lrt (query, from_date, to_date, "pol", translator)
    elif paper == "ku":
        utilities.set_directory (os.path.join (os.getcwd (), "articles", "kurier"))
        print ("Kurier downloads are extremely slow.")
        download_all_kurier (query, from_date, to_date, translator)
    elif paper == "kw":
        utilities.set_directory (os.path.join (os.getcwd (), "articles", "kw"))
        download_all_kw (query, from_date, to_date, translator)
