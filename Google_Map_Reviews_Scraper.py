#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import re
import csv
import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup
import time
import re
from bs4 import BeautifulSoup


# In[8]:


pub_list = pd.read_csv('Greater Manchester JDW Pubs.csv')
pub_list


# In[9]:


def save_reviews_to_csv(all_reviews, filename):
    fieldnames = [
        "Reviewer Name",
        "Review Date",
        "Star Rating",
        "Review Text",
        "Total Reviews by Reviewer",
        "Total Photos by Reviewer",  
        "Is Local Guide",
        "Number of Images",
        "Image URLs",
        "Price per Person",
        "Food Rating", 
        "Service Rating",
        "Atmosphere Rating",
        "Recommended Dishes"    ]
    
       
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for review in all_reviews:
            writer.writerow(review)



def save_html_content(driver, base_path, pub_name, sorting_option):
    html_content = driver.page_source
    filename = os.path.join(base_path, pub_name, "html", f"{pub_name}_{sorting_option}.html")
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(html_content)


# In[10]:


def process_and_save_reviews(pub_list):
    base_path = r"C:\Users\User\Desktop\projects\MLDM COURSEWORK\TASK 3"
    
    for index, row in pub_list.iterrows():
        pub_name = row['Pub Name']
        pub_name = row['Pub Name'].strip().replace(' ', '_')

        url = row['Google Map Address']
        
        # Create main folder and subfolders for the pub
        main_folder = os.path.join(base_path, pub_name)
        html_folder = os.path.join(main_folder, 'html')
        category_folder = os.path.join(main_folder, 'category')
        
        os.makedirs(main_folder, exist_ok=True)
        os.makedirs(html_folder, exist_ok=True)
        os.makedirs(category_folder, exist_ok=True)
        
        all_dataframes = []  # to collect dataframes for merging
        
        for sorting_option in ['relevant','newest','highest rating','lowest rating']:# 
            all_reviews, driver = scrape_reviews_for_pub(pub_name, url, sorting_option)
            
            # Save the current page's HTML content
            save_html_content(driver, base_path, pub_name, sorting_option)
            
            # Save the scraped reviews to a CSV file
            csv_file = os.path.join(category_folder, f"{pub_name}_{sorting_option}.csv")
            save_reviews_to_csv(all_reviews, csv_file)
            
            #  get all image URLs and download images:  
            image_urls = [review['Image URLs'] for review in all_reviews if review['Image URLs']]
            # Flatten the list of image URLs since each entry may contain multiple URLs separated by commas
            image_urls = [url for sublist in image_urls for url in sublist.split(',')]
            # Calling the function to download images
            download_images(image_urls, category_folder)
            
            driver.close()
            
            # Load the saved CSV into a dataframe for later merging
            df = pd.read_csv(csv_file)
            all_dataframes.append(df)
            
        # Merge all the dataframes
        merged_df = pd.concat(all_dataframes, ignore_index=True)
        
        # Deduplicate
        merged_df.drop_duplicates(inplace=True)
        
        # Save the merged dataset
        merged_df.to_csv(os.path.join(main_folder, f"{pub_name}_merged.csv"), index=False)


# In[11]:


import requests
import os
import imghdr

def download_images(image_urls, save_folder):
    for i, url in enumerate(image_urls):
        response = requests.get(url)
        if response.status_code == 200:
            # Determine the final path with the correct extension
            temp_path = os.path.join(save_folder, f"temp_image_{i}")
            with open(temp_path, 'wb') as file:
                file.write(response.content)
            
            # Detect the image extension
            image_type = imghdr.what(temp_path)
            if image_type:
                # Prepare the final path with the correct extension
                final_path = os.path.join(save_folder, f"image_{i}.{image_type}")
                # Check if a file with the same name already exists
                if os.path.exists(final_path):
                 #   print(f"File {final_path} already exists. Skipping download.")
                    # Remove the temp file as we are skipping this image
                    os.remove(temp_path)
                    continue  # Skip to the next image
                # Rename the temporary file with the correct extension
                os.rename(temp_path, final_path)
            else:
                print(f"Could not identify image type for URL: {url}")
                # Remove the temp file if it's not a valid image
                os.remove(temp_path)


# In[12]:


