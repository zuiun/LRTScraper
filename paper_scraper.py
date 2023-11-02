# import argparse
# import calendar
import colorama
import math
# import multiprocessing
import os
import pdfkit
import requests
import time
from bs4 import BeautifulSoup
from collections.abc import Callable
from colorama import Fore, Style
from concurrent import futures
from datetime import date, datetime
from enum import auto, IntFlag
from translatepy import Translate
from translatepy.translators import GoogleTranslate

WORKING_DIRECTORY_BASE = None

class Download (IntFlag):
    ARTICLE = auto ()
    TRANSLATION = auto ()

'''
Prints text with timestamp

text: str = text to print

Pre: None
Post: None
Return: None
'''
def time_print (text: str):
    print (f"{Fore.YELLOW}{datetime.now ().strftime ('%H:%M:%S')}{Style.RESET_ALL}: {text}{Style.RESET_ALL}", flush = True)

'''
Imports a file

path: str = path to file

Pre: None
Post: None
Return: Response = response of file
'''
def import_file (path: str) -> requests.Response:
    try:
        file = requests.get (path, timeout = 10)
    except requests.exceptions.Timeout as exception:
        time_print (f"{Fore.RED}File timeout error for {path}: {exception}")
        return None
    except requests.exceptions.SSLError as exception:
        time_print (f"Retrying due to {Fore.RED}SSL error for {path}: {exception}")
        file = requests.get (path, timeout = 10, verify = False)

    try:
        file.raise_for_status ()
    except requests.exceptions.HTTPError as exception:
        time_print (f"{Fore.RED}File import error for {path}: {exception}")
        return None

    file.encoding = "UTF-8"
    return file

'''
Imports a file as JSON

path: str = path to file

Pre: None
Post: None
Return: dict = JSON of file
'''
def import_json (path: str) -> dict:
    return import_file (path).json () # Don't catch exceptions, as API failure should be fatal

'''
Formats a file for printing

file: BeautifulSoup = file to print

Pre: None
Post: None
Return: str = HTML of stripped file
'''
def format_html (file: BeautifulSoup) -> str:
    current = file.article.contents [0]

    # Remove content that isn't the main article
    for i in current.parents:
        if i.name == "body":
            break

        for j in i.find_previous_siblings ():
            j.decompose ()

        for j in i.find_next_siblings ():
            j.decompose ()

    for i in file.css.select ("script"):
        i.decompose ()

    for i in file.css.select ("style"):
        i.decompose ()

    # Remove elements specific to KW
    # for i in file.css.select ("div.td-is-sticky"):
    #     i.decompose ()

    # for i in file.css.select ("div.tdc-element-style"):
    #     i.decompose ()

    return file.prettify ()

'''
Converts an HTML string to PDF

file: str = file to convert
name: str = name of file
decorator: function = decorator for file
arguemnts: tuple = arguments for decorator

Pre: None
Post: None
Return: bool = True if PDF conversion succeeded, else False
'''
def convert_pdf (file: str, name: str, decorator: Callable [[str, tuple], str] = None, arguments: tuple = None) -> bool:
    time_print (f"Attempting PDF conversion for {name}")

    if os.path.exists (name):
        time_print (f"{Fore.RED}PDF conversion error for {name}: File already exists")
        return False
    else:
        if decorator:
            file = decorator (file, arguments)

        try:
            pdfkit.from_string (file, name, options = {"enable-local-file-access": ""})
        except Exception as exception:
            time_print (f"{Fore.RED}PDF conversion error for {name}: {exception}")
            return False

        return True

'''
Translates an HTML string to English

file: str = file to translate
arguments: tuple = translation information (name, translator, language)

Pre: None
Post: None
Return: str = Translated file
'''
def translate_file (file: str, arguments: tuple) -> str:
    name, translator, language = arguments
    time_print (f"Attempting file translation for {name}")

    try:
        file = translator.translate_html (file, destination_language = "eng", source_language = language)
    except Exception as exception:
        time_print (f"{Fore.RED}File translation error for {name}: {exception}")
        return None

    return file

