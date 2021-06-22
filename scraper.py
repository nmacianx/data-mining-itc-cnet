from bs4 import BeautifulSoup
import requests
import datetime
import os
from configuration import Configuration

BASE_URL = "https://www.cnet.com/news/"
DOMAIN_URL = "https://www.cnet.com"
NEWS_UNKNOWN_STRUCTURE = "Can't scrape unknown website structure."
DESTINATION_FILE_NAME = 'scraping.txt'
CONFIGURATION = Configuration(['#topStories > div > a[href]', '.moreTopStories .assetBody > a[href]'], [
    {
        'header': '.content-header',
        'title': '.content-header .c-head h1.speakableText',
        'description': '.content-header .c-head p.c-head_dek',
        'authors': '.content-header .c-assetAuthor_authors a.author',
        'date': '.content-header .c-assetAuthor_date time'
    },
    {
        'header': '.c-globalHero_content',
        'title': '.c-globalHero_content h1.c-globalHero_heading',
        'description': '.c-globalHero_content p.c-globalHero_description',
        'authors': '.c-globalHero_content .c-globalAuthor_meta a.c-globalAuthor_link',
        'date': '.c-globalHero_content .c-globalAuthor_meta time'
    }
])


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

    for pattern_to_search in CONFIGURATION.main_patterns_extract_urls:
        top_stories = soup.select(pattern_to_search[0])
        scrape_urls += [DOMAIN_URL + a.get(pattern_to_search[1]) for a in top_stories]

    return scrape_urls


def scrape_regular_story(soup, template):
    """
    Scrapes a regular story site (most news follow this site structure, for
    example: https://www.cnet.com/news/amazon-sued-repeatedly-for-lost-wages-avoids-paying-workers-for-long-waits-and-walks/
    some can be different like the ones using Nuxt.js) looking for the title,
    description, authors and published date.
    Args:
        soup (): BeautifulSoup object with the story site parsed
        template: template to use for extract elements from soup

    Returns:
        news_content: dictionary with the scraped data found in the site
    """
    news_content = {}
    header = soup.select(template['title'])
    if len(header) > 0:
        news_content['title'] = header[0].getText()

    description = soup.select(template['description'])
    if len(description) > 0:
        news_content['description'] = description[0].getText()

    authors = soup.select(template['authors'])
    if len(authors) > 0:
        news_content['authors'] = [a.getText() for a in authors]

    date = soup.select(template['date'])
    if len(date) > 0:
        news_content['date'] = date[0].getText()

    return news_content


def scrape_story(url):
    """
    Given an URL for a story, it first check if it follows the regular structure
    and calls the regular scraper. If it doesn't, it checks for the special full
    width image structure and calls it. Otherwise it returns an error message.
    If the scraper succeeds, it returns the scraped data.
    Args:
        url (): URL for the story to be scraped

    Returns:
        news_content: dict with scraped data if succeeds or error if not known site structure
    """
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    for template in CONFIGURATION.templates:
        header = soup.select(template['header'])

        if len(header) > 0:
            news_content = scrape_regular_story(soup, template)
            news_content['url'] = url

            return news_content

    return {'url': url, 'error': NEWS_UNKNOWN_STRUCTURE}


def scrape_stories(scrape_urls):
    """
    Scrape the pages for their urls

    :param scrape_urls: urls of pages to scrape
    :return: scraped pages
    """

    results = []

    for ix, news in enumerate(scrape_urls):
        print(f'Scraping story no. {ix + 1}...')
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
        authors, date, URL, and optionally 'error'.

    """
    file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), DESTINATION_FILE_NAME)
    with open(file_path, 'a') as f:
        f.write('Scraping session: {}\n'.format(
            datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")))
        f.write('====================\n')
        for ix, news in enumerate(results):
            f.write('\n\nStory {}:\n'.format(ix + 1))
            if 'title' in news:
                f.write('Title: {}\n'.format(news['title'].strip()))
            if 'description' in news:
                f.write('Description: {}\n'.format(news['description'].strip()))
            if 'authors' in news:
                authors = ', '.join(news['authors'])
                f.write('Author/s: {}\n'.format(authors.strip()))
            if 'date' in news:
                f.write('Published date: {}\n'.format(news['date'].strip()))
            if 'url' in news:
                f.write('URL: {}\n'.format(news['url']))
            if 'error' in news:
                f.write('Error: {}\n'.format(news['error']))
        f.write('====================\n\n')


def main():
    urls = scrape_main_page()
    print('{} stories will be scraped'.format(len(urls)))
    scrape_results = scrape_stories(urls)
    save_results(scrape_results)
    print('{} stories were scraped!'.format(len(urls)))


if __name__ == '__main__':
    main()
