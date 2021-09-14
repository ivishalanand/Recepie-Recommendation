import pickle
import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver


def get_nutritional_info(soup, meal, index, url):
    data = []
    nutrition_dict = {}
    try:
        table = soup.find('table', attrs={'class': 'NutritionalInformationPanel_table__9Ndzx'})
        table_body = table.find('tbody')

        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])  # Get rid of empty values

        nutrition_dict = {"energy": {"per 100g": data[0][0], "per serving": data[0][1]},
                          "fat": {"per 100g": data[2][0], "per serving": data[2][1]},
                          "saturated_fat": {"per 100g": data[3][0], "per serving": data[3][1]},
                          "carbohydrate": {"per 100g": data[4][0], "per serving": data[4][1]},
                          "sugars": {"per 100g": data[5][0], "per serving": data[5][1]},
                          "fibre": {"per 100g": data[6][0], "per serving": data[6][1]},
                          "protein": {"per 100g": data[7][0], "per serving": data[7][1]},
                          "salt": {"per 100g": data[8][0], "per serving": data[8][1]},
                          }
    except:
        nutrition_dict: {}
        print_and_log("get_nutritional_info", index, meal, url)
    return nutrition_dict


def get_ingredients(soup):
    ingredients = [ingredient.get_text() for ingredient in soup.find_all("li", class_="IngredientList_entry__2S-YP")]
    return ingredients


def print_and_log(method, index, meal, url):
    log = "Error occurred in '{}' | index = {} | meal = {} | URL = {}\n".format(method, index, meal, url)
    print(log)
    with open("log.txt", "a") as file_object:
        # Append 'hello' at the end of file
        file_object.write(log)


def get_allergen(soup, meal, index, url):
    try:
        text = soup.find_all("div", class_="AllergensPanel_subtitle__6tpxA typography_fontSemiBold__I_LGP")[0].getText()
        allergen = text[text.find("(") + 1:text.find(")")].split(",")
    except:
        allergen = `None`
        print_and_log("get_allergen", index, meal, url)

    return allergen


def get_ratings(soup):
    try:
        stars_str = str(soup.find_all("span", class_="Rating_starsContainer__3v8m6 Rating_starsContainerLarge__2v5Q0")[0])
        rating = stars_str.count("Rating_starHalf__1liuu")/2 + stars_str.count("Rating_starFull__ZwdaZ")
    except:
        rating = 0
    return rating


def scrape_data(soup, index, url, driver):
    try:
        meal = soup.find("div", class_="RecipeHero_title__QhCLR").get_text()
    except:
        soup = get_page_soup(url, driver)
        meal = soup.find("div", class_="RecipeHero_title__QhCLR").get_text()

    reviews = soup.find("div", class_="RecipeHero_info__7c9En").get_text()
    description = soup.find("p", class_="ExpandingText_readMoreWrapper__1LKqW").get_text()
    prep_time = soup.find_all("div", class_="RecipeHero_metaItem__YXg_2")[0].get_text()
    try:
        region = soup.find_all("div", class_="RecipeHero_metaItem__YXg_2")[1].get_text()
    except:
        region = ""
    portion_size = soup.find("div", class_="ForXPeopleSubheading_forXPeopleSubheading__UxZgO "
                                           "typography_fontStyleSubHead__21OvR "
                                           "IngredientsPanel_subheading__IbZnA").get_text()
    basic_ingredients = soup.find("div", class_="RecipeBasicsSection_label__10eFC").get_text().split(",")
    nutritional_info = get_nutritional_info(soup, meal, index, url)
    cooking_instruction = [instruction.get_text() for instruction in
                           soup.find_all("li", class_="StepListItem_stepListItem__2z5zk")]
    ingredients = get_ingredients(soup)
    allergen = get_allergen(soup, meal, index, url)
    rating = get_ratings(soup)

    meal_info_dict = {"meal": meal,
                      "reviews": reviews,
                      "description": description,
                      "prep_time": prep_time,
                      "region": region,
                      "portion_size": portion_size,
                      "basic_ingredients": basic_ingredients,
                      "cooking_instruction": cooking_instruction,
                      "nutritional_info": nutritional_info,
                      "ingredients": ingredients,
                      "allergen": allergen,
                      "rating": rating
                      }

    return meal_info_dict


def save_data(data, index, div):
    if index % div == 0:
        with open('data.pkl', 'wb') as f:
            pickle.dump(data, f)
        print("SAVING........... - {} out of 2460 saved!".format(index))
    return


def get_page_soup(url, driver):
    driver.get(url)
    time.sleep(1)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, features="html.parser")
    return soup


def scrape():
    driver = webdriver.Chrome(executable_path='/Users/visanand2/Desktop/Pycharm/Recepie-Recommendation/chromedriver')

    recipe_links = pd.read_csv("Meals_slug.csv")
    recipe_links["url"] = recipe_links.url.apply(lambda x: "https:gousto.co.uk" + x)
    recipe_links.drop(0, axis=0, inplace=True)
    data = []

    for index, url in enumerate(recipe_links["url"]):
        print("Running on index {}".format(index))
        soup = get_page_soup(url, driver)
        data.append([index, scrape_data(soup, index, url, driver)])
        save_data(data, index, 100)

    save_data(data, index, 1)


if __name__ == '__main__':
    scrape()
