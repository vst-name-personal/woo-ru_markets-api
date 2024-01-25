import os

from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor 

from modules.woo import get_products_count, get_products, update_product, batch_update_product
from modules.markets.ozon import ozon_request_product_info
from modules.markets.wb import *
from modules.markets.ym import *

from modules.logger import logger

#WB
wb_token = str(os.getenv('wb_token'))

markets_list = ("ozon", "wb", "ym", "mm", "vk")
#cleanup_terms()

def main():
    # Get products from WooCommerce API
    count = get_products_count()
    page = 1
    if count:
        if count > 100:
            products = None
            response_status_code = None
            woo_response = get_products(page)
            if woo_response[0]:
                products = woo_response[0]
            if woo_response[1]:
                response_status_code = woo_response[1]
            if page in woo_response:
                page = woo_response["page"]
            if response_status_code != 200:
                logger.warning(f"Products retrieval failed...{response_status_code}")
        else:
            products = None
            response_status_code = None
            woo_response = get_products()
            if woo_response[0]:
                products = woo_response[0]
            if woo_response[1]:
                response_status_code = woo_response[1]
            if page in woo_response:
                page = woo_response["page"]
            if response_status_code != 200:
                logger.ERROR(f"Products retrieval failed...{response_status_code}")
        logger.info(f"Number of retrieved products: {len(products)}")
    
    list_of_products = []
    if count == None:
        count = len(products)
    while count > 0:
        # Loop through each product
        products_modified = 0
        for product in products:
            market_urls = 0
            product_modified = 0
            sku = product.get("sku")
            if sku == "None":
                logger.error(f"SKU for product {product.get('id')} is not set")
                break
            
            #Fetch required product info
            ozon, wb, ym, mm = {}, {}, {}, {}
            with ThreadPoolExecutor(max_workers=4) as executor:
                # Submit multiple functions concurrently for the current product
                future_ozon = executor.submit(ozon_request_product_info, sku)
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
                    logger.error(f"futures error = {e}")
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
                if num_price_sources and price != 0:
                    product["price"] = price / num_price_sources
                else:
                    product["price"] = 0
                product["manage_stock"] = "true"
                if product["stock_quantity"] != "0":
                    product["stock_status"] = "instock"
            
            #Updating product meta_data for markets            
            if ozon or wb or ym or mm:
                product_meta = product["meta_data"]
                if ozon:
                    logger.info(f"updating meta for ozon on {product['id']}, with SKU: {product['sku']}")
                    #ozon["url"] not in (item.get("url") for item in product_meta):
                    for item in product_meta:
                        if item["key"] == "ozon_url":
                            if int(ozon["stock"]) > 0:
                                if item["value"] != ozon["url"]:
                                    item["value"] = ozon["url"]
                                    market_urls += 1
                            else:
                                item["value"] = ozon["url"] #"Unavailable"
                            found_bool = True
                        else:
                            found_bool = False
                    if found_bool == False:
                        new_item = {"key": "ozon_url",
                                "value": ozon["url"]}
                        product_meta.append(new_item)
                        market_urls += 1
                    product_modified += 1                  
                    
            # Check if it's ready to publish
            if (
                market_urls > 0
                and product.get('sku') != ""
                and product.get('images') != ""
                and product.get('description') != ""
                and product.get('stock_quantity') not in ["", "0"]
                and market_urls != 0
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
                list_of_products.append(product)
            if count != 0:
                count -= 1
                logger.debug(f"{count}...products remaining")
            else:
                break
        
        # Move to the next page
        if page != 1:
            page += 1
            products, response_status_code, page = get_products(page)
            if response_status_code != 200:
                break
            logger.debug(f"Getting page {page}")
    retry = 0
    while len(list_of_products) != 0 and retry != 0:
        if len(list_of_products) < 100:
            status_code = batch_update_product(list_of_products)
            if status_code == 200:
                short_list_of_products = list_of_products[:]
                list_of_products = short_list_of_products
            else:
                retry = 3
                retry -= 1
        else:
            short_list_of_products = list_of_products[:10]
            list_of_products = short_list_of_products
            batch_update_product(short_list_of_products)
    logger.info("Products processing finished")
            
            
if __name__ == "__main__":
        main()