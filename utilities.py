import os
import requests
from bs4 import BeautifulSoup, SoupStrainer
from xhtml2pdf import pisa

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
    except requests.exceptions.HTTPError:
        print (f"File import error for {path}: {requests.exceptions.HTTPError}")
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
Strips a file of unnecessary elements

file: string = HTML of file

Pre: None
Post: None
Return: string = HTML of stripped file
'''
def strip_file (file):
    article = SoupStrainer ("article")
    article = BeautifulSoup (file, "html.parser", parse_only = article)

    for i in article.css.select ("script"):
        i.extract ()

    for i in article.css.select ("style"):
        i.extract ()

    # Problems with KW
    for i in article.css.select ("div.td-is-sticky"):
        i.extract ()

    for i in article.css.select ("div.tdc-element-style"):
        i.extract ()

    return article.prettify ()

'''
Downloads an article as PDF

path: string = path to article
date_time: string = date and time in YYYYMMDDHHmm format

Pre: None
Post: None
Return: bool = True if PDF conversion succeeded, else False
'''
def download_article (path, date_time):
    if os.path.exists (f"{date_time}.pdf"):
        print (f"Download error for {path}: File already exists")
        return False
    else:
        article = import_file (path).text
        output = open (f"{date_time}.pdf", "w+b") # File name given in specifications
        article = strip_file (article)
        print (article)
        article = pisa.CreatePDF (article, output) # True if PDF conversion failed, else False
        output.close ()
        return not article.err

'''
Downloads a page

paths: list = list of article paths
date_times: list = list of article dates and times in YYYYMMDDHHmm format

Pre: None
Post: None
Return: None
'''
def download_page (paths, date_times):
    for i in range (len (paths)):
        if not utilities.download_article (paths [i], date_times [i]):
            print (f"PDF download error for {paths [i]}")

'''
Sets (and creates, if necessary) new working directory within current working directory

path: string = path to directory

Pre: None
Post: None
Return: None
'''
def set_directory (path):
    directory = os.path.join (os.getcwd (), path)

    if not os.path.exists (directory):
        os.makedirs (directory)

    os.chdir (directory)
    print ("Working directory is " + directory)

if __name__ == "__main__":
    # Download tests
    set_directory ("articles")
    # TODO: Fix encoding/font issues
    # download_article ("https://www.lrt.lt/naujienos/sportas/10/2071596/kovosime-su-latvija-lietuva-iveike-issikvepusio-donciciaus-vedama-slovenija", "lrt")
    # download_article ("https://www.kurier.lt/v-den-polonii-v-vilnyuse-projdet-besplatnyj-koncert/", "kurier")
    # download_article ("https://kurierwilenski.lt/2023/09/07/naukowcy-o-uzaleznieniach-i-samobojstwach-wsrod-mlodziezy/", "kw")
