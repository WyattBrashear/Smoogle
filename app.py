import json
import os
import sqlite3
import threading
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from flask import Flask, request, render_template
from sklearn.feature_extraction.text import TfidfVectorizer

def get_favicon(url):
    #So turns out BS4 can just extract the favicons for you (:P)
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    favicon = soup.find_all('link', rel=['icon', 'shortcut icon'])
    if favicon:
        if not favicon[0]['href'].startswith('http'):
            if '/' in favicon[0]['href']:
                return f"{url}{favicon[0]['href']}"
            else:
                return f"{url}/{favicon[0]['href']}"
        else:
            return favicon[0]['href']
    else:
        return f"{url}/favicon.ico"

def _init_db():
    db = sqlite3.connect('SearchData.db')
    db.execute('CREATE TABLE IF NOT EXISTS SearchData (url TEXT, title TEXT, content TEXT, datetime TEXT, itfdf TEXT, favicon TEXT)')
    db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS SearchData_index USING fts5(url, title, content, favicon)")
    db.commit()
app = Flask(__name__)

def exec_crawl(url, depth):
    db = sqlite3.connect('SearchData.db')
    depth = int(depth)
    headers = {'User-Agent': "SmoogleBot"}
    r = requests.get(url, headers=headers)
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
    db.execute('INSERT INTO SearchData (url, title, content, datetime, itfdf, favicon) VALUES (?, ?, ?, ?, ?, ?)',
               (url, title, str(soup.get_text()), datetime.now().isoformat(), json.dumps(json_data), get_favicon(url)))
    db.execute('INSERT INTO SearchData_index (url, title, content, favicon) VALUES (?, ?, ?, ?)',
               (url, title, str(soup.get_text()), get_favicon(url)))
    links = soup.find_all('a')
    db.commit()
    if depth > 0:
        for link in links:
            if link.get('href') is not None:
                if link.get('href').startswith('http') and link.get('href') not in db.execute(
                        'SELECT url FROM SearchData').fetchall():
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
                        db.execute(
                            'INSERT INTO SearchData (url, title, content, datetime, itfdf, favicon) VALUES (?, ?, ?, ?, ?, ?)',
                            (link['href'], title, str(soup.get_text()), datetime.now().isoformat(),
                             json.dumps(json_data), get_favicon(link['href'])))
                        db.execute('INSERT INTO SearchData_index (url, title, content, favicon) VALUES (?, ?, ?, ?)',
                                   (link['href'], title, str(soup.get_text()), get_favicon(link['href'])))
                        db.commit()
                    except Exception as e:
                        print(e)
                    time.sleep(5)
        db.commit()

@app.route("/crawl", methods=["POST"])
def crawl():
    url = request.form["url"]
    depth = int(request.form["depth"])
    threading.Thread(target=lambda: exec_crawl(url, depth)).start()
    return 'Crawling Started, <a href="/">Go Home</a>', 202
@app.route("/crawl-web/", methods=["GET"])
def crawl_get():
    db = sqlite3.connect('SearchData.db')
    data = db.execute("SELECT url FROM SearchData").fetchall()
    return render_template("crawl.html", indexed=len(data))
@app.route('/')
def index():
    db = sqlite3.connect('SearchData.db')
    db.execute("SELECT url FROM SearchData")
    data = db.execute("SELECT url FROM SearchData").fetchall()
    return render_template(os.path.join('index.html'), indexed=len(data))

@app.route('/search/', methods=['POST'])
def search():
    db = sqlite3.connect('SearchData.db')
    query = request.form['query']
    if query == "":
        query = "None"
    db_query = "SELECT url, title, favicon FROM SearchData_index WHERE SearchData_index MATCH ? ORDER BY rank"
    #get the ITFDF data from the database
    data = db.execute(db_query, (f'"{query}"',)).fetchall()
    return render_template('search.HTML', data=data, query=query)

_init_db()
if __name__ == '__main__':
    db = sqlite3.connect('SearchData.db')
    _init_db()
    app.run()
