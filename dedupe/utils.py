import os
import re
import string
import numpy as np
import dedupe
from unidecode import unidecode
from nltk.tokenize import WhitespaceTokenizer

w_tokenizer = WhitespaceTokenizer()
punct_re = re.compile('[{}]'.format(re.escape(string.punctuation)))

states = {
 'Alabama': 'AL',
 'Alaska': 'AK',
 'American Samoa': 'AS',
 'Arizona': 'AZ',
 'Arkansas': 'AR',
 'California': 'CA',
 'Colorado': 'CO',
 'Connecticut': 'CT',
 'Delaware': 'DE',
 'District of Columbia': 'DC',
 'Florida': 'FL',
 'Georgia': 'GA',
 'Guam': 'GU',
 'Hawaii': 'HI',
 'Idaho': 'ID',
 'Illinois': 'IL',
 'Indiana': 'IN',
 'Iowa': 'IA',
 'Kansas': 'KS',
 'Kentucky': 'KY',
 'Louisiana': 'LA',
 'Maine': 'ME',
 'Maryland': 'MD',
 'Massachusetts': 'MA',
 'Michigan': 'MI',
 'Minnesota': 'MN',
 'Mississippi': 'MS',
 'Missouri': 'MO',
 'Montana': 'MT',
 'National': 'NA',
 'Nebraska': 'NE',
 'Nevada': 'NV',
 'New Hampshire': 'NH',
 'New Jersey': 'NJ',
 'New Mexico': 'NM',
 'New York': 'NY',
 'North Carolina': 'NC',
 'North Dakota': 'ND',
 'Northern Mariana Islands': 'MP',
 'Ohio': 'OH',
 'Oklahoma': 'OK',
 'Oregon': 'OR',
 'Pennsylvania': 'PA',
 'Puerto Rico': 'PR',
 'Rhode Island': 'RI',
 'South Carolina': 'SC',
 'South Dakota': 'SD',
 'Tennessee': 'TN',
 'Texas': 'TX',
 'Utah': 'UT',
 'Vermont': 'VT',
 'Virgin Islands': 'VI',
 'Virginia': 'VA',
 'Washington': 'WA',
 'West Virginia': 'WV',
 'Wisconsin': 'WI',
 'Wyoming': 'WY'
}

def preprocess(text):
    """
    Preprocess text before dedupe

    Parameters
    ----------
    text : str, input abstract of papers/posters string
    stemming : boolean, apply Porter stemmer if True,
        default True
    """
    if isinstance(text, (type(None), float)):
        text_preprocess = ''
    else:
        text = unidecode(text).lower()
        text = punct_re.sub(' ', text) # remove punctuation
        text_preprocess = w_tokenizer.tokenize(text)
        text_preprocess = ' '.join(text_preprocess)
    return text_preprocess


def read_setting_file(filename='settings'):
    """Read dedupe settings file"""
    settings_file = filename
    print('reading from ', settings_file)
    with open(settings_file, 'rb') as sf:
        deduper = dedupe.StaticDedupe(sf)
    return deduper


def read_training_file(deduper, filename='training.json'):
    """Read dedupe training file"""
    training_file = filename
    print('reading labeled examples from ', training_file)
    with open(training_file, 'rb') as tf:
        deduper.readTraining(tf)
    return deduper


def write_setting_file(deduper, filename='settings'):
    """Write dedupe setting file"""
    settings_file = filename
    with open(settings_file, 'wb') as sf:
        deduper.writeSettings(sf)
    print("Setting file saved")


def write_training_file(deduper, filename='training.json'):
    """Give a deduper, write a training file"""
    with open(filename, 'w') as tf:
        deduper.writeTraining(tf)
    print("Training file saved")


def format_text(text):
    """Fill empty string with none"""
    try:
        return preprocess(text)
    except:
        pass
    return ''


def dataframe_to_dict(df):
    """
    Transforms a pandas' dataframe to a dict used by dedupe
    """
    return dict((i, a) for (i, a) in enumerate(df.to_dict('records')))


def add_dedupe_col(df, df_dict, deduper, threshold):
    """
    add a deduplication column to the dataframe `df` using the `deduper`
    """
    df_new = df.copy()
    df_new['dedupe_id'] = None
    clustered = deduper.match(df_dict, threshold)
    clustered = list(clustered)
    cluster_assignment_idx = np.array([[row_id, c_id]
                                       for c_id in range(len(clustered))
                                       for row_id in clustered[c_id][0]])

    df_new.dedupe_id.iloc[cluster_assignment_idx[:, 0]] = cluster_assignment_idx[:, 1]
    new_idx = range(df_new.dedupe_id.max() + 1, df_new.dedupe_id.max() + 1 + df_new.dedupe_id.isnull().sum())
    df_new.dedupe_id[df_new.dedupe_id.isnull()] = new_idx
    return df_new
