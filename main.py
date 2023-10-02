import crochet
crochet.setup()

from flask import Flask , render_template, jsonify, request, redirect, url_for
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher
import time
import os

# Importing our Scraping Function and Crawler from beautifulsoup
from Search.search import Crawler, Website, Content, getPage, getBS
from WikiHub.WikiHub.spiders.wikifinder import WikiFinder

# Creating Flask App Variable

app = Flask(__name__)

crawl_runner = CrawlerRunner()

# By Deafult Flask will come into this when we run the file
@app.route('/')
def index():
	return render_template("index.html") # Returns index.html file in templates folder.


# After clicking the Submit Button FLASK will come into this
@app.route('/', methods=['POST'])
def submit():
    if request.method == 'POST':
        wiki = request.form['wiki']
        subject = request.form['subject']
        global base
        base = wiki
        global topics
        topics = subject.split()
        
        # This will remove any existing file with the same name so that the scrapy will not append the data to any previous file.
        if os.path.exists("<path_to_outputfile.json>"): 
        	os.remove("<path_to_outputfile.json>")
                 
        global output_data
        output_data = []
        global output_search
        output_search = []

        return redirect(url_for('scrape')) # Passing to the Scrape function


@app.route("/results")
def scrape():

    scrape_with_crochet(base=base) # Passing that URL to our Scraping Function
    
    if topics:
        print("oi, rodei")
        crawl_with_bs(topics)

    time.sleep(5) # Pause the function while the scrapy spider is running
    
    # return jsonify(output_data) # Returns the scraped data after being running for 10 seconds.
    return render_template("index.html", data=output_data, search_data=output_search)

@crochet.run_in_reactor
def scrape_with_crochet(base):
    # This will connect to the dispatcher that will kind of loop the code between these two functions.
    dispatcher.connect(_crawler_result, signal=signals.item_scraped)
    
    # This will connect to the WikiFinder function in our scrapy file and after each yield will pass to the crawler_result function.
    eventual = crawl_runner.crawl(WikiFinder, category = base)
    return eventual

#This will append the data to the output data list.
def _crawler_result(item, response, spider):
    output_data.append(dict(item))

def crawl_with_bs(topics):
    site = getBS("https://www.fandom.com/?s=" + base.replace(" ", ""))
    wiki_site = site.select('a.top-community-content')[0]['href']
    crawler = Crawler()
    siteData = [
                [base.replace(" ", ""), wiki_site, wiki_site + "/wiki/Special:Search?query={}&scope=internal&navigationSearch=true&so=trending",
                'a.unified-search__result__title', True, 'span.mw-page-title-main',
                'span.mw-headline', 'img.pi-image-thumbnail', 'div.mw-parser-output p']
                ]
    sites = []
    for item in topics:
        for row in siteData:
            sites.append(Website(row[0], row[1], row[2],
            row[3], row[4], row[5], row[6], row[7], row[8]))
            for targetSite in sites:
                for topic in topics:
                    print("\nGETTING INFO ABOUT: " + topic)
                    print("INFO FROM: " + row[0])
                    output_search.append(crawler.search(topic, targetSite))

if __name__== "__main__":
    app.run(debug=True)