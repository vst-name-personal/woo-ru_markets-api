import os
import requests

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

def get_all_attributes():
    print("retrieving global list of attributes")
    if host_header:
        print("host header true")
        response = requests.get(f"{service_url}/wp-json/wc/v3/products/attributes", auth=(consumer_key, consumer_secret), headers=service_headers)
    else:
        print("host header false")
        response = requests.get(f"{site_url}/wp-json/wc/v3/products/attributes", auth=(consumer_key, consumer_secret))
    if response.status_code == 200:
        attribute_list = response.json()
        return attribute_list
    else:
        print(f"Failed to get attributes, http code is {response.status_code}")
        return None
    
def add_product_attributes(product, market_attributes):
    print(f"Adding missing attributes from global to product {product.get('id')}, with SKU: {product.get('sku')}")
    new_attributes = []
    attribute_list = get_all_attributes()  # Assuming this function retrieves attribute list
    if attribute_list:
        product_attributes = product["attributes"]
        product_attributes_map = {attr["name"] for attr in product_attributes}  # Convert attribute names to a set
        for attr in market_attributes:
            # Check if the attribute doesn't exist in product_attributes and retrieve its definitions
            if attr not in product_attributes_map:
                attr_definitions = next((attr_item for attr_item in attribute_list if attr_item["name"] == attr), None)
                if attr_definitions:
                        new_attributes.append({
                        'id': f'{attr_definitions["id"]}',
                        'name': f'{attr_definitions["name"]}',
                        'slug': f'{attr_definitions["slug"]}',
                        'variation': 'false',
                        'order_by': 'menu_order',
                        'options': []
                        })

    if new_attributes:
        product_attributes.extend(new_attributes)
    return product
            
def post_attributes(payload):
    print("posting new attributes to global")
    if host_header:
        response = requests.post(f"{service_url}/wp-json/wc/v3/products/attributes", auth=(consumer_key, consumer_secret), json=payload, headers=service_headers)
    else:
        response = requests.post(f"{site_url}/wp-json/wc/v3/products/attributes", auth=(consumer_key, consumer_secret), json=payload)
    if response and response.status_code != 200:
        print(f"Failed to post attributes {response.status_code}")
        return
    return response

def get_terms(**kwargs):
    product_id = 0
    if "attribute_id" in kwargs:
        attribute_id = kwargs["attribute_id"]
    else:
        return
    if "product_in" in kwargs:
        product_id = kwargs["product_id"]
    print(f"retrieving terms for attribute id: {attribute_id}")
    if product_id:
        payload={"product": product_id}
        if host_header:
            response = requests.get(f"{service_url}/wp-json/wc/v3/products/attributes/{attribute_id}/terms", auth=(consumer_key, consumer_secret), headers=service_headers)
        else:
            response = requests.get(f"{site_url}/wp-json/wc/v3/products/attributes/{attribute_id}/terms", auth=(consumer_key, consumer_secret), json=payload)
    else:
        if host_header:
            response = requests.get(f"{service_url}/wp-json/wc/v3/products/attributes/{attribute_id}/terms", auth=(consumer_key, consumer_secret), headers=service_headers)
        else:
            response = requests.get(f"{site_url}/wp-json/wc/v3/products/attributes/{attribute_id}/terms", auth=(consumer_key, consumer_secret))
    if response.status_code == 200:
        terms_list = response.json()
        return terms_list
    else:
        print(f"Failed to get terns, http code is {response.status_code}")
        return None

