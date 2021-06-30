# Scraper User Settings
LOGGING = True
SHOULD_SAVE = True
FAIL_SILENTLY = False

# Scraper internal config
BASE_URL = "https://www.cnet.com/news/"
DOMAIN_URL = "https://www.cnet.com"
DESTINATION_FILE_NAME = 'scraping.txt'

CONSOLE_WELCOME_MESSAGE = 'CNET News Web Scraper initialized'
ERROR_FILE_PATH = "Error! Path to file_name doesn't exist."

CONFIG_PATTERN_COMMON = '#topStories > div > a[href]'
CONFIG_PATTERN_NUXT_JS = '.moreTopStories .assetBody > a[href]'
CONFIG_MAIN_PATTERN = [
    CONFIG_PATTERN_COMMON,
    CONFIG_PATTERN_NUXT_JS
]

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
    },
    {
        'field': 'date',
        'multiple': False,
    },
]