from tinydb import TinyDB,Query
from datetime import datetime
import os

class Database:
    def __init__(self,db_path="data.json"):
        dirname = os.path.dirname(db_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
            self.db = TinyDB(db_path)
            self.products_table = self.db.table('products')

    def insert_product(self,product_data):
        product_data["Created at"] = datetime.now().isoformat()
        self.products_table.insert(product_data)

    def get_product(self,asin):
        product_table = Query()
        return self.products_table.search(product_table.ASIN == asin)
    
    def get_all_products(self):
        return self.products_table.all()
    
    def search_products(self,search_criteria):
            product_table = Query()
            query = None
            for key,value in search_criteria.item():
                 if query is None:
                    query = (product_table[key] == value)
            else:
                query = query & (product_table[key] == value)
                      
            
            return self.products_table.search(query) if query else []