import os
import requests

# Get all products from WooCommerce API
site_url = os.getenv('site_url')
consumer_key = os.getenv('consumer_key')
consumer_secret = os.getenv('consumer_secret')

def get_attributes():
    response = requests.get(f"{site_url}/wp-json/wc/v3/products/attributes", auth=(consumer_key, consumer_secret))
    if response.status_code == 200:
        attribute_list = response.json()
        return attribute_list
    else:
        print(f"Failed to get attributes, http code is {response.status_code}")
        return None

def post_attributes(payload):
    response = requests.post(f"{site_url}/wp-json/wc/v3/products/attributes", auth=(consumer_key, consumer_secret), json=payload)
    if response.status_code != 200:
        print("Failed to post attributes")

def get_terms(product_id, attribute_id):
    response = requests.get(f"{site_url}/wp-json/wc/v3/products/attributes/{attribute_id}/terms", auth=(consumer_key, consumer_secret))
    if response.status_code == 200:
        terms_list = response.json()
        return terms_list
    else:
        print(f"Failed to get terns, http code is {response.status_code}")
        return None

def get_products(page):
    params = {'page': page}
    response = requests.get(f"{site_url}/wp-json/wc/v3/products", auth=(consumer_key, consumer_secret), params=params)
    if response.status_code == 200:
        products = response.json()
        page += 1
        return products, page
    else:
        print(f"Failed to get product on {page}, http code is {response.status_code}")
        page += 1
        return None, page

def add_missing_attributes(market_attributes):
    product_new_attribute_count = 0
    new_attributes = []
    attribute_list = get_attributes()
    
    if attribute_list is not None:
        for attr in market_attributes:
            if attr not in attribute_list:
                new_attributes.append({
                    'name': f'{attr}',
                    'slug': f'pa_{attr}',
                    "order_by": "menu_order"
                })
                product_new_attribute_count += 1

        if product_new_attribute_count:
            for new_attribute in new_attributes:
                if not any(attr['name'] == new_attribute['name'] for attr in attribute_list):
                    print(f"No {new_attribute['name']} attribute found in existing attributes.")
                    print(f"Attempting to create attribute {new_attribute['name']}.")
                    post_attributes(new_attribute)
                    attribute_list.append(new_attribute)  # Add the new attribute to the list
    
    return attribute_list
