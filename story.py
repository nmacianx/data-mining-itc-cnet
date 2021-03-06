class Story:
    """
    Class that holds all the information related to a news story
    """
    def __init__(self, index, title, description,
                 date, authors=None, url=None, tags=None):
        """
        Creates an instance object for the Story class
        Args:
            index: int - needed to print the number of story when saving
            title: string - title of the story
            description: string - description of the story
            date: string - published date of the story
            authors: list of Author objects that wrote the story
            url: story's original URL
            tags: list of Tag objects
        """
        if index is None:
            raise ValueError('An index needs to be provided to a Story.')
        if title is None:
            raise ValueError('A title needs to be provided to a Story.')
        if description is None:
            raise ValueError('A description needs to be provided to a Story.')
        if date is None:
            raise ValueError('A date needs to be provided to a Story.')

        self.index = index
        self.title = title.strip()
        self.description = description.strip()
        self.date = date.strip()
        self.url = url
        self.authors = authors
        self.tags = tags

    def __str__(self):
        """
        String representation of a story, using its title
        """
        return self.title

    def set_url(self, url):
        """
        Sets a new value to the story URL variable
        Args:
            url (): URL to set
        """
        self.url = url

    def get_full_info_lines(self):
        """
        Function that returns a list of lines, meant to be written into a file.
        It contains all the information for the story object.
        Returns:
            lines: list of strings
        """
        lines = ['\n\nStory {}:\n'.format(self.index),
                 'Title: {}\n'.format(self.title),
                 'Description: {}\n'.format(self.description)]
        if self.authors is not None and len(self.authors) > 0:
            line_author = 'Author/s: {}\n'.format(', '.join(
                         map(lambda a: a.get_username(), self.authors)))
            lines.append(line_author)
        lines_2 = ['Date: {}\n'.format(self.date),
                   'URL: {}\n'.format(self.url)]
        lines += lines_2
        if self.tags is not None and len(self.tags) > 0:
            tags_lines = ['Tags: \n']
            for t in self.tags:
                tags_lines.append('- {}'.format(str(t)))
            lines += tags_lines

        return lines
