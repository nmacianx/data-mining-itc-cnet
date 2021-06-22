# data-mining-itc-cnet

### Project description
This project is a Python web scraper required for the course **"Fellows - Data 
Science & Machine Learning"**, part of the Israel Tech Challenge Academy. More 
information can be found by visiting [itc.tech](https://www.itc.tech/).

Our specific project scrapes the top stories at CNET's news portal, 
[cnet.com/news](https://www.cnet.com/news/). It gets the URLs for the top
stories in the main site, and then scrapes each of the URLs gathering the title,
description, author/s and published data.

We've found so far two different site structures for Cnet's stories, and we will
try to scrape following these patterns. In case our scrapers finds an unknown 
pattern, it will not scrape it and save an error message in that case. Examples
of these two patterns are 
[this one](https://www.cnet.com/news/windows-11-everything-we-want-to-see-in-the-new-microsoft-os/)
and [this one](https://www.cnet.com/features/gps-rules-everything-a-satellite-launch-this-week-keeps-its-upgrade-rolling/).


### Requirements
This project was built using **Python 3.8.2**, so make sure you're running that 
version.
Create a virtual environment using `venv` and install all the dependencies 
listed in the file `requirements.txt` by running:

`pip install -r requirements.txt`

### Running the scraper
In order to run the scraper, activate your virtual environment and run:

`python scraper.py`

It will create a `scraping.txt` file with the scraped data and append data to 
the file each time it's run.

### Authors
- [Nicolas Macian](https://github.com/nmacianx/)
- [Alejandro Alberto Vidaurrázaga Iturmendi](https://github.com/Alejandro-Vidaurrazaga)