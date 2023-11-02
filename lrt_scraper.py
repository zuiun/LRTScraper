import calendar
import colorama
import math
# import multiprocessing
import os
import pdfkit
import requests
import sys
import time
from argparse import ArgumentParser, SUPPRESS
from bs4 import BeautifulSoup
from collections.abc import Callable
from colorama import Fore, Style
from concurrent import futures
from datetime import date, datetime
from enum import auto, IntFlag
from translatepy import Translate
from translatepy.translators import GoogleTranslate

WORKING_DIRECTORY_BASE = None
PAGES = 12
# There are 44 articles per page
PROCESSES = 44
LANGUAGES = ["lit", "eng", "rus", "pol", "ukr"]

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
    time_print (f"Attempting article translation for {name}")

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
Downloads all pages in a date range

query: str = search query
from_date: date = search from date
to_date: date = search to date
language: str = article language
translator: Translator = article translator

Pre: None
Post: Changes current working directory
Return: None
'''
def download_all (query: str, from_date: date, to_date: date, language: str, translator: Translate = None, concurrent: bool = True):
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

    for i in range (from_date.year, to_date.year + 1):
        year_base = set_directory (os.path.join (WORKING_DIRECTORY_BASE, str (i)))

        for j in range (1, 13):
            if date (i, j, from_date.day) >= from_date and date (i, j, 1) <= to_date:
                set_directory (os.path.join (year_base, f"0{j}" if j < 10 else str (j)))
                month_start = date (i, j, 1)
                month_length = calendar.monthrange (month_start.year, month_start.month) [1]
                month_end = date (i, j, month_length)

                if j == from_date.month:
                    month = (from_date, month_end)
                elif j == to_date.month:
                    month = (month_start, to_date)
                else:
                    month = (month_start, month_end)

                k = 1
                search = import_json (f"https://www.lrt.lt/api/search?page={k}&q={query}&count=44&dfrom={month [0].isoformat ()}&dto={month [1].isoformat ()}&{category}")
                pages = []
                total = math.ceil (int (search ['total_found']) / 44)

                while len (search ["items"]) > 0:
                    page = []
                    time_print (f"Getting information for page {k} of {total}")
                    start = time.perf_counter ()
                    downloads = 0

                    for j in search ["items"]:
                        # If scraping Lithuanian articles, skip non-Lithuanian articles
                        if j ["is_video"] == 0 and j ["is_audio"] == 0 and (language != "lit" or (j ["article_category_id"] != 17 and j ["article_category_id"] != 19 and j ["article_category_id"] != 1261 and j ["article_category_id"] != 1263)):
                            # Skip sports (article_category_id = 10, extremely slow)
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
                                page.append ((path, (name, converted), translator, language, k, download))

                    if concurrent:
                        if len (page) > 0:
                            pages.append (page)

                        if len (pages) == PAGES or k == total:
                            with futures.ThreadPoolExecutor (max_workers = PROCESSES) as pool:
                                articles = [k for j in pool.map (download_page, pages) for k in j]
                                articles = pool.map (download_article, articles)
                                downloads += list (articles).count (True)

                            pages.clear ()
                    elif len (page) > 0:
                        for j in download_page (page):
                            downloads += download_article (j)

                    # concurrent ~= 0.20 - 0.80 articles / sec
                    # sequential ~= 0.40 articles / sec
                    if downloads > 0:
                        total = round (time.perf_counter () - start)
                        time_print (f"{Fore.CYAN}Downloaded {downloads} articles in {total} sec, {round (downloads / total, 2)} articles / sec{Style.RESET_ALL}")

                    k += 1
                    search = import_json (f"https://www.lrt.lt/api/search?page={k}&q={query}&count=44&dfrom={month [0].isoformat ()}&dto={month [1].isoformat ()}&{category}")

if __name__ == "__main__":
    parser = ArgumentParser (prog = "LRT Scraper", description = "Web scraper for LRT, Lithuania's largest news service.")
    parser.add_argument ("-l", "--language", choices = LANGUAGES, default = SUPPRESS, help = "article language")
    parser.add_argument ("-q", "--query", nargs = "?", const = "", default = SUPPRESS, help = "search query (blank accepted)")
    parser.add_argument ("-f", "--from", dest = "from_date", default = SUPPRESS, help = "search from date (ISO, YYYY-MM-DD)")
    parser.add_argument ("-t", "--to", nargs = "?", const = "", dest = "to_date", default = SUPPRESS, help = "search to date (ISO, YYYY-MM-DD, blank means today)")
    parser.add_argument ("-c", "--concurrent", action = "store_true", default = SUPPRESS, help = "use concurrency (may be faster and more reliable)")
    parser.add_argument ("-v", "--verbose", action = "store_true")
    arguments = parser.parse_args ()
    colorama.init ()
    language = arguments.language if "language" in arguments else input ("Choose a language (lit, eng, rus, pol, ukr): ")

    while language not in LANGUAGES:
        language = input ("Invalid choice. Choose a language: ")

    query = arguments.query if "query" in arguments else input ("Enter your query (blank queries are accepted): ")
    from_date = arguments.from_date if "from_date" in arguments else input ("Enter a from date (ISO, YYYY-MM-DD): ")

    while True:
        try:
            from_date = date.fromisoformat (from_date)
        except ValueError as exception:
            from_date = input ("Invalid date. Enter a from date: ")
        else:
            break

    to_date = arguments.to_date if "to_date" in arguments else input ("Enter a to date (ISO, YYYY-MM-DD, blank entry means today): ")

    while True:
        if not to_date.strip ():
            to_date = date.today ()
            print (f"Using today ({to_date}) as to date")
            break

        try:
            to_date = date.fromisoformat (to_date)
        except ValueError as exception:
            to_date = input ("Invalid date. Enter a to date: ")
        else:
            if from_date > to_date:
                to_date = input ("Invalid date. Enter a to date: ")
            else:
                break

    concurrent = arguments.concurrent if "concurrent" in arguments else input ("Use concurrency (y/n, may be faster and more reliable): ")

    while concurrent != "y" and concurrent != "n" and concurrent != True and concurrent != False:
        concurrent = input ("Invalid choice. Use concurrency: ")

    if concurrent == "y":
        concurrent = True
    elif concurrent == "n":
        concurrent = False

    translator = None if language == "eng" else Translate ([GoogleTranslate])
    global verbose
    verbose = arguments.verbose
    WORKING_DIRECTORY_BASE = set_directory (os.path.join (os.getcwd (), "articles", language))
    download_all (query, from_date, to_date, language, translator, concurrent)
