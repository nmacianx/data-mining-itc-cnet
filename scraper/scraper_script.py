import datetime
import os
import requests
from bs4 import BeautifulSoup


SITE_URL = 'https://www.cnet.com/news/'


class Configuration:
    """
    It is in charge of handling everything related to the Configuration of the scraper
    """

    def __init__(self, parent_element, patterns, *, class_=None):
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

        self.mapping_original_order = []
        self._configuration = {
            'parent_element': parent_element,
            'class': class_,
            # 'all': all_elements,
            'patterns': self.__sort_patterns(patterns)
        }

    def __getitem__(self, item):
        return self._configuration[item]

    def __sort_patterns(self, patterns: list):
        """
        Sort the patterns by the amount of elements it has

        :param patterns: patterns to sort
        :return: sorted patterns
        """

        elements = [pattern.split('.') for pattern in patterns]
        elements.sort(key=lambda x: len(x), reverse=True)
        self.mapping_original_order = [elements.index(i.split('.')) for i in patterns]

        return elements


class Scraper:
    """
    Through this class it is possible to configure and scrape a specific website
    """

    def __init__(self, site_url, configurations, path_to_save_file='/'):
        """
        Build the Scraper class, given the url values of the site and the settings to scrape it

        :param site_url: url of the site to download
        :param configurations: settings to scrape the site
        :param path_to_save_file: path where the scraped content will be save
        """

        if not os.path.isdir(path_to_save_file):
            print(f'Directory \'{path_to_save_file}\' does not exist')
            self._file_to_save_path = ''
        else:
            self._file_to_save_path = path_to_save_file + 'my_scrapper.csv'

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
                parent_elements = soup.find_all(configuration['parent_element'], class_=configuration['class'])
                parent_elements = self.__filter_parents(parent_elements, configuration)
                scrapped_for_parent_elements = []
                scraped_element = []

                i = 0
                for pattern in configuration['patterns']:
                    j = 0
                    for parent_element in parent_elements:
                        self.__iterate_in_depth(parent_element, pattern, extracted_pattern=scraped_element)

                        if i == 0:
                            scrapped_for_parent_elements.append(scraped_element)
                        else:
                            scrapped_for_parent_elements[j].append(scraped_element[0])

                        scraped_element = []
                        j += 1

                    i += 1

                scrapped.append(scrapped_for_parent_elements)
        except AttributeError as ae:
            print(str(ae).replace('$paren_pattern', configuration['parent_element']))
            scrapped = []
        except TypeError as te:
            print(te)
            scrapped = []
        except Exception as ex:
            print('Error')
            print(ex)
            scrapped = []

        self.__write_csv_file(scrapped, [self.configurations[i].mapping_original_order for i, _ in enumerate(self.configurations)])

    def __filter_parents(self, parent_elements, configuration):
        """
        Filter all found html elements to match all configuration patterns

        :param parent_elements: html elements found
        :param configuration: patterns that must match
        :return: filtered html elements
        """

        matched_elements = []
        filtered_parent_elements = parent_elements

        for pattern in configuration['patterns']:
            for parent_element in filtered_parent_elements:
                if self.__iterate_in_depth(parent_element, pattern):
                    matched_elements.append(parent_element)

            filtered_parent_elements = matched_elements
            matched_elements = []

        return filtered_parent_elements

    def __iterate_in_depth(self, root, elements: list, iter_i=0, *, extracted_pattern=None):
        """
        Search deep for pattern compliance and keep it when found if extracted_pattern is not None

        :param extracted_pattern: list item to keep pattern when its found
        :param root: html a element to start the deep search with
        :param elements: pattern to look for
        :param iter_i: iteration counter
        :return: True if the element is found, False otherwise
        """

        if len(elements) - 1 == iter_i:
            tag = elements[iter_i]

            if tag == 'text':
                if extracted_pattern is not None:
                    extracted_pattern.append(root.text.strip())
                return True
            else:
                syntax = tag.split('[')
                element_child = root.find(syntax[0])

                if not element_child:
                    return False

                if extracted_pattern is not None:
                    if syntax[1][:len(syntax[1]) - 1] == 'href' or syntax[1][:len(syntax[1]) - 1] == 'src':
                        extracted_pattern.append(
                            self._domain_url + element_child.attrs[syntax[1][:len(syntax[1]) - 1]].strip())
                    else:
                        extracted_pattern.append(element_child.attrs[syntax[1][:len(syntax[1]) - 1]].strip())

                return True
        else:
            tag = elements[iter_i]
            element_parent = root.find_all(tag)

            found = False
            i = 0
            while i < len(element_parent) and not found:
                found = self.__iterate_in_depth(element_parent[i], elements, iter_i + 1, extracted_pattern=extracted_pattern)
                i += 1

            return found

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

    def __write_csv_file(self, elements, writing_order, mode='at'):
        """
        Save scraped items to csv file

        :param elements: elements to save
        :param writing_order: order in which scraped items should be written
        :param mode: writing mode. By default it will add the elements to the file in question
        """

        if len(elements) == 0:
            return

        with open(self._file_to_save_path, mode) as file_to_save:
            for i, element in enumerate(elements):
                for item in element:
                    text = '; '.join([item[j] for j in writing_order[i]]).strip()
                    file_to_save.write(datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S") + '; ' + text + '\n')
                    print(datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S") + '; ' + text)


scraper = Scraper(SITE_URL, [Configuration('div', ['div.a[href]', 'div.h3.a.text', 'div.p.a.text'], class_='riverPost'),
                             Configuration('div', ['div.a[href]', 'div.div.h6.a.text'], class_='col-2 assetWrap'),
                             Configuration('div', ['div.a[href]', 'div.div.h5.a.text', 'div.div.div.text'], class_='col-4 assetWrap'),
                             Configuration('div', ['a[href]', 'div.h6.a.text'], class_='assetBody dekRight riverPost')],
                  'C:/Users/Alejandro/Downloads/')
scraper.scrape()
