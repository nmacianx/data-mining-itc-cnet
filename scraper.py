from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, \
    WebDriverException
from database import MySqlConnection as SqlConn
import requests
import datetime
import os
from story import Story
from author import Author
from tag import Tag
from settings import *


class Scraper:
    """
    Scraper class that scrapes CNET news site, gathers top stories' URLs and
    scrapes its content. It can save the results to a text file.
    """

    def __init__(self, config, logging=True, should_save=True,
                 mode=MODE_TOP_STORIES, fail_silently=False, file_name=None,
                 file_full_path=False, author=None, tag=None,
                 number=None):
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
            number: optional - limit the amount of stories to scrape.
        """
        self.config = config
        self.logging = logging
        self.should_save = should_save
        self.fail_silently = fail_silently
        self.urls = []
        self.stories = []
        self.authors = []
        self.tags = []
        self.author = author
        self.tag = tag
        self.number = number if number is not None else MAX_URLS_DEFAULT

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
        if self.mode == MODE_TOP_STORIES:
            self.scrape_top_stories_page()
        elif self.mode == MODE_AUTHOR:
            self.scrape_stories_author()
        else:
            self.scrape_stories_tag()

        if self.logging:
            print('{} stories will be scraped'.format(len(self.urls)))
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

        self.urls = self.urls[:self.number]

    def scrape_stories_tag(self):
        """
        Scrapes the tag website to get a list of stories and saves them in a
        class attribute so they can be scraped later.
        """
        page = requests.get(TAG_URL + self.tag)
        if page.status_code != SUCCESS_STATUS_CODE:
            raise RuntimeError('Error! Tag {} was not found.'.format(self.tag))
        soup = BeautifulSoup(page.content, 'html.parser')
        tag_stories = soup.select(self.config.get_tag_urls_pattern())
        if len(tag_stories) == 0:
            raise RuntimeError('Error! No stories with the tag {} were found.'
                               .format(self.tag))
        urls = [a.get('href') for a in tag_stories]
        urls = list(filter(lambda x: NEWS_URL_FILTER in x, urls))
        self.urls += [DOMAIN_URL + u for u in urls]
        self.urls = self.urls[:self.number]

    def _check_selenium_404(self, driver):
        """
        Checks if the desired page to scrape returned a 404 error by checking
        the pattern for a 404 error page. If a 404 error was encountered, it
        raises an error.
        Args:
            driver: Chrome webdriver instance used by Selenium
        """
        try:
            driver.find_element_by_css_selector(SELENIUM_CHECK_404)
        except NoSuchElementException:
            raise RuntimeError("Error! Author {} wasn't found."
                               .format(self.author))

    def _await_author_profile_load(self, driver):
        """
        Makes Selenium webdriver instance wait for the dynamic results of the
        articles written by an author to be loaded.
        Args:
            driver: Chrome webdriver instance used by Selenium
        """
        try:
            WebDriverWait(driver, SELENIUM_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                "#ugc_content > .result-list"))
            )
        except WebDriverException:
            driver.quit()
            raise RuntimeError("Error! Couldn't fetch Author {} profile."
                               .format(self.author))

    def scrape_stories_author(self):
        """
        Scrapes an Author profile using Selenium to get the URLs for the
        articles and saves them to self.urls
        It checks for an unknown author and raises an exception in that case.

        """
        driver = webdriver.Chrome(executable_path=SELENIUM_DRIVER_PATH)
        driver.get(BASE_AUTHOR_URL + self.author)
        self._check_selenium_404(driver)
        driver.find_element_by_css_selector(SELENIUM_ARTICLES).click()
        self._await_author_profile_load(driver)

        try:
            urls = driver.find_elements_by_css_selector(
                self.config.get_author_urls_pattern())
            urls = [u.get_attribute('href') for u in urls]
            self.urls = list(filter(lambda x: NEWS_URL_FILTER in x, urls))
            self.urls = self.urls[:self.number]
        except WebDriverException:
            driver.quit()
            raise RuntimeError("Error! Couldn't fetch Author {} profile."
                               .format(self.author))
        driver.quit()

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
        tags = self._scrape_obj(soup, self.config.get_stories_tag_template(),
                                STORY_TAG_SCRAPE_FIELDS)
        tags_topic = self._scrape_obj(
            soup,
            self.config.get_stories_tag_topic_template(),
            STORY_TAG_SCRAPE_FIELDS)
        authors = ['+'.join(a.split('profiles/')[1][:-1].split())
                   for a in s['authors']]
        authors_created = self._get_or_create_authors(authors)

        tags_parsed = []
        tags_topic_parsed = []
        if 'name' in tags and 'url' in tags:
            tags_parsed = zip(tags['name'], tags['url'])
        if 'name' in tags_topic and 'url' in tags_topic:
            tags_topic_parsed = zip(tags_topic['name'], tags_topic['url'])

        tags = self._get_or_create_tags(tags_parsed)
        tags_topic = self._get_or_create_tags(tags_topic_parsed)
        tags += tags_topic
        try:
            story = Story(index + 1, s['title'], s['description'], s['date'],
                          authors_created, tags=tags)
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
                        s[f['field']] = element[0].get(f['attr'], None)
                    else:
                        s[f['field']] = [el.get(f['attr'], None)
                                         for el in element]
            elif 'optional' in f and f['optional']:
                s[f['field']] = None
        return s

    def _scrape_author(self, username):
        """
        Scrapes an author with a given username, creates the instance, adds it
        to the scraper's known authors and returns it.
        Args:
            username: username for the author to scrape

        Returns:
            author: Author object for the author scraped
        """
        page = requests.get(BASE_AUTHOR_URL + username)
        soup = BeautifulSoup(page.content, 'html.parser')
        if page.status_code != SUCCESS_STATUS_CODE:
            raise RuntimeError("Warning! Author {} couldn't be scraped."
                               .format(username))
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
        """
        Given a list of authors' usernames, it returns a list of Author objects.
        It checks if the desired author was already scraped or it will be
        scraped if it wasn't before
        Args:
            authors: list of authors' usernames

        Returns:
            result: list of Author objects
        """
        result = []
        for a in authors:
            found = None
            for author_obj in self.authors:
                if a == author_obj.get_username():
                    found = author_obj
            if found is not None:
                result.append(found)
            else:
                try:
                    result.append(self._scrape_author(a))
                except RuntimeError as e:
                    print(e)
                except ValueError as e:
                    print(e)
        return result

    def _get_or_create_tags(self, tags):
        """
        Given a list of tags as tuples, it returns a list of Tag objects.
        It checks if the desired tag was already created or it will do it.
        Args:
            tags: list of tags tuples following the structure (name, URL)

        Returns:
            result: list of Tag objects
        """
        result = []
        for t in tags:
            if t[0] is not None and t[1] is not None:
                found = None
                for tag in self.tags:
                    if t[1] == tag.get_url():
                        found = tag
                if found is not None:
                    result.append(found)
                else:
                    try:
                        new_tag = Tag(name=t[0], url=t[1])
                        result.append(new_tag)
                    except AttributeError as e:
                        pass
        return result

    def save_results(self):
        """
        Function that saves the information scraped to the database.
        """
        SqlConn.save_results(self.stories)
        if self.logging:
            print('Results were saved!')

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
