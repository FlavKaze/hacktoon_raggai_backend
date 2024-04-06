from bs4 import BeautifulSoup
import requests
import os

#Defining pages
starting_page = "https://simpsons.fandom.com/wiki/Special:AllPages"
seed_page = "https://simpsons.fandom.com"  #Crawling the English Wikipedia



def get_links_episodes(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html')
    links_general = soup.find('div', class_='mw-allpages-body').find_all('li')
    links = [link.find('a')['href'] for link in links_general if link.find('a')]
    next_page = soup.find('div', class_='mw-allpages-nav').find_all('a')[-1]['href']
    return links, next_page


def crawl_page(url):
    response = requests.get(seed_page + url)
    soup = BeautifulSoup(response.content, 'html')
    h2_tags = soup.find_all('h2')
    p_tags = soup.find_all('p')
    text = ''
    for h2, p in zip(h2_tags, p_tags[1:]):
        text += h2.text + '\n' + p.text + '\n'
    with open('./pages/' + url.split('/')[-1] + '.txt', 'w') as f:
        f.write(text)

if __name__ == "__main__":
    links, next_page = get_links_episodes(starting_page)

    while True:
        for link in links:
            try:
                crawl_page(link)
                print(len(os.listdir('./pages')))
            except:
                pass

        try:
            links, next_page = get_links_episodes(seed_page + next_page)
        except:
            pass

        if not next_page:
            break