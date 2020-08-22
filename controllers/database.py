from pip._vendor import requests
from pony.orm import PrimaryKey, Optional, Required, db_session, Database
from flask_login import UserMixin
import json
import random
import base64
from PIL import Image
from webptools import dwebp


class PonyDB:
    db = Database()

    def __init__(self, bcrypt=None):
        self.bcrypt = bcrypt
        self.seed = False

        self.db.bind(provider='sqlite', filename='shop', create_db=True)

        self.db.generate_mapping(create_tables=True)

        if self.seed:
            self.seed_database('controllers/seed.json')

    class Product(db.Entity):
        id = PrimaryKey(int, auto=True)
        title = Required(str)
        category = Optional(str)
        subcategory = Optional(str)
        price = Optional(int)
        description = Optional(str)
        image = Optional(str)
        brand = Optional(str)
        gender = Optional(str)


    class User(UserMixin, db.Entity):
        id = PrimaryKey(int, auto=True)
        username = Required(str, unique=True)
        password = Required(bytes, unique=True)
        age = Optional(int)
        gender = Optional(str)
        occupation = Optional(str)
        question_1 = Optional(str)
        question_2 = Optional(str)

    @db_session
    def add_user(self, username, password, gender=''):
        PonyDB.User(username=username,
                    password=password,
                    gender=gender)

    @db_session
    def add_product(self, title,category,subcategory, price, description, image):
        PonyDB.User(title=title,
                    category=category,
                    subcategory=subcategory,
                    price=price,
                    description=description,
                    image=image)

    @db_session
    def add_user_details(self, id, age, gender, question1):
        PonyDB.UserDetails(user_id=id, age=age, gender=gender, question_1=question1)

    @db_session
    def get_products(self, user_gender='neutral'):
        result = PonyDB.Product.select(lambda x: (x.gender == user_gender or x.gender == 'neutral')).random(100)

        if len(result) > 0:
            return self.serialize_result(result)
        else:
            return None

    @db_session
    def get_product_by_id(self, product_id):
        result = PonyDB.Product.select(lambda p: p.id == product_id).page(1)
        if len(result) > 0:
            result = result[0]
            return result
        else:
            return None

    @db_session
    def get_product_by_category(self, product_category='', user_gender='neutral', general=False):
        if general:
            result = PonyDB.Product.select(lambda x: product_category.lower() in x.category).random(100)
        else:
            result = PonyDB.Product.select(lambda x: product_category.lower() in x.category
                                            and (x.gender.startswith(user_gender) or x.gender == 'neutral')).random(100)

        if len(result) > 0:
            return self.serialize_result(result)
        else:
            return None

    @db_session
    def get_product_by_subcategory(self, product_subcategory='',  user_gender='neutral', general=False):
        if general:
            result = PonyDB.Product.select(lambda x: product_subcategory.lower() in x.subcategory).random(100)
        else:
            result = PonyDB.Product.select(lambda x: product_subcategory.lower() in x.subcategory
                                            and (x.gender.startswith(user_gender) or x.gender == 'neutral')).random(100)
        if len(result) > 0:
            return self.serialize_result(result)
        else:
            return []

    @db_session
    def get_product_by_brand(self, product_subcategory='', product_brand='',  user_gender='neutral'):
        print("in query", product_subcategory, product_brand)
        result = PonyDB.Product.select(lambda x: product_brand.lower() in x.brand
                                                 and (x.gender.startswith(user_gender) or x.gender == 'neutral')
                                                 and product_subcategory.lower() in x.subcategory)
        if len(result) > 0:
            return self.serialize_result(result)
        else:
            return None

    @db_session
    def get_product_by_price(self,product_subcategory='', product_brand='', price='',   user_gender='neutral'):
        print('price is', price, "type", "product subcategory=", product_subcategory)

        price = price * 100

        if product_subcategory != '' and product_brand != '':
            result = PonyDB.Product.select(lambda x: product_subcategory.lower() in x.subcategory
                                                    and product_brand.lower() in x.brand
                                                    and (x.gender == user_gender or x.gender == 'neutral')
                                                    and x.price <= price)
        elif product_subcategory != '':
            result = PonyDB.Product.select(lambda x: product_subcategory.lower() in x.subcategory
                                                    and (x.gender == user_gender or x.gender == 'neutral')
                                                    and x.price <= price)
        else:
            result = PonyDB.Product.select(lambda x: (x.gender == user_gender or x.gender == 'neutral')
                                                    and x.price <= price)
        if len(result) > 0:
            return self.serialize_result(result)
        else:
            return None


    @db_session
    def get_random_products(self, size):

        result = PonyDB.Product.select_by_sql("SELECT * FROM Product ORDER BY RANDOM()")
        if len(result) > 0:
            return self.serialize_result(result, size)
        else:
            return None

    @db_session
    def update_url(self, product_id,image_url):
        p =PonyDB.Product[product_id]
        p.set(image=image_url)


    @db_session
    def get_user(self, username):
        result = PonyDB.User.select(lambda s: s.username == username).page(1)
        if len(result) > 0:
            result = result[0]
            return result
        else:
            return None

    @db_session
    def get_user_by_id(self, userid):
        result = PonyDB.User.select(lambda s: s.id == userid).page(1)
        if len(result) > 0:
            result = result[0]
            return result
        else:
            return None

    @db_session
    def seed_database(self, dump_filename):

        data = json.load(open(dump_filename, 'r'))
        for record in data['Users']:
            PonyDB.User(username=record['username'], password=self.bcrypt.generate_password_hash(record['password']))

    @db_session
    def serialize_result(self, products, size_=100):
        product_list = []
        for row in products:

            row_dict = {}
            row_dict['id'] = row.id
            row_dict['title'] = row.title.split(',')[0]
            row_dict['image'] = row.image
            row_dict['price'] ='€ '+str(float(row.price/100))
            row_dict['category'] = row.category
            row_dict['subcategory'] = row.subcategory
            row_dict['description'] = row.description
            product_list.append(row_dict)

        return product_list[:size_]

def main():
    db = PonyDB()
    result = db.get_product_by_brand(product_subcategory='', product_brand='adidas',  user_gender='male')
    print(len(result))
    result = db.get_random_products(7000)
    print(len(result))
    i = 0
    for r in result:
        link = r["image"]
        if link.startswith("data:image/webp;base64"):
            blob = link
            filedir = '../test/' + str(i)+'_'+r['subcategory']
            print(filedir)
            with open(filedir+".webp", 'wb') as fh:
                # Get only revelant data, deleting "data:image/png;base64,"
                data = blob.split(',')[1]
                fh.write(base64.b64decode(data))
                i+=1
                db.update_url(r['id'], str(i)+'_'+r['subcategory']+'.jpg')

        # if link.startswith("http"):
        #     print(link)
        #     print(link.split("/")[-1])
        #     response = requests.get(link)
        #     if response is not None:
        #         filename = link.split("/")[-1]
        #         file = open("../test/"+filename, "wb")
        #         file.write(response.content)
        #         file.close()
        #         db.update_url(r["id"],filename)
        #     else:
        #         print("image is not retrived", link)
if __name__ == '__main__':
    main()