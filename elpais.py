from bs4 import BeautifulSoup

import json
import requests


ROOT_URL = 'https://elpais.com'
HEADERS = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "+
    "(KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36"
}


class VideoArticles:

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

    def get_article_data(self, url):
        """ Scrap article data from video~article and returns it"""
        article_data = {}
        
        response = requests.get(url, headers=HEADERS)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        script_tags = soup.find_all('script', type="application/ld+json")
        for script in script_tags:
            if '"@type":"NewsArticle"' in script.string:
                article_object = json.loads(script.string)
                article_data['url'] = article_object.get('url')
                article_data['publish_date'] = article_object.get('datePublished')
                article_data['title'] = article_object.get('headline')
                article_data['text'] = article_object.get('articleBody')
                article_data['video'] = self._download_file(article_object['video'])
                break
            elif '"@type":["ReportageNewsArticle"]' in script.string:
                article_object = json.loads(script.string)
                article_data['url'] = article_object.get('mainEntityOfPage')
                article_data['publish_date'] = article_object.get('datePublished')
                article_data['title'] = article_object.get('headline')
                article_data['text'] = article_object.get('articleBody')
                article_data['video'] = "media/"
                break

        return article_data

    def get_video_urls(self):
        """Scrap video~articles urls from elpais (España) and return them"""

        elpais_href_list = []
        
        response = requests.get(ROOT_URL+'/s/setEspana.html', headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        script_tags = soup.find_all('script', type="application/ld+json")
        
        for script in script_tags:
            if '"@type":"VideoObject"' in script.string:
                article_object = json.loads(script.string)
                elpais_href_list.append(article_object.get('url'))
        
        return elpais_href_list        

if __name__=='__main__':

    v_a = VideoArticles()

    video_urls = v_a.get_video_urls()
    
    data_list=[]
    if video_urls:
        for link in video_urls:
            data = v_a.get_article_data(link)
            if data:
                data_list.append(data)
    print("DONE")
    #  PENDING
    # for data in data_list:
    #     save_to_db(data)