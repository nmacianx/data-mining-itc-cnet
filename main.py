from configuration import Configuration
from scraper import Scraper
from settings import CONFIG_MAIN_PATTERN, CONFIG_TEMPLATES, LOGGING, \
    FAIL_SILENTLY, DESTINATION_FILE_NAME


def main():
    """
    Configures the Scraper, instantiates it and runs it
    """
    config = Configuration(CONFIG_MAIN_PATTERN, CONFIG_TEMPLATES)
    try:
        scraper = Scraper(config, logging=LOGGING, should_save=True,
                          fail_silently=FAIL_SILENTLY,
                          file_name=DESTINATION_FILE_NAME)
        scraper.scrape()
    except ValueError as e:
        print(e)
        exit(1)
    except RuntimeError as e:
        print(e)
        exit(2)
    except OSError as e:
        print(e)
        exit(3)


if __name__ == '__main__':
    main()
