import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import json
import os

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--disable-web-security')
options.add_argument('--allow-running-insecure-content')
options.add_argument('--allow-cross-origin-auth-prompt')
browser = webdriver.Chrome(options=options)
logging.basicConfig(filename='errors.log', level=logging.ERROR)

# attempt with selenium
# medium article that helped: https://medium.com/@dian.octaviani/method-1-4-automation-of-google-image-scraping-using-selenium-3972ea3aa248
def get_google_img(search_query):
    # Open browser to begin search
    try:
        search_url = f'https://www.google.com/search?q={search_query}&source=lnms&tbm=isch'
        
        browser.get(search_url)

        # XPath for the 1st image that appears in Google: //*[@id="islrg"]/div[1]/div[1]/a[1]/div[0]/img
        img_box = browser.find_element("xpath",'//*[@id="islrg"]/div[1]/div[1]/a[1]/div[1]/img')
        # Click on the thumbnail
        img_box.click()

        time.sleep(1)
        # XPath for the img containing the correct src (might change, if it breaks then inspect element and copy XPATH)
        try:
            WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="Sva75c"]/div[2]/div/div[2]/div[2]/div[2]/c-wiz/div[2]/div[1]/div[1]/div[2]/div/a/img'))
            )
        finally:
            fir_img = browser.find_element(By.XPATH,'//*[@id="Sva75c"]/div[2]/div/div[2]/div[2]/div[2]/c-wiz/div[2]/div[1]/div[1]/div[2]/div/a/img')
            # Retrieve attribute of src from the element
            img_src = fir_img.get_attribute('src')

            # check if img_src starts with https://swebtoon-phinf.pstatic.net
            if img_src.startswith("https://swebtoon-phinf.pstatic.net"):
                return img_src
            else:
                logging.error(''+search_query+' | ''failed''')
                return

    except Exception as e: 
        logging.error(''+search_query+' | '+str(e)+'')

    
# this script gets webtoon data from the genres page, which has duplicates in different genres
# I realized after it is probably better to get the list of webtoons from https://www.webtoons.com/en/dailySchedule instead 
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

            # get image from first google image result
            image = get_google_img(query)

            # webtoon data
            webtoon_data = {
                "url": webtoon_url,
                "title": title,
                "genre": genre,
                "views_count": views_count,
                "subscribed_count": subscribed_count,
                "rating": rating,
                "img_url": image 
            }

            # store in list
            all_webtoon_data.append(webtoon_data)
        browser.close()
        browser.quit()
        
        return all_webtoon_data
    except requests.exceptions.RequestException as e:
        print(f'An error occurred while making the request: {e}')
    except AttributeError as e:
        print(f'An error occurred while parsing the HTML content: {e}')

if __name__ == '__main__':
    file_path = 'all_webtoon_data.json'
 
    if not os.path.exists(file_path):
        all_webtoon_data = get_all_webtoons_data()

        # Convert the list of objects to a JSON string
        json_data = json.dumps(all_webtoon_data)

        # Open a file for writing
        with open('all_webtoon_data.json', 'w') as file:
            # Write the JSON string to the file
            file.write(json_data)



    



    
    