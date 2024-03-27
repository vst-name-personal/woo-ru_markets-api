import os
import requests

from modules.logger import logger

# Get all products from WooCommerce API
site_url = os.getenv('site_url')
service_url = os.getenv("service_url")
if service_url is not None:
    dummy_request = requests.get("https://google.com")
    default_headers = dummy_request.request.headers
    host_header = {"Host": site_url}
    service_headers = {**default_headers, **host_header}
else:
    host_header = None
consumer_key = os.getenv('consumer_key')
consumer_secret = os.getenv('consumer_secret')

def get_products(page):
    if page:
        params = {"page": page}
        logger.debug(f"retrieving products on page {page}")
    else:
        return None
    logger.debug(f"Fetching page {page}")
    if host_header:
        logger.debug("Service host url is present")
        response = requests.get(f"{service_url}/wp-json/wc/v3/products", auth=(consumer_key, consumer_secret), params=params, headers=service_headers)
    else:
        response = requests.get(f"{site_url}/wp-json/wc/v3/products", auth=(consumer_key, consumer_secret), params=params)
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
    b = {}
    if products:
        # Prepare updates for each product
        for product in products:
            meta_data_dict = product["meta_data"]
            payload_list.append({
                "id": product['id'],
                'status': product['status'],
                'price': str(product['price']),
                'regular_price': str(product['regular_price']),
                'manage_stock': product['manage_stock'],
                'stock_quantity': product['stock_quantity'],
                "meta_data": product["meta_data"]
            })

        # Send a single request with all updates
        update_payload = {"update": payload_list}
        if service_url:
            response = requests.post(f"{service_url}/wp-json/wc/v3/products/batch", auth=(consumer_key, consumer_secret), json=update_payload, headers=service_headers)
        else:
            response = requests.post(f"{site_url}/wp-json/wc/v3/products/batch", auth=(consumer_key, consumer_secret), json=update_payload)
        if response.status_code == 200:
            logger.info(f"Products  updated successfully.")
            return int(response.status_code)
        else:
            logger.error(f"Failed to update products. Status code: {response.status_code}")
            return int(response.status_code)