from bs4 import BeautifulSoup
import requests
import datetime
import os
from story import Story
from author import Author
from settings import *


class Scraper:
    """
    Scraper class that scrapes CNET news site, gathers top stories' URLs and
    scrapes its content. It can save the results to a text file.
    """
    def __init__(self, config, logging=True, should_save=True,
                 mode=MODE_TOP_STORIES, fail_silently=False, file_name=None,
                 file_full_path=False, author=None, tag=None):
        """
        Constructor for the Scraper class
        Args:
            config: Configuration object - Needed to define the way the site
                is scraped
            logging: boolean - defines if program will print output to the
                console or not
            mode: can either be 'top_stories', 'author' or 'tag'. Will
                determine the scraper entry point.
            should_save: boolean - can disable the data saving to the text
                file. Mainly for testing
            fail_silently: boolean - if a story can't be scraped, it can stop
                the program execution or skip that particular one
            file_name: string - file name to be used to save the data
            file_full_path: boolean - determines if the provided file_name
                is a full path or just the name.
            author: author to scrape if mode is set to author.
            tag: tag to scrape if mode is set to tag.
        """
        self.config = config
        self.logging = logging
        self.should_save = should_save
        self.fail_silently = fail_silently
        self.urls = []
        self.stories = []
        self.authors = []
        self.author = author
        self.tag = tag

        if mode not in SCRAPE_MODE:
            raise ValueError('Scrape mode can only take one of the three '
                             'values: top_stories, author or tag')
        self.mode = mode
        if self.mode == MODE_AUTHOR and author is None:
            raise AttributeError('An author needs to be passed to the scraper '
                                 'because author mode was set.')
        if self.mode == MODE_TAG and tag is None:
            raise AttributeError('A tag needs to be passed to the scraper '
                                 'because tag mode was set.')

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
        self.scrape_top_stories_page()
        self.scrape_stories()
        if self.should_save:
            self.save_results()
        else:
            self.print_results()

    def scrape_top_stories_page(self):
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

        for template in self.config.story_templates:
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

    def _scrape_story_content(self, soup, template, index):
        """
        Scrapes the provided site's content according to the provided template
        structure looking for the title, description, authors and published
        date. It call a function to get or create the authors if they haven't
        been scraped before.
        Args:
            soup: BeautifulSoup object with the story site parsed
            template: template to be used to extract the desired content of the
                site
            index: index to be assigned to the Story object

        Returns:
            story: Story object with all the scraped information
        """
        s = self._scrape_obj(soup, template, STORY_SCRAPE_FIELDS)
        authors = [a.split('profiles/')[1][:-1] for a in s['authors']]
        authors_created = self._get_or_create_authors(authors)
        try:
            story = Story(index + 1, s['title'], s['description'], s['date'],
                          authors_created)
        except ValueError as e:
            print('Error! Something unexpected happened when scraping a story:')
            raise ValueError(e)

        return story

    @staticmethod
    def _scrape_obj(soup, template, fields):
        """
        Function that retrieves the fields specified according to a template in
        the provided site parsed by BS4.
        Args:
            soup: BeautifulSoup instance of a site to scrape an object's data
            template: template to be used to extract the desired content of the
                site.
            fields: dictionary of fields to scrape according to a template. It
                provides configuration for how to get the values.

        Returns:
            s: dictionary of scraped object with the attributes retrieved.
        """
        s = {}
        for f in fields:
            element = soup.select(template[f['field']])
            if len(element) > 0:
                if 'attr' not in f:
                    if not f['multiple']:
                        s[f['field']] = element[0].getText()
                    else:
                        s[f['field']] = [el.getText() for el in element]
                else:
                    if not f['multiple']:
                        s[f['field']] = element[0][f['attr']]
                    else:
                        s[f['field']] = [el[f['attr']] for el in element]
            elif 'optional' in f and f['optional']:
                s[f['field']] = None
        return s

    def _scrape_author(self, username):
        page = requests.get(BASE_AUTHOR_URL + username)
        soup = BeautifulSoup(page.content, 'html.parser')
        template = self.config.get_author_template()
        s = self._scrape_obj(soup, template, AUTHOR_SCRAPE_FIELDS)
        for field in AUTHOR_SCRAPE_FIELDS:
            if field['field'] not in s:
                print('Error! Something unexpected happened when scraping '
                      'an Author:')
                raise RuntimeError("Field '{}' is missing when trying "
                                   "to scrape Author: {}".format(field['field'],
                                                                 username))

        try:
            author = Author(username, s['name'], s['member_since'],
                            location=s['location'], occupation=s['occupation'],
                            website=s['website'])
        except ValueError as e:
            print('Error! Something unexpected happened when scraping the '
                  'Author: {}'.format(username))
            raise ValueError(e)
        self.authors.append(author)
        return author

    def _get_or_create_authors(self, authors):
        result = []
        for a in authors:
            found = None
            for author_obj in self.authors:
                if a == author_obj.get_username():
                    found = author_obj
            if found is not None:
                result.append(found)
            else:
                result.append(self._scrape_author(a))
        return result

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
        #  TODO: Need to save data to the database, add Author data

    def print_results(self):
        """
        Function that prints to the console the information for the scraped
        stories in a nicely formatted way, including the current
        datetime. It also prints the information for the authors of those
        stories.
        """
        print('Scraping session: {}\n'.format(
            datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")))
        print('====================\n')
        for story in self.stories:
            text = story.get_full_info_lines()
            for line in text:
                print(line)
        print('====================')
        for author in self.authors:
            text = author.get_full_info_lines()
            for line in text:
                print(line)
        print('====================\n\n')
