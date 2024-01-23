import requests

def ozon_request_product_info(SKU, ozon_client, ozon_key):
    url = "https://api-seller.ozon.ru/v2/product/info"
    headers = {
    "Client-Id": ozon_client,
    "Api-Key": ozon_key
    }
    json_body = {
    "offer_id": SKU
    }

    response = requests.post(url, headers=headers, json=json_body)
    if response.status_code == 404:
        print(f"replacing substring in {SKU}")
        json_body["offer_id"] = json_body["offer_id"].replace(".", ",")
        print(f"making request for ozon info {SKU}")
        response = requests.post(url, headers=headers, json=json_body)
    if response.status_code == 200:
        print("ozon 200")
        data = response.json()
        ozon_sku = str(data["result"]["sku"])
        ozon_stock = str(data["result"]["stocks"]["present"])
        ozon_price = str(data["result"]["price"])
        ozon_url = "https://ozon.ru/products/" + str(ozon_sku) + "?utm_source=site&utm_medium=market_btns&utm_campaign=vendor_org_1001462"
        if ozon_url and ozon_stock and ozon_price:
            print(f"returning ozon data for {SKU}")
            data = {"market_name": "ozon",
                    'url': ozon_url,
                    'stock': ozon_stock,
                    'price': ozon_price}
            return data
    else:
        print(f"ozon api http error: {response.status_code}")
        return

# ozon = ozon_request_product_info("Деткм/0.5л", "1410340", "d1878175-748e-45cd-a474-060631516513")
# print(ozon)