'''
Downloads an article as PDF

information: tuple = page information (article, path, name, translator [optional], language [optional])

Pre: None
Post: None
Return: bool = True if PDF conversion succeeded, else False
'''
def download_article (information: tuple) -> bool:
    article, path, name, * translation = information
    time_print (f"Attempting article download for {path} as {name}")

    if len (translation) == 2 and convert_pdf (article, name, translate_file, (name, translation [0], translation [1])):
        time_print (f"{Fore.GREEN}Translation download success for {name}")
        return True
    elif convert_pdf (article, name):
        time_print (f"{Fore.GREEN}Article download success for {name}")
        return True
    else:
        time_print (f"{Fore.RED}Article download failure for {name}")
        return False

'''
Downloads and translates a page

information: list of tuples = article information (path, names (original, converted), translator, language, number, download)

Pre: None
Post: None
Return: list of tuples = article data (article, path, name, translator, language)
'''
def download_page (information: list) -> list:
    articles = []
    time_print (f"Downloading page {information [0] [4]}")

    for i in information:
        path, names, translator, language, _, download = i
        original, converted = names
        article = import_file (path)
        article = BeautifulSoup (article.text, "html.parser")
        article = format_html (article)

        if Download.ARTICLE in download:
            articles.append ((article, path, original))

        if Download.TRANSLATION in download:
            articles.append ((article, path, converted, translator, language))

    return articles

'''
Sets (and creates, if necessary) new working directory

path: str = path to directory

Pre: None
Post: None
Return: str = new working directory
'''
def set_directory (path: str) -> str:
    if not os.path.exists (path):
        os.makedirs (path)

    os.chdir (path)
    print ("Working directory is " + path)
    return path

