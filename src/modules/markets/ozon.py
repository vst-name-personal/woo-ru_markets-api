import os

from requests_ratelimiter import LimiterSession

from modules.logger import ozon_logger

def market_ozon(products):
    url = "https://api-seller.ozon.ru/v2/product/info"
    headers = {
        "Client-Id": os.getenv("Client-Id"),
        "Api-Key": os.getenv("Api-Key")
        }
    session = LimiterSession(per_minute=50)
    ozon_data = {}
    zero_sku = 0
    wrong_sku = []
    no_sku = []
    for product in products:
        if "sku" not in product:
            continue
        json_body = {
        "offer_id": product["sku"]
        }
        response = session.post(url, headers=headers, json=json_body)
        if response.status_code == 404:
            ozon_logger.error(f"404 - {product['sku']}")
            ozon_logger.error(f"Replacing SKU with , version {product['sku']} ")
            json_body["offer_id"] = json_body["offer_id"].replace(".", ",")
            response = session.post(url, headers=headers, json=json_body)
            if response.status_code == 200:
                ozon_logger.error(f"Fix SKU {product['sku']}")
                wrong_sku.append(product["sku"])
            if response.status_code != 200:
                ozon_logger.error(f"NO SKU ERROR FOR OZON: {product['sku']}")
                no_sku.append(product["sku"])
                ozon_data[product["id"]] = {"market_name": "ozon",
                        'sku': product["sku"],
                        'url': "None",
                        'stock': ozon_stock,
                        'price': ozon_price}
        if response.status_code == 200:
            ozon_logger.debug("ozon 200")
            ozon_response = response.json()
            ozon_sku = str(ozon_response["result"]["sku"])
            ozon_stock = str(ozon_response["result"]["stocks"]["present"])
            ozon_price = str(ozon_response["result"]["price"])
            ozon_url = None
            if ozon_sku != "0" and ozon_sku != "":
                ozon_url = "https://ozon.ru/products/" + str(ozon_sku) #+ "?utm_source=site&utm_medium=market_btns&utm_campaign=vendor_org_1001462"
            else:
                zero_sku += 1
                ozon_data[product["id"]] = {"market_name": "ozon",
                                            'sku': product["sku"],
                                            'url': "None",
                                            'stock': ozon_stock,
                                            'price': ozon_price}
            if ozon_sku and ozon_url and ozon_stock and ozon_price:
                ozon_logger.debug(f"returning ozon data for {product['sku']}")
                ozon_data[product["id"]] = {"market_name": "ozon",
                                            'sku': product["sku"],
                                            'url': ozon_url,
                                            'stock': ozon_stock,
                                            'price': ozon_price}
            else:
                ozon_logger.error(f"ozon data, missing: {product['sku']}, '{ozon_url}','{ozon_stock}','{ozon_price}'")
        else:
            ozon_logger.error(f"ozon api http error: {response.status_code}")
    ozon_logger.critical(f"Inactive products: {zero_sku}")
    ozon_logger.critical(f"wrong sku's #{len(wrong_sku)}: {' '.join(wrong_sku)}")
    ozon_logger.critical(f"404 sku's #{len(no_sku)}: {' '.join(no_sku)}")
    ozon_logger.debug(f"returning ozon data for {len(ozon_data)} products")
    return ozon_data