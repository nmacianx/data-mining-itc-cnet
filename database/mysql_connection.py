import pymysql.cursors
from settings import HOST, USER, PASSWORD, DATABASE, MODE_TOP_STORIES


class MySqlConnection:
    connection = pymysql.connect(host=HOST, user=USER, password=PASSWORD,
                                 database=DATABASE,
                                 cursorclass=pymysql.cursors.DictCursor)

    @staticmethod
    def save_results(data, mode):
        """
        Save the information in the database taking into account the
        scraping mode

        Args:
            data: scraping values to be save in the database
            mode: mode in which the page was scraped
        """

        if mode == MODE_TOP_STORIES:
            MySqlConnection._save_top_stories(data)

    @staticmethod
    def _save_top_stories(stories):
        """
        When the page was scraped in MODE_TOP_STORIES mode this function is
        responsible for saving information in the database

        Args:
            stories: list that contains the items to be saved as well as the
            authors and tags of each
        """

        with MySqlConnection.connection:
            with MySqlConnection.connection.cursor() as cursor:
                for story in stories:
                    id_merged_story = MySqlConnection._merge_story(story,
                                                                   cursor)

                    for author in story.authors:
                        id_merged_author = MySqlConnection._merge_author(author,
                                                                         cursor)
                        MySqlConnection._merge_stories_authors(
                            [id_merged_story, id_merged_author], cursor)

                    for tag in story.tags:
                        id_merged_tag = MySqlConnection._merge_tag(tag, cursor)
                        MySqlConnection._merge_stories_tags([id_merged_story,
                                                             id_merged_tag],
                                                            cursor)

    @staticmethod
    def _merge_story(story, cursor):
        """
        Insert the story into the database or update the information of this
        if it already exists

        Args:
            story: story that is going to be saved in the database
            cursor: object that contains information regarding the connection
            with the database

        Returns:
            row_id: row ID of the inserted/updated item
        """

        sql_header = 'INSERT INTO article (title, date, url) '
        sql_values = f'VALUES ("{story.title}", "{story.date}", "{story.url}") '
        sql_duplicate = 'ON DUPLICATE KEY UPDATE date = "{}", url = "{}"'\
            .format(story.date, story.url)
        cursor.execute(sql_header + sql_values + sql_duplicate)
        MySqlConnection.connection.commit()
        row_id = cursor.lastrowid

        if row_id == 0:
            cursor.execute(f'SELECT id_article FROM article WHERE title = '
                           f'"{story.title}"')
            row_id = cursor.fetchone()['id_article']

        return row_id

    @staticmethod
    def _merge_author(author, cursor):
        """
        Insert the author into the database or update the information of this
        if it already exists

        Args:
            author: author that is going to be saved in the database
            cursor: object that contains information regarding the connection
            with the database

        Returns:
            row_id: row ID of the inserted/updated item
        """

        sql_header = 'INSERT INTO author (nick_name, name, location, ' \
                     'occupation, url, member_since) '
        sql_values = f'VALUES ("{author.username}", "{author.name}", ' \
                     f'"{author.location}", "{author.occupation}", ' \
                     f'"{author.website}", "{author.member_since}") '
        sql_duplicate = f'ON DUPLICATE KEY UPDATE name = "{author.name}", ' \
                        f'location = "{author.location}", ' \
                        f'occupation = "{author.occupation}", ' \
                        f'url = "{author.website}", ' \
                        f'member_since = "{author.member_since}"'
        cursor.execute(sql_header + sql_values + sql_duplicate)
        MySqlConnection.connection.commit()
        row_id = cursor.lastrowid

        if row_id == 0:
            cursor.execute(f'SELECT id_author FROM author WHERE nick_name = '
                           f'"{author.username}"')
            row_id = cursor.fetchone()['id_author']

        return row_id

    @staticmethod
    def _merge_stories_authors(values, cursor):
        """
        Insert the relationship, or update it, from an author with an story

        Args:
            values: contains the IDs of the different elements, author and
            story, which will be related
            cursor: object that contains information regarding the connection
            with the database
        """

        sql_header = 'INSERT INTO article_author (id_article, id_author) '
        sql_values = f'VALUES ({values[0]}, {values[1]}) '
        sql_duplicate = f'ON DUPLICATE KEY UPDATE id_article = {values[0]}, ' \
                        f'id_author = {values[1]}'
        cursor.execute(sql_header + sql_values + sql_duplicate)
        MySqlConnection.connection.commit()

    @staticmethod
    def _merge_tag(tag, cursor):
        """
        Insert the tag into the database or update the information of this
        if it already exists

        Args:
            tag: tag that is going to be saved in the database
            cursor: object that contains information regarding the connection
            with the database

        Returns:
            row_id: row ID of the inserted/updated item
        """

        sql_header = 'INSERT INTO hashtag (name, url, is_topic) '
        sql_values = f'VALUES ("{tag.name}", "{tag.url}", ' \
                     f'{1 if tag.is_topic else 0}) '
        sql_duplicate = f'ON DUPLICATE KEY UPDATE url = "{tag.url}", ' \
                        f'is_topic = {1 if tag.is_topic else 0}'
        cursor.execute(sql_header + sql_values + sql_duplicate)
        MySqlConnection.connection.commit()
        row_id = cursor.lastrowid

        if row_id == 0:
            cursor.execute(f'SELECT id_hashtag FROM hashtag WHERE name = '
                           f'"{tag.name}"')
            row_id = cursor.fetchone()['id_hashtag']

        return row_id

    @staticmethod
    def _merge_stories_tags(values, cursor):
        """
        Insert the relationship, or update it, from an tag with an story

        Args:
            values: contains the IDs of the different elements, story and tag,
            which will be related
            cursor: object that contains information regarding the connection
            with the database
        """

        sql_header = 'INSERT INTO article_hashtag (id_article, id_hashtag) '
        sql_values = f'VALUES ({values[0]}, {values[1]}) '
        sql_duplicate = f'ON DUPLICATE KEY UPDATE id_article = {values[0]}, ' \
                        f'id_hashtag = {values[1]}'
        cursor.execute(sql_header + sql_values + sql_duplicate)
        MySqlConnection.connection.commit()
