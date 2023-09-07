import requests

'''
Downloads an article

Pre: None
Post: None
Return: None
'''
def download_article ():
    return None

'''
Downloads a page

page_number: int = page number
query: string = search query
from_date: string = from date in yyyy-mm-dd format
to_date: string = to date in yyyy-mm-dd format

Pre: None
Post: None
Return: JSON = JSON of page API call
'''
def download_page (page_number, query, from_date, to_date):
    # LRT
    page = requests.get (f"https://www.lrt.lt/api/search?page={page_number}&q={query}&count=44&dfrom={from_date}&dto={to_date}&order=desc")
    page = page.json ()

    for i in page ["items"]:
        download_article ()

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

    while (len (page ["items"]) > 0):
        page = download_page (i, query, from_date, to_date)
        i += 1

download_all ("belarus", "2021-01-01", "2021-01-31")

while (True):
    continue
