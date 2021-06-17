from bs4 import BeautifulSoup
import requests
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

    def __init__(self, site_url, configurations):
        """
        Build the Scraper class, given the url values of the site and the settings to scrape it

        :param site_url: url of the site to download
        :param configurations: settings to scrape the site
        """

        self._site_url = site_url
        self._domain_url = self.__get_domain_from_url()
        self.configurations = configurations
        self.html_text = ''
        self.get_site_web(self._site_url)

    def __get_domain_from_url(self):
        """
        Returns the domain of the site url
        """
        # ''.
        return self._site_url

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

        soup = BeautifulSoup(self.html_text, 'lxml')
        scrapped = []

        asd2 = soup.find_all('div', class_='col-2 assetWrap')

        for a in asd2:
            print(self._site_url + a.div.a['href'])
            print(a.div.h6.a.text)
            print(a.div.span.text)

        for configuration in self.configurations:
            if not configuration['all']:
                scrapped.append(self.__scrape_one_item(soup, configuration))
            else:
                scrapped.append(self.__scrape_all_items(soup, configuration))

    def __scrape_one_item(self, html, configuration: Configuration):
        """
        It is used when all_elements = False is specified in the configuration.
        Scrape a single element from the parent_element

        :param html: parsed html site
        :return: all the elements specified in the configuration patterns
        """

        element = html.find(configuration['parent_element'], class_=configuration['class'])
        patterns_text = []
        
        for pattern in configuration['patterns']:
            print(element)
            element_child = element
            for tag in pattern.split('.'):
                if tag == 'text':
                    patterns_text.append(element.text.strip())
                elif '[' in tag:
                    syntax = tag.split('[')
                    element_child = element_child.find(syntax[0])
                    patterns_text.append(element_child.attrs[syntax[1][:len(syntax[1]) - 1]].strip())
                else:
                    element_child = element_child.find(tag)
            print()

        return patterns_text

    def __scrape_all_items(self, html, configuration: Configuration):
        elements = html.find_all(configuration['parent_element'], class_=configuration['class'])

        # for element in elements:



    asd = Scraper(SITE_URL, [Configuration('div', ['div.a[href]', 'div.div.h5.a.text', 'div.div.div.text'], 'col-4 assetWrap')])


asd.scrape()