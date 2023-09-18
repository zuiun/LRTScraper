import os
import pdfkit
import requests
from bs4 import BeautifulSoup
from translatepy import Translate

'''
Imports a file

path: string = path to file

Pre: None
Post: None
Return: Response = response of file
'''
def import_file (path):
    file = requests.get (path)

    try:
        file.raise_for_status ()
    except requests.exceptions.HTTPError as exception:
        print (f"File import error for {path}: {exception}")
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
Downloads an article as PDF

path: string = path to article
date_time: string = date and time in YYYYMMDDHHmm format

Pre: None
Post: None
Return: bool = True if PDF conversion succeeded, else False
'''
def download_article (path, date_time, translator, language):
    file = f"{date_time}.pdf"
    print (f"Attempting article download for {path} as {file}")

    if os.path.exists (file):
        print (f"File creation error for {file}: File already exists")
        return False
    else:
        try:
            pdfkit.from_url (path, file)
        except Exception as exception:
            print (f"PDF conversion error for {file}: {exception}")
            return False

        print (f"Article download success for {file}")
    
    if translator:
        file = f"en_{file}"
        print (f"Attempting article translation for {path} as {file}")
        article = import_file (path)
        article = BeautifulSoup (article.text, "html.parser")
        article = format_html (article)

        try:
            article = translator.translate_html (article, destination_language = "eng", source_language = language)
        except Exception as exception:
            print (f"Article translation error for {file}: {exception}")
            return False

        try:
            pdfkit.from_string (article, file, options = {"enable-local-file-access": ""})
        except Exception as exception:
            print (f"PDF conversion error for {file}: {exception}")
            return False

        print (f"Article translation success for {file}")
        return True

    return True

'''
Downloads a page

paths: list = list of article paths
date_times: list = list of article dates and times in YYYYMMDDHHmm format

Pre: None
Post: None
Return: None
'''
def download_page (paths, date_times, translator = None, language = "auto"):
    for i in range (len (paths)):
        download_article (paths [i], date_times [i], translator, language)

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
