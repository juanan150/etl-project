from sqlalchemy import Column, String, Integer

from sql_conn import Base

#create the database object
class Article(Base):
    __tablename__ = 'articles'
    #columns definition
    id = Column(String, primary_key=True)
    body = Column(String)
    host = Column(String)
    newspaper_uid = Column(String)
    n_tokens_body = Column(Integer)
    n_tokens_title = Column(Integer)
    url = Column(String, unique=True)

    #method that will create a row for the db
    def __init__(self,
                 uid,
                 body,
                 host,
                 newspaper_uid,
                 n_tokens_body,
                 n_tokens_title,
                 title,
                 url):
        self.id = uid
        self.body = body
        self.host = host
        self.newspaper_uid = newspaper_uid
        self.n_tokens_body = n_tokens_body
        self.n_tokens_title = n_tokens_title
        self.title=title
        self.url=url
