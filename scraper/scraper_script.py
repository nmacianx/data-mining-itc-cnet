import os

from bs4 import BeautifulSoup
import requests
import re
from textparser import Tag

SITE_URL = 'https://www.cnet.com/news/'


class Configuration:
    """
    It is in charge of handling everything related to the Configuration of the scraper
    """

    def __init__(self, parent_element, patterns, class_=None, all_elements=False):
        """
        Build the Configuration class through the input parameters parent_element, class_, all_elements, patterns

        :param parent_element: tag where the search will start
        :param class_: is used to specify a class to search for the tab given in the parameter parent_element
        :param all_elements: is used to specify if you want to find all matches or only the first one
        :param patterns: patterns that will be used to extract the elements. E
        ach must have the form tab1.tab2.tab3 ... tab.(text | ['href'] | ['src'] | ['attribute of a tab'])
        and the first one is directly the son of parent_element

        Example of the use of a valid patterns value:
            [
                'div.div.a[href]',
                'div.div.h2.text',
                'div.video[src]',
                'h2.a[alt]'
            ]
        """

        self._configuration = {
            'parent_element': parent_element,
            'class': class_,
            'all': all_elements,
            'patterns': patterns
        }

    def __getitem__(self, item):
        return self._configuration[item]


class Scraper:
    """
    Through this class it is possible to configure and scrape a specific website
    """

    def __init__(self, site_url, configurations, file_to_save_path='/'):
        """
        Build the Scraper class, given the url values of the site and the settings to scrape it

        :param site_url: url of the site to download
        :param configurations: settings to scrape the site
        """

        if not os.path.isdir(file_to_save_path):
            print(f'Directory \'{file_to_save_path}\' does not exist')
            self._file_to_save_path = ''
        else:
            self._file_to_save_path = file_to_save_path

        self._site_url = site_url
        self._domain_url = self.__get_domain_from_url()
        self.configurations = configurations
        self.html_text = ''
        self.get_site_web(self._site_url)

    def get_site_web(self, url):
        """
        Download the html that represents the given URL

        :param url: url to download
        :return: html text of the given URL
        """

        self.html_text = None

        try:
            self.html_text = requests.request('GET', url).text
        except requests.exceptions.ConnectionError:
            print(f'Error getting url: {SITE_URL}')
        except Exception as ex:
            print(ex)

    def scrape(self):
        """
        Scrape a website and save the information in a CSV file
        """

        if not self.html_text:
            print('Invalid HTML. Use the get_site_web(url) function with a valid url to download the site')
            return

        if self._file_to_save_path == '':
            print('I can\'t scrap without file to save it')
            return

        soup = BeautifulSoup(self.html_text, 'lxml')
        scrapped = []

        try:
            for configuration in self.configurations:
                if not configuration['all']:
                    scrapped.append(self.__scrape_one_item(soup.find(configuration['parent_element'],
                                                                     class_=configuration['class']), configuration))
                else:
                    scrapped.append(self.__scrape_all_items(soup.find_all(configuration['parent_element'],
                                                                      class_=configuration['class']), configuration))
        except AttributeError as ae:
            print(str(ae).replace('$paren_pattern', configuration['parent_element']))
        except Exception as ex:
            print(ex)

        self.__write_csv_file(scrapped)

    def __scrape_one_item(self, parent_element, configuration: Configuration):
        """
        It is used when all_elements = False is specified in the configuration.
        Scrape a single element from the parent_element

        :param html: parsed html site
        :param configuration: configuration to use for scrap
        :return: all the elements specified in the configuration patterns
        """

        patterns_text = []

        if not parent_element:
            raise AttributeError('An error occurred while executing the \'$paren_pattern\' parent pattern.')

        try:
            for pattern in configuration['patterns']:
                element_child = parent_element

                for tag in pattern.split('.'):
                    if tag == 'text':
                        patterns_text.append(element_child.text.strip())
                    elif '[' in tag:
                        syntax = tag.split('[')
                        element_child = element_child.find(syntax[0])

                        if syntax[1][:len(syntax[1]) - 1] == 'href' or syntax[1][:len(syntax[1]) - 1] == 'src':
                            patterns_text.append(self._domain_url + element_child.attrs[syntax[1][:len(syntax[1]) - 1]].strip())
                        else:
                            patterns_text.append(element_child.attrs[syntax[1][:len(syntax[1]) - 1]].strip())
                    else:
                        element_child = element_child.find(tag)
        except AttributeError:
            print(f'An error occurred while executing the pattern {pattern}. '
                  f'Possibly there are no labels in that order recursively')
        except TypeError:
            print('An error occurred while iterating the configurations. '
                  'Possibly there are none or they are poorly structured')
        except Exception:
            print('An error occurred')

        return patterns_text

    def __scrape_all_items(self, parent_elements, configuration: Configuration):
        """
        It is used when all_elements = True is specified in the configuration.
        Scrape all elements from parent_elements

        :param parent_elements: parsed html site of all matches
        :param configuration: configuration to use for scrap
        :return: all the elements specified in the configuration patterns of all matches of parent_elements
        """

        if not parent_elements:
            raise AttributeError('An error occurred while executing the \'$paren_pattern\' parent pattern.')

        patterns_text = []

        for parent_element in parent_elements:
            patterns_text.append(self.__scrape_one_item(parent_element, configuration))

        return patterns_text

    def __get_domain_from_url(self):
        """
        Returns the domain of the site url
        """

        i = 0
        count = 0
        while i < len(self._site_url):
            if self._site_url[i] == '/':
                count += 1
            elif count == 3:
                return self._site_url[: i - 1]

            i += 1

    def __write_csv_file(self, elements, path='/', mode='x'):
        pass


asd = Scraper(SITE_URL, [Configuration('diva', ['div.a[href]', 'div.div.h5.a.text', 'div.div.div.text'], 'col-4 assetWrap'),
                         Configuration('div', ['div.a[href]', 'div.h6.a.text', 'div.span.text'], 'col-2 assetWrap', all_elements=True)])


asd.scrape()