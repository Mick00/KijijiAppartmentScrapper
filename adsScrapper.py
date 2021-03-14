import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
from time import sleep
from random import randint

links = pd.read_csv("links.csv", index_col=0)


def classInJs(name):
    return re.compile(name + ".*")


def get_value(string):
    if len(string) > 0:
        strings = string.split(":")
        if len(strings) >= 2:
            return strings[1].strip()
    return ""


def flatten_dict_(pyobj, keystring=''):
    if type(pyobj) == dict:
        keystring = keystring + '_' if keystring else keystring
        for k in pyobj:
            yield from flatten_dict_(pyobj[k], keystring + str(k))
    else:
        yield keystring, pyobj


def flatten_dict(dict):
    return {k: v for k, v in flatten_dict_(dict)}


def extract_price(soup):
    price = ""

    for element in soup.find_all(class_=[classInJs("priceWrapper")]):
        span = element.find("span")
        price = span.get("content")
    return price


def extract_title(soup):
    title = ""
    for element in soup.find_all("h1", class_=[classInJs("title")]):
        title = element.text.strip()
    return title


def extract_address(soup):
    address = ""
    for element in soup.find_all(class_=[classInJs("address")]):
        address = element.text.strip()
    return address


def extract_type(soup):
    type = ""
    elements = soup.find_all(class_=[classInJs("noLabelValue")])
    if len(elements) > 0:
        type = elements[0].text.strip()
    return type


def extract_rooms(soup):
    room = ""
    elements = soup.find_all(class_=[classInJs("noLabelValue")])
    if len(elements) > 1:
        room = get_value(elements[1].text.strip())
    return room


def extract_bathroom(soup):
    bathroom = ""
    elements = soup.find_all(class_=[classInJs("noLabelValue")])
    if len(elements) > 2:
        bathroom = get_value(elements[2].text.strip())
    return bathroom


def extract_services(soup):
    services = {}
    for element in soup.find_all("h4", string=["Services inclus"]):
        for service_list in element.next_siblings:
            for item in service_list.find_all(class_=[classInJs("groupItem")]):
                service = item.find("svg").get("aria-label")
                if len(service) > 0:
                    service = service.split(":")
                    services[service[1].strip()] = service[0] == "Oui" or service[0] == "Yes"
    return services


def fetch_ad(link):
    ad = {}
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'html.parser')
    ad["link"] = link
    ad["price"] = extract_price(soup)
    ad["title"] = extract_title(soup)
    ad["address"] = extract_address(soup)
    ad["type"] = extract_type(soup)
    ad["rooms"] = extract_rooms(soup)
    ad["bathroom"] = extract_bathroom(soup)
    ad["services"] = extract_services(soup)
    return flatten_dict(ad)


def fetch_ads(df):
    ads = []
    for i, row in df.iterrows():
        ads.append(fetch_ad("https://www.kijiji.ca" + row["link"]))
        print(f'{i+1}/{len(df.index)}')
        sleep(randint(2, 5))
    return pd.DataFrame(ads)

print("https://www.kijiji.ca" + links.loc[0].link)

ads = fetch_ads(links[:100])
ads.to_csv("ads.csv")
