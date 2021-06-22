class Configuration:
    """
    It is in charge of handling everything related to the Configuration of the scraper
    """

    def __init__(self, main_patterns_extract_urls: list[str], templates: list[dict]):
        """
        Build the Configuration class through the input parameter patterns

        :param templates: list of all templates, in a dictionary structure, to use for scrape the urls extracted
        :param main_patterns_extract_urls: patterns that will be used to extract the elements.
        Each must have the form of CSS selector
        .|#element > tag1 > taN > tag_with_attr_to_extract[href | src | attribute of tag])

        Example of the use of a valid patterns value:
            [
                '#id_element > div a[href]',
                '.class_parent .class_son1 .class_sonN > h2[title]'
                'div > div > img[src]'
            ]

        Example of the use of a valid templates value:
            [
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
                },
            ]
        """

        self.main_patterns_extract_urls = main_patterns_extract_urls
        self.__fix_main_patterns_extract_urls()
        self.templates = templates

    def __fix_main_patterns_extract_urls(self):
        """
        Formats user-input patterns for internal use
        """

        self.main_patterns_extract_urls = [
            [pattern.split('[')[0], pattern.split('[')[1][:-1]] for pattern in self.main_patterns_extract_urls
        ]
