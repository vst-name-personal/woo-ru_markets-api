import os
import requests

from modules.logger import logger, ozon_logger

def ozon_request_product_info(SKU):
    url = "https://api-seller.ozon.ru/v2/product/info"
    headers = {
    "Client-Id": os.getenv("Client-Id"),
    "Api-Key": os.getenv("Api-Key")
    }
    json_body = {
    "offer_id": SKU
    }

    response = requests.post(url, headers=headers, json=json_body)
    if response.status_code == 404:
        ozon_logger.error(f"404 - {SKU} ")
        json_body["offer_id"] = json_body["offer_id"].replace(".", ",")
        logger.error(f"making request for ozon info {SKU}")
        response = requests.post(url, headers=headers, json=json_body)
        if response.status_code != 200:
            ozon_logger.critical(f"CRITICAL ERROR FOR OZON: {SKU}")
            return
    if response.status_code == 200:
        logger.debug("ozon 200")
        data = response.json()
        ozon_sku = str(data["result"]["sku"])
        ozon_stock = str(data["result"]["stocks"]["present"])
        ozon_price = str(data["result"]["price"])
        ozon_url = "https://ozon.ru/products/" + str(ozon_sku) + "?utm_source=site&utm_medium=market_btns&utm_campaign=vendor_org_1001462"
        if ozon_url and ozon_stock and ozon_price:
            logger.debug(f"returning ozon data for {SKU}")
            data = {"market_name": "ozon",
                    'url': ozon_url,
                    'stock': ozon_stock,
                    'price': ozon_price}
            if ozon_sku == 0:
                data[2] = ""
            return data
    else:
        ozon_logger.error(f"ozon api http error: {response.status_code}")
        return