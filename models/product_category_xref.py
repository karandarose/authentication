from db import db

product_category_association_table = db.Table(
    "Products_Categories",
    db.Column("product_id", db.ForeignKey("Products.product_id"), primary_key=True),
    db.Column("category_id", db.ForeignKey("Categories.category_id"), primary_key=True)
)
