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


def fetch_ads(start, end):
    pages = np.arange(start, end, 1)
    ads = pd.DataFrame(columns=["page", "link"])
    for page_n in pages:
        page = fetch_page("https://www.kijiji.ca/b-appartement-condo/ville-de-montreal/" + str(page_n) +
                            "/c37l1700281?radius=10.0&ad=offering&address=Montr%C3%A9al%2C+QC+H2W+1S8&ll=45.503905,-73.570856", 3)
        if page:
            soup = BeautifulSoup(page.text, 'html.parser')
            my_table = soup.find_all(class_=['title'])
            for tag in my_table:
                link = tag.get("href")
                if link:
                    ads = ads.append({"page": page_n, "link": link}, ignore_index=True)
            if page_n < end:
                sleep(randint(2, 5))
        else:
            print("Couldn't finish full scrapping. Stopped at page", page_n)
            break
    return ads


links = fetch_ads(1, 80)
links.to_csv("links.csv")