'''
Downloads all LRT pages in a date range

query: str = search query
from_date: date = from date in ISO format
to_date: date = to date in ISO format
language: str = article language
translator: Translator = article translator

Pre: None
Post: Changes current working directory
Return: None
'''
def download_all_lrt (query: str, from_date: date, to_date: date, language: str, translator: Translate = None, concurrent: bool = True):
    category = ""

    if language == "lit":
        category = "order=desc"
    elif language == "rus":
        category = "category_id=17"
    elif language == "eng":
        category = "category_id=19"
    elif language == "pol":
        category = "category_id=1261"
    elif language == "ukr":
        category = "category_id=1263"

    # months = []
    # page = 0

    # for i in range (from_date.year, to_date.year - from_date.year):
    #     for j in range (from_date.month, to_date.month - from_date.month):
    #         month_start = date (i, j, 1)
    #         month_length = calendar.monthrange (month_start.year, month_start.month) [1]
    #         month_end = date (i, j, month_length)

    #         if j == from_date.month:
    #             months.append ((from_date, month_end))
    #         elif j == to_date.month:
    #             months.append ((month_start, to_date))
    #         else:
    #             months.append (month_start, month_end)

    # for i in months:
    #     page += 1
    #     api = import_json (f"https://www.lrt.lt/api/search?page={page}&q={query}&count=44&dfrom={i [0].isoformat ()}&dto={i [1].isoformat ()}&{category}")
    #     pages = []
    #     set_directory (WORKING_DIRECTORY_BASE, i [0].month)

    #     while len (api ["items"]) > 0:
    #         information = []
    #         time_print (f"Getting information for page {i} of {math.ceil (int (api ['total_found']) / 44)}")
    #         start = time.perf_counter ()
    #         downloaded = 0

    #         for j in api ["items"]:
    #             # If scraping Lithuanian articles, skip non-Lithuanian articles
    #             if j ["is_video"] == 0 and j ["is_audio"] == 0 and (language != "lit" or (j ["article_category_id"] != 17 and j ["article_category_id"] != 19 and j ["article_category_id"] != 1261 and j ["article_category_id"] != 1263)):
    #                 # TODO: Fix sports (article_category_id = 10, extremely slow)
    #                 if j ["article_category_id"] == 10:
    #                     continue

    #                 path = f"https://www.lrt.lt{j ['url']}"
    #                 name = f"{''.join (filter (lambda c: c not in '. :', j ['item_date']))}.pdf"
    #                 converted = f"en_{name}"
    #                 download = Download (0)

    #                 if not os.path.exists (name):
    #                     download |= Download.ARTICLE

    #                 if not os.path.exists (converted):
    #                     download |= Download.TRANSLATION

    #                 if Download.ARTICLE in download or Download.TRANSLATION in download:
    #                     information.append ((path, (name, converted), translator, language, i, download))

    #         if concurrent:
    #             if len (information) > 0:
    #                 pages.append (information)

    #             if len (pages) == PROCESSES:
    #                 # Maps each page to a thread
    #                 with futures.ThreadPoolExecutor (max_workers = THREADS) as pool:
    #                     articles, translations = zip (* pool.map (download_page, pages))

    #                 for i in range (len (pages)):
    #                     # Maps each article to a process
    #                     with multiprocessing.Pool (processes = PROCESSES) as pool:
    #                         downloaded = pool.map (download_article, articles [i]).count (True)
    #                         downloaded += pool.map (download_translation, translations [i]).count (True)
    #                         # time.sleep (TIMEOUT)
    #                         # pool.terminate ()

    #                 pages.clear ()
    #                 # processes = max (20): 
    #                 # processes = max (20): 
    #                 # processes = max (20): 
    #                 # processes = max (20): 
    #                 # average, processes = max (20): 
    #                 total = time.perf_counter () - start
    #                 time_print (f"{colorama.Fore.CYAN}Downloaded {downloaded} articles in {total} sec, {downloaded / total} articles / sec")
    #         elif len (information) > 0:
    #             articles, translations = download_page (information)

    #             for j in articles:
    #                 downloaded += download_article (j)

    #             for j in translations:
    #                 downloaded += download_translation (j)

    #             # ~ 0.40 articles / sec
    #             total = time.perf_counter () - start
    #             time_print (f"{colorama.Fore.CYAN}Downloaded {downloaded} articles in {total} sec, {downloaded / total} articles / sec{colorama.Style.RESET_ALL}")

    i = 1
    page = import_json (f"https://www.lrt.lt/api/search?page={i}&q={query}&count=44&dfrom={from_date.isoformat ()}&dto={to_date.isoformat ()}&{category}")
    pages = []
    total = math.ceil (int (page ['total_found']) / 44)

    while len (page ["items"]) > 0:
        information = []
        time_print (f"Getting information for page {i} of {total}")
        start = time.perf_counter ()
        downloaded = 0

        for j in page ["items"]:
            # If scraping Lithuanian articles, skip non-Lithuanian articles
            if j ["is_video"] == 0 and j ["is_audio"] == 0 and (language != "lit" or (j ["article_category_id"] != 17 and j ["article_category_id"] != 19 and j ["article_category_id"] != 1261 and j ["article_category_id"] != 1263)):
                # TODO: Fix sports (article_category_id = 10, extremely slow)
                if j ["article_category_id"] == 10:
                    continue

                path = f"https://www.lrt.lt{j ['url']}"
                name = f"{''.join (filter (lambda c: c not in '. :', j ['item_date']))}.pdf"
                converted = f"en_{name}"
                download = Download (0)

                if not os.path.exists (name):
                    download |= Download.ARTICLE

                if not os.path.exists (converted):
                    download |= Download.TRANSLATION

                if Download.ARTICLE in download or Download.TRANSLATION in download:
                    information.append ((path, (name, converted), translator, language, i, download))

        if concurrent:
            if len (information) > 0:
                pages.append (information)

            if len (pages) == 12 or i == total:
                # Maps each page to a thread
                with futures.ThreadPoolExecutor (max_workers = 44) as pool:
                    articles = pool.map (download_page, pages)
                    
                    for j in articles:
                        results = pool.map (download_article, j)
                        downloaded += list (results).count (True)

                pages.clear ()
                # ~ 0.20 - 0.80 articles / sec
                total = time.perf_counter () - start
                time_print (f"{Fore.CYAN}Downloaded {downloaded} articles in {total} sec, {downloaded / total} articles / sec")
        elif len (information) > 0:
            for j in download_page (information):
                downloaded += download_article (j)

            # ~ 0.40 articles / sec
            total = time.perf_counter () - start
            time_print (f"{Fore.CYAN}Downloaded {downloaded} articles in {total} sec, {downloaded / total} articles / sec{Style.RESET_ALL}")

        i += 1
        page = import_json (f"https://www.lrt.lt/api/search?page={i}&q={query}&count=44&dfrom={from_date.isoformat ()}&dto={to_date.isoformat ()}&{category}")

