from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from parsel import Selector
import re
import time
import sys
from PlacesVisualiser import *
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.chrome.service import Service
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

googleAcceptButtonClicked = True

# Assuming chromedriver is in your PATH or you have the path to it
service = Service('chromedriver.exe')  # Replace 'chromedriver.exe' with your actual path if not in PATH

options = webdriver.ChromeOptions()
options.add_argument('headless')  # Make browser open in background
service.start()  # Start the ChromeDriver service


def create_driver():
    """
    Function to create a new instance of the webdriver.
    """
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True


def scrollDownLeftMenuOnGoogleMaps(driver, counter, waitingTime):
    menu_xpath = '/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div[3]/div'
    if check_exists_by_xpath(driver, menu_xpath):
        for i in range(counter):
            wait = WebDriverWait(driver, waitingTime)
            menu_left = wait.until(EC.visibility_of_element_located((By.XPATH, menu_xpath)))
            scroll_origin = ScrollOrigin.from_element(menu_left)
            ActionChains(driver).scroll_from_origin(scroll_origin, 0, 500).perform()


def searchForPlace(url, typeOfPlace):
    driver = create_driver()
    global googleAcceptButtonClicked
    driver.get(url)
    time.sleep(3)

    scrollDownLeftMenuOnGoogleMaps(driver, counter=3, waitingTime=10)

    page_content = driver.page_source
    response = Selector(page_content)

    placesResults = []
    for el in response.xpath('//div[contains(@aria-label, "Resultados")]/div/div[./a]'):
        placesResults.append({
            'link': el.xpath('./a/@href').extract_first(''),
            # 'title': el.xpath('./a/@aria-label').extract_first(''),
            'type': typeOfPlace
        })

    driver.quit()
    return placesResults


def clickAcceptAllButton(driver):
    global googleAcceptButtonClicked
    button_path = '//button[text()="Aceptar todo"]'
    wait = WebDriverWait(driver, 10)
    button = wait.until(EC.visibility_of_element_located((By.XPATH, button_path)))
    button.click()
    googleAcceptButtonClicked = True


def addLonLatToDataFrame(df):
    lat = []
    lon = []
    for index, row in df.iterrows():
        link = df.at[index, 'link']
        latLon = re.search('!3d(.*)!16', link).group(1).split('!4d')
        lat.append(latLon[0])
        lon.append(latLon[1])

    df['lat'] = lat
    df['lon'] = lon
    df = df[['lat', 'lon', 'type', 'link']]

    return df


def closeDriver(driver):
    driver.quit()


def generateUrls(typeOfPlace):
    pointsDirectory = "generatedPoints/"
    points_df = pd.read_csv(pointsDirectory + "measure_points_1r_1c.csv", index_col=False)

    base = 'https://www.google.com/maps/search/'
    generated_urls = []

    for index, row in points_df.iterrows():
        point_lat = row['lat']
        point_lon = row['lon']
        zoom = 16
        url = base
        url += str(typeOfPlace) + '/@'
        url += str(point_lat) + ',' + str(point_lon) + ',' + str(zoom) + 'z'
        generated_urls.append(url)
    return generated_urls


if __name__ == "__main__":

    start = time.time()

    types_of_places = sys.argv[1:]

    if len(types_of_places) == 0:
        types_of_places = ['parque']

    print(types_of_places)
    for typeOfPlace in types_of_places:

        urls = generateUrls(typeOfPlace)
        print("total number of points to check:" + str(len(urls)))

        list_of_places = []
        progressCounter = 0

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(searchForPlace, url, typeOfPlace): url for url in urls}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    new_places = future.result()
                    list_of_places += new_places
                except Exception as exc:
                    print(f'URL {url} generated an exception: {exc}')
                progressCounter += 1
                print("progress: " + str(round(100 * progressCounter / len(urls), 2)) + "%")

        df = pd.DataFrame(list_of_places)
        df = df.drop_duplicates()
        df = addLonLatToDataFrame(df)

        print("number of places:" + str(df.shape[0]))

        df.to_csv('database/' + typeOfPlace + '_v1.csv', index=False)

    end = time.time()
    print("total time:" + str(end - start) + " seconds --> " + str((end - start) / 60) + " minutes")
