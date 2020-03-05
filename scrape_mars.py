from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import pymongo
import tweepy
import config


def scrape():
    mars_data = {}

    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}

    browser = Browser("chrome", **executable_path, headless=True)
    
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    html = browser.html
    soup = bs(html, "html.parser")

    title = soup.find('div', class_='content_title').get_text()
    date = soup.find('div', class_='list_date').get_text()
    summary = soup.find('div', class_="article_teaser_body").get_text()

    url2 = "https://www.jpl.nasa.gov"

    browser.visit(url2 + "/spaceimages/?search=&category=Mars")

    html = browser.html
    soup = bs(html, 'html.parser')

    featured_image = soup.find('article', class_="carousel_item").find('a')['data-fancybox-href']
    featured_image_url = url2 + featured_image

    auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
    auth.set_access_token(config.access_token, config.access_token_secret)

    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

    full_tweet = api.user_timeline("marswxreport" , count = 1)

    mars_weather = full_tweet[0]['text']
    tweet_date = full_tweet[0]['created_at'][0:10]
    tweet_url = full_tweet[0]['entities']['urls'][0]['url']


    url4 = "https://space-facts.com/mars/"

    data = pd.read_html(url4)

    mars_info = pd.DataFrame(data[0])
    df = pd.DataFrame(data[1])

    mars_earth = df.set_index("Mars - Earth Comparison")

    mars_info.columns = ['Mars','Data']

    mars_table = mars_info.set_index("Mars")

    table = mars_table.to_html()
    table2 = mars_earth.to_html()


    url5 = "https://astrogeology.usgs.gov"
    browser.visit(url5 + "/search/results?q=hemisphere+enhanced&k1=target&v1=Mars")

    html = browser.html
    soup = bs(html, 'html.parser')

    results = soup.find_all('div', class_="item")

    links = {}
    hemisphere_image_urls = []
    data = []
    for result in results:
        link = result.find('a')['href']
        data.append(link)
        
    for link in data:
        browser.visit(url5 + link)

        html = browser.html
        soup = bs(html, 'html.parser')
        links = {
            'title': soup.find('div').find('h2').text.replace(' Enhanced', ''),
            'image_url': soup.find('li').find('a')['href']
        }
        hemisphere_image_urls.append(links)

    
    mars_data = {
        'news_title': title,
        'date': date,
        'summary': summary, 
        'image_url': featured_image_url,
        'weather': mars_weather,
        'tweet': tweet_date,
        'url': tweet_url,
        'table': table,
        'table2': table2,
        'images': hemisphere_image_urls
    }
    return mars_data

