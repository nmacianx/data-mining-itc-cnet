class Author:
    """
    Class that holds all the information related to an author
    """
    def __init__(self, username, name, member_since, location=None,
                 occupation=None, website=None):
        """
        Creates an instance of an Author
        Args:
            username: string - identifies the Author among all others
            name: string - name of the author
            member_since: string - date the Author joined CNET
            location: string - location of the author
            occupation: string - occupation of the author
            website: string - website of the author
        """
        if username is None:
            raise ValueError('An Author cannot be created without a username.')
        if name is None:
            raise ValueError('A name needs to be provided to an Author.')
        if member_since is None:
            raise ValueError('A member_since needs to be provided to an '
                             'Author.')
        self.username = username
        self.name = name.strip()
        self.member_since = member_since.split('\n')[-2].strip()
        self.location = location.strip() if location is not None else None
        self.occupation = occupation.strip() if occupation is not None else None
        self.website = website.strip() if website is not None else None

    def __str__(self):
        """
        String representation of an Author, using its name
        """
        return self.name

    def get_username(self):
        """
        Function that returns the username for the Author
        """
        return self.username

    def get_full_info_lines(self):
        """
        Function that returns a list of lines, meant to be written into a file.
        It contains all the information for the Author object.
        Returns:
            lines: list of strings
        """
        lines = ['\n\nAuthor {}:\n'.format(self.username),
                 'Name: {}\n'.format(self.name),
                 'Member since: {}\n'.format(self.member_since)]

        if self.location is not None:
            lines.append('Location: {}\n'.format(self.location))
        if self.occupation is not None:
            lines.append('Occupation: {}\n'.format(self.occupation))
        if self.website is not None:
            lines.append('Website: {}\n'.format(self.website))
        return lines