def scrape_reviews_for_pub(pub_name, url, sorting_option='relevant'):
    # Set up the Selenium WebDriver
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)

    # Load the review page
    driver.get(url)

    accept_button = driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button/span')
    accept_button.click()


    # Wait for up to 10 seconds before throwing a timeout exception
    wait = WebDriverWait(driver, 10)

    element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[2]/div[2]/div[2]')))
    element.click()                                                 


    # XPath for the 'Sort' button
    sort_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[8]/div[2]/button/span/span'

    # Locate the 'Sort' button and click on it
    sort_button = driver.find_element(By.XPATH, sort_xpath)
    sort_button.click()

    # Wait for the dropdown to appear
    first_option_xpath = '//*[@id="action-menu"]/div[1]'
    wait.until(EC.presence_of_element_located((By.XPATH, first_option_xpath)))

    # Logic to choose the sorting option based on the argument
    sort_xpath_dict = {
        'relevant': '//*[@id="action-menu"]/div[1]',
        'newest': '//*[@id="action-menu"]/div[2]',
        'highest rating': '//*[@id="action-menu"]/div[3]',
        'lowest rating': '//*[@id="action-menu"]/div[4]'
    }
    
    sorting_element = driver.find_element(By.XPATH, sort_xpath_dict[sorting_option])
    sorting_element.click()

    
    # Find scroll layout
    scrollable_div = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]')

    # Scroll 110 times to load all permissible 1090 reviews
    for i in range(130):
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
        time.sleep(4)
        
        # Click all 'More' buttons to reveal full review texts
        more_buttons = driver.find_elements(By.XPATH, "//button[contains(., 'More')]")
        for button in more_buttons:
            if button.text == "More": #Check if the button text is exactly "More"
                try:
                    driver.execute_script("arguments[0].click();", button)
                    # Add a short sleep to allow the content to load
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Could not click 'More' button: {e}")
                
                
                
    # Extracting the reviews
    reviews = driver.find_elements(By.CSS_SELECTOR, ".jftiEf.fontBodyMedium")
    all_reviews = []
   
    
    
    for review in reviews:
        
         # Extract the HTML content of the review
        review_html = review.get_attribute('outerHTML')
        # Create a BeautifulSoup object for the individual review
        soup = BeautifulSoup(review_html, 'html.parser')
        
        
        
        
        # Extracting star rating
        star_elements = review.find_elements(By.CSS_SELECTOR, ".kvMYJc img.vzX5Ic")
        rating = len(star_elements)

        # Extracting review date
        try:
            date = review.find_element(By.CSS_SELECTOR, ".rsqaWe").text
        except NoSuchElementException:
            date = "Unknown date"

        # Extracting review text
        try:
            review_text_elem = review.find_element(By.CSS_SELECTOR, ".wiI7pd")
            review_text = review_text_elem.text
        except NoSuchElementException:
            review_text = "No review text"

        # Extracting reviewer name
        reviewer_name = review.find_element(By.CSS_SELECTOR, ".d4r55").text

       
                # Extract total reviews by reviewer and photos count
        total_reviews_elem = review.find_elements(By.CSS_SELECTOR, "div.RfnDt")
        total_reviews_text = total_reviews_elem[0].text if total_reviews_elem else ''
        
        # Extract review count
        review_count_match = re.search(r'([\d,]+)\s+reviews?', total_reviews_text)
        review_count = review_count_match.group(1).replace(',', '') if review_count_match else 'No reviews count'

        # Extract photo count
        photo_count_match = re.search(r'([\d,]+)\s+photos?', total_reviews_text)
        photo_count = photo_count_match.group(1).replace(',', '') if photo_count_match else 'No photos count'


        
        
        # Extracting if reviewer is a Local Guide
 
        is_local_guide = 'Local Guide' in total_reviews_text

        
        # Extracting image URLs
        img_buttons = review.find_elements(By.CSS_SELECTOR, ".Tya61d")
        img_urls = []
        for btn in img_buttons:
            style = btn.get_attribute("style")
            match = re.search(r'background-image: url\("(.*?)"\)', style)
            if match:
                img_urls.append(match.group(1))

        # Extracting number of images
        num_images = len(img_buttons)
        
        
        # Initialize placeholders for the new details
        price_per_person = "Not found"
        recommended_dishes = "Not found"
        
                   
        # Assuming the structure is similar for price, ratings, and recommended dishes within each review
        price_per_person_container = soup.find('span', string="Price per person")
        price_per_person = "Not found"
        if price_per_person_container:
            price_per_person_value = price_per_person_container.find_next('span', attrs={"aria-label": True})
            price_per_person = price_per_person_value.get_text(strip=True) if price_per_person_value else "Not found"

       # Scrape ratings
        ratings = {}
        rating_categories = soup.find_all("div", class_="PBK6be")
        for category in rating_categories:
            # The text in the category contains both the name and the value, e.g., "Service: 5"
            category_text = category.get_text(strip=True)
            if ':' in category_text:
                rating_type, rating_value = category_text.split(':', 1)
                ratings[rating_type.strip()] = rating_value.strip()
                
            # Extract the individual ratings
        food_rating = ratings.get('Food', 'Not rated')  # Use 'Not rated' or any other default value you prefer
        service_rating = ratings.get('Service', 'Not rated')
        atmosphere_rating = ratings.get('Atmosphere', 'Not rated')

       # Scrape "Recommended dishes"
        recommended_dishes_container = soup.find('span', string=lambda text: text and "Recommended dishes" in text)
        # Initialize as not found
        recommended_dishes = "Not found"

        # If the label is found, find the associated dishes in the next 'div'
        if recommended_dishes_container:
            # Assuming there might be multiple 'span' elements for multiple dishes
            dishes_spans = recommended_dishes_container.find_next('div').find_all('span')
            unique_dishes = set(dish.get_text(strip=True) for dish in dishes_spans if dish.get_text(strip=True))
            # Converting back to a sorted list and joining with commas
            recommended_dishes = ', '.join(sorted(unique_dishes))


            

        review_details = {
            "Reviewer Name": reviewer_name,
            "Review Date": date,
            "Star Rating": rating,
            "Review Text": review_text,
            "Total Reviews by Reviewer": review_count,
            "Total Photos by Reviewer": photo_count,  # Add this line
            "Number of Images": num_images,
            "Image URLs": ','.join(img_urls),
            "Is Local Guide": is_local_guide,
            "Price per Person": price_per_person,
            "Food Rating": food_rating,
            "Service Rating": service_rating,
            "Atmosphere Rating": atmosphere_rating,
            "Recommended Dishes": recommended_dishes
        }


        all_reviews.append(review_details)
    
   # driver.close()
    return all_reviews, driver


# In[ ]:


process_and_save_reviews(pub_list)

