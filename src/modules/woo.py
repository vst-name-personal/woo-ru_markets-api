def check_ready(product):
    # Check if the product has images
    if 'images' in product and len(product['images']) > 0:
        return True
    else:
        return False
    
    for attribute in attributes_to_check:
        if attribute in product and product[attribute]:
            return True
    return False

# Example usage:
attributes_to_check = ['images', 'description', 'gallery']