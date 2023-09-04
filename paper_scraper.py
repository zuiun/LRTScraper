from urllib.request import urlopen

def get_paper ():
    while (True):
        paper = input ("Choose paper (E/L/P/R): ")
        if (paper.upper () == "E"):
            return ("https://www.lrt.lt/en/search")
        if (paper.upper () == "L"):
            return ("https://www.lrt.lt/paieska")
        elif (paper.upper () == "P"):
            return ("https://kurierwilenski.lt/", "https://www.lrt.lt/pl/search")
        elif (paper.upper () == "R"):
            return ("https://www.kurier.lt/", "https://www.lrt.lt/ru/poisk")
        else:
            print ("Invalid option.")

print (urlopen (get_paper ()))

# Testing purposes
while (True):
    continue
