import requests
from urllib.request import urlopen

ENGLISH = "E"
LITHUANIAN = "L"
POLISH = "P"
RUSSIAN = "R"

# choose_papers
#
# Chooses papers based on language
#
# pre: none
# post: none
# return: list of strings = search URLs for papers
def choose_papers ():
    print (f"{ENGLISH}: LRT\n{LITHUANIAN}: LRT\n{POLISH}: KW, LRT\n{RUSSIAN}: K, LRT")

    while (True):
        paper = input (f"Choose paper ({ENGLISH}/{LITHUANIAN}/{POLISH}/{RUSSIAN}): ")
        if (paper.upper () == ENGLISH):
            return ["https://www.lrt.lt/en/search"]
        if (paper.upper () == LITHUANIAN):
            return ["https://www.lrt.lt/paieska"]
        elif (paper.upper () == POLISH):
            return ["https://kurierwilenski.lt/", "https://www.lrt.lt/pl/search"]
        elif (paper.upper () == RUSSIAN):
            # Kurier doesn't seem to open
            # return ["https://www.kurier.lt/", "https://www.lrt.lt/ru/poisk"]
            return ["https://www.lrt.lt/ru/poisk"]
        else:
            print ("Invalid option.")

def main ():
    websites = choose_papers ()

    for i in websites:
        print (urlopen (i))

    # LRT uses XHR requests
    # KW and Kurier use "[page/xx/]?s="

main ()
