import utilities

'''
Downloads an LRT page

page_number: int = page number
query: string = search query
from_date: string = from date in yyyy-mm-dd format
to_date: string = to date in yyyy-mm-dd format

Pre: None
Post: None
Return: dict = JSON of page API call
'''
def download_page_lrt (page_number, query, from_date, to_date):
    page = utilities.import_json (f"https://www.lrt.lt/api/search?page={page_number}&q={query}&count=44&dfrom={from_date}&dto={to_date}&order=desc")

    for i in page ["items"]:
        if not utilities.download_article (f"https://www.lrt.lt/{i ['url']}", filter (lambda c: c not in ". :", i ["item_date"])):
            print (f"PDF download error for {i ['title']}")

    return page

'''
Downloads all LRT pages in a date range

query: string = search query
from_date: string = from date in yyyy-mm-dd format
to_date: string = to date in yyyy-mm-dd format

Pre: None
Post: None
Return: None
'''
def download_all_lrt (query, from_date, to_date):
    i = 1
    page = download_page_lrt (i, query, from_date, to_date)

    while len (page ["items"]) > 0:
        i += 1
        page = download_page_lrt (i, query, from_date, to_date)

if __name__ == "__main__":
    utilities.set_directory ("articles")
    # download_all_lrt ("belarus", "2021-01-01", "2021-01-31")
