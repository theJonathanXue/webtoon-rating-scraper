import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
import json
import os


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}

# attempt with selenium
# medium article that helped: https://medium.com/@dian.octaviani/method-1-4-automation-of-google-image-scraping-using-selenium-3972ea3aa248
def get_google_img(search_query):
    search_url = f'https://www.google.com/search?q={search_query}&source=lnms&tbm=isch'

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--allow-cross-origin-auth-prompt')

    browser = webdriver.Chrome(options=options)

    # Open browser to begin search
    browser.get(search_url)

    # XPath for the 1st image that appears in Google: //*[@id="islrg"]/div[1]/div[1]/a[1]/div[0]/img
    img_box = browser.find_element("xpath",'//*[@id="islrg"]/div[1]/div[1]/a[1]/div[1]/img')
    # Click on the thumbnail
    img_box.click()

    # Wait between interaction
    time.sleep(2)

    page_source = browser.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    image = soup.find('img', class_='n3VNCb KAlRDb')['src']
    print(image)
    return image

    # this gets the image stored as base64 encoded hash 
    # session = requests.Session()

    # driver = webdriver.Firefox()
    # # going to Images Section
    # driver.get(f'https://www.google.com/search?q={search_query}&source=lnms&tbm=isch')

    # img_box = browser.find_element_by_xpath('//*[@id="islrg"]/div[1]/div[1]/a[1]/div[1]/img')
    # img_box.click()

    # driver.implicitly_wait(5)

    
    # page_source = driver.page_source
    # driver.close()

    # soup = BeautifulSoup(page_source, 'html.parser')
    # img_tag = soup.find('img', class_='rg_i Q4LuWd')
    # # a_tag = soup.find('a', class_='wXeWr islib nfEiy')

    # # print(a_tag)
    # # a_response = session.get(a_tag['href'], headers=headers)
    # # a_soup = BeautifulSoup(a_response.text, 'html.parser')
    # image = soup.find('img', class_='n3VNCb KAlRDb')
    # print(image['href'])
    
    # # print(img_tag['src'])
    
    # driver.quit()

# # attempt with requests
# # google changes the html formatting all the time so this breaks
# def get_google_img(query):
#     """
#     gets a link to the first google image search result
#     :param query: search query string
#     :result: url string to first result
#     """
#     try:
#         url = "https://www.google.com/search?q=" + str(query) + "&source=lnms&tbm=isch"
#         print(url)

#         html = requests.get(url, headers=headers).text
#         soup = BeautifulSoup(html, 'html.parser')

#         # first attempt that used to work
#         # get first google image result (index 0 is the google logo)
#         images = soup.findAll('img')
#         image = images[1]
#         return

#         # second attempt
#         # get all images with alt that includes the string 'webtoon'
#         swebtoon = "https://swebtoon-phinf.pstatic.net/"
#         image = soup.select_one('a.wXeWr.islib.nfEiy')
#         print(image)

#         if not image:
#             print('no image found')
#             return 
#         return image['src']
#     except requests.exceptions.RequestException as e:
#         print(f'An error occurred while making the request to find image: {e}')
#     except AttributeError as e:
#         print(f'An error occurred while parsing the HTML content to find image: {e}')
    

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

    with open(file_path) as json_file:
        # load the json data into a variable
        data = json.load(json_file)
    print(data[0])
    print(len(data))
    query = 'https://swebtoon-phinf.pstatic.net/ true beauty webtoon'
    get_google_img(query)
    
    