from bs4 import BeautifulSoup
import requests
import datetime
import os
from story import Story
from settings import *


class Scraper:
    """
    Scraper class that scrapes CNET news site, gathers top stories' URLs and
    scrapes its content. It can save the results to a text file.
    """
    def __init__(self, config, logging=True, should_save=True,
                 fail_silently=False, file_name=None, file_full_path=False):
        """
        Constructor for the Scraper class
        Args:
            config (): Configuration object - Needed to define the way the site
                is scraped
            logging (): boolean - defines if program will print output to the
                console or not
            should_save (): boolean - can disable the data saving to the text
                file. Mainly for testing
            fail_silently (): boolean - if a story can't be scraped, it can stop
                the program execution or skip that particular one
            file_name (): string - file name to be used to save the data
            file_full_path (): boolean - determines if the provided file_name
                is a full path or just the name.
        """
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
        """
        Functions that runs the scraping process: gets the URLs for the top
        stories, scrapes them and saves the results.

        """
        self.scrape_main_page()
        self.scrape_stories()
        if self.should_save:
            self.save_results()

    def scrape_main_page(self):
        """
        Scrapes the main site to look for the top stories in the site. Given
        that the link point to a relative address, we build the full address for
        each story and saves the list of the URLs that point to the top stories.
        """
        page = requests.get(BASE_URL)
        soup = BeautifulSoup(page.content, 'html.parser')

        for pattern in self.config.main_urls_pattern:
            top_stories = soup.select(pattern[0])
            if len(top_stories) == 0:
                raise RuntimeError('Error! Scraping the main site to get the'
                                   'news list failed.')
            self.urls += [DOMAIN_URL + a.get(pattern[1]) for a in top_stories]

        if self.logging:
            print('{} stories will be scraped'.format(len(self.urls)))

    def scrape_stories(self):
        """
        Iterates over the existing URLs and calls the scraping method over each
        of them. Saves the result in an object variable.
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
        scraped, it tries to match the site's header to a known site structure
        and calls the content scraper if the structure is matched.
        If it doesn't match any of the known site structures, it will print an
        error message and raise an exception.
        If the scraper succeeds, it returns the scraped Story object.

        Args:
            url: URL for the story to be scraped
            index: index to be assigned to the Story object

        Returns:
            story: Story object with all the scraped information
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
        else:
            print('Warning! An error occurred when trying to scrape the story: '
                  '{}'.format(url))

    @staticmethod
    def _scrape_story_content(soup, template, index):
        """
        Scrapes the provided site's content according to the provided template
        structure looking for the title, description, authors and published
        date.
        Args:
            soup: BeautifulSoup object with the story site parsed
            template: template to be used to extract the desired content of the
                site
            index: index to be assigned to the Story object

        Returns:
            story: Story object with all the scraped information
        """
        s = {}

        for f in STORY_SCRAPE_FIELDS:
            element = soup.select(template[f['field']])
            if len(element) > 0:
                if not f['multiple']:
                    s[f['field']] = element[0].getText()
                else:
                    s[f['field']] = [el.getText() for el in element]
        try:
            story = Story(index + 1, s['title'], s['description'], s['date'],
                          s['authors'])
        except ValueError as e:
            print('Error! Something unexpected happened when scraping a story:')
            raise ValueError(e)

        return story

    def save_results(self):
        """
        Function that appends the information for the scraped stories appends it
        to a text file in a nicely formatted way, including the current
        datetime.
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
