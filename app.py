import flask_login
from flask import Flask, request, jsonify, json, render_template, flash, redirect, url_for, session

from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from pony.flask import Pony
from controllers.database import PonyDB
from flask_bcrypt import Bcrypt
import os
from flask_socketio import SocketIO
from controllers.treebot import Chatbot
from datetime import timedelta

app = Flask(__name__)
app.config['TESTING'] = False
app.debug = False

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
ALLOWED_EXTENSIONS = set(['png', 'jpg'])

UPLOAD_FOLDER = os.path.abspath('static/products/')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

socketio = SocketIO(app)

login_manager = LoginManager()
login_manager.init_app(app)

bcrypt = Bcrypt(app)

Pony(app)
ponyDB = PonyDB(bcrypt)
chatbot = Chatbot()

class UserAnswers:

    def __init__(self):
        self.user_answers = []
        self.subcategory= ''

    def get_answers(self):
        return self.user_answers

    def add_answer(self, answers):
        for answer in answers:
            self.user_answers.append(answer)

    def add_subcategory(self, subcategory):
        self.subcategory = subcategory
    def get_subcategory(self):
        return self.subcategory

userAnswers = UserAnswers()

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)

@login_manager.user_loader
def load_user(id):
    user = ponyDB.get_user_by_id(id)
    return user

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')

@app.route('/')
@login_required
def home():
    products = ponyDB.get_products(user_gender=current_user.gender)
    categories = [product['category'] for product in products]
    print(set(categories))
    return render_template('index.html', products=products, categories=list(set(categories)))


@app.route('/login', methods=['GET'])
def login_get():
    return render_template('login.html')

@app.route('/products', methods=['GET'])
def get_general_products():
    category = str(request.args.get('category'))
    products = ponyDB.get_product_by_category(product_category=category, general=True)
    subcategories = [product['subcategory'] for product in products]
    return render_template('index.html', products=products, subcategories=list(set(subcategories)))

@app.route('/productsubs', methods=['GET'])
def get_general_products_subcategory():
    sub_category = str(request.args.get('subcategory'))
    products = ponyDB.get_product_by_subcategory(product_subcategory=sub_category, general=True)
    sub_categories = [product['subcategory'] for product in products]
    return render_template('index.html', products=products, subcategories=list(set(sub_categories)))


@app.route('/validate_login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    user = ponyDB.get_user(username)

    if user is not None:
        if not bcrypt.check_password_hash(user.password, password):
            print(bcrypt.check_password_hash(user.password, password))
            flash('Please check your login details and try again.')
            return redirect(url_for('login_get'))
        login_user(user)

        return redirect(url_for('home'))
    flash('Please check your login details and try again.')
    return redirect(url_for('login_get'))

@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')

@app.route('/handlesignup', methods=['POST'])
def handle_signup():

    username = request.form.get('username')
    password = request.form.get('password')
    try:
        gender = request.form.get('gender')
    except:
        gender = ''
    user = ponyDB.get_user(username)
    print('user', username)
    print('password', password)
    print("gender", gender)

    if user is not None:
        flash('username already exists.')
        return redirect(url_for('home'))

    ponyDB.add_user(username, bcrypt.generate_password_hash(password), gender=gender)
    user = ponyDB.get_user(username)

    login_user(user)
    print("rendering home")
    return redirect(url_for('home'))


def message_received(methods=['GET', 'POST']):
    print('message was received!!!')

subcategory = None
@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    if 'data' in json.keys():
        print(str(json))
    response_data = {}

    if 'message' in json.keys():
        message = json['message']
        response = chatbot.get_answer(message)
        products = []
        degree = response[1]
        name = response[2]

        product_list = []

        if degree == 'category':
            products = ponyDB.get_product_by_category(product_category=name,
                                                      user_gender=current_user.gender)
        elif degree == 'subcategory':
            products = ponyDB.get_product_by_subcategory(product_subcategory=name,
                                                         user_gender=current_user.gender)
        elif degree == 'brand':
            sub_category = response[3]
            userAnswers.add_subcategory(str(sub_category))
            products = ponyDB.get_product_by_brand(product_subcategory=sub_category,
                                                   product_brand=name,
                                                   user_gender=current_user.gender)

        elif degree == 'product_price':
            products += ponyDB.get_product_by_price(product_subcategory=userAnswers.get_subcategory(),
                                                    user_gender=current_user.gender,
                                                    price=name)
        elif degree == 'general_answer':
            userAnswers.add_answer(name)
            for n in name:
                products += ponyDB.get_product_by_subcategory(product_subcategory=str(n),
                                                              user_gender=current_user.gender)
        elif degree == 'price_answer':
                answers = userAnswers.get_answers()
                for n in answers:
                    products += ponyDB.get_product_by_price(product_subcategory=str(n),
                                                            user_gender=current_user.gender,
                                                            price=name)
        else:
            products = ponyDB.get_products()

        if products is not None:
            product_list = products

        response_data['response'] = response[0]
        response_data['products'] = product_list
    socketio.emit('my response', response_data, callback=message_received)


@app.route('/get_products', methods=['POST', 'GET'])
@login_required
def get_products():
    message = str(request.form.get('message'))
    response = chatbot.get_answer(message)

    return response[0]

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_get'))


if __name__ == '__main__':
    app.run(port=5020)
    #app.run()
