from bs4 import BeautifulSoup
import requests
import datetime
import os


BASE_URL = "https://www.cnet.com/news/"
DOMAIN_URL = "https://www.cnet.com"
NEWS_UNKNOWN_STRUCTURE = "Can't scrape unknown website structure."


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


def scrape_regular_story(soup):
    """
    Scrapes a regular story site (most news follow this site structure, for
    example: https://www.cnet.com/news/amazon-sued-repeatedly-for-lost-wages-avoids-paying-workers-for-long-waits-and-walks/
    some can be different like the ones using Nuxt.js) looking for the title,
    description, authors and published date.
    Args:
        soup (): BeautifulSoup object with the story site parsed

    Returns:
        news_content: dictionary with the scraped data found in the site
    """
    news_content = {}
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

    return news_content


def scrape_nuxt_story(soup):
    """
    Scrapes a special Nuxt.js story site (full width image header,check example
    https://www.cnet.com/features/gps-rules-everything-a-satellite-launch-this-week-keeps-its-upgrade-rolling/
    ) looking for the title, description, authors and published date.
    Args:
        soup (): BeautifulSoup object with the story site parsed

    Returns:
        news_content: dictionary with the scraped data found in the site
    """
    news_content = {}
    title = soup.select('.c-globalHero_content h1.c-globalHero_heading')
    if len(title) > 0:
        news_content['title'] = title[0].getText()

    description_selector = '.c-globalHero_content p.c-globalHero_description'
    description = soup.select(description_selector)
    if len(description) > 0:
        news_content['description'] = description[0].getText()

    aut_sel = '.c-globalHero_content .c-globalAuthor_meta a.c-globalAuthor_link'
    authors = soup.select(aut_sel)
    if len(authors) > 0:
        news_content['authors'] = [a.getText() for a in authors]

    date = soup.select('.c-globalHero_content .c-globalAuthor_meta time')
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
        news_content: dict with scraped data if succeeds or error if not known
            site structure
    """
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    regular_header = soup.select('.content-header')

    if len(regular_header) > 0:
        news_content = scrape_regular_story(soup)
        news_content['url'] = url
        return news_content
    else:
        nuxt_header = soup.select('.c-globalHero_content')
        if len(nuxt_header) > 0:
            news_content = scrape_nuxt_story(soup)
            news_content['url'] = url
            return news_content
        else:
            return {'url': url, 'error': NEWS_UNKNOWN_STRUCTURE}


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
        authors, date, URL, and optionally 'error'.

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
