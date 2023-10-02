# Aqui vamos escrever o scrapper q vai usar as urls de search
# com beautifulsoup (acho q n precisa de scrapy)
import requests
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import os
import json

class Content:
    # class-base comum para todos os artigos/páginas, ou nesse caso, infos
    def __init__(self, topic, title, headlines, body, imgurl, url):
        self.topic = topic
        self.title = title
        self.headlines = headlines
        self.body = body
        self.imgurl = imgurl
        self.url = url
    def print(self):
        print("New article found for topic: {}".format(self.topic))
        print("TITLE: {}".format(self.title))
        print("HEADLINES: {}".format(self.headlines))
        print("BODY: {}".format(self.body))
        print("IMAGE URL: {}".format(self.imgurl))
        print("URL: {}\n".format(self.url))
    def write(self):
        # content=''.join('''"title": "{}", "headlines": {}, "body": "{}", "imageurl": "{}", "url": "{}"'''.format(
        #     self.title, self.headlines, self.body, self.imgurl, self.url))
        content = {
            "title": self.title,
            "headlines": self.headlines,
            "body": self.body,
            "imageurl": self.imgurl,
            "url": self.url
        }
        file.write(json.dumps(content)+',')

class Website:
    # contém informações sobre a estrutura do site 
    def __init__(self, name, url, searchUrl, resultListing, absoluteUrl, titleTag, headlineTag, imgTag, bodyTag):
        self.name = name
        self.url = url
        self.searchUrl = searchUrl
        self.resultListing = resultListing
        self.absoluteUrl = absoluteUrl
        self.titleTag = titleTag
        self.headlineTag = headlineTag
        self.imgTag = imgTag
        self.bodyTag = bodyTag

class Crawler:
    # o web crawler que rastreia sites por meio de pesquisa
    def getPage(self, url):
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException:
            return None
        return BeautifulSoup(req.text, 'html.parser')
    
    def safeGet(self, pageObj, selector):
        childObj = pageObj.select(selector)
        if childObj is not None and len(childObj) > 0:
            return childObj[0].get_text()
        return ""
    
    def safeGet_img(self, pageObj, selector):
        childObj = pageObj.select(selector)
        if childObj is not None and len(childObj) > 0:
            return childObj[0]['src']
        return ""
    
    def safeGet_list(self, pageObj, selector):
        result_list = []
        childObj = pageObj.select(selector)
        if childObj is not None and len(childObj) > 0:
            for child in childObj:
                result_list.append(child.get_text().strip().replace('\n', ' ').replace('\t', ' '))
            return result_list
        return ""
    
    def search(self, topic, site):
        # pesquisa um dado site em busca de um dado tópico e registra
        # todas as páginas encontradas
        visitedUrl = set()
        bs = self.getPage(site.searchUrl.format(topic))
        urlList = bs.select(site.resultListing)
        for url in enumerate(urlList):
            # print(urlList)
            url = url[1]['href']
            if url in visitedUrl:
                continue
            visitedUrl.add(url)
            if (site.absoluteUrl):
                bs = self.getPage(url)
            else:
                bs = self.getPage(site.url + url)
            if bs is None:
                print("Something was wrong with that page or URL. Skipping!")
                return
            title = self.safeGet(bs, site.titleTag)
            headline = self.safeGet_list(bs, site.headlineTag)
            img = self.safeGet_img(bs, site.imgTag)
            body = self.safeGet_list(bs, site.bodyTag)
            if title != '':
                print(title)
                content = Content(topic, title, headline, body, img, url)
                content.write()

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

# passar a wiki que se quer, e os tópicos que se quer pesquisar dentro dessa wiki
wiki = "minecraft"
topics_list = ['nether']

site = getBS("https://www.fandom.com/?s=" + wiki.replace(" ", ""))
wiki_site = site.select('a.top-community-content')[0]['href']
crawler = Crawler()

siteData = [
    [wiki, wiki_site, wiki_site + "/wiki/Special:Search?query={}&scope=internal&navigationSearch=true&so=trending",
    'a.unified-search__result__title', True, 'span.mw-page-title-main',
    'span.mw-headline', 'img.pi-image-thumbnail', 'div.mw-parser-output p']
]
sites = []

# abrir arquivo em txt para salvar resultados
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'results.json')
file = open(file_path, mode='w', encoding='utf-8')
file.write('[')

for row in siteData:
    sites.append(Website(row[0], row[1], row[2],
    row[3], row[4], row[5], row[6], row[7], row[8]))
    topics = topics_list
    for targetSite in sites:
        for topic in topics:
            print("\nGETTING INFO ABOUT: " + topic)
            print("INFO FROM: " + row[0])
            crawler.search(topic, targetSite)
file.write('{}]')
file.close()