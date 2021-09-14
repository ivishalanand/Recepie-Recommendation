import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver


def setup():
    driver = webdriver.Chrome(executable_path='/Users/visanand2/Desktop/Pycharm/Recepie-Recommendation/scraper/chromedriver')

    driver.get('https://www.gousto.co.uk/cookbook/recipes?page=153')
    time.sleep(5)  # Let the user actually see something!

    try:
        close_popup = driver.find_element_by_class_name(
            "sumome-react-wysiwyg-component sumome-react-wysiwyg-popup-button sumome-react-wysiwyg-button")
        close_popup.click()
    except:
        pass

    return driver


def get_meal_slug(soup):
    meals_slug = []
    slugs = soup.find_all("a", class_='Link_link__3euZY anchor_defaultLinkStyle__2hBMg typography_fontSemiBold__2UvpS')
    for slug in slugs:
        meals_slug.append(slug['href'])

    pd.DataFrame(meals_slug, columns=["url"]).to_csv("Meals_slug.csv", index=False)


def get_data(driver):
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, features="html.parser")
    get_meal_slug(soup)
    return


if __name__ == '__main__':
    driver = setup()
    get_data(driver)
