import json
import requests


def _download_file(url, name=None):
        """Download video if exists save it in a file then returns path"""
        downloaded_video = []
        path="media/"
        
        if name:
            filename = name
        else:
            filename = url.split('/')[-1]

        r = requests.get(url, stream=True)
        
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk:
                    f.write(chunk)

        path+=filename
        return path

def get_post_data(post):
    """Return post data"""
    post_data = {}
    post = post['node']
    post_type = post['__typename'].lower()
    post_data['id'] = post['id']
    post_data['date'] = post['taken_at_timestamp']
    post_data['texto'] = post['edge_media_to_caption']['edges'][0]['node']['text']
    post_data['media'] = _download_file(post['display_url'],post_data['id']+'.jpg') if 'image' in post_type else _download_file(post['video_url'],post_data['id']+'.mp4')
    post_data['likes'] = post['edge_liked_by']['count']
    post_data['comments'] = post['edge_media_to_comment']['count']

    return post_data
def scrap_ig_requests(user):
    
    """Get json representation ig user data"""
    
    url = f"https://www.instagram.com/{user}/?__a=1"

    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "+
        "(KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36"
    }

    response = requests.get(url,headers=headers)
    response = response.json()
    data = {}
    graphql = response['graphql']['user']

    data['id'] = graphql['id']
    data['name'] = graphql['full_name']
    data['following'] = graphql['edge_follow']
    data['followers'] = graphql['edge_followed_by']
    posts = graphql['edge_owner_to_timeline_media']['edges']

    posts_data = []
    for post in posts:        

        posts_data.append(get_post_data(post))
    data['posts_data'] = posts_data

    return data




print(scrap_ig_requests('claroperu'))