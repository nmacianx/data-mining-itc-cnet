from configuration import Configuration
from scraper import Scraper
from settings import CONFIG_MAIN_PATTERN, CONFIG_TEMPLATES, LOGGING, \
    FAIL_SILENTLY, DESTINATION_FILE_NAME


def main():
    config = Configuration(CONFIG_MAIN_PATTERN, CONFIG_TEMPLATES)
    scraper = Scraper(config, logging=LOGGING, should_save=True,
                      fail_silently=FAIL_SILENTLY,
                      file_name=DESTINATION_FILE_NAME)
    scraper.scrape()


if __name__ == '__main__':
    main()
