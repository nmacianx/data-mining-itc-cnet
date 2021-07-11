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

In order to run the scraper in `author` mode, Selenium is used to scrape the 
URLs and it requires a ChromeDriver that can be downloaded from 
[here](https://chromedriver.chromium.org/downloads). Note: the chrome driver
version needs to match your local Chrome version (Google Chrome is a 
requirement).

Save the `chromedriver` executable inside the folder `/chromedriver/` in this
project.

### Running the scraper
In order to run the scraper, activate your virtual environment and run:

`python main.py [-h] [-a AUTHOR] [-t TAG] [-c] [-v] {top_stories,tag,author}`

* Mandatory arguments:
    - mode: can be `top_stories`, `tag` or `author`.
    - `-a --author`: author to scrape if mode = `author`.
    - `-t --tag`: tag to scrape if mode = `tag`.
* Optional arguments:
    - `-n --number`: limit the number of stories to scrape.
    - `-h --help`: get help for running the scraper.
    - `-c --console`: print the results to the console instead of saving them.
    - `-v --verbose`: log status information to the console while running the 
      scraper.

It will create a `scraping.txt` file with the scraped data and append data to 
the file each time it's run.

### Database design
In order to save the scraped information as well as to give it a better sense, a database 
was designed. In order to work with this database, the script `data_mining.sql` must be executed. 
Below is a view of the structure of the tables that make up said database.


<table>
    <tr>
      <th colspan="2" >Article</th>
    </tr>
    <tr>
      <tr>
      <th>Name</th>
      <th>Type</th>
    </tr>
    <tr>
      <td>id_article</td>
      <td>int(11)</td>
    </tr>
    <tr>
      <td>title</td>
      <td>varchar(255)</td>
    </tr>
    <tr>
      <td>date</td>
      <td>varchar(255)</td>
    </tr>
    <tr>
      <td>url</td>
      <td>varchar(255)</td>
    </tr>
</table>
Save the information regarding the scraped stories

<table>
    <tr>
      <th colspan="2" >Author</th>
    </tr>
    <tr>
      <tr>
      <th>Name</th>
      <th>Type</th>
    </tr>
    <tr>
      <td>id_author</td>
      <td>int(11)</td>
    </tr>
    <tr>
      <td>nick_name</td>
      <td>varchar(255)</td>
    </tr>
    <tr>
      <td>name</td>
      <td>varchar(255)</td>
    </tr>
    <tr>
      <td>location</td>
      <td>varchar(255)</td>
    </tr>
    <tr>
      <td>occupation</td>
      <td>varchar(255)</td>
    </tr>
    <tr>
      <td>url</td>
      <td>varchar(255)</td>
    </tr>
    <tr>
      <td>member_since</td>
      <td>varchar(255)</td>
    </tr>
</table>

Save the information regarding the authors of the scraped stories

<table>
    <tr>
      <th colspan="2" >Hashtags</th>
    </tr>
    <tr>
      <tr>
      <th>Name</th>
      <th>Type</th>
    </tr>
    <tr>
      <td>id_hashtag</td>
      <td>int(11)</td>
    </tr>
    <tr>
      <td>name</td>
      <td>varchar(255)</td>
    </tr>
    <tr>
      <td>url</td>
      <td>varchar(255)</td>
    </tr>
    <tr>
      <td>is_topic</td>
      <td>bit(1)</td>
    </tr>
</table>

Save the information regarding the tags of the scraped stories

<table>
    <tr>
      <th colspan="2">Article_author</th>
    </tr>
    <tr>
      <tr>
      <th>Name</th>
      <th>Type</th>
    </tr>
    <tr>
      <td>id_article_author</td>
      <td>int(11)</td>
    </tr>
    <tr>
      <td>id_article</td>
      <td>int(11)</td>
    </tr>
    <tr>
      <td>is_author</td>
      <td>int(11)</td>
    </tr>
</table>

Save the relationship between a story and its authors

<table>
    <tr>
      <th colspan="2">Article_hashtag</th>
    </tr>
    <tr>
      <tr>
      <th>Name</th>
      <th>Type</th>
    </tr>
    <tr>
      <td>id_article_hashtag</td>
      <td>int(11)</td>
    </tr>
    <tr>
      <td>id_article</td>
      <td>int(11)</td>
    </tr>
    <tr>
      <td>is_hashtag</td>
      <td>int(11)</td>
    </tr>
</table>

Save the relationship between a story and its tags

### Authors
- [Nicolas Macian](https://github.com/nmacianx/)
- [Alejandro Alberto Vidaurrázaga Iturmendi](https://github.com/Alejandro-Vidaurrazaga)