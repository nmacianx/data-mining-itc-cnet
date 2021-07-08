from settings import DOMAIN_URL


class Tag:
    """
    Class that holds all the information related to a tag
    """
    def __init__(self, name, url):
        if not isinstance(name, str):
            raise AttributeError("The tag's name needs to be a string.")
        if not isinstance(url, str):
            raise AttributeError("The tag's URL needs to be a string.")
        if name == '':
            raise AttributeError("The tag's name can't be an empty string.")
        if url == '':
            raise AttributeError("The tag's URL can't be an empty string.")
        self.name = name
        self.url = DOMAIN_URL + url
        self.is_topic = '/topics/' in self.url

    def __str__(self):
        """
        String representation of a Tag, using its name and URL
        """
        return 'Tag - name: {} - URL: {} - Is Topic: {}'\
            .format(self.name, self.url, self.is_topic)

    def get_name(self):
        """
        Returns the name of the tag
        """
        return self.name

    def get_url(self):
        """
        Returns the url of the tag
        """
        return self.url
