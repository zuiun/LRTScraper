import os
import pdfkit
import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style
from concurrent import futures
from datetime import datetime

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

text: string = text to print

Pre: None
Post: None
Return: None
'''
def time_print (text):
    print (f"{Fore.YELLOW}{datetime.now ().strftime ('%H:%M:%S')}{Style.RESET_ALL}: {text}{Style.RESET_ALL}", flush = True)

'''
Converts file name to translated name

name: string = File name to translate

Pre: None
Post: None
Return: string = Converted file name
'''
def convert_name (name):
    return f"en_{name}"

'''

'''


'''
Imports a file

path: string = path to file

Pre: None
Post: None
Return: Response = response of file
'''
def import_file (path):
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

path: string = path to file

Pre: None
Post: None
Return: dict = JSON of file
'''
def import_json (path):
    return import_file (path).json () # Don't catch exceptions, as API failure should be fatal

'''
Formats a file for printing

file: BeautifulSoup = HTML of file

Pre: None
Post: None
Return: string = HTML of stripped file
'''
def format_html (file):
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
Downloads and translates an article as PDFs

information: tuple = page information (paths, date_times, translator, language)

Pre: None
Post: None
Return: bool = True if PDF conversion succeeded, else False
'''
def download_article (information):
    article, path, name = information
    time_print (f"Attempting article download for {path} as {name}")

    if os.path.exists (name):
        time_print (f"{Fore.RED}File creation error for {name}: File already exists")
    else:
        try:
            pdfkit.from_string (article, name, options = {"enable-local-file-access": ""})
        except Exception as exception:
            time_print (f"{Fore.RED}PDF conversion error for {name}: {exception}")
            return False

        time_print (f"{Fore.GREEN}Article download success for {name}")

    return True

'''
Downloads and translates an article as PDFs

information: tuple = page information (paths, date_times, translator, language)

Pre: None
Post: None
Return: bool = True if PDF conversion succeeded, else False
'''
def download_translation (information):
    article, path, name, translator, language = information
    time_print (f"Attempting article translation for {path} as {name}")

    if os.path.exists (name):
        time_print (f"{Fore.RED}File creation error for {name}: File already exists")
    else:
        try:
            article = translator.translate_html (article, destination_language = "eng", source_language = language)
        except Exception as exception:
            time_print (f"{Fore.RED}Article translation error for {name}: {exception}")
            return False

        try:
            pdfkit.from_string (article, name, options = {"enable-local-file-access": ""})
        except Exception as exception:
            time_print (f"{Fore.RED}PDF conversion error for {name}: {exception}")
            return False

        time_print (f"{Fore.GREEN}Article translation success for {name}")

    return True

'''
Downloads and translates a page

pages: list of tuples = article information (file, path, date_time, translator, language, number)

Pre: None
Post: None
Return: None
'''
def download_page (information):
    articles = []
    translations = []
    time_print (f"Downloading page {information [0] [4]}")

    for i in information:
        path, name, translator, language, _ = i

        if not os.path.exists (path) and not os.path.exists (convert_name (path)):
            article = import_file (path)
            article = BeautifulSoup (article.text, "html.parser")
            article = format_html (article)
            converted = convert_name (name)

            if not os.path.exists (path):
                articles.append ((article, path, name))

            if not os.path.exists (converted):
                translations.append ((article, path, converted, translator, language))

    with futures.ThreadPoolExecutor (44) as pool:
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

path: string = path to directory

Pre: None
Post: None
Return: string = new working directory
'''
def set_directory (path):
    if not os.path.exists (path):
        os.makedirs (path)

    os.chdir (path)
    print ("Working directory is " + path)
    return path
