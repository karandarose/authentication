from flask import jsonify, request

from db import db
from models.product import Products, product_schema, products_schema
from models.category import Categories
from util.reflection import populate_object
from lib.authenticate import authenticate_return_auth

def create_product():
    post_data = request.form if request.form else request.get_json()

    new_product = Products.new_product_obj()
    populate_object(new_product, post_data)

    try:
        db.session.add(new_product)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to create product: {e}"}), 400

    return jsonify({"message": "product created", "result": product_schema.dump(new_product)}), 201

def get_products():
    product_query = db.session.query(Products).all()

    if not product_query:
        return jsonify({"message": "no products found"}), 404

    return jsonify({"message": "products found", "results": products_schema.dump(product_query)}), 200

def get_active_products():
    product_query = db.session.query(Products).filter(Products.active == True).all()

    if not product_query:
        return jsonify({"message": "no active products found"}), 404

    return jsonify({"message": "active products found", "results": products_schema.dump(product_query)}), 200

def get_product_by_id(product_id):
    product_query = db.session.query(Products).filter(Products.product_id == product_id).first()

    if not product_query:
        return jsonify({"message": "product not found"}), 404

    return jsonify({"message": "product found", "result": product_schema.dump(product_query)}), 200

def get_products_by_company_id(company_id):
    product_query = db.session.query(Products).filter(Products.company_id == company_id).all()

    if not product_query:
        return jsonify({"message": "no products found for this company"}), 404

    return jsonify({"message": "products found", "results": products_schema.dump(product_query)}), 200

def update_product_by_id(product_id):
    post_data = request.form if request.form else request.get_json()
    product_query = db.session.query(Products).filter(Products.product_id == product_id).first()

    if not product_query:
        return jsonify({"message": "product not found"}), 404

    populate_object(product_query, post_data)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to update product: {e}"}), 400

    return jsonify({"message": "product updated", "result": product_schema.dump(product_query)}), 200

def delete_product_by_id(product_id):
    product_query = db.session.query(Products).filter(Products.product_id == product_id).first()

    if not product_query:
        return jsonify({"message": "product not found"}), 404

    try:
        db.session.delete(product_query)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to delete product: {e}"}), 400

    return jsonify({"message": "product deleted"}), 200

def create_product_category():
    post_data = request.form if request.form else request.get_json()

    product_id = post_data.get('product_id')
    category_id = post_data.get('category_id')

    product_query = db.session.query(Products).filter(Products.product_id == product_id).first()
    category_query = db.session.query(Categories).filter(Categories.category_id == category_id).first()

    if not product_query or not category_query:
        return jsonify({"message": "product or category not found"}), 404

    if category_query not in product_query.categories:
        product_query.categories.append(category_query)
        db.session.commit()

    return jsonify({"message": "category added to product", "result": product_schema.dump(product_query)}), 201