import requests
from bs4 import BeautifulSoup

# Webtoon list url 
url = 'https://www.webtoons.com/en/genre'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all the webtoon cards in the webpage
webtoons = soup.find_all('a', class_='card_item')

for webtoon in webtoons:
    webtoonUrl = webtoon['href']
    webtoonResponse = requests.get(webtoonUrl)
    webtoonSoup = BeautifulSoup(webtoonResponse.text, 'html.parser')
    counts = webtoonSoup.find_all('em', class_='cnt')
    # fields we want
    title = webtoonSoup.find('h1', class_='subj' ).text
    genre = webtoonSoup.find('h2', class_='genre g_romance' ).text
    viewsCount = counts[0].text
    subscribedCount = counts[1].text
    rating = counts[2].text
    # can't access image so will find another way to get an image
    # image = webtoon.find('img')['src']
    print(title, genre, viewsCount, subscribedCount, rating)