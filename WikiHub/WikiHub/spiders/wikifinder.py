from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

class WikiFinder(CrawlSpider):
    name = 'wikifinder'
    allowed_domains = ['fandom.com']
    start_urls = ['https://onepiece.fandom.com/wiki/One_Piece_Wiki']
    rules = [
        Rule(LinkExtractor(allow='https://[A-Za-z0-9]+\.fandom\.com(|/wiki/)$'), callback='parse_items', follow=True, cb_kwargs={'is_main': True}),
        # Rule(LinkExtractor(allow='https://[A-Za-z0-9]+\.fandom\.com/wiki/[A-Za-z0-9]+'), callback='parse_items', follow=False, cb_kwargs={'is_main': False})
    ]

    def parse_items(self, response, is_main):
        # print(response.url)
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
    