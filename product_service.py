def filter_products(products, search="", category="All", max_price=100000):
    search = (search or "").strip().lower()
    result = []
    for p in products:
        if category != "All" and p["category"] != category:
            continue
        if float(p["price"]) > float(max_price):
            continue
        searchable = f"{p['name']} {p['description']} {p['material']} {p['category']}".lower()
        if search and search not in searchable:
            continue
        result.append(p)
    return result

def get_product_by_id(products, product_id):
    return next((p for p in products if int(p["id"]) == int(product_id)), None)
