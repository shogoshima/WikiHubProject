from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.exceptions import CloseSpider
import requests
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def getPage(url):
  try:
    html = urlopen(url)
  except HTTPError:
    return None
  except URLError:
    return None
  return html

def getBS(url):
  page = getPage(url)
  if page:
    return BeautifulSoup(getPage(url).read(), 'html.parser')
  return None

class WikiFinder(CrawlSpider):
    name = 'wikifinder'
    allowed_domains = ['fandom.com']
    start_urls = []
    rules = [
        Rule(LinkExtractor(allow='https://[A-Za-z0-9]+\.fandom\.com(|/wiki/)$'), callback='parse_items', follow=True, cb_kwargs={'is_main': True}),
        # Rule(LinkExtractor(allow='https://[A-Za-z0-9]+\.fandom\.com/wiki/[A-Za-z0-9]+'), callback='parse_items', follow=False, cb_kwargs={'is_main': False})
    ]
    item_count = 0
    
    def __init__(self, category='', **kwargs): # The category variable will have the input url
        self.myBaseUrl = category
        site = getBS("https://www.fandom.com/?s=" + category.replace(" ", ""))
        wiki_site = site.select('a.top-community-content')[0]['href']
        self.start_urls = [wiki_site]
        super().__init__(**kwargs)

        custom_settings = {'FEED_URI': 'WikiHub/outputfile.json'}
        # This will tell scrapy to store the scraped data to outputfile.json and for how long the spider should run.

    def parse_items(self, response, is_main):
        if self.item_count == 10:
          raise CloseSpider('item count limit exceeded')
        else:
          self.item_count += 1
        title = response.css('a.fandom-community-header__community-name::text').extract_first()
        print('Title is: {} '.format(title))
        if is_main:
            url = response.url
            yield {
                "title": ' '.join(title.split()),
                "url": url
            }
        else:
            # url = response.url
            # wikiUrl = url[:url.index("wiki/") + len("wiki/")]
            # yield {
            #     "title": ' '.join(title.split()),
            #     "url": url,
            #     "wikiUrl": wikiUrl
            # }
            
            print('Url is not absolute')
    