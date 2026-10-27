from services.product_service import filter_products

def test_filter_products():
    products = [
        {"id": 1, "name": "Pearl Earrings", "category": "Earrings", "price": 1000,
         "material": "Pearl", "description": "Small pearl earrings"},
        {"id": 2, "name": "Gold Necklace", "category": "Necklaces", "price": 2500,
         "material": "Gold-plated", "description": "Simple necklace"},
    ]
    assert len(filter_products(products, search="pearl")) == 1
    assert len(filter_products(products, category="Necklaces")) == 1
    assert len(filter_products(products, max_price=1500)) == 1
