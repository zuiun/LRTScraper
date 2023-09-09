import os
import pdfkit
import requests
# from bs4 import BeautifulSoup

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

html: string = HTML of file

Pre: None
Post: None
Return: string = HTML of stripped file
'''
# def format_html (html):
    # file = BeautifulSoup (html, "html.parser")
    # current = file.article.contents [0]

    # Remove content that isn't the main article
    # for i in current.parents:
    #     if i.name == "body":
    #         break

    #     for j in i.find_previous_siblings ():
    #         j.decompose ()

    #     for j in i.find_next_siblings ():
    #         j.decompose ()

    # for i in file.css.select ("script"):
    #     i.decompose ()

    # for i in file.css.select ("style"):
    #     i.decompose ()

    # Remove elements specific to KW
    # for i in file.css.select ("div.td-is-sticky"):
    #     i.decompose ()

    # for i in file.css.select ("div.tdc-element-style"):
    #     i.decompose ()

    # current = file.new_tag ("style")
    # current.string = "p { font-family: \"Times New Roman\" }"
    # file.head.append (current)
    # return file.prettify ()

'''
Downloads an article as PDF

path: string = path to article
date_time: string = date and time in YYYYMMDDHHmm format

Pre: None
Post: None
Return: bool = True if PDF conversion succeeded, else False
'''
def download_article (path, date_time):
    file = f"{date_time}.pdf"

    if os.path.exists (file):
        print (f"File creation error for {file}: File already exists")
        return False
    else:
        try:
            pdfkit.from_url (path, file)
        except Exception as exception:
            print (f"PDF conversion error for {path}: {exception}")
            return False

        print (f"PDF download success for {path}")
        return True

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
        download_article (paths [i], date_times [i])

def download_range (query, from_date, to_date, collector, parser):
    return None

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
    download_article ("https://www.lrt.lt/naujienos/sportas/10/2071596/kovosime-su-latvija-lietuva-iveike-issikvepusio-donciciaus-vedama-slovenija", "lrt")
    download_article ("https://www.kurier.lt/v-den-polonii-v-vilnyuse-projdet-besplatnyj-koncert/", "kurier")
    download_article ("https://kurierwilenski.lt/2023/09/07/naukowcy-o-uzaleznieniach-i-samobojstwach-wsrod-mlodziezy/", "kw")