def update_terms(product, market, attribute, market_attributes):
    print(f"updating terms for product {product.get('id')}, with SKU: {product.get('sku')} ")
    market_name = market["market_name"]
    market_url = market["url"]
    market_stock = market["stock"]
    market_price = market["price"]
    url_set = False    
    if attribute:
        if attribute["name"] in market_attributes:
            attribute_terms = get_terms(product_id=product["id"], attribute_id=attribute["id"])
            if url_set == False:
                if attribute['name'] == market_name + "_url":
                    if len(attribute_terms) > 1:
                        for term in attribute_terms:
                            if term["count"] == 0:
                                delete_term(attribute["id"], term["id"])
                    if len(attribute_terms) == 1:
                        if attribute_terms[0]["name"] != market_url:
                            attribute_terms[0]["name"] = market_url
                            attribute_terms[0]["slug"] = str(product["id"]) + "_" + market_name + "_url"
                            if attribute_terms[0]["id"]:
                                term_id = str(attribute_terms[0]["id"])
                                if host_header:
                                    response = requests.put(f"{service_url}/wp-json/wc/v3/products/attributes/{attribute['id']}/terms/{term_id}", auth=(consumer_key, consumer_secret), json=attribute_terms[0], headers=service_headers)
                                else:
                                    response = requests.put(f"{site_url}/wp-json/wc/v3/products/attributes/{attribute['id']}/terms/{term_id}", auth=(consumer_key, consumer_secret), json=attribute_terms[0])
                                attribute["options"] = market_url
                    if attribute_terms is None:
                        payload = {"name": market_url,
                                    "slug": str(product["id"]) + "_" + market + "_url"}
                        if service_url:
                            response = requests.post(f"{service_url}/wp-json/wc/v3/products/attributes/{attribute['id']}/terms", auth=(consumer_key, consumer_secret), json=payload, headers=service_headers)
                        else:
                            response = requests.post(f"{site_url}/wp-json/wc/v3/products/attributes/{attribute['id']}/terms", auth=(consumer_key, consumer_secret), json=payload)
                        term_data = response.json()
                    # if attribute_terms is None:
                    #     payload = {
                    #         'name': {market_url}
                    #     }
                    #     response = requests.put(f"{site_url}/wp-json/wc/v3/products/attributes/{attribute['id']}/terms/", auth=(consumer_key, consumer_secret))
                    #     if response.status_code == 200:
                    #         attribute["options"] = market_url
                #url_set = True
    return product
 
def cleanup_terms():
    print("Initiating orphaned terms cleanup")
    attributes = get_all_attributes()
    deleted_terms = 0
    if attributes is None:
        return
    for attribute in attributes:
        if any(name in attribute["name"] for name in ["ozon", "wb", "ym", "mm"]):
            terms = get_terms(attribute_id=attribute["id"])
            if terms:
                for term in terms:
                    if term["count"] == 0:
                        print(f"Removing orphaned term {term['name']} from {attribute['name']}")
                        delete_term(attribute["id"], term["id"])
                        deleted_terms += 0
    print(f"Deleted {deleted_terms} orphans terms")
                        

def delete_term(attribute_id, term_id):
    if service_url:
        requests.delete(f"{service_url}/wp-json/wc/v3/products/attributes/{attribute_id}/terms/{term_id}", auth=(consumer_key, consumer_secret), headers=service_headers)
    else:
        requests.delete(f"{site_url}/wp-json/wc/v3/products/attributes/{attribute_id}/terms/{term_id}", auth=(consumer_key, consumer_secret))

def get_products_count():
    print(f"retrieving products count")
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
        return

def get_products(page=None):
    print(f"retrieving all products")
    if page:
        params = {"page": page}
        print(f"retrieving products on page {page}")
    if host_header:
        print("Service host url is present")
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
    print(f"Updating product {product.get('id')}, with SKU: {product.get('sku')}")
    product_id = product['id']
    payload = {
        'name': product['name'],
        'attributes': product.get('attributes', []),
        'status': product['status'],
        'price': product['price'],
        'manage_stock': product['manage_stock'],
        'stock_quantity': product['stock_quantity'],
        'status': product['status']
    }
    if service_url:
        response = requests.put(f"{service_url}/wp-json/wc/v3/products/{product_id}", auth=(consumer_key, consumer_secret), json=payload, headers=service_headers)
    else:
        response = requests.put(f"{site_url}/wp-json/wc/v3/products/{product_id}", auth=(consumer_key, consumer_secret), json=payload)
    if response.status_code == 200:
        print(f"Product {product_id}  updated successfully.")
        product_updated = response.json()
        print(f"Product {product_id} with SKU {product['sku']} has been updated . Response: {response.status_code}")
        return product_updated
    else:
        print(f"Failed to update product {product_id} . Status code: {response.status_code}")
        return product

def add_missing_attributes(market_attributes):
    new_attributes = []
    attribute_list = get_all_attributes()
    print("adding globally missing market attributes")
    if attribute_list is not None:
        for attr in market_attributes:
            if attr not in attribute_list:
                new_attributes.append({
                    'name': f'{attr}',
                    'slug': f'pa_{attr}',
                    "order_by": "menu_order",
                    "visible": "false"
                })
                
        if new_attributes:
            for new_attribute in new_attributes:
                if not any(attr['name'] == new_attribute['name'] for attr in attribute_list):
                    print(f"No {new_attribute['name']} attribute found in existing attributes.")
                    print(f"Attempting to create attribute {new_attribute['name']}.")
                    response = post_attributes(new_attribute)
                    if response:
                        data = response.json()
                        attribute_list = data
                    else:
                        return
    return attribute_list
