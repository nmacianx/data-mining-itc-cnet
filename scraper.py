from bs4 import BeautifulSoup
import requests
import datetime
import os


BASE_URL = "https://www.cnet.com/news/"
DOMAIN_URL = "https://www.cnet.com"

page = requests.get(BASE_URL)
soup = BeautifulSoup(page.content, 'html.parser')
scrape_urls = []
# print(soup.prettify())

top_stories = soup.select('#topStories > div > a')
scrape_urls += [DOMAIN_URL + a.get('href') for a in top_stories]

more_top_stories = soup.find(class_='moreTopStories')
more_links = more_top_stories.select('.assetBody > a')
scrape_urls += [DOMAIN_URL + a.get('href') for a in more_links]
# We have all the top stories URLs
print('{} stories will be scraped'.format(len(scrape_urls)))

# Now we scrape each story
results = []
for ix, news in enumerate(scrape_urls):
    print('Scraping story no. {}...'.format(ix + 1))
    news_content = {}
    page = requests.get(news)
    soup = BeautifulSoup(page.content, 'html.parser')

    header = soup.select('.content-header .c-head h1.speakableText')
    if len(header) > 0:
        news_content['title'] = header[0].getText()

    description = soup.select('.content-header .c-head p.c-head_dek')
    if len(description) > 0:
        news_content['description'] = description[0].getText()

    authors = soup.select('.content-header .c-assetAuthor_authors a.author')
    if len(authors) > 0:
        news_content['authors'] = [a.getText() for a in authors]

    date = soup.select('.content-header .c-assetAuthor_date time')
    if len(date) > 0:
        news_content['date'] = date[0].getText()
    results.append(news_content)

file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'scraping.txt')
with open(file_path, 'a') as f:
    f.write('Scraping session: {}\n'.format(
        datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")))
    f.write('====================\n')
    for ix, news in enumerate(results):
        f.write('\n\nStory {}:\n'.format(ix + 1))
        if 'title' in news:
            f.write('Title: {}\n'.format(news['title']))
        if 'description' in news:
            f.write('Description: {}\n'.format(news['description']))
        if 'authors' in news:
            authors = ', '.join(news['authors'])
            f.write('Author/s: {}\n'.format(authors))
        if 'date' in news:
            f.write('Published date: {}\n'.format(news['date']))
