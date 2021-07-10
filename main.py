import argparse
from configuration import Configuration
from scraper import Scraper
from settings import CONFIG_MAIN_PATTERN, CONFIG_TEMPLATES, SCRAPE_MODE, \
    FAIL_SILENTLY, DESTINATION_FILE_NAME, MODE_TAG, MODE_TOP_STORIES, \
    MODE_AUTHOR, CONFIG_AUTHOR_TEMPLATE, CONFIG_STORIES_TAG_TEMPLATE, \
    CONFIG_STORIES_TAG_TOPIC_TEMPLATE, TESTING


def main():
    """
    Configures the Scraper, instantiates it and runs it
    """
    parser = argparse.ArgumentParser(description='CNET News Scraper')
    parser.add_argument('mode', choices=SCRAPE_MODE,
                        help="The scraping can start with the top stories, "
                             "an author or a tag.")
    parser.add_argument('-a', '--author',
                        help="The author to scrape if mode is author.")
    parser.add_argument('-n', '--number', type=int,
                        help="Amount of stories to scrape.")
    parser.add_argument('-t', '--tag',
                        help="The tag to scrape if mode is tag.")
    parser.add_argument('-c', "--console", action='store_true',
                        help='Print results in stdout instead of saving them.')
    parser.add_argument('-v', "--verbose", action='store_true',
                        help='Log extra information to the stdout.')

    args = parser.parse_args()
    should_save = True
    logging = False
    if args.console:
        should_save = False
    if args.verbose:
        logging = True

    if args.mode == MODE_TOP_STORIES:
        if args.author:
            parser.error('Top stories mode should not be passed an author '
                         'argument.')
        elif args.tag:
            parser.error('Top stories mode should not be passed a tag '
                         'argument.')
    elif args.mode == MODE_AUTHOR:
        if not args.author:
            parser.error('For author mode, the parameter author needs to be '
                         'set (-a / --author).')
    elif args.mode == MODE_TAG:
        if not args.tag:
            parser.error('For tag mode, the parameter tag needs to be set '
                         '(-t / --tag).')
    if args.tag and args.author:
        parser.error("Incorrect arguments. Can't set tag and author together.")

    config = Configuration(CONFIG_MAIN_PATTERN, CONFIG_TEMPLATES,
                           CONFIG_AUTHOR_TEMPLATE, CONFIG_STORIES_TAG_TEMPLATE,
                           CONFIG_STORIES_TAG_TOPIC_TEMPLATE)
    try:
        scraper = Scraper(config, logging=logging, should_save=should_save,
                          fail_silently=FAIL_SILENTLY,
                          file_name=DESTINATION_FILE_NAME, mode=args.mode,
                          author=args.author, tag=args.tag, number=args.number)
        scraper.scrape()
    except ValueError as e:
        print(e)
        exit(1)
    except RuntimeError as e:
        print(e)
        exit(2)
    except AttributeError as e:
        print(e)
        exit(2)
    except OSError as e:
        print(e)
        exit(3)


def main_testing():
    """
    Test the main method
    """

    config = Configuration(CONFIG_MAIN_PATTERN, CONFIG_TEMPLATES,
                           CONFIG_AUTHOR_TEMPLATE, CONFIG_STORIES_TAG_TEMPLATE,
                           CONFIG_STORIES_TAG_TOPIC_TEMPLATE)
    try:
        scraper = Scraper(config, False, file_name=DESTINATION_FILE_NAME)
        scraper.scrape()
    except ValueError as e:
        print(e)
        exit(1)
    except RuntimeError as e:
        print(e)
        exit(2)
    except AttributeError as e:
        print(e)
        exit(2)
    except OSError as e:
        print(e)
        exit(3)


if __name__ == '__main__':
    if TESTING:
        main_testing()
    else:
        main()
