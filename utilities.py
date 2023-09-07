import os
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
Return: dict = JSON of file
'''
def import_json (path):
    return import_file (path).json () # Don't catch exceptions, as API failure should be fatal

'''
Downloads an article as PDF

url: dict = information from page API call

Pre: None
Post: None
Return: bool = True if PDF conversion succeeded, else False
'''
def download_article (url, date):
    article = import_file (url)
    file_name = date + ".pdf" # File name given in specifications
    output = open (file_name, "w+b")
    status = pisa.CreatePDF (article, output) # True if PDF conversion failed, else False
    output.close ()
    return not status.err

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
