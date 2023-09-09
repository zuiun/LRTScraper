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

'''
Downloads all pages in a date range

website: string = website
collector: function = data collector for website, must return (paths, date_times) for download_page
args: dict = arguments for collector
    query: string = search query
    from_date: string = from date in YYYY-MM-DD format
    to_date: string = to date in YYYY-MM-DD format

Pre: None
Post: Changes current working directory
Return: None
'''
def download_range (website, collector, args):
    i = 1

    if website == "lrt":
        args ["path"] = "https://www.lrt.lt"
        args ["category"] = "order=desc"
    elif website == "kurier":
        args ["path"] = "https://www.kurier.lt"
        args ["a_selector"] = "div.post-item a.plain"
        args ["time_selector"] = "time.entry-date"
    elif website == "kw":
        args ["path"] = "https://kurierwilenski.lt"
        args ["a_selector"] = "div.tdb_module_loop h3.entry-title a"
        args ["time_selector"] = "time.entry-date"
    elif website == "lrt-en":
        args ["path"] = "https://www.lrt.lt"
        args ["category"] = "category_id=19"
    elif website == "lrt-ru":
        args ["path"] = "https://www.lrt.lt"
        args ["category"] = "category_id=17"
    elif website == "lrt-pl":
        args ["path"] = "https://www.lrt.lt"
        args ["category"] = "category_id=1261"
    else:
        print ("Invalid website")
        return

    args ["page_number"] = i
    information = collector (args)

    while information is not None:
        download_page (information [0], information [1])
        i += 1
        args ["page_number"] = i
        information = collector (args)

'''
Sets (and creates, if necessary) new working directory

path: string = path to directory

Pre: None
Post: None
Return: None
'''
def set_directory (path):
    if not os.path.exists (path):
        os.makedirs (path)

    os.chdir (path)
    print ("Working directory is " + path)

if __name__ == "__main__":
    # Download tests
    set_directory (os.path.join (os.getcwd (), "articles"))
    download_article ("https://www.lrt.lt/naujienos/sportas/10/2071596/kovosime-su-latvija-lietuva-iveike-issikvepusio-donciciaus-vedama-slovenija", "lrt")
    download_article ("https://www.kurier.lt/v-den-polonii-v-vilnyuse-projdet-besplatnyj-koncert/", "kurier")
    download_article ("https://kurierwilenski.lt/2023/09/07/naukowcy-o-uzaleznieniach-i-samobojstwach-wsrod-mlodziezy/", "kw")
