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
ozon_client = str(os.getenv('Client-Id'))
ozon_key = str(os.getenv('Api-Key'))
#WB
wb_token = str(os.getenv('wb_token'))

market_attributes = ("ozon_url", "ozon_stock", "ozon_enabled" "wb_url", "wb_stock", "wb_enabled", "ym_url", "ym_stock", "ym_enabled", "mm _url", "mm_stock", "mm_enabled")
markets_list = ("ozon", "wb", "ym", "mm", "vk")
attribute_list = add_missing_attributes(market_attributes)
cleanup_terms()
page = 1
def main(products, page=None):    
    while True:
        # Loop through each product
        products_modified = 0
        for product in products:
            market_urls = 0
            product_modified = 0
            sku = product.get("sku")
            if sku == "None":
                print(f"SKU for product {product.get('id')} is not set")
                break
            
            #Fetch required product info
            ozon, wb, ym, mm = {}, {}, {}, {}
            with ThreadPoolExecutor(max_workers=4) as executor:
                # Submit multiple functions concurrently for the current product
                future_ozon = executor.submit(ozon_request_product_info, sku, ozon_client, ozon_key)
                #future_wb = executor.submit(sku, ozon_client, ozon_key)
                #future_ym = executor.submit(sku, ozon_client, ozon_key)
                #future_mm = executor.submit(sku, ozon_client, ozon_key)
                try:
                    # Wait for the results
                    ozon = future_ozon.result()
                    #wb = future_wb.result()
                    #ym = future_ym.result()
                    #mm = future_mm.result()
                except Exception as e:
                    print(f"futures error = {e}")
            #ozon = ozon_request_product_info(sku, ozon_client, ozon_key)
            if ozon or wb or ym or mm:
                stock = 0
                if ozon:
                    stock += int(ozon["stock"])
                if wb:
                    stock += int(wb["stock"])                        
                if ym:
                    stock += int(ym["stock"])
                if mm:
                    stock += int(mm["stock"])
                                
                product["stock_quantity"] = stock
                price = 0
                num_price_sources  = 0
                if ozon:
                    price += float(ozon["price"])
                    num_price_sources += 1
                if wb:
                    price += float(wb["price"])
                    num_price_sources += 1
                if ym:
                    price += float(ym["price"])
                    num_price_sources += 1
                if mm:
                    price += float(mm["price"])
                    num_price_sources += 1
                if num_price_sources and price:
                    product["price"] = price / num_price_sources
                else:
                    product["price"] = 0
                product["manage_stock"] = "true"
                if product["stock_quantity"] != "0":
                    product["stock_status"] = "instock"
            
            # Attributes modification
            if 'attributes' in product:
                attributes = product['attributes']
            else:
                break
                    
            #Update attributes with imported values(if changed)
            product_updated = add_product_attributes(product, market_attributes)
            if product_updated:
                try:
                    product =  {**product, **product_updated}
                except Exception as e:
                    print(f"product update exception e: {e}")
            #Checking and updating market attribute terms
            if ozon or wb or ym or mm:
                if ozon:
                    for attribute in attributes:
                        if attribute["name"] in market_attributes:
                            print(f"updating terms for ozon at attribute {attribute['name']} on {product['id']}, with SKU: {product['sku']}")
                            product = update_terms(product, ozon, attribute, market_attributes)
                if wb:
                    for attribute in attributes:
                        if attribute["name"] in market_attributes:
                            print(f"updating terms for ozon at attribute {attribute['name']} on {product['id']}, with SKU: {product['sku']}")
                            product = update_terms(product, ozon, attribute, market_attributes)
                if ym:
                    for attribute in attributes:
                        if attribute["name"] in market_attributes:
                            print(f"updating terms for ozon at attribute {attribute['name']} on {product['id']}, with SKU: {product['sku']}")
                            product = update_terms(product, ozon, attribute, market_attributes)
                if mm:
                    for attribute in attributes:
                        if attribute["name"] in market_attributes:
                            print(f"updating terms for ozon at attribute {attribute['name']} on {product['id']}, with SKU: {product['sku']}")
                            product = update_terms(product, ozon, attribute, market_attributes)                        
                    
                #Checking and updating market attributes visibility
                for attribute in attributes:
                    if attribute['name'] in market_attributes: 
                        if "visible" in attribute and attribute['visible'] and attribute['visible'][0]:
                            attribute['visible'] = "false"
                            product_modified += 1
                        elif "visible" not in attribute:
                            attribute["visible"] = "false"
                            product_modified += 1
                        if 'options' in attribute and attribute['options'] and attribute['options'][0] and attribute['options'][0] != []:
                            market_urls += 1

            # Check if it's ready to publish
            if (
                market_urls > 0
                and product.get('sku') != ""
                and product.get('images') != ""
                and product.get('description') != ""
                and product.get('stock_quantity') != "" or product.get('stock_quantity') != "0"
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
                response = update_product(product)
            products_modified += 1
            
        # Move to the next page
        if page:
            page += 1
        if product_modified > 1:
            response = update_product(product)
        print(f"Getting page {page}")
            
if __name__ == "__main__":
    # Get products from WooCommerce API
    count = get_products_count()
    if count:
        if count > 100:
            products = None
            response_status_code = None
            woo_response = get_products(page)
            print(f"Fetching products...response is {response_status_code}")
            if products in woo_response: products = woo_response["products"]
            if response_status_code in woo_response: response_status_code = woo_response["response_status_code"]
            if page in woo_response: page = woo_response["page"]
        else:
            products = None
            response_status_code = None
            woo_response = get_products()
            print(f"Fetching products...response is {response_status_code}")
            if products in woo_response: products = woo_response["products"]
            if response_status_code in woo_response: response_status_code = woo_response["response_status_code"]
            if page in woo_response: page = woo_response["page"]
        if not products and response_status_code != 200:
            print(f"no more products, page: {page}")
            products, response_status_code, page = get_products(page)
            if products and response_status_code == 200:
                print(f"Fetching products failed - response is {response_status_code}")
                # Break the loop if there are no more pages
            if not products and response_status_code != 200:
                print(f"no more products, page: {page}")
                exit()
        print(f"Number of retrieved products in: {len(products)}")
        main(products, page)