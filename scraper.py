from bs4 import BeautifulSoup
import requests
import datetime
import os
from configuration import Configuration
from settings import *


def scrape_main_page(config):
    """
    Scrapes the main site to look for the top 13 stories in the site. Given that
    the link point to a relative address, we build the full address for each
    story and return a list of the URLs that point to the top stories.

    Args:
        config: Configuration object that includes the patterns to extract from
            the main page

    Returns:
    scrape_urls: list of URLs to the top stories in the site.
    """
    scrape_urls = []
    page = requests.get(BASE_URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    for pattern_to_search in config.main_urls_pattern:
        top_stories = soup.select(pattern_to_search[0])
        scrape_urls += [DOMAIN_URL + a.get(pattern_to_search[1])
                        for a in top_stories]

    return scrape_urls


def scrape_story_content(soup, template):
    """
    Scrapes the provided site's content according to the provided template
    structure looking for the title, description, authors and published date.
    Args:
        soup: BeautifulSoup object with the story site parsed
        template: template to be used to extract the desired content of the site

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


def scrape_story(url, config):
    """
    Given an URL for a story and the configuration for the content to be
    scraped, it first tries to match the site's header to a known site structure
    and calls the content scraper if the structure is matched. \
    If it doesn't match any of the known site structures, it will returns an
    error message.
    If the scraper succeeds, it returns the scraped data.

    Args:
        url: URL for the story to be scraped
        config: Configuration object to be used to scrape each URL

    Returns:
        news_content: dict with scraped data if succeeds or error if not known
            site structure
    """
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    for template in config.templates:
        header = soup.select(template['header'])

        if len(header) > 0:
            news_content = scrape_story_content(soup, template)
            news_content['url'] = url

            return news_content

    return {'url': url, 'error': NEWS_UNKNOWN_STRUCTURE}


def scrape_stories(scrape_urls, config):
    """
    Scrape the provided URLs to get their data

    Args:
        scrape_urls: urls of pages to scrape
        config: Configuration object to be used to scrape each URL

    Returns:
         scraped pages
    """

    results = []

    for ix, news in enumerate(scrape_urls):
        print(f'Scraping story no. {ix + 1}...')
        content = scrape_story(news, config)
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
    config = Configuration(CONFIG_MAIN_PATTERN, CONFIG_TEMPLATES)
    print(CONSOLE_WELCOME_MESSAGE)
    print('=================================\n')
    urls = scrape_main_page(config)
    print('{} stories will be scraped'.format(len(urls)))
    scrape_results = scrape_stories(urls, config)
    save_results(scrape_results)
    print('{} stories were scraped!'.format(len(urls)))


if __name__ == '__main__':
    main()
