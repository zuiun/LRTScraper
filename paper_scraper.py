# import argparse
import colorama
import math
import multiprocessing
import os
# import time
import utilities
# from bs4 import BeautifulSoup
from concurrent import futures
from datetime import date, datetime
from translatepy import Translate
from translatepy.translators import GoogleTranslate

'''
Downloads all LRT pages in a date range

query: str = search query
from_date: str = from date in YYYY-MM-DD format
to_date: str = to date in YYYY-MM-DD format
language: str = article language
translator: Translator = article translator

Pre: None
Post: Changes current working directory
Return: None
'''
def download_all_lrt (query: str, from_date: str, to_date: str, language: str, translator: Translate = None, concurrent: bool = True):
    category = ""

    # TODO: Find correct category for Lithuanian
    if language == "lit":
        category = "order=desc"
    elif language == "eng":
        category = "category_id=19"
    elif language == "rus":
        category = "category_id=17"
    elif language == "pol":
        category = "category_id=1261"
    elif language == "ukr":
        category = "category_id=1263"

    i = 1
    page = utilities.import_json (f"https://www.lrt.lt/api/search?page={i}&q={query}&count=44&dfrom={from_date}&dto={to_date}&{category}")
    pages = []

    while len (page ["items"]) > 0:
        information = []
        utilities.time_print (f"Getting information for page {i} of {math.ceil (int (page ['total_found']) / 44)}")

        for j in page ["items"]:
            if j ["is_video"] == 0 and j ["is_audio"] == 0:
                # article_category_id = 19 is English news
                # TODO: Fix sports (article_category_id = 10, extremely slow)
                if (language == "lit" and j ["article_category_id"] != 19) or j ["article_category_id"] == 10:
                    continue

                path = f"https://www.lrt.lt{j ['url']}"
                name = f"{''.join (filter (lambda c: c not in '. :', j ['item_date']))}.pdf"
                converted = f"en_{name}"
                download = utilities.Download (0)

                if not os.path.exists (name):
                    download |= utilities.Download.ARTICLE

                if not os.path.exists (converted):
                    download |= utilities.Download.TRANSLATION

                if utilities.Download.ARTICLE in download or utilities.Download.TRANSLATION in download:
                    information.append ((path, (name, converted), translator, language, i, download))

        if concurrent:
            if len (information) > 0:
                pages.append (information)

            if len (pages) == utilities.PROCESSES:
                with futures.ThreadPoolExecutor (max_workers = utilities.THREADS) as pool:
                    articles, translations = zip (* pool.map (utilities.download_page, pages))

                for i in range (len (pages)):
                    with multiprocessing.Pool (processes = utilities.PROCESSES) as pool:
                        pool.map (utilities.download_article, articles [i])
                        pool.map (utilities.download_translation, translations [i])
                        # time.sleep (utilities.TIMEOUT)
                        # pool.terminate ()

                pages.clear ()
        elif len (information) > 0:
            articles, translations = utilities.download_page (information)

            for j in articles:
                utilities.download_article (j)

            for j in translations:
                utilities.download_translation (j)

        i += 1
        page = utilities.import_json (f"https://www.lrt.lt/api/search?page={i}&q={query}&count=44&dfrom={from_date}&dto={to_date}&{category}")

'''
Downloads all KW pages in a date range
CURRENTLY DEPRECATED DUE TO ONGOING IMPROVEMENTS

query: str = search query
from_date: str = from date in YYYY-MM-DD format
to_date: str = to date in YYYY-MM-DD format
translator: Translate = article translator

Pre: None
Post: Changes current working directory
Return: None
'''
def download_all_kw (query: str, from_date: str, to_date: str, translator: Translate = None):
    pass
    # i = 1
    # page = utilities.import_file (f"https://kurierwilenski.lt/?s={query}")

    # while page is not None:
    #     page = BeautifulSoup (page.text, "html.parser")
    #     links = page.css.select ("div.tdb_module_loop h3.entry-title a")
    #     dates = page.css.select ("time.entry-date")
    #     paths = []
    #     date_times = []
    #     finished = False

    #     for j in range (len (dates)):
    #         date = dates [j] ["datetime"]

    #         if from_date <= date [: 10] <= to_date:
    #             paths.append (links [j] ["href"])
    #             date_times.append ("".join (filter (lambda c: c not in "-T:", date [: 16])))
    #         elif date [: 10] < from_date:
    #             finished = True
    #             break

    #     utilities.download_page (paths, date_times, translator, "pol")

    #     if finished:
    #         break

    #     i += 1
    #     page = utilities.import_file (f"https://kurierwilenski.lt/page/{i}/?s={query}")

if __name__ == "__main__":
    colorama.init ()
    # paper = input ("Choose a paper (lrt = LRT [LT], le = LRT [EN], lr = LRT [RU], lp = LRT [PL], lu = LRT [UA], kw = Kurier Wileński): ")
    paper = "lrt"

    while paper != "lrt" and paper != "le" and paper != "lr" and paper != "lp" and paper != "lu" and paper != "kw":
        paper = input ("Invalid choice. Choose a paper: ")

    # query = input ("Enter your query (blank queries are accepted): ")
    # from_date = input ("Enter a from date (YYYY-MM-DD): ")
    query = ""
    from_date = "2020-01-01"

    while True:
        try:
            date.fromisoformat (from_date)
        except ValueError as exception:
            from_date = input ("Invalid date. Enter a from date: ")
        else:
            break

    # to_date = input ("Enter a to date (YYYY-MM-DD, blank entry means today): ")
    to_date = "2020-02-19"

    while True:
        if not to_date.strip ():
            to_date = datetime.now ().isoformat () [: 10]
            print (f"Today is {to_date}")

        try:
            date.fromisoformat (to_date)
        except ValueError as exception:
            to_date = input ("Invalid date. Enter a to date: ")
        else:
            if from_date > to_date:
                to_date = input ("Invalid date. Enter a to date: ")
            else:
                break

    # concurrent = input ("Use concurrency (y/n, concurrency is faster, but more error-prone): ")
    concurrent = "y"

    while concurrent != "y" and concurrent != "n":
        paper = input ("Invalid choice. Use concurrency: ")

    concurrent = True if concurrent == "y" else False
    translator = Translate ([GoogleTranslate])

    if paper == "lrt":
        utilities.set_directory (os.path.join (os.getcwd (), "articles", "lrt", "lit"))
        download_all_lrt (query, from_date, to_date, "lit", translator, concurrent)
    elif paper == "le":
        utilities.set_directory (os.path.join (os.getcwd (), "articles", "lrt", "eng"))
        download_all_lrt (query, from_date, to_date, "eng", concurrent = concurrent)
    elif paper == "lr":
        utilities.set_directory (os.path.join (os.getcwd (), "articles", "lrt", "rus"))
        download_all_lrt (query, from_date, to_date, "rus", translator, concurrent)
    elif paper == "lp":
        utilities.set_directory (os.path.join (os.getcwd (), "articles", "lrt", "pol"))
        download_all_lrt (query, from_date, to_date, "pol", translator, concurrent)
    elif paper == "lu":
        utilities.set_directory (os.path.join (os.getcwd (), "articles", "lrt", "ukr"))
        download_all_lrt (query, from_date, to_date, "ukr", translator, concurrent)
    elif paper == "kw":
        utilities.set_directory (os.path.join (os.getcwd (), "articles", "kw"))
        download_all_kw (query, from_date, to_date, translator)
