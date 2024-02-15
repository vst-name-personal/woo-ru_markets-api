import os
import time
from concurrent.futures import ThreadPoolExecutor 

from dotenv import load_dotenv
load_dotenv()


from modules.woo import get_products, update_product, batch_update_product
from modules.markets.ozon import market_ozon
from modules.markets.wb import market_wb
from modules.markets.ym import *

from modules.logger import logger

markets_list = ("ozon", "wb", "ym", "mm", "vk")
#cleanup_terms()

def main():
    # Get products from WooCommerce API
    page = 1
    products = []
    updated_products = []
    count = 0
    while True:
        response_status_code = None
        woo_response = get_products(page)
        if woo_response[0]:
            fetched_products = woo_response[0]
            products.extend(fetched_products)
            logger.info(f"Acquired {len(products)} products")
        if woo_response[1]:
            response_status_code = woo_response[1]
        if page in woo_response:
            page = woo_response[2]
        if response_status_code != 200:
            logger.warning(f"Products retrieval failed...{response_status_code}")
        if woo_response[0] == []:
            break
        else:
            page += 1
            
        
    if count != len(products) or count is None:
        count = len(products)

    #Fetch required product info
    # Initialize empty dictionaries
    ozon, wb, ym, mm = {}, {}, {}, {}

    # Create a list to store non-empty dictionaries
    marketplace_data_list = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(market_ozon, products), executor.submit(market_wb, products)]

        for future, marketplace_name in zip(futures, ["ozon", "wb"]):
            try:
                # Wait for the results
                marketplace_data = future.result()

                # Only add to the list if the data is not empty
                if marketplace_data:
                    marketplace_data_list.append({marketplace_name: marketplace_data})

            except Exception as e:
                logger.critical(f"Error in {marketplace_name: marketplace_name}: {e}")

    while count > 0:
        # Loop through each product
        for product in products:
            product_modified = 0
            market_urls = 0
            stock = 0
            price = 0
            for marketplace_data in marketplace_data_list:
                if marketplace_data:
                    market_name = list(marketplace_data.keys())[0]
                    market_data = marketplace_data.get(market_name, {})
                    if market_data and product["id"] in market_data:
                        if int(market_data[product["id"]]["stock"]):
                            stock += int(market_data[product["id"]]["stock"])
                            
                        if price > float(market_data[product["id"]]["price"]):
                            price = float(market_data[product["id"]]["price"])
                            
            if product["stock_quantity"] != stock:
                product["stock_quantity"] = stock
                product_modified += 1
                
            if product["stock_quantity"] != "0":
                product["stock_status"] = "instock"
            else:
                product["stock_status"] = "outofstock"
            
            if product["price"] != str(price):
                product["price"] = price
                product["regular_price"] = price
                product_modified += 1


                
            product_meta = product.get("meta_data")
            #Updating product meta_data for markets
            for marketplace_data in marketplace_data_list:
                if marketplace_data:
                    market_name = list(marketplace_data.keys())[0]
                    market_name_url = market_name + "_url"
                    market_data = marketplace_data.get(market_name, {})
                    logger.debug(f"updating meta for {market_name} on {product['id']}, with SKU: {product['sku']}")
                    found_bool = False
                    for item in product_meta:
                        if str(item["key"]) == market_name_url:
                            if int(market_data[product["id"]]["stock"]) > 0 and str(market_data[product["id"]]["url"]) not in ["None", "Unavailable"]:
                                market_urls += 1
                                if item["value"] != market_data[product["id"]]["url"]:
                                    item["value"] = market_data[product["id"]]["url"]
                                    product_modified += 1 
                            else:
                                item["value"] = "Unavailable"
                                product_modified += 1 
                            found_bool = True
                            
                    if found_bool == False:
                        #print(product["id"])
                        #print(ozon[product["id"]]["url"])
                        product_meta.append({
                                        "key": market_name_url,
                                        "value": market_data[product["id"]]["url"]
                                        })
                        logger.critical(f"adding new meta_data to product{product['id']}")
                        market_urls += 1
                        product_modified += 1 
                    
            # Check if it's ready to publish
            keys_to_check = {"ozon_url", "wb_url", "ym_url", "mm_url", "vk_url"}
            keys = [any(key in d["key"] for key in keys_to_check) for d in product_meta]
            product["manage_stock"] = "true"
            if (
                market_urls > 0
                and product['sku'] != ""
                #and product['images'] != []
                #and product['description'] != ""
                and product['stock_quantity'] not in ["", "0"]
                and int(product['stock_quantity']) > 0
                and any(keys)
            ):
                if product['status'] != "publish":
                    product['status'] = 'publish'
                    product_modified += 1
            else:
                if product['status'] != "draft":
                    product['status'] = 'draft'
                    product_modified += 1
            
            # Add changed product to a new list
            if product_modified:
                updated_products.append(product)
            if count != 0:
                count -= 1
                logger.debug(f"{count}...products remaining")
        
    retry = 3
    logger.info(f"Products to update: {len(updated_products)}")
    while len(updated_products) or retry:
        short_list_of_products = updated_products[:25]
        status_code = batch_update_product(short_list_of_products)
        
        if status_code == 200:
            updated_products = updated_products[25:]
        else:
            retry -= 1
            
        if retry == 0:
            break
        logger.info(f"Left to update: {len(updated_products)}")
    logger.info("Products processing finished")

            
            
if __name__ == "__main__":
        main()