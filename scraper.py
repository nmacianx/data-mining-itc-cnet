from bs4 import BeautifulSoup
import requests
import datetime
import os


BASE_URL = "https://www.cnet.com/news/"
DOMAIN_URL = "https://www.cnet.com"


def scrape_main_page():
    """
    Scrapes the main site to look for the top 13 stories in the site. Given that
    the link point to a relative address, we build the full address for each
    story and return a list of the URLs that point to the top stories.

    Returns:
    scrape_urls: list of URLs to the top stories in the site.
    """
    scrape_urls = []
    page = requests.get(BASE_URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    top_stories = soup.select('#topStories > div > a')
    scrape_urls += [DOMAIN_URL + a.get('href') for a in top_stories]

    more_top_stories = soup.find(class_='moreTopStories')
    more_links = more_top_stories.select('.assetBody > a')
    scrape_urls += [DOMAIN_URL + a.get('href') for a in more_links]

    return scrape_urls


def scrape_story(url):
    news_content = {}
    page = requests.get(url)
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

    news_content['url'] = url

    return news_content


def scrape_stories(scrape_urls):
    results = []
    for ix, news in enumerate(scrape_urls):
        print('Scraping story no. {}...'.format(ix + 1))
        content = scrape_story(news)
        results.append(content)
    return results


def save_results(results):
    """
    Function that receives the scraped data and appends it to a text file in
    a nicely formatted way, including the current datetime.

    Args:
        results (): list of objects where each object contains data associated
        to each story. The attributes for a story are: title, description,
        authors, date and URL.

    """
    file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'scraping.txt')
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
            if 'url' in news:
                f.write('URL: {}\n'.format(news['url']))
        f.write('====================\n\n')


def main():
    urls = scrape_main_page()
    print('{} stories will be scraped'.format(len(urls)))
    scrape_results = scrape_stories(urls)
    save_results(scrape_results)


if __name__ == '__main__':
    main()
