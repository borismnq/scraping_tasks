from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException,NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import time
import json
import re


ROOT_URL = 'https://facebook.com'
EMAIL = "boris_wtf@hotmail.com"
PASS= "Cabrones543"
HEADERS = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "+
    "(KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36"
}


class Facebook:

    def __init__(self):
        self.driver = None
        pass

    def create_webdriver(self):
        """ Creates a chrome webdriver with custom options"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        # options.add_argument("window-size=1400,900")
        options.add_argument('--incognito')    
        options.add_argument('--ignore-certificate-errors')        
        self.driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)
        return self.driver

    def login_fb(self):
        """Login on fb, and waiting for page load"""
        try:
            self.driver.get("http://www.facebook.com")

            username = self.driver.find_element(By.ID,"email")
            password = self.driver.find_element(By.ID,"pass")

            username.send_keys("boris_wtf@hotmail.com")
            password.send_keys(PASS)

            self.driver.find_element(By.ID,"u_0_b").click()
            print("click")
            # wait = WebDriverWait(self.driver,0).until(EC.element_to_be_located((By.NAME, 'body')))

            time.sleep(10)
            print("time over")
            return True
        except NoSuchElementException as e:
            return False

    def scroll_custom(self,pxs):
        """Scrolls custom pixeles and wait 4 secs for loading"""

        try:
            print("scroll")            
            self.driver.execute_script(f"window.scrollBy(0, {pxs})")
            time.sleep(4)
            return True
        except Exception as e:
            print(e)
            return False

    def find_posts(self):
        """Returns all posts from facebook feed"""

        try:            
            return self.driver.find_elements_by_xpath("//div[@data-testid='Keycommand_wrapper_feed_story']")
        except NoSuchElementException as e:
            return None

    def find_attached_posts(self, posts):
        """Returns all attached posts from list of posts"""
        attached_posts = []
        for post in posts:
            try:
                soup = BeautifulSoup(post.get_attribute('innerHTML'), 'html.parser')
                if soup.select('div[data-testid*=Keycommand_wrapper_feed_attached_story]')!=[]:
                    attached_posts.append(post)
            except NoSuchElementException as e:
                print("NO ELEMENT")
                pass

        return attached_posts

    def hover_and_parse(self,attached_post):
        """Returns html after hover each time element of attached post in order to make some other elements loads"""
        try: 
            div_describedby = attached_post.find_element_by_xpath(".//div[@aria-describedby]")

            classes_group = div_describedby.get_attribute('aria-describedby').split(" ")
            posted_time_pre = attached_post.find_element_by_id(classes_group[0])
            posted_time = posted_time_pre.find_elements_by_xpath('./span')

            for time_obj in posted_time:
                if not time_obj.get_attribute('class'):
                    # time.sleep(3)
                    hover = ActionChains(self.driver).move_to_element(time_obj)
                    hover.perform()
                    print("HOVERED 1")
                    # time.sleep(3)
            
            attached_object = attached_post.find_element_by_xpath(".//div[@data-testid='Keycommand_wrapper_feed_attached_story']")
            span = attached_object.find_element_by_xpath(".//span[@aria-labelledby]")
            if span:
                hover = ActionChains(self.driver).move_to_element(span)
                hover.perform()
                print("HOVERED 2")
                # time.sleep(2)

            return BeautifulSoup(attached_post.get_attribute('innerHTML'), 'html.parser')
        except NoSuchElementException as e:
            print("NOT FOUND",e)
            return None
        
    def find_who_shared_post(self,html):
        """Returns id and name of who shared the post"""
        try:

            aria_labelled_by = html.find('div',{"aria-labelledby" : True})
            h4_label = aria_labelled_by.find('h4',id=aria_labelled_by['aria-labelledby'])

            who_shared_post = h4_label.find('span',{"class" : None}).string
            post_id = self.find_post_id(aria_labelled_by.find('h4',id=aria_labelled_by['aria-labelledby']).parent.parent.parent)
            return {"who_shared_post":who_shared_post,"post_id":post_id}
        except TypeError as e:
            print(e)
            return None

    def find_who_original_post(self,html):
        """Returns id and name of who posted original post"""

        try:

            attached_info = html.find('div',{"data-testid":'Keycommand_wrapper_feed_attached_story'})
            who_original_post = ""
            if attached_info.find('strong'):
                who_original_post = attached_info.find('strong').find('span').string                      
            elif attached_info.select_one('a > span'):
                who_original_post = attached_info.select_one('a > span').string
                
            post_id = self.find_post_id(attached_info)

            return {"who_original_post":who_original_post,"post_id":post_id}
        except TypeError as e:
            print(e)
            return None
    
    def find_post_id(self,html):
        """Returns post id"""

        try:

            id_list = []
            links = html.find_all('a',href=re.compile('posts'))
            links += html.find_all('a',href=re.compile('photos'))
            links += html.find_all('a',href=re.compile('permalink'))
            links += html.find_all('a',href=re.compile('groups'))
            
            for link in links:
                fb_id = None
                if 'posts' in link['href']:
                    fb_id = link['href'].split('?')[0].split('/')[-1]
                    
                elif 'groups' in link['href'] and 'permalink' in link['href']:
                    fb_id = link['href'].split('?')[0].split('/')[-2]
                
                    
                elif 'permalink' in link['href'] :
                    fb_id= link['href'].split('fbid=')[1].split('&')[0]
                
                if not fb_id:
                    if 'photos' in link['href']:
                        fb_id = link['href'].split('?')[0].split('/')[-2]
                    if 'videos' in link['href']:
                        fb_id = link['href'].split('?')[0].split('/')[-2]
                if fb_id:
                    id_list.append(fb_id)
            shared_original_ids = []
            for _id in id_list:            
                if _id not in shared_original_ids:
                    shared_original_ids.append(_id)
            
            return shared_original_ids[0]
        except TypeError as e:
            print(e)
            return None


if __name__=='__main__':
    
    facebook = Facebook()
    webdriver = facebook.create_webdriver()
    posts = None
    response = []
    if webdriver:
        logged = facebook.login_fb()
        if logged:
            scrolled = facebook.scroll_custom(2500)
            if scrolled:
                posts = facebook.find_posts()
    
    attached_posts = None
    if posts:
        attached_posts = facebook.find_attached_posts(posts) 
    else:
        webdriver.quit()
        print("NO POSTS")
        print(response)
    
    if attached_posts:
        print(len(attached_posts))
        for att in attached_posts:
            attached_post = {}    
            
            soup = facebook.hover_and_parse(att)
            
            if soup:
                
                shared_info = facebook.find_who_shared_post(soup)
                if shared_info:
                    attached_post['shared'] = shared_info['who_shared_post']
                    attached_post['shared_id'] = shared_info['post_id']
                
                original_info = facebook.find_who_original_post(soup)
                if original_info:
                    attached_post['original'] = original_info['who_original_post']
                    attached_post['original_id'] = original_info['post_id']

                response.append(attached_post)
            else:
                
                print("PARSING PROBLEMS")

        webdriver.quit()
        print(response)
    else:
        webdriver.quit()
        print("NO ATTACHED POSTS")

        print(response)
