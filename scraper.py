from bs4 import BeautifulSoup
import requests
import datetime
import os
from story import Story
from settings import *


class Scraper:
    def __init__(self, config, logging=True, should_save=True,
                 fail_silently=False, file_name=None, file_full_path=False):
        self.config = config
        self.logging = logging
        self.should_save = should_save
        self.fail_silently = fail_silently
        self.urls = []
        self.stories = []
        if self.should_save and file_name is None:
            raise ValueError('File name needs to be provided '
                             'if should_save=True')
        if file_full_path:
            file_dir = os.path.dirname(file_name)
            if file_dir:
                if not os.path.isdir(file_dir):
                    raise ValueError(ERROR_FILE_PATH)
            else:
                raise ValueError(ERROR_FILE_PATH)
            self.file_path = file_name
        else:
            self.file_path = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), file_name)

        if self.logging:
            print(CONSOLE_WELCOME_MESSAGE)
            print('=================================\n')

    def scrape(self):
        self.scrape_main_page()
        self.scrape_stories()
        if self.should_save:
            self.save_results()

    def scrape_main_page(self):
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
        page = requests.get(BASE_URL)
        soup = BeautifulSoup(page.content, 'html.parser')

        for pattern in self.config.main_urls_pattern:
            top_stories = soup.select(pattern[0])
            self.urls += [DOMAIN_URL + a.get(pattern[1]) for a in top_stories]

        if self.logging:
            print('{} stories will be scraped'.format(len(self.urls)))

    def scrape_stories(self):
        """
        Args:
            scrape_urls: urls of pages to scrape
            config: Configuration object to be used to scrape each URL
        Returns:
            scraped pages
        """

        for ix, url in enumerate(self.urls):
            if self.logging:
                print('Scraping story no. {}...'.format(ix + 1))
            story = self._scrape_story(url, ix)
            if story is not None:
                self.stories.append(story)
        if self.logging:
            print('{} stories were scraped!'.format(len(self.urls)))

    def _scrape_story(self, url, index):
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

        for template in self.config.templates:
            header = soup.select(template['header'])
            if len(header) > 0:
                story = self._scrape_story_content(soup, template, index)
                story.set_url(url)
                return story

        if not self.fail_silently:
            raise RuntimeError('An error occurred when trying to scrape '
                               'the story: {}'.format(url))

    @staticmethod
    def _scrape_story_content(soup, template, index):
        """
        Scrapes the provided site's content according to the provided template
        structure looking for the title, description, authors and published date.
        Args:
            soup: BeautifulSoup object with the story site parsed
            template: template to be used to extract the desired content of the site

        Returns:
            news_content: dictionary with the scraped data found in the site
        """
        s = {}

        for f in STORY_SCRAPE_FIELDS:
            element = soup.select(template[f['field']])
            if len(element) > 0:
                if not f['multiple']:
                    s[f['field']] = element[0].getText()
                else:
                    s[f['field']] = [el.getText() for el in element]
        story = Story(index + 1, s['title'], s['description'], s['date'],
                      s['authors'])

        return story

    def save_results(self):
        """
        Function that receives the scraped data and appends it to a text file in
        a nicely formatted way, including the current datetime.

        Args:
            results (): list of objects where each object contains data associated
            to each story. The attributes for a story are: title, description,
            authors, date, URL, and optionally 'error'.

        """
        with open(self.file_path, 'a') as f:
            f.write('Scraping session: {}\n'.format(
                datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")))
            f.write('====================\n')
            for story in self.stories:
                f.writelines(story.get_full_info_lines())
            f.write('====================\n\n')
        if self.logging:
            print('Results were saved!')
