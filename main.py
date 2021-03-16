from adsScrapper import fetch_ads
from listingScrapper import fetch_listing
import pandas as pd
#links = fetch_listing(1, 80)
#links.to_csv("links.csv")
links = pd.read_csv("links.csv")
ads = fetch_ads(links)
ads.to_csv("ads.csv")