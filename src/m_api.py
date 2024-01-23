import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor 

import requests

from modules.woo import *
from modules.markets.ozon import *
from modules.markets.wb import *
from modules.markets.ym import *

load_dotenv()

#Ozon
ozon_client = os.getenv('Client-Id')
ozon_key = os.getenv('Api-Key')
#WB
wb_token = os.getenv('wb_token')

page = 1

market_attributes = ("ozon_url", "ozon_stock", "wb_url", "wb_stock", "ym_url", "ym_stock", "mm_url", "mm_stock", "vk_url", "vk_stock")
markets_list = ("ozon", "wb", "ym", "mm", "vk")
attribute_list = add_missing_attributes(market_attributes)

while True:
    # Get products from WooCommerce API with pagination
    response, page = get_products(page)
    if response != None and response.status_code == 200:
        print(f"response is {response.status_code}")
        products = response.json()

        # Break the loop if there are no more pages
    if not products:
        print(f"no more products, page: {page}")
        break
    
    # Loop through each product
    for product in products:
        market_urls = 0
        product_modified = 0
        sku = product.get("sku")
        if sku == "None":
            print(f"SKU for prodcut {product.get('id')} is not set")
            break
        #Fetch required product info
        ozon, wb, ym, mm = (), (), (), ()
        with ThreadPoolExecutor() as executor:
            # Submit multiple functions concurrently for the current product
            future_ozon = executor.submit(ozon_request_product_info, sku, ozon_client, ozon_key)
            #future_wb = executor.submit(sku, ozon_client, ozon_key)
            #future_ym = executor.submit(sku, ozon_client, ozon_key)
            #future_mm = executor.submit(sku, ozon_client, ozon_key)

            # Wait for the results
            ozon = future_ozon.result()
            #wb = future_wb.result()
            #ym = future_ym.result()
            #mm = future_mm.result()
        
        
        product["price"] = sum(result[1] for result in (markets_list) if result)
        product["stock"] = sum(result[2] for result in (markets_list) if result)
        
        # Attributes modification
        if 'attributes' in product:
            attributes = product['attributes']
        else:
            break
                
        #Update attributes with imported values(if changed)
        for attribute in attributes:
            #Checking and updating market attribute terms
            if ozon or wb or ym or mm:
                if attribute['name'] == 'ozon_url':
                    if attribute.get('value') != ozon[0]:
                        
                        attr_terms = get_terms(product.get("id"))
                        attr_terms = attr_terms.json()
                        if ozon[0] in attr_terms:
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
            update_url = f"{site_url}/wp-json/wc/v3/products/{product_id}"
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


