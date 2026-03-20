import os
import sqlite3
import threading

from flask import Flask, request, render_template


def _init_db():
    db = sqlite3.connect('SearchData.db')
    db.execute('CREATE TABLE IF NOT EXISTS SearchData (url TEXT, title TEXT, content TEXT, datetime TEXT, idfdf TEXT)')
    db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS SearchData_index USING fts5(url, title, content)")
    db.commit()
app = Flask(__name__)

@app.route("/crawl", methods=["POST"])
def crawl():
    url = request.form["url"]
    depth = int(request.form["depth"])
    threading.Thread(target=lambda: os.system(f"python SmoogleCrawler.py {url} --depth {depth}")).start()
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
    db_query = "SELECT url, title FROM SearchData_index WHERE SearchData_index MATCH ? ORDER BY rank"
    #get the IDFDF data from the database
    data = db.execute(db_query, (query,)).fetchall()
    return render_template('search.HTML', data=data, query=query)

_init_db()
if __name__ == '__main__':
    db = sqlite3.connect('SearchData.db')
    db.execute('CREATE TABLE IF NOT EXISTS SearchData (url TEXT, title TEXT, datetime TEXT)')
    db.commit()
    app.run()
