import requests
from bs4 import BeautifulSoup
import json
import os

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}

# google changes the html formatting all the time so this breaks
def get_google_img(query):
    """
    gets a link to the first google image search result
    :param query: search query string
    :result: url string to first result
    """
    try:
        url = "https://www.google.com/search?q=" + str(query) + "&source=lnms&tbm=isch"
        print(url)

        html = requests.get(url, headers=headers).text
        soup = BeautifulSoup(html, 'html.parser')

        # first attempt that used to work
        # get first google image result (index 0 is the google logo)
        images = soup.findAll('img')
        image = images[1]
        return

        # second attempt
        # get all images with alt that includes the string 'webtoon'
        swebtoon = "https://swebtoon-phinf.pstatic.net/"
        image = soup.select_one('a.wXeWr.islib.nfEiy')
        print(image)

        if not image:
            print('no image found')
            return 
        return image['src']
    except requests.exceptions.RequestException as e:
        print(f'An error occurred while making the request to find image: {e}')
    except AttributeError as e:
        print(f'An error occurred while parsing the HTML content to find image: {e}')
    

def get_all_webtoons_data():
    # store webtoons data in list
    all_webtoon_data = []

    # Webtoon list url 
    try:
        session = requests.Session()
        url = 'https://www.webtoons.com/en/genre'
        response = session.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all the webtoon cards in the webpage
        webtoons = soup.find_all('a', class_='card_item')

        for webtoon in webtoons:
            webtoon_url = webtoon['href']
            webtoon_response = session.get(webtoon_url, headers=headers)
            webtoon_soup = BeautifulSoup(webtoon_response.text, 'html.parser')
            counts = webtoon_soup.find_all('em', class_='cnt')

            # fields we want
            title = webtoon_soup.find('h1', class_='subj' ).text
            genre = webtoon_soup.select('.genre')[0].text
            views_count = counts[0].text
            subscribed_count = counts[1].text
            rating = counts[2].text

            # can't access image directly from webtoons page so will find another way to get an image
            query = "https://swebtoon-phinf.pstatic.net/" + title + "webtoon"
            # image = get_google_img(query)

            # webtoon data
            webtoon_data = {
                "url": webtoon_url,
                "title": title,
                "genre": genre,
                "views_count": views_count,
                "subscribed_count": subscribed_count,
                "rating": rating,
                # "image": image 
            }

            # store in list
            all_webtoon_data.append(webtoon_data)
        
        return all_webtoon_data
    except requests.exceptions.RequestException as e:
        print(f'An error occurred while making the request: {e}')
    except AttributeError as e:
        print(f'An error occurred while parsing the HTML content: {e}')

if __name__ == '__main__':
    file_path = 'all_webtoon_data.json'

    # 
    if not os.path.exists(file_path):
        all_webtoon_data = get_all_webtoons_data()

        # Convert the list of objects to a JSON string
        json_data = json.dumps(all_webtoon_data)

        # Open a file for writing
        with open('all_webtoon_data.json', 'w') as file:
            # Write the JSON string to the file
            file.write(json_data)
    
    