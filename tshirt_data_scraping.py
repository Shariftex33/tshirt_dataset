import os
import time
import csv
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# Path to the chromedriver executable (update this with the correct path)
chromedriver_path = 'chromedriver.exe'  # Example path

# Set up the webdriver service and options
service = Service(chromedriver_path)
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode

# Specify the page range
start_page = 88  # Starting page
end_page = 101    # Ending page (you can modify as per your need)

# Specify the CSV file path
csv_file_path = 'product_data1.csv'

# Loop over the specified page range
for page_num in range(start_page, end_page + 1):
    print(f"Processing page {page_num}...")

    # Start a new Chrome session
    driver = webdriver.Chrome(service=service, options=options)

    # URL to scrape (with page number)
    url = f'https://www.daraz.com.bd/catalog/?_keyori=ss&clickTrackInfo=textId--304874222729381822__abId--None__pvid--16e4ab33-2895-4710-9ce5-2696f097691f__matchType--1__abGroup--None__srcQuery--t%20shirt__spellQuery--t%20shirt__ntType--nt-common&from=suggest_normal&page={page_num}&q=t%20shirt&spm=a2a0e.searchlist.search.2.69fb3441lp39W2&sugg=t%20shirt_0_1'

    # Open the webpage
    driver.get(url)

    # Wait for the page to fully load
    time.sleep(5)  # Adjust this depending on how fast the page loads

    # Extract the full <body> content
    body_content = driver.find_element(By.TAG_NAME, 'body').get_attribute('outerHTML')

    # Save the <body> content to a file (overwrite each time)
    html_file_path = 'daraz_body_full.html'
    with open(html_file_path, 'w', encoding='utf-8') as file:
        file.write(body_content)

    # Close the browser session
    driver.quit()

    print(f"Page {page_num} HTML saved successfully!")

    # --- Second part: Processing the saved HTML ---

    # Load the HTML file
    with open(html_file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Find all product items
    products = soup.find_all('div', class_='Bm3ON')

    # List to store product details
    product_details = []

    # Loop through each product item and extract information
    for product in products:
        product_name = product.find('div', class_='RfADt').a['title'] if product.find('div', class_='RfADt') else 'N/A'
        price = product.find('span', class_='ooOxS').text if product.find('span', class_='ooOxS') else 'N/A'
        discount = product.find('span', class_='IcOsH').text if product.find('span', class_='IcOsH') else 'N/A'
        sold_count = product.find('span', class_='_1cEkb').text if product.find('span', class_='_1cEkb') else 'N/A'
        rating = product.find('span', class_='qzqFw').text if product.find('span', class_='qzqFw') else 'N/A'
        location = product.find('span', class_='oa6ri')['title'] if product.find('span', class_='oa6ri') else 'N/A'
        product_link = product.find('a')['href'] if product.find('a') else 'N/A'
        product_id = product['data-item-id'] if 'data-item-id' in product.attrs else 'N/A'
        sku = product['data-sku-simple'] if 'data-sku-simple' in product.attrs else 'N/A'

        # Append the extracted information to the list
        product_details.append({
            'Product Name': product_name,
            'Price': price,
            'Discount': discount,
            'Sold Count': sold_count,
            'Rating': rating,
            'Location': location,
            'Product Link': product_link,
            'Product ID': product_id,
            'SKU': sku,
        })

    # Check if there are any product details to write
    if product_details:
        # Check if the CSV file exists to determine if headers are needed
        file_exists = os.path.isfile(csv_file_path)

        # Write the data to the CSV file
        with open(csv_file_path, mode='a', newline='', encoding='utf-8') as csv_file:
            fieldnames = product_details[0].keys()  # Get the field names from the first product
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            # Write the header only if the file does not exist
            if not file_exists:
                writer.writeheader()

            # Write the product data
            for product in product_details:
                writer.writerow(product)

        print(f"Data from page {page_num} saved to CSV file successfully!\n")
    else:
        print(f"No products found on page {page_num}.")
