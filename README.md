# LRT Scraper

Web scraper for [LRT](https://www.lrt.lt/), Lithuania's largest news service.

## Installation

Paper Scraper uses [Python 3](https://www.python.org/) and requires multiple packages and one external program.
```
python -m pip install -r requirements.txt
```
pdfkit requires wkhtmltopdf, which can be found [here](https://wkhtmltopdf.org/).
wkhtmltopdf should be added to the system path, which is explained [here](https://stackoverflow.com/a/48511113).
You may choose not to do this if you know how to change pdfkit's path to wkhtmltopdf.

## Usage

Run `lrt_scraper.py` and follow the directions.
