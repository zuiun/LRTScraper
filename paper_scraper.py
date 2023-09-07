import requests
from xhtml2pdf import pisa

'''
Imports a file

path: string = path to file

Pre: None
Post: None
Return: response = response of file
'''
def import_file (path):
    file = requests.get (path)

    try:
        file.raise_for_status ()
    except requests.exceptions.HTTPError:
        print (f"File import error for {path}: {requests.exceptions.HTTPError}")

    return file

'''
Imports a file as a JSON

path: string = path to file

Pre: None
Post: None
Return: JSON = JSON of file
'''
def import_json (path):
    return import_file (path).json () # Don't catch exceptions, as API failure is fatal

'''
Downloads an article as PDF

information: dict = information from page API call

Pre: None
Post: None
Return: bool = True if PDF conversion succeeded, else False
'''
def download_article (information):
    article = import_file (f"https://www.lrt.lt/{information ['url']}")
    file_name = filter (lambda i: i not in ". :", information ["item_date"]) + ".pdf" # File name given in specifications
    output = open (file_name, "w+b")
    status = pisa.CreatePDF (article, output)
    output.close ()
    return not status.err

'''
Downloads a page

page_number: int = page number
query: string = search query
from_date: string = from date in yyyy-mm-dd format
to_date: string = to date in yyyy-mm-dd format

Pre: None
Post: None
Return: dict = JSON of page API call
'''
def download_page (page_number, query, from_date, to_date):
    # LRT
    page = import_json (f"https://www.lrt.lt/api/search?page={page_number}&q={query}&count=44&dfrom={from_date}&dto={to_date}&order=desc")

    for i in page ["items"]:
        if not download_article (i):
            print (f"PDF download error for {i ['title']}")

    return page

'''
Downloads all pages in a date range

query: string = search query
from_date: string = from date in yyyy-mm-dd format
to_date: string = to date in yyyy-mm-dd format

Pre: None
Post: None
Return: None
'''
def download_all (query, from_date, to_date):
    i = 1
    page = download_page (i, query, from_date, to_date)

    while len (page ["items"]) > 0:
        i += 1
        page = download_page (i, query, from_date, to_date)

download_all ("belarus", "2021-01-01", "2021-01-31")
