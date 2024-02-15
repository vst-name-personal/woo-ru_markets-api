import os

from requests_ratelimiter import LimiterSession
import json
from modules.logger import wb_logger

def market_wb(products):
    url_products = "https://suppliers-api.wildberries.ru/content/v2/get/cards/list"
    url_prices = "https://suppliers-api.wildberries.ru/public/api/v1/info?quantity=0"
    url_warehouses = "https://suppliers-api.wildberries.ru/api/v3/warehouses"
    url_stocks = "https://suppliers-api.wildberries.ru/api/v3/stocks"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {os.getenv('wb_token')}",
        "Content-Type": "application/json",
    }
    session = LimiterSession(per_minute=50)
    wrong_sku = []
    no_sku = []
    
    json_body_products = {
        "settings": {
            "cursor": {
            "limit": 1000
            },
            "filter": {
                "withPhoto": -1
            }
        }
    }
    
    response_products = session.post(url_products, headers=headers, json=json_body_products) #product data
    if response_products.status_code == 200:
        wb_logger.debug("wb products 200")
        wb_products = response_products.json()
        wb_logger.debug(f"wb prices #: {len(wb_products['cards'])}")
    else:
        return
        
    response_prices = session.get(url_prices, headers=headers) #product prices
    if response_prices.status_code == 200:
        wb_logger.debug("wb prices 200")
        wb_prices = response_prices.json()
        wb_logger.debug(f"wb prices #: {len(wb_prices)}")
    else:
        return
    
    barcodes = []
    products_data = {}
    for product in products:
        product_found = False
        for wb_product in wb_products["cards"]:
            if wb_product["vendorCode"] == product["sku"] or wb_product["vendorCode"].replace('.', ',') == product["sku"]:
                product_found = True
                if "," in wb_product["vendorCode"]:
                    wb_logger.error(f"Fix SKU {product['sku']}")
                    wrong_sku.append(product["sku"].replace('.', ','))
                products_data[int(product["id"])] = ({
                    "market_name": "wb",
                    'sku': product["sku"],
                    'url': f"https://www.wildberries.ru/catalog/{wb_product['nmID']}/detail.aspx",
                    'stock': int(0),
                    'price': float(0),
                    'nmID': str(wb_product["nmID"]),
                })
                for price in wb_prices:
                    if wb_product["nmID"] == price["nmId"]:
                        if price["price"] != 0:
                            products_data[int(product["id"])]["price"] = round(float(price["price"]) - (float(price["discount"]) / 100 * float(price["price"])))
                
                if "sizes" in wb_product and wb_product["sizes"]:
                    for size_entry in wb_product["sizes"]:
                        skus = size_entry.get("skus", [])
                        barcodes.extend(skus)
                    products_data[int(product["id"])]["barcodes"] = skus
            
        if product_found == False:
            wb_logger.error(f"NO SKU ERROR FOR WB: {product['sku']}")
            no_sku.append(product["sku"])
            products_data[product["id"]] = {
                "market_name": "wb",
                'sku': product["sku"],
                'url': "None",
                'stock': int(0),
                'price': float(0),
                'nmID': None,
                'barcodes': {0, 0}
            }

    response_warehouses = session.get(url_warehouses, headers=headers) #warehouse list
    warehouses_ids = []
    json_stocks_sku = {}
    json_stocks_sku["skus"] = barcodes
    if response_warehouses.status_code == 200:
        warehouses = response_warehouses.json()
        wb_logger.debug(f"wb get.warehouses 200, # {len(warehouses)}")
        for warehouse in warehouses:
            warehouses_ids.append(warehouse["id"])
    for warehouse in warehouses_ids:
        response_stocks = session.post(f"{url_stocks}/{warehouse}", headers=headers, json=json_stocks_sku) #product stocks
        if response_stocks.status_code == 200:
            products_stocks = response_stocks.json()["stocks"]
            wb_logger.debug(f"wb get.stocks 200, # {len(products_stocks)}")
        else:
            wb_logger.critical(response_stocks.reason)
    
    active = 0
    for product_data_key, product_data_items in products_data.items():
        for stock in products_stocks:
            if stock["sku"] in product_data_items["barcodes"]:
                product_data_items["stock"] += stock["amount"]
                
        if product_data_items["stock"] == 0 and product_data_items["url"] != None:
            product_data_items["url"] = "Unavailable"
        
        if product_data_items["url"].startswith("https") == True:
            active += 1 
        if "nmID" in product_data_items:
            product_data_items.pop("nmID")
        if "barcodes" in product_data_items:
            product_data_items.pop("barcodes")
            
    wb_logger.critical(f"Unavailable for products: {len(products) - active}")
    wb_logger.critical(f"Active products # {active}")
    wb_logger.critical(f"wrong sku's #{len(wrong_sku)}: {' '.join(wrong_sku)}")
    wb_logger.critical(f"404 sku's #{len(no_sku)}: {' '.join(no_sku)}")
    wb_logger.debug(f"returning wb data for {len(products_data)} products")
    return products_data