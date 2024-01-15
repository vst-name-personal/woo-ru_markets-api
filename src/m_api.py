import os
from dotenv import load_dotenv

import mysql.connector
import requests

from modules.woo import *

load_dotenv()
# MySQL connection
# conn = mysql.connector.connect(
#     host= os.getenv('db_host'),
#     user=os.getenv('db_user'),
#     password=os.getenv('db_password'),
#     database=os.getenv('wp_api')
# )

#woo
# Function to get all products and update attributes
# Get all products from WooCommerce API
products_url = os.getenv('woo_products')
consumer_key = os.getenv('consumer_key')
consumer_secret = os.getenv('consumer_secret')

# Function to get all products and update attributes
def update_product(page=1):
    while True:
        # Get products from WooCommerce API with pagination
        params = {'page': page}
        response = requests.get(products_url, auth=(consumer_key, consumer_secret), params=params)
        products = response.json()

        # Break the loop if there are no more pages
        if not products:
            break

        # Loop through each product
        for product in products:
            market_attributes = ["ozon_url", "wb_url", "ym_url", "mm_url", "vk_url"]
            market_urls = 0
            product_modified = 0

            # Check if the product has the specified attributes
            if 'attributes' in product:
                attributes = product['attributes']
                # Flag to check if any attributes were modified
                # List of attributes to check and update
                for attribute in attributes:
                    if attribute['name'] in market_attributes:
                        # Check if the attribute is set to 'visible'
                        if attribute['visible']:
                            # Update the attribute to 'visible: false'
                            attribute['visible'] = False
                            product_modified += 1
                        if 'options' in attribute and attribute['options'] and attribute['options'][0]:
                            market_urls += 1

            # Check if it's ready to publish
            if (
                market_urls > 0
                and product.get('sku') != ""
                and product.get('images') != ""
                and product.get('description') != ""
            ):
                if product['status'] != "publish":
                    product['status'] = 'publish'
                    product_modified += 1
            else:
                if product['status'] != "draft":
                    product['status'] = 'draft'
                    product_modified += 1

            # Update the product with modified attributes
            if product_modified > 0:
                product_id = product['id']
                update_url = f"{products_url}/{product_id}"
                update_payload = {'attributes': product.get('attributes', []), 'status': product['status']}
                update_response = requests.put(update_url, auth=(consumer_key, consumer_secret), json=update_payload)

                if update_response.status_code == 200:
                    print(f"Product {product_id}  updated successfully.")
                else:
                    print(f"Failed to update product {product_id} . Status code: {update_response.status_code}")

        # Move to the next page
        page += 1
        print(f"Getting page {page}")

# Call the function to update attributes with pagination
update_product()



