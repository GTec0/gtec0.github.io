---
layout: post
title: Webscraping with python and bs4
tags: [python, web scraping, beautifulsoup, data extraction, python tutorial, web automation, scraping, programming, coding, requests, beginner friendly, how-to, guide]
comments: true
mathjax: true
author: Asahluma Tyika
---
# Web Scraping with Python and BeautifulSoup

Web scraping allows you to extract data from websites using code. In this tutorial, we’ll use **Python** and **BeautifulSoup** to scrape a webpage.

## Prerequisites

Make sure you have Python installed. Then, install the required package:

```
pip install beautifulsoup4 requests
```

## Basic Web Scraping

Here’s a simple script to scrape titles from a website:

```
import requests
from bs4 import BeautifulSoup

url = "https://example.com"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

for title in soup.find_all("h2"):
    print(title.text)
    
```

## Explanation

*   `requests.get(url)` fetches the webpage.
*   `BeautifulSoup(response.text, "html.parser")` parses the HTML.
*   `soup.find_all("h2")` finds all `<h2>` tags and extracts text.

## Conclusion

Web scraping is a powerful technique to extract information. Make sure to follow a website’s **robots.txt** rules before scraping.