if __name__ == "__main__":
    colorama.init ()
    # paper = input ("Choose a paper (lrt = LRT [LT], le = LRT [EN], lr = LRT [RU], lp = LRT [PL], lu = LRT [UA], kw = Kurier Wileński): ")
    paper = "lrt"

    while paper != "lrt" and paper != "le" and paper != "lr" and paper != "lp" and paper != "lu":
        paper = input ("Invalid choice. Choose a paper: ")

    # query = input ("Enter your query (blank queries are accepted): ")
    # from_date = input ("Enter a from date (YYYY-MM-DD): ")
    query = ""
    from_date = "2023-05-01"

    while True:
        try:
            from_date = date.fromisoformat (from_date)
        except ValueError as exception:
            from_date = input ("Invalid date. Enter a from date: ")
        else:
            break

    # to_date = input ("Enter a to date (ISO, YYYY-MM-DD, blank entry means today): ")
    to_date = "2023-05-02"

    while True:
        if not to_date.strip ():
            to_date = date.today ()
            print (f"Today is {to_date}")

        try:
            to_date = date.fromisoformat (to_date)
        except ValueError as exception:
            to_date = input ("Invalid date. Enter a to date: ")
        else:
            if from_date > to_date:
                to_date = input ("Invalid date. Enter a to date: ")
            else:
                break

    # concurrent = input ("Use concurrency (y/n, concurrency is slower, but more reliable): ")
    concurrent = "y"

    while concurrent != "y" and concurrent != "n":
        concurrent = input ("Invalid choice. Use concurrency: ")

    concurrent = True if concurrent == "y" else False
    translator = Translate ([GoogleTranslate])

    if paper == "lrt":
        WORKING_DIRECTORY_BASE = set_directory (os.path.join (os.getcwd (), "articles", "lrt", "lit"))
        download_all_lrt (query, from_date, to_date, "lit", translator, concurrent)
    elif paper == "le":
        WORKING_DIRECTORY_BASE = set_directory (os.path.join (os.getcwd (), "articles", "lrt", "eng"))
        download_all_lrt (query, from_date, to_date, "eng", concurrent = concurrent)
    elif paper == "lr":
        WORKING_DIRECTORY_BASE = set_directory (os.path.join (os.getcwd (), "articles", "lrt", "rus"))
        download_all_lrt (query, from_date, to_date, "rus", translator, concurrent)
    elif paper == "lp":
        WORKING_DIRECTORY_BASE = set_directory (os.path.join (os.getcwd (), "articles", "lrt", "pol"))
        download_all_lrt (query, from_date, to_date, "pol", translator, concurrent)
    elif paper == "lu":
        WORKING_DIRECTORY_BASE = set_directory (os.path.join (os.getcwd (), "articles", "lrt", "ukr"))
        download_all_lrt (query, from_date, to_date, "ukr", translator, concurrent)
