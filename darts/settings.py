# -*- coding: utf-8 -*-
# flake8: noqa

# Scrapy settings for darts project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'darts'

SPIDER_MODULES = ['darts.scraper.spiders']
NEWSPIDER_MODULE = 'darts.scraper.spiders'

DATABASE_URL = 'postgresql+psycopg2cffi://darts:darts@localhost/darts'
REDIS_URL = 'redis://localhost:6379'
REDISTOGO_URL = None
SECRET_KEY = '-8@a4n0{cK576B0oUH_M++Xo[]]pr8'

SIMULATIONS_PER_PAGE = 20
PROFILES_PER_PAGE = 20

JOB_TIMEOUT = 3000

SLACK_API_TOKEN = None
SLACK_BOT_NAME = 'dartsbot'

SCRAPING = False

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'darts (+http://www.yourdomain.com)'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS=32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY=3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN=16
#CONCURRENT_REQUESTS_PER_IP=16

# Disable cookies (enabled by default)
#COOKIES_ENABLED=False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED=False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'darts.middlewares.MyCustomSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'darts.middlewares.MyCustomDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'darts.scraper.pipelines.ItemToDBPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# NOTE: AutoThrottle will honour the standard settings for concurrency and delay
#AUTOTHROTTLE_ENABLED=True
# The initial download delay
#AUTOTHROTTLE_START_DELAY=5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY=60
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG=False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED=True
#HTTPCACHE_EXPIRATION_SECS=0
#HTTPCACHE_DIR='httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES=[]
#HTTPCACHE_STORAGE='scrapy.extensions.httpcache.FilesystemCacheStorage'

# =========================================================================== #

import os
from os import pardir
from os.path import join, dirname
from dotenv import load_dotenv

import yaml

# Load environment variables from the .env file
dotenv_path = join(dirname(__file__), pardir, '.env')
load_dotenv(dotenv_path)

# Load custom settings from the YAML file specified by APP_SETTINGS_YAML
custom_settings_filepath = os.environ.get('APP_SETTINGS_YAML')
if custom_settings_filepath is not None:
    with open(custom_settings_filepath) as infile:
        globals().update(yaml.safe_load(infile))

# Load any settings from environment variables
for var, value in locals().copy().items():
    if var.isupper():
        if os.environ.get(var):
            globals()[var] = os.environ[var]

if not SCRAPING and (
    'postgres' in DATABASE_URL and 'psycopg2cffi' not in DATABASE_URL):
    DATABASE_URL = 'postgres+psycopg2cffi{}'.format(
        DATABASE_URL.lstrip('postgres')
    )
