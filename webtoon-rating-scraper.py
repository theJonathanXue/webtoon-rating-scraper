import requests
from bs4 import BeautifulSoup

def get_google_img(query):
    """
    gets a link to the first google image search result
    :param query: search query string
    :result: url string to first result
    """
    url = "https://www.google.com/search?q=" + str(query) + "&source=lnms&tbm=isch"
    headers={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}

    html = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html, 'html.parser')
    # get first google image result (index 0 is the google logo)
    image = soup.findAll('img')[1]

    if not image:
        return 
    return image['src']

def get_all_webtoons_data():
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
        # can't access image directly from webtoons page so will find another way to get an image
        # image = webtoon.find('img')['src']
        query = "https://swebtoon-phinf.pstatic.net/" + title + "webtoon"
        image = get_google_img(query)

if __name__ == '__main__':
    get_all_webtoons_data()