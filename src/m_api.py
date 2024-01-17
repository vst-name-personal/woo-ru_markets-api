import os
from dotenv import load_dotenv

import requests

from modules.woo import *
from modules.markets.ozon import *
from modules.markets.wb import *
from modules.markets.ym import *

load_dotenv()

#woo
# Get all products from WooCommerce API
products_url = "***REMOVED***/wp-json/wc/v3/products"
attributes_url = "***REMOVED***/wp-json/wc/v3/products/attributes"
consumer_key = os.getenv('consumer_key')
consumer_secret = os.getenv('consumer_secret')
#Ozon
ozon_client = os.getenv('Client-Id')
ozon_key = os.getenv('Api-Key')
#WB
wb_token = os.getenv('wb_token')
#YM
# Function to get all products and update attributes


# Function to get all products and update attributes
def update_product(page=1):
    while True:
        # Get products from WooCommerce API with pagination
        params = {'page': page}
        response = requests.get(products_url, auth=(consumer_key, consumer_secret), params=params)
        if response.status_code == 200:
            print(f"response is {response.status_code}")
            products = response.json()

            # Break the loop if there are no more pages
            if not products:
                print(f"no more products, page: {page}")
                break

            # Loop through each product
            for product in products:
                market_attributes = ("ozon_url", "ozon_stock", "wb_url", "wb_stock", "ym_url", "ym_stock", "mm_url", "mm_stock", "vk_url", "vk_stock")
                new_attributes = []
                market_urls = 0
                product_modified = 0
                product_new_attribute = 0
                sku = product.get("sku")
                if sku == "None":
                    print(f"SKU for prodcut {product.get('id')} is not set")
                    break
                ozon = ozon_request_product_info(product.get("sku"), ozon_client, ozon_key)
                #wb = wb_request_product_info(product.get("sku"), wb_token)
                #ym = ym_request_product_info(product.get("sku"), ym_token)
                # Attributes modification
                #Grabbing attributes
                if 'attributes' in product:
                    attributes = product['attributes']
                    # List of attributes to check and update
                if ozon:
                    if not any(attr.get('name') == 'ozon_url' for attr in attributes):
                        new_attributes.append({
                            'name': 'ozon_url',
                            'slug': 'pa_ozon_url',
                            "order_by": "menu_order"
                        })
                        product_new_attribute += 1
                    if not any(attr.get('name') == 'ozon_stock' for attr in attributes):
                        new_attributes.append({
                            'name': 'ozon_stock',
                            'slug': 'pa_ozon_stock',
                            "order_by": "menu_order"
                        })
                        product_new_attribute += 1
                    if not any(attr.get('name') == 'ozon_price' for attr in attributes):
                        new_attributes.append({
                            'name': 'ozon_price',
                            'slug': 'pa_ozon_price',
                            "order_by": "menu_order"
                        })
                        product_new_attribute += 1
                        
                    if product_new_attribute:
                        print(f"fetching existing attributes")
                        attribute_list = requests.get(attributes_url, auth=(consumer_key, consumer_secret))
                        for new_attribute in new_attributes:
                            if attribute_list.status_code == 200:
                                existing_attributes = attribute_list.json()
                                if not any(attr['name'] == new_attribute['name'] for attr in existing_attributes):
                                    print(f"no {new_attribute['name']} attribute found in existing attributes")
                                    payload = new_attribute
                                    print(f"attemting to create attribute {new_attribute['name']}")
                                    update_response = requests.post(attributes_url, auth=(consumer_key, consumer_secret), json=payload)
                                    attribute_list = requests.get(attributes_url, auth=(consumer_key, consumer_secret))
                        
                #Update attributes with imported values(if changed)
                for attribute in attributes:
                    #Checking and updating market attribute terms
                    if ozon:
                        if attribute['name'] == 'ozon_url':
                            if attribute.get('value') != ozon[0]:
                                attribute['options'].append(ozon[0])
                                attribute['visible'] = False
                                product_modified += 1
                    #Checking and updating market attributes visibility
                    if attribute['name'] in market_attributes: 
                        if attribute['visible']:
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
                if product_modified:
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
        else:
            print(f"failed request {response.status_code}")
# Call the function to update attributes with pagination
update_product()



