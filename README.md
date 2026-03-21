# Smoogle (Search Engine)
## What is it?
Smoogle is a spiritual successor to a project I created a while back called "JASE (Just Another Search Engine)". As per
many of my older projects, it was completely vibe coded. I feel shame regarding that. Thus, (instead of sitting around) 
I created a new version.
## Crawling information
Smmogle's crawler is semi-automatic. It requires a user in order to start it. It sends one request every five seconds
(Normal Crawling Etiquette)
### How is Crawling Started?
1. A user does not see a website that they want
2. They go to the crawling page
3. They set how deep they want to crawl
4. They enter the link
5. They click "Crawl!"
6. The website will be indexed

## Demo
Demo is currently hosted on:
http://srv1496621.hstgr.cloud

## Endpoint Documentation
POST: /crawl. Accepts Form Data: {url: STR, depth: INT} Returns: HTML data
GET: /crawl-web. Web interface for the web crawler.
GET: /. Home Page
POST: /search. Search for a term. Accepts Form Data: {query: STR} Returns: A rendered template of search.html
