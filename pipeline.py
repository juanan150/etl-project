import subprocess
import logging
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
#webpages to be scrapped
news_sites_uids = ['elcolombiano', 'elpais']

def main():
    _extract()
    _transform()
    _load()


def _extract():
    #message printed in terminal
    logger.info('Starting extract process')
    for news_site_uid in news_sites_uids:
        #run tasks in cmd, first main.py from extract folder and then move the resulting dirty file into transform folder
        subprocess.run(['python', 'main.py', news_site_uid], cwd='./extract')
        subprocess.run(['move','{}*.csv'.format(news_site_uid),'../transform/{}_.csv'.format(news_site_uid)], cwd='./extract', shell=True)


def _transform():
    #message printed in terminal
    logger.info('Starting transform process')
    for news_site_uid in news_sites_uids:
        #create 2 names variables
        dirty_data_filename = '{}_.csv'.format(news_site_uid)
        clean_data_filename = 'clean_{}'.format(dirty_data_filename)
        #take the dirty file, trasform it, and save it as a clen file, delete the dirty file and then move the clen file into the load folder
        subprocess.run(['python', 'newspaper_recipe.py',
                        dirty_data_filename], cwd='./transform')
        subprocess.run(['del','/f', dirty_data_filename], cwd='./transform', shell=True)
        subprocess.run(['move', clean_data_filename, '../load/{}.csv'.format(news_site_uid)],
                       cwd='./transform', shell=True)


def _load():
    #message printed in terminal
    logger.info('Starting load process')
    for news_site_uid in news_sites_uids:
        #create a name variable
        clean_data_filename = '{}.csv'.format(news_site_uid)
        #take the clean file and store it into a db, and then delete the clean file
        subprocess.run(['python', 'save_sql.py', clean_data_filename], cwd='./load')
        subprocess.run(['del','/f', clean_data_filename], cwd='./load',shell=True)


if __name__ == '__main__':
    main()
