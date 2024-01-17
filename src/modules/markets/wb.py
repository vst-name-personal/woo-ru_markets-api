# import requests

# def wb_request_product_info(SKU, wb_token):
#     url = "https://suppliers-api.wildberries.ru/content/v1/cards/filter"
#     headers = {
#     "Client-Id": ozon_client,
#     "Api-Key": ozon_key
#     }
#     json_body = {
#     "offer_id": SKU
#     }
#     response = requests.post(url, headers=headers, json=json_body)
#     if response.status_code != 200:
#         a = 1
#     else:
#         if response.status_code == 200:
#         data = response.json()
#         ozon_sku = data["object"]["data"]["0"]["sku"]
#         ozon_stock = data["object"]["data"]["0"]["present"]
#         ozon_price = data["object"]["data"]["0"]["price"]
#     ozon_url = "https://ozon.ru/products/" + str(ozon_sku) + "?utm_source=site&utm_medium=market_btns&utm_campaign=vendor_org_1001462"
#     return ozon_url, ozon_stock, ozon_price