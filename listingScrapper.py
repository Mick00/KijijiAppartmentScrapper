from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from time import sleep
from random import randint


def fetch_page(url, retry):
    page = False
    tries = 0
    while not page and tries <= retry:
        tries += 1
        try:
            page = requests.get(url)
        except:
            print("Request to", url, "failed. Sleeping 10 secs. Attempt", tries, "/", retry)
            sleep(10)
    return page


def fetch_listing(start, end):
    pages = np.arange(start, end+1, 1)
    ads = pd.DataFrame(columns=["page", "link", "distance"])
    for page_n in pages:
        page = fetch_page("https://www.kijiji.ca/b-appartement-condo/ville-de-montreal/" + str(page_n) +
                            "/c37l1700281?radius=12.0&ad=offering&address=Montr%C3%A9al%2C+QC+H2W+1S8&ll=45.503905,-73.570856", 3)
        if page:
            soup = BeautifulSoup(page.text, 'html.parser')
            cards = soup.find_all(class_=['info-container'])
            for card in cards:
                ad = {"page": page_n}
                link = False
                distance = False
                link = card.find("a", class_=["title"]).get("href")
                if link:
                    ad["link"] = link
                distance = card.find(class_=["distance"]).text.strip()
                if distance:
                    ad["distance"] = distance
                ads = ads.append(ad, ignore_index=True)
            print(f'{page_n}/{end}')
            if page_n < end:
                sleep(randint(2, 5))
        else:
            print("Couldn't finish full scrapping. Stopped at page", page_n)
            break
    return ads
