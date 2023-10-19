import os
import pdfkit
import requests
from bs4 import BeautifulSoup
from collections.abc import Callable
from colorama import Fore, Style
from concurrent import futures
from datetime import datetime
from enum import auto, IntFlag

class Download (IntFlag):
    ARTICLE = auto ()
    TRANSLATION = auto ()

# class Page:
#     def __init__ (self, information, number, language = "auto", translator = None):
#         self.information = information
#         self.number = number
#         self.language = language
#         self.translator = translator

#     def __iter__ (self):
#         self.iterator = iter (self.information)
#         return self.iterator

#     def __next__ (self):
#         return next (self.iterator)

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
        print (f"{Fore.RED}File import error for {path}: {exception}")
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
    for i in file.css.select ("div.td-is-sticky"):
        i.decompose ()

    for i in file.css.select ("div.tdc-element-style"):
        i.decompose ()

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

        time_print (f"{Fore.GREEN}PDF conversion success for {name}")
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

information: tuple = page information (article, path, name)

Pre: None
Post: None
Return: bool = True if PDF conversion succeeded, else False
'''
def download_article (information: tuple) -> bool:
    article, path, name = information
    time_print (f"Attempting article download for {path} as {name}")

    if convert_pdf (article, name):
        time_print (f"{Fore.GREEN}Article download success for {name}")
        return True
    else:
        time_print (f"{Fore.RED}Article download failure for {name}")
        return False

'''
Translates an article as PDF

information: tuple = page information (article, path, name, translator, language)

Pre: None
Post: None
Return: bool = True if PDF conversion succeeded, else False
'''
def download_translation (information: tuple) -> bool:
    article, path, name, translator, language = information
    time_print (f"Attempting translation download for {path} as {name}")

    if convert_pdf (article, name, translate_file, (name, translator, language)):
        time_print (f"{Fore.GREEN}Translation download success for {name}")
        return True
    else:
        time_print (f"{Fore.RED}Translation download failure for {name}")
        return False

'''
Downloads and translates a page

information: list of tuples = article information (path, names (original, converted), translator, language, number, download)

Pre: None
Post: None
Return: None
'''
def download_page (information: list):
    articles = []
    translations = []
    time_print (f"Downloading page {information [0] [4]}")

    for i in information:
        path, names, translator, language, _, download = i
        original, converted = names

        if not os.path.exists (original) and not os.path.exists (converted):
            article = import_file (path)
            article = BeautifulSoup (article.text, "html.parser")
            article = format_html (article)

            if Download.ARTICLE in download:
                articles.append ((article, path, original))

            if Download.TRANSLATION in download:
                translations.append ((article, path, converted, translator, language))

    with futures.ThreadPoolExecutor (max_workers = 44) as pool:
        try:
            list (pool.map (download_article, articles, timeout = 30))
        except futures.TimeoutError:
            time_print (f"{Fore.RED}Timout on article download")

        try:
            list (pool.map (download_translation, translations, timeout = 30))
        except futures.TimeoutError:
            time_print (f"{Fore.RED}Timout on article translation")

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
