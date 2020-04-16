from nltk.corpus import stopwords
import nltk
import hashlib
import pandas as pd
from urllib.parse import urlparse
import argparse
import logging
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

nltk.download('punkt')
nltk.download('stopwords')


def main(filename):
    logger.info('Starting cleaning process')
    #read file with pandas
    df = _read_data(filename)
    #extract the newspaper webpage
    newspaper_uid = _extract_newspaper_uid(filename)
    #add newspaper webpage to the df as a new column
    df = _add_newspaper_uid_column(df, newspaper_uid)
    #extract webpage host
    df = _extract_host(df)
    #fill missing titles with the url
    df = _fill_missing_titles(df)
    #generate id codes for the rows
    df = _generate_uids_for_rows(df)
    #remove the \n symbol from the body
    df = _remove_new_lines_from_body(df)
    #create a column with the important words(tokens) for the title
    df = _add_tokens_counter(df, 'title')
    #create a column with the important words(tokens) for the body
    df = _add_tokens_counter(df, 'body')
    #remove duplicated values
    df = _remove_duplicates_entries(df, 'title')
    #drop rows with missing values
    df = _drop_rows_with_missing_values(df)
    _save_data(df, filename)

    return df


def _read_data(filename):
    logger.info('Reading file {}'.format(filename))
    #read csv file
    return pd.read_csv(filename)


def _extract_newspaper_uid(filename):
    logger.info('Extracting newspaper uid')
    #from the filename extract the newspaper uid
    newspaper_uid = filename.split('_')[0]
    logger.info('Newspaper uid detected: {}'.format(newspaper_uid))
    return newspaper_uid


def _add_newspaper_uid_column(df, newspaper_uid):
    logger.info('Filling column newspaper_uid with {}'.format(newspaper_uid))
    #add the newspaper uid to the df
    df['newspaper_uid'] = newspaper_uid
    return df


def _extract_host(df):
    logger.info('Extracting hosts from urls')
    #returns the host from the url using the urlparse method of the urllib lib
    df['host'] = df['url'].apply(lambda url: urlparse(url).netloc)
    return df


def _fill_missing_titles(df):
    logger.info('Filling missing titles')
    missing_title_mask = df['title'].isna()
    #extracts the news title from the news url and replacing the - with ' '
    missing_titles = (df[missing_title_mask]['url']
                      .str.extract(r'(?P<missing_titles>[^/]+)$')
                      .applymap(lambda title: title.split('-'))
                      .applymap(lambda title_word_list: ' '.join(title_word_list))
                      )
    df.loc[missing_title_mask, 'title'] = missing_titles.loc[:, 'missing_titles']
    return df


def _generate_uids_for_rows(df):
    logger.info('Generating uids for each row')
    #create unique ids per row
    uids = (df
            .apply(lambda row: hashlib.md5(bytes(row['url'].encode())), axis=1).
            apply(lambda hash_object: hash_object.hexdigest())
            )
    df['uid'] = uids
    return df.set_index('uid')


def _remove_new_lines_from_body(df):
    #map the body creating a list per character, identify the \n, and replace it wiht '', and then rejoin the list to create the body again
    logger.info('Removing new lines from the body')
    stripped_body = (df
                     .apply(lambda row: row['body'], axis=1)
                     .apply(lambda body: list(body))
                     .apply(lambda letters: list(map(lambda letter: letter.replace('\n', ''), letters)))
                     .apply(lambda letters: ''.join(letters))
                     )
    df['body'] = stripped_body
    return df


def _add_tokens_counter(df, column_name):
    logger.info('Adding {} tokens counter'.format(column_name))
    #generate a list with the non-important words in spanish
    stop_words = set(stopwords.words('spanish'))
    #create a list with all the words of the text, check if it's alphanumeric, convert to lowercase,
    #check that the words don't exist in stop words and then check the len of the resulting list
    tokens_column = (df
                     .dropna()
                     .apply(lambda row: nltk.word_tokenize(row[column_name]), axis=1)
                     .apply(lambda tokens: list(filter(lambda token: token.isalpha(), tokens)))
                     .apply(lambda tokens: list(map(lambda token: token.lower(), tokens)))
                     .apply(lambda word_list: list(filter(lambda word: word not in stop_words, word_list)))
                     .apply(lambda valid_word_list: len(valid_word_list)))
    df['n_tokens_{}'.format(column_name)] = tokens_column
    return df


def _remove_duplicates_entries(df, column_name):
    #remove news with the same title, keeping the first one
    logger.info('Removing duplicated entries')
    df.drop_duplicates(subset=[column_name], keep='first', inplace = True)
    return df


def _drop_rows_with_missing_values(df):
    #drop rows that have NaN values
    logger.info('Dropping rows with missing values')
    return df.dropna()


def _save_data(df, filename):
    #save the resulting df into a csv file with the 'clean' word in it
    clean_filename = 'clean_{}'.format(filename)
    logger.info('Saving data at locvation {}'.format(clean_filename))
    df.to_csv(clean_filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename',
                        help='The path to the dirty data',
                        type=str)
    args = parser.parse_args()
    df = main(args.filename)
    print(df)
