# Scraper User Settings
FAIL_SILENTLY = True

MODE_TOP_STORIES = 'top_stories'
MODE_TAG = 'tag'
MODE_AUTHOR = 'author'

SCRAPE_MODE = [MODE_TOP_STORIES, MODE_TAG, MODE_AUTHOR]

# Scraper internal config
BASE_URL = "https://www.cnet.com/news/"
BASE_AUTHOR_URL = "https://www.cnet.com/profiles/"
DOMAIN_URL = "https://www.cnet.com"
TAG_URL = 'https://www.cnet.com/tags/'
DESTINATION_FILE_NAME = 'scraping.txt'
MAX_URLS_DEFAULT = 15
SUCCESS_STATUS_CODE = 200
NEWS_URL_FILTER = '/news/'

CONSOLE_WELCOME_MESSAGE = 'CNET News Web Scraper initialized'
ERROR_FILE_PATH = "Error! Path to file_name doesn't exist."

CONFIG_PATTERN_COMMON = '#topStories > div > a[href]'
CONFIG_PATTERN_NUXT_JS = '.moreTopStories .assetBody > a[href]'
CONFIG_MAIN_PATTERN = [
    CONFIG_PATTERN_COMMON,
    CONFIG_PATTERN_NUXT_JS
]

CONFIG_AUTHOR_URLS = '.result-list > section.searchItem .itemDetails a[href]'
CONFIG_TAG_URLS = 'section.listing > .asset > .assetBody > a'

COMMON_PREFIX = '.content-header'
CONFIG_TEMPLATE_COMMON = {
    'header': COMMON_PREFIX,
    'title': COMMON_PREFIX + ' .c-head h1.speakableText',
    'description': COMMON_PREFIX + ' .c-head p.c-head_dek',
    'authors': COMMON_PREFIX + ' .c-assetAuthor_authors a.author',
    'date': COMMON_PREFIX + ' .c-assetAuthor_date time'
}
NUXT_PREFIX = '.c-globalHero_content'
CONFIG_TEMPLATE_NUXT_JS = {
    'header': NUXT_PREFIX,
    'title': NUXT_PREFIX + ' h1.c-globalHero_heading',
    'description': NUXT_PREFIX + ' p.c-globalHero_description',
    'authors': NUXT_PREFIX + ' .c-globalAuthor_meta a.c-globalAuthor_link',
    'date': NUXT_PREFIX + ' .c-globalAuthor_meta time'
}
CONFIG_TEMPLATES = [
    CONFIG_TEMPLATE_COMMON,
    CONFIG_TEMPLATE_NUXT_JS
]

STORY_SCRAPE_FIELDS = [
    {
        'field': 'title',
        'multiple': False,
    },
    {
        'field': 'description',
        'multiple': False,
    },
    {
        'field': 'authors',
        'multiple': True,
        'attr': 'href',
    },
    {
        'field': 'date',
        'multiple': False,
    },
]

# Selenium config for authors
SELENIUM_DRIVER_PATH = './chromedriver/chromedriver'
SELENIUM_TIMEOUT = 15
SELENIUM_ARTICLES = '#user_tab > div.col-2 > div > section > ul > ' \
                    'li:nth-child(2) > a'
SELENIUM_CHECK_404 = '#profile-info > h1 > span:nth-child(1)'

AUTHOR_PREFIX = '#profile-info'
CONFIG_AUTHOR_TEMPLATE = {
    'name': AUTHOR_PREFIX + ' h1 > span[itemprop="name"]',
    'member_since': AUTHOR_PREFIX + '> div:nth-child(3) > p:nth-child(1)',
    'location': AUTHOR_PREFIX + ' p[itemprop="address"] > span',
    'occupation': AUTHOR_PREFIX + ' p > span[itemprop="title"]',
    'website': AUTHOR_PREFIX + ' p > span[itemprop="url"]',

}

AUTHOR_SCRAPE_FIELDS = [
    {
        'field': 'name',
        'multiple': False,
    },
    {
        'field': 'member_since',
        'multiple': False,
    },
    {
        'field': 'location',
        'multiple': False,
        'optional': True,
    },
    {
        'field': 'occupation',
        'multiple': False,
        'optional': True,
    },
    {
        'field': 'website',
        'multiple': False,
        'optional': True,
    },
]

STORY_TAGS_SELECTOR = '.tagList > a.tag:not(.broadInterest)'
CONFIG_STORIES_TAG_TEMPLATE = {
    'name': STORY_TAGS_SELECTOR,
    'url': STORY_TAGS_SELECTOR,
}

STORY_TAGS_TOPIC_PREFIX = '.tagList > a.tag.broadInterest'
CONFIG_STORIES_TAG_TOPIC_TEMPLATE = {
    'name': STORY_TAGS_TOPIC_PREFIX + ' span.text',
    'url': STORY_TAGS_TOPIC_PREFIX,
}

STORY_TAG_SCRAPE_FIELDS = [
    {
        'field': 'name',
        'multiple': True,
    },
    {
        'field': 'url',
        'multiple': True,
        'attr': 'href',
    },
]

# Database Connection
HOST = 'localhost'
USER = 'root'
PASSWORD = ''
DATABASE = 'data_mining'
