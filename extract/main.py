from common import config
import news_page_objects as news
from urllib3.exceptions import MaxRetryError
from requests.exceptions import HTTPError
import re
import argparse
import csv
import datetime
import logging
#allos to print info in the terminal
logging.basicConfig(level=logging.INFO)


logger = logging.getLogger(__name__)
#check the links structure
is_well_formed_link = re.compile(r'^https?://.+/.+$')
is_root_path = re.compile(r'^/.+$')


def _news_scraper(news_site_uid):
    #take the url from the config.yaml
    host = config()['news_sites'][news_site_uid]['url']
    logging.info('Beginning scraper for {}'.format(host))
    #create a news homepage object
    homepage = news.HomePage(news_site_uid, host)

    articles = []
    for link in homepage.article_links:
        #call the function that fetches the article
        article = _fetch_article(news_site_uid, host, link)

        if article:
            logger.info('Article fetched!')
            articles.append(article)
    #save info in a csv file
    _save_articles(news_site_uid, articles)


def _save_articles(news_site_uid, articles):
    #get date
    now = datetime.datetime.now().strftime('%Y_%m_%d')
    #csv file name
    out_file_name = '{news_site_uid}_{datetime}_articles.csv'.format(
        news_site_uid=news_site_uid,
        datetime=now)
    #take the headers for the csv file based on the attributes of the article page object that don't start with _
    csv_headers = list(filter(lambda property: not property.startswith('_'), dir(articles[0])))
    with open(out_file_name, mode = 'w+', encoding="utf-8") as f:
        writer = csv.writer(f)
        #write the csv header in the csv file
        writer.writerow(csv_headers)

        for article in articles:
            row = [str(getattr(article, prop)) for prop in csv_headers]
            #write the articles in the csv file
            writer.writerow(row)



def _fetch_article(news_site_uid, host, link):
    logger.info('Start fetching article at {}'.format(link))

    article = None
    try:
        #create an article page object with the link built with the host link and the link from the homepage object
        article = news.ArticlePage(news_site_uid, _build_link(host, link))
    except(HTTPError, MaxRetryError) as e:
        logger.warning('Error while fetching the article', exc_info=False)

    if article and not article.body:
        logger.warning('Invalid article, there is no body')
        return None

    return article


def _build_link(host, link):
    if is_well_formed_link.match(link):
        return link
    elif is_root_path.match(link):
        return '{}{}'.format(host, link)
    else:
        return '{host}/{uri}'.format(host=host, uri=link)


if __name__ == '__main__':
    #allows to input the data when the program is executed in the terminal (e.g. python main.py elcolombiano)
    parser = argparse.ArgumentParser()  
    #bring the webpages keys from the config.yaml
    news_site_choices = list(config()['news_sites'].keys())
    parser.add_argument('news_site',
                        help='The news site taht you want to scrape',
                        type=str,
                        choices=news_site_choices)

    args = parser.parse_args()
    _news_scraper(args.news_site)
