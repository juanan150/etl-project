from common import config
import requests
import bs4
#define the news webpage super class, and the homepage and article page as sub classes of the super class
class NewsPage:
    #constructor
    def __init__(self, news_site_uid, url):
        #dict from config.yaml file that depends on the news_site_uid
        self._config = config()['news_sites'][news_site_uid]
        #queries from the config.yaml file
        self._queries = self._config['queries']
        self._html = None
        self._url = url
        #starts the request
        self._visit(url)

    def _select(self, query_string):
        #look in the html file from bs4 parser based on the query_string
        return self._html.select(query_string)
    
    def _visit(self,url):
        #requests to the webpage
        response = requests.get(url,timeout=20, verify=False, stream=True)
        response.raise_for_status()
        #transform it into a html structure in order to use the tags for future queries
        self._html = bs4.BeautifulSoup(response.text, 'html.parser')
    

class HomePage(NewsPage):

    def __init__(self,news_site_uid,url):
        #inherit the super class constructor
        super().__init__(news_site_uid, url)

    #add an attribute using the @property in order to use a function
    @property
    def article_links(self):
        link_list = []
        #iterate using the info from the config.yaml file (homepage_article_links)
        for link in self._select(self._queries['homepage_article_links']):
            if link and link.has_attr('href'):
                #save news links in a list
                link_list.append(link)
        
        return set(link['href'] for link in link_list)


class ArticlePage(NewsPage):
    def __init__(self, news_site_uid, url):
        #inherit the super class constructor
        super().__init__(news_site_uid, url)

    #add an attribute using the @property in order to use a function
    @property
    def body(self):
        #query in the html file from bs4 parser for the news body
        result = self._select(self._queries['article_body'])

        return result[0].text if len(result) else ''

    @property
    def title(self):
        #query in the html file from bs4 parser for the news title
        result = self._select(self._queries['article_title'])

        return result[0].text if len(result) else ''

    @property
    def url(self):
        #news page url
        result = self._url;

        return result