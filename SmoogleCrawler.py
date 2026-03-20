import argparse
import sqlite3
import time
from datetime import datetime
import json
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
import requests
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument('url', help='url to crawl')
parser.add_argument('--depth', type=int, default=1, help='depth of crawling')
args = parser.parse_args()

db = sqlite3.connect('SearchData.db')
db.execute('CREATE TABLE IF NOT EXISTS SearchData (url TEXT, title TEXT, content TEXT, datetime TEXT, idfdf TEXT)')
db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS SearchData_index USING fts5(url, title, content)")
db.commit()
depth = int(args.depth)
headers = {'User-Agent': "SmoogleBot"}
r = requests.get(args.url, headers=headers)
soup = BeautifulSoup(r.text, 'html.parser')
documents = [str(soup.get_text())]
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(documents)
json_data = {
    "wordlist": vectorizer.get_feature_names_out().tolist()
}
try:
    title = soup.title.text
except:
    title = "None"
db.execute('INSERT INTO SearchData (url, title, content, datetime, idfdf) VALUES (?, ?, ?, ?, ?)', (args.url, title, str(soup.get_text()),datetime.now().isoformat(), json.dumps(json_data)))
db.execute('INSERT INTO SearchData_index (url, title, content) VALUES (?, ?, ?)',
           (args.url, title, str(soup.get_text()),))
links = soup.find_all('a')
db.commit()
if depth > 0:
    for link in links:
        if link.get('href') is not None:
            if link.get('href').startswith('http') and link.get('href') not in db.execute('SELECT url FROM SearchData').fetchall():
                print(link['href'])
                try:
                    r = requests.get(link['href'], headers=headers)
                    soup = BeautifulSoup(r.text, 'html.parser')
                    documents = [str(soup.get_text())]
                    vectorizer = TfidfVectorizer()
                    tfidf_matrix = vectorizer.fit_transform(documents)
                    json_data = {
                        "wordlist": vectorizer.get_feature_names_out().tolist()
                    }
                    try:
                        title = soup.title.text
                    except Exception as e:
                        print(e)
                        title = "None"
                    db.execute('INSERT INTO SearchData (url, title, content, datetime, idfdf) VALUES (?, ?, ?, ?, ?)',
                               (link['href'], title, str(soup.get_text()), datetime.now().isoformat(), json.dumps(json_data)))
                    db.execute('INSERT INTO SearchData_index (url, title, content) VALUES (?, ?, ?)',
                               (link['href'], title, str(soup.get_text()),))
                    db.commit()
                except Exception as e:
                    print(e)
    db.commit()