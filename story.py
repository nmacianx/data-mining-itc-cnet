class Story:
    # Class that holds all the information related to a news story
    def __init__(self, index, title, description,
                 date, authors=None, url=None):
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

        if authors is not None:
            self.authors = ', '.join([a.strip() for a in authors])
        else:
            self.authors = None

    def __str__(self):
        return self.title

    def set_url(self, url):
        self.url = url

    def get_full_info_lines(self):
        lines = ['\n\nStory {}:\n'.format(self.index),
                 'Title: {}\n'.format(self.title),
                 'Description: {}\n'.format(self.description),
                 'Author/s: {}\n'.format(self.authors),
                 'Date: {}\n'.format(self.date),
                 'URL: {}\n'.format(self.url)]

        return lines
