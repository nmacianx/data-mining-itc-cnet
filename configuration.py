class Configuration:
    """
    Class in charge of handling everything related to the scraper's settings
    """

    def __init__(self, main_urls_pattern, story_templates, author_template,
                 stories_tag_template, stories_tag_topic_template,
                 author_urls_pattern):
        """
        Build the Configuration class through the input parameter patterns

        Args:
            main_urls_pattern: patterns that will be used to extract the
                elements.
            story_templates: list of all templates, in a dictionary structure,
                to use for scrape the stories from the extracted urls
            author_template: template to use to scrape an author
            stories_tag_template: template to use to scrape tags from stories
            stories_tag_topic_template: template to use to scrape special topic
                tags from stories
            author_urls_pattern: template to use to scrape the URLS for the news
                posted by an author

        Each must have the form of CSS selector
        .|#element > tag1 > taN > tag_with_attr_to_extract[href | src |
                                                            attribute of tag])

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
                'description': '.c-globalHero_content
                                            p.c-globalHero_description',
                'authors': '.c-globalHero_content .c-globalAuthor_meta
                                                        a.c-globalAuthor_link',
                'date': '.c-globalHero_content .c-globalAuthor_meta time'
            },
        ]
        """

        self.main_urls_pattern = main_urls_pattern
        self._fix_main_patterns_extract_urls()
        self.story_templates = story_templates
        self.author_template = author_template
        self.stories_tag_template = stories_tag_template
        self.stories_tag_topic_template = stories_tag_topic_template
        self.author_urls_pattern = author_urls_pattern

    def _fix_main_patterns_extract_urls(self):
        """
        Formats user-input patterns for internal use
        """

        self.main_urls_pattern = [
            [pattern.split('[')[0], pattern.split('[')[1][:-1]]
            for pattern in self.main_urls_pattern
        ]

    def get_author_template(self):
        """
        Returns the author template
        """
        return self.author_template

    def get_stories_tag_template(self):
        """
        Returns the stories' tag template
        """
        return self.stories_tag_template

    def get_stories_tag_topic_template(self):
        """
        Returns the stories' tag template, specific when the tag is a topic
        """
        return self.stories_tag_topic_template

    def get_author_urls_pattern(self):
        """
        Returns the pattern to fetch the URLs from an Author profile
        """
        return self.author_urls_pattern
