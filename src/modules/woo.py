import os
import requests

from modules.logger import logger

# Get all products from WooCommerce API
site_url = os.getenv('site_url')
service_url = os.getenv("service_url", "None")
if service_url:
    dummy_request = requests.get("https://google.com")
    default_headers = dummy_request.request.headers
    host_header = {"Host": site_url}
    service_headers = {**default_headers, **host_header}
else:
    host_header = None
consumer_key = os.getenv('consumer_key')
consumer_secret = os.getenv('consumer_secret')

def get_products_count():
    logger.debug(f"retrieving products count")
    if host_header:
        response = requests.get(f"{service_url}/wp-json/wc/v3/reports/products/totals", auth=(consumer_key, consumer_secret), headers=service_headers)
    else:
        response = requests.get(f"{site_url}/wp-json/wc/v3/reports/products/totals", auth=(consumer_key, consumer_secret))
    if response.status_code == 200:
        data = response.json()
        count = 0
        for info in data:
            count += int(info["total"])
        if count != 0:
            return count
        else:
            return
    else:
        logger.error(f"Retrieval products count failed...{response.status_code}")
        return

def get_products(page=None):
    if page:
        params = {"page": page}
        logger.debug(f"retrieving products on page {page}")
    else:
        params = {"per_page": "100"}
        logger.debug(f"retrieving all products")
    if host_header:
        logger.debug("Service host url is present")
        if page:
            response = requests.get(f"{service_url}/wp-json/wc/v3/products", auth=(consumer_key, consumer_secret), params=params, headers=service_headers)
        else:
            response = requests.get(f"{service_url}/wp-json/wc/v3/products", auth=(consumer_key, consumer_secret), headers=service_headers)
    else:
        if page:
            response = requests.get(f"{site_url}/wp-json/wc/v3/products", auth=(consumer_key, consumer_secret), params=params)
        else:
            response = requests.get(f"{site_url}/wp-json/wc/v3/products", auth=(consumer_key, consumer_secret))
    if response.status_code == 200:
        products = response.json()
        if page:
            return products, int(response.status_code), int(page)
        else:
            return products, int(response.status_code)
    else:
        print(f"Failed to get product on {page}, http code is {response.status_code}")
        page += 1
        return None, int(response.status_code), int(page)
    
def update_product(product):
    logger.debug(f"Updating product {product.get('id')}, with SKU: {product.get('sku')}")
    product_id = product['id']
    payload = {
        'name': product['name'],
        #'attributes': product.get('attributes', []),
        'status': product['status'],
        'price': product['price'],
        'manage_stock': product['manage_stock'],
        'stock_quantity': product['stock_quantity'],
        'status': product['status'],
        'meta_data': product['meta_data']
    }
    if service_url:
        response = requests.put(f"{service_url}/wp-json/wc/v3/products/{product_id}", auth=(consumer_key, consumer_secret), json=payload, headers=service_headers)
    else:
        response = requests.put(f"{site_url}/wp-json/wc/v3/products/{product_id}", auth=(consumer_key, consumer_secret), json=payload)
    if response.status_code == 200:
        product_updated = response.json()
        logger.debug(f"Product {product_id} with SKU {product['sku']} has been updated . Response: {response.status_code}")
        return product_updated
    else:
        print(f"Failed to update product {product_id} . Status code: {response.status_code}")
        return product

def batch_update_product(products):
    logger.info(f"Batch updating products...{len(products)}")
    payload_list = []
    if products:
        for product in products:
            payload_list.append({"update": [{
                        'name': product['name'],
                        #'attributes': product.get('attributes', []),
                        'status': product['status'],
                        'price': product['price'],
                        'manage_stock': product['manage_stock'],
                        'stock_quantity': product['stock_quantity'],
                        'meta_data': product['meta_data']
                        }]})
        if service_url:
            response = requests.put(f"{service_url}/wp-json/wc/v3/products/batch", auth=(consumer_key, consumer_secret), json=payload_list, headers=service_headers)
        else:
            response = requests.put(f"{site_url}/wp-json/wc/v3/products/batch", auth=(consumer_key, consumer_secret), json=payload_list)
        if response.status_code == 200:
            logger.info(f"Products  updated successfully.")
            return int(response.status_code)
        else:
            logger.error(f"Failed to update products. Status code: {response.status_code}")
            return int(response.status_code)