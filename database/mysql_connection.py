from datetime import datetime
import pymysql.cursors
from settings import HOST, USER, PASSWORD, DATABASE


class MySqlConnection:
    connection = pymysql.connect(host=HOST, user=USER, password=PASSWORD,
                                 database=DATABASE,
                                 cursorclass=pymysql.cursors.DictCursor)

    @staticmethod
    def save_results(data):
        """
        Save the scraped information in the database,
        that is, stories, tags and authors

        Args:
            data: scraping values to be save in the database
        """

        with MySqlConnection.connection:
            with MySqlConnection.connection.cursor() as cursor:
                for element in data:
                    id_merged_story = MySqlConnection._merge_story(element,
                                                                   cursor)

                    if element.authors is not None:
                        for author in element.authors:
                            id_merged_author = MySqlConnection._merge_author(
                                author, cursor)
                            MySqlConnection._merge_stories_authors(
                                [id_merged_story, id_merged_author], cursor)

                    if element.tags is not None:
                        for tag in element.tags:
                            id_merged_tag = MySqlConnection._merge_tag(tag,
                                                                       cursor)
                            MySqlConnection._merge_stories_tags(
                                [id_merged_story, id_merged_tag], cursor)

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

        date_time_obj = MySqlConnection._fix_date(story.date)
        formatted_date = ' '.join([str(date_time_obj.date()),
                                   str(date_time_obj.time())])
        description = MySqlConnection.clean_text(story.description)
        title = story.title

        sql_header = 'INSERT INTO article (title, date, url, description) '
        sql_values = f'VALUES ("{title}", "{formatted_date}", ' \
                     f'"{story.url}", "{description}") '
        sql_duplicate = 'ON DUPLICATE KEY UPDATE date = "{}", title = "{}", ' \
                        'description = "{}"' \
            .format(formatted_date, title, description)
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

        formatted_member_since = MySqlConnection._fix_date(author.member_since,
                                                           'author')
        sql_header = 'INSERT INTO author (nick_name, name, location, ' \
                     'occupation, url, member_since) '
        sql_values = f'VALUES ("{author.username}", "{author.name}", ' \
                     f'"{author.location}", "{author.occupation}", ' \
                     f'"{author.website}", "{formatted_member_since}") '
        sql_duplicate = f'ON DUPLICATE KEY UPDATE name = "{author.name}", ' \
                        f'location = "{author.location}", ' \
                        f'occupation = "{author.occupation}", ' \
                        f'url = "{author.website}", ' \
                        f'member_since = "{formatted_member_since}"'
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

    @staticmethod
    def _fix_date(date_to_fix, date_type='story'):
        """
        Fix the date to match the desired format

        Args:
            date_type: specify if it is an author or story date
            date_to_fix: date to fix format

        Returns:
            fixed_date: returns the date with the desired format to save it in
            the database
        """

        if date_type == 'story':
            try:
                if 'a.m.' in date_to_fix or 'p.m.' in date_to_fix:
                    fixed_date = date_to_fix.replace('a.m.', 'AM')\
                                     .replace('p.m.', 'PM')[:-3]
                    date_time_obj = datetime.strptime(fixed_date,
                                                      '%B %d, %Y %I:%M %p')
                else:
                    date_time_obj = datetime.strptime(date_to_fix, '%B %d, %Y')
            except Exception:
                print('No matching date format found for story,'
                      ' set current date')
                date_time_obj = datetime.today()

            return date_time_obj
        else:
            try:
                date_time_obj = datetime.strptime(date_to_fix, '%B %d, %Y')\
                    .date()
            except Exception:
                print('No matching date format found for author,'
                      ' set current date')
                date_time_obj = datetime.today()

            return date_time_obj

    @staticmethod
    def clean_text(text_to_clean):
        """
        Fix the quotes and double quotes so that they can be used within a text
        without problems

        Args:
            text_to_clean: text to which the transformation will be carried out

        Returns:
            text ready to be saved in the database
        """

        text_to_clean = text_to_clean.replace('\'', '\\\'')
        text_to_clean = text_to_clean.replace('\"', '\\\"')

        return text_to_clean
