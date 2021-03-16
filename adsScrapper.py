import pandas as pd
from bs4 import BeautifulSoup
import re
from time import sleep
from random import randint
from listingScrapper import fetch_page


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
                break
            break
        break
    return services


def extract_parking_spots(soup):
    parking_spots = 0
    for element in soup.find_all("dt", string=["Stationnement inclus"]):
        for sibling in element.next_siblings:
            parking_spots = sibling.text.strip()
            break
        break
    return parking_spots


def extract_utilities(soup):
    utilities = []
    for element in soup.find_all("h4", string=["Électroménagers"]):
        for service_list in element.next_siblings:
            for item in service_list.find_all(class_=[classInJs("groupItem")]):
                utilities.append(item.text.strip())
    return ", ".join(utilities)


def extract_furnished(soup):
    furnished = False
    for element in soup.find_all("dt", string=["Meublé"]):
        for sibling in element.next_siblings:
            furnished = sibling.text.strip()
            furnished = furnished == "Oui" or furnished == "Yes"
            break
        break
    return furnished


def extract_size(soup):
    size = ""
    for element in soup.find_all("dt", string=["Taille (pieds carrés)"]):
        for sibling in element.next_siblings:
            size = sibling.text.strip()
            break
        break
    return size


def extract_air_conditioner(soup):
    air_conditioned = False
    for element in soup.find_all("dt", string=["Air conditionné"]):
        for sibling in element.next_siblings:
            air_conditioned = sibling.text.strip()
            air_conditioned = air_conditioned == "Oui" or air_conditioned == "Yes"
            break
        break
    return air_conditioned


def extract_allow_pets(soup):
    allow_pets = ""
    for element in soup.find_all("dt", string=["Animaux acceptés"]):
        for sibling in element.next_siblings:
            allow_pets = sibling.text.strip()
            break
        break
    return allow_pets

def fetch_ad(link):
    ad = {}
    page = fetch_page(link, 3)
    soup = BeautifulSoup(page.text, 'html.parser')
    ad["link"] = link
    ad["price"] = extract_price(soup)
    ad["title"] = extract_title(soup)
    ad["address"] = extract_address(soup)
    ad["type"] = extract_type(soup)
    ad["rooms"] = extract_rooms(soup)
    ad["bathroom"] = extract_bathroom(soup)
    ad["services"] = extract_services(soup)
    ad["parking_spots"] = extract_parking_spots(soup)
    ad["utilities"] = extract_utilities(soup)
    ad["furnished"] = extract_furnished(soup)
    ad["size"] = extract_size(soup)
    ad["air_conditioned"] = extract_air_conditioner(soup)
    ad["allow_pets"] = extract_allow_pets(soup)
    return flatten_dict(ad)


def fetch_ads(df):
    ads = []
    for i, row in df.iterrows():
        ads.append(fetch_ad("https://www.kijiji.ca" + row["link"]))
        print(f'{i+1}/{len(df.index)}')
        sleep(randint(2, 5))
    return pd.DataFrame(ads)



#print(fetch_ad("https://www.kijiji.ca/v-appartement-condo/ville-de-montreal/4-1-2-style-condo-tout-inclus-semi-meuble/1553388246"))
#print(fetch_ad("https://www.kijiji.ca/v-appartement-condo/ville-de-montreal/condo-4-1-2-meuble-vieux-port-centre-ville-1-mois-offert/1516967309?undefined"))
#ads = fetch_ads(links[:1])
#print(ads)
#ads.to_csv("ads.csv")
