from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import arabic_reshaper
from bidi.algorithm import get_display
import snscrape.modules.twitter as sntwitter
import sys
import time
import re
from re import search
import pandas as pd


driver=None
current_scrolls = 0
old_height = 0
def driveCreation():
    try:
        global driver
        options = Options()
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        #options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1420,1080")

        try:
            driver = webdriver.Firefox(options=options)
        except Exception as e:
            print(sys.exc_info()[0])
            exit()
    except WebDriverException as e:
        print(sys.exc_info()[0])
        exit() 


#Scroll over all the page given a specific number of scrolls
def scroll(total_scrolls):
    scrolls = 0
    while (scrolls < total_scrolls):
        try:
            scrollHeight = driver.execute_script("return window.scrollMaxY")
            while driver.execute_script("return window.pageYOffset") < scrollHeight:
                driver.execute_script("window.scrollByPages(1)")
                scrolls = scrolls +1
                time.sleep(0.5)        
        except TimeoutException:
            print('ok')
            print(sys.exc_info()[0])
    return

def arabic_reshape(content):
    try:
        tweet=re.sub(r'[a-zA-Z0-9!@#$%^&*(){};:,./<>?]', '', content).strip()
        reshaped_text = arabic_reshaper.reshape(tweet)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception as e:
        print(sys.exc_info()[0])
        pass


def scrape(url,total_scrolls=2,username="",search_query="",limit=500):
    commments_scrolled=[]

    try:
        if search('youtube',url):
            res=driveCreation()
            time.sleep(5)

            driver.get(url)

            scroll(total_scrolls)
            #time.sleep(10)

            comments = driver.find_elements_by_css_selector('.ytd-comment-renderer .style-scope div yt-formatted-string[id="content-text"]')
            for idx,comment in enumerate(comments):
                if (comment.text != ''):
                    try:
                        reshaped_text = arabic_reshaper.reshape(comment.text)  
                        bidi_text = get_display(reshaped_text)
                        commments_scrolled.append(bidi_text)
                    except AssertionError:
                        pass
                else:
                    span = comment.find_elements_by_xpath('.//span')
                    res_sp=""
                    for element in span:
                        res_sp += element.text
                    commments_scrolled.append(res_sp)
                    pass
            return commments_scrolled
        else:
            tweets_list2 = []
            tweets_list1=[]
            if(search_query != ""):
                for i,tweet in enumerate(sntwitter.TwitterSearchScraper(search_query,'since:2020-06-01 until:2020-07-31').get_items()):
                    if i> limit:
                        break
                    try:
                        tweet_reshaped =arabic_reshape(tweet.content)
                        tweets_list1.append(tweet_reshaped)     
                    except Exception as e:
                        print(sys.exc_info()[0])
                        pass
            if (username != ""):
                for i,tweet in enumerate(sntwitter.TwitterSearchScraper('from:',username).get_items()):
                    if i> limit:
                        break 
                    try:
                        print(tweet.content)
                        tweet_reshaped =arabic_reshape(tweet.content)
                        tweets_list2.append(tweet_reshaped)     
                    except Exception as e:
                        print(sys.exc_info()[0])
                        pass

            list_res = tweets_list1 + tweets_list2
            return list_res

    except:
        pass

scraped_data  = scrape(url='https://www.youtube.com/watch?v=fCIcQn_6Vgg',username="",search_query="",limit=200)
print(scraped_data)
