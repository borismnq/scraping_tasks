#  feed div, role="feed"
#  eachpost, div, data-pagelet=contains "FeedUnit_"
#  modal div, testid=Keycommand_wrapper_ModalLayer
#  span, class="oi732d6d ik7dh3pa d2edcug0 qv66sw1b c1et5uql 
#               a8c37x1j muag1w35 enqfppq2 jq4qci2q a3bd9o3v 
#               knj5qynh m9osqain", dir="auto" , SEARCH FOR ITS PARENT

    
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import Comment

import time
import json
import requests
import re


ROOT_URL = 'https://facebook.com'
EMAIL = "boris_wtf@hotmail.com"
PASS= "Cabrones543"
HEADERS = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "+
    "(KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36"
}


class AttachedPosts:

    def __init__(self):
        pass

    def _download_file(self, video_objects):
        """Download video if exists save it in a file then returns path"""
        downloaded_video = []
        path="media/"
        for video_object in video_objects:
            if 'contentUrl' in video_object.keys() and video_object['contentUrl']!='':
                
                url = video_object['contentUrl']
                filename = url.split('/')[-1]
                r = requests.get(url, stream=True)
                
                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024): 
                        if chunk:
                            f.write(chunk)

                path+=filename
        return path    

if __name__=='__main__':
    
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--incognito')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("window-size=1400,900")

    driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)
    driver.get("http://www.facebook.com")

    username = driver.find_element(By.ID,"email")
    password = driver.find_element(By.ID,"pass")

    username.send_keys("boris_wtf@hotmail.com")
    password.send_keys(PASS)

    driver.find_element(By.ID,"u_0_b").click()
    time.sleep(7)
    driver.execute_script("window.scrollBy(0, 2000)")
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # driver.quit()
    feed_span = soup.find('span', id='ssrb_feed_start')
    posts  = []
    for sibling in feed_span.next_siblings:
        if not isinstance(sibling,Comment):
            if 'role' in sibling.attrs.keys() and 'feed' in sibling.attrs.values():
                posts_feed = sibling
    
    for tag in posts_feed:
        if not isinstance(tag,Comment):
            if 'data-pagelet' in tag.attrs.keys():
                posts.append(tag)

    #  EACH POST
    
    posts = [post for post in posts if post.select('div[data-testid*=Keycommand_wrapper_feed_attached_story]')!=[]]

    response = []
    for post in posts:
        post_data = {}
        href = post.find('a',href=re.compile('facebook')).find('a')
        if href.has_attr('aria-label'):
            post_data['who_shared'] = href['aria-label']
        
        attached_object = post.select('div[data-testid*=Keycommand_wrapper_feed_attached_story]')

        if attached_object:
            for at in attached_object:
                post_data['who_original'] = at.find('span',class_=None).string

        response.append(post_data)

    print(response)
