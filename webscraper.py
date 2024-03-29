# -*- coding: utf-8 -*-
"""webscraper

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1yx5YHl7ohXCgMVPEKiSM4aH_XPAWfAKW

Quick Plan/Notes I've written down for making this webscraper:

Selenium - Web/Browser Controlling Library
https://www.selenium.dev/documentation/

randomstreetview.com - use for getting random locations by country. Also provides address.
https://randomstreetview.com/

The steps:
0. Before you start, keep a list of all European countries to explore. 
1. From randomstreetview.com, grab a new, random location from a country from the list.
2. Capture Screenshot of size 1200 x 1800
3. Grab address from the website, find numerical coordinates
4. Save photos in a folder. Name of the folder should be the name of the country. Name of the photo should be [Latitude]_[Longitude].jpg
5. Repeat for several photos

At the end we should have something like:

-Photos
    - France
        -45.245_32.519.jpg
        -69.420_42.185.jpg
        -...
    - Germany
        -...
        -...
"""

# Maybe further imports for photo handling and excel printing, if that's more to our taste
import selenium
import numpy
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import time
import os

sys.path.insert(0, '/usr/lib/chromium-browser/chromedriver')

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

google_maps_url = "https://maps.google.ca"
random_street_view_site = "https://randomstreetview.com/"
"""
# Full list
list_of_countries = ["France", "Germany", "United Kingdom", "Italy", "Spain", 
                     "Ukraine", "Poland", "Romania", "Netherlands","Belgium", 
                     "Switzerland", "Portugal", "Norway", "Ireland", "Finland", 
                     "Iceland", "Hungary", "Greece", "Denmark"]
"""
list_of_countries = ["United Kingdom", "Italy", "Spain", 
                     "Ukraine", "Poland", "Romania", "Netherlands","Belgium", 
                     "Switzerland", "Portugal", "Norway", "Ireland", "Finland", 
                     "Iceland", "Hungary", "Greece", "Denmark"]

# Making directories
for country in list_of_countries:
	if not os.path.exists(country):
	    os.makedirs(country)

# keep two drivers open for easier management
driver_ranStreetView = webdriver.Chrome(ChromeDriverManager().install())
driver_maps = webdriver.Chrome(ChromeDriverManager().install())
#driver_ranStreetView = webdriver.Chrome('chromedriver', chrome_options=chrome_options)
#driver_maps = webdriver.Chrome('chromedriver', chrome_options=chrome_options)

# Navigate to url
driver_ranStreetView.get(random_street_view_site)
driver_maps.get(google_maps_url)
driver_ranStreetView.set_window_size(500, 400)

street_view_img_id = "mapsConsumerUiSceneInternalCoreScene__widget-scene-canvas"
street_view_img_class = "mapsConsumerUiSceneInternalCoreScene__widget-scene.widget-scene"

for country in list_of_countries:
    #Reinitialize current url
    driver_ranStreetView.get(random_street_view_site)

    #Select
    dropdown_element = driver_ranStreetView.find_element_by_id("countries")
    select = Select(dropdown_element)

    select.select_by_visible_text(country)
    print(driver_ranStreetView.current_url)
    curr_country_url = driver_ranStreetView.current_url

    # For each image, save images
    num_images = 100
    
    for i in range(num_images):

        time.sleep(1)
        # Refresh page for another random locations 
        driver_ranStreetView.refresh()
        #driver_ranStreetView.get(curr_country_url)

        # Retrieve Address
        try:
            wait = WebDriverWait(driver_ranStreetView, 20).until(EC.visibility_of_element_located((By.ID, "address"))).get_attribute("value")
        except selenium.common.exceptions.TimeoutException:
            continue
        address = driver_ranStreetView.find_element(by=By.ID, value="address").text
        print(address)

        # Search on Google Maps
        try:
            wait_maps = WebDriverWait(driver_maps, 20).until(EC.visibility_of_element_located((By.NAME, "q"))).get_attribute("value")
        except selenium.common.exceptions.TimeoutException:
            continue
        searchbox = driver_maps.find_element(By.NAME, "q")
        searchbox.clear()
        searchbox.send_keys(address)
        searchbox.send_keys(Keys.RETURN)
        time.sleep(1)
        #element_present = EC.presence_of_element_located((By.ID, 'main'))			
        #wait = WebDriverWait(driver_maps, 20).until(element_present)                
        print(driver_maps.current_url)

        # Extract lat lon from url
        latlon = (driver_maps.current_url.split("@")[1]).split(",")
        lat = latlon[0]
        lon = latlon[1]

        # Save Screenshot
        photo_name = lat + "_" + lon + ".png"
        print(photo_name)
        try:
            wait = WebDriverWait(driver_ranStreetView, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[aria-label='Street View']"))).get_attribute("value")
        except selenium.common.exceptions.TimeoutException:
            continue
        
        # Remove unnecessary elements (full screen button, address)
        # Can add more elements to remove if needed
        driver_ranStreetView.execute_script("""
        var btn = document.getElementsByClassName("gm-control-active gm-fullscreen-control")[0];
        btn.parentNode.removeChild(btn);
        var addr = document.getElementById("address");
        addr.remove();
        """)

        canvas = driver_ranStreetView.find_element(By.CSS_SELECTOR, '[aria-label="Street View"]')
        canvas.screenshot(country + "/" + photo_name)
        screenshot = Image.open(country + "/" + photo_name)
        #screenshot.show()