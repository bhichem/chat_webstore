from anytree import NodeMixin, RenderTree
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from anytree.importer import JsonImporter
from anytree import RenderTree
from anytree.exporter import DotExporter, JsonExporter
import json

porter = PorterStemmer()

def stem_tokens(token_words):
    stemmed_tokens = []
    filtered_words = token_words

    for word in filtered_words:
        stemmed_tokens.append(porter.stem(word))

    return stemmed_tokens


class MyBaseClass(object):
    foo = 0

class MyNode(MyBaseClass, NodeMixin):
    def __init__(self, name, keywords=None, question=None, degree='', parent=None, children=None):
        super(MyBaseClass, self).__init__()
        self.name = name
        self.question = question
        self.degree = degree
        self.parent = parent
        self.keywords = keywords
        self.q_idx = 0

        if children:
            self.children = children

class Chatbot():
    def __init__(self, dir='controllers/'):

        importer = JsonImporter()

        with open(dir + 'test2.json', 'r') as f:
            data = json.load(f)
            r = json.dumps(data)
            self.root = importer.import_(r)

        self.current_node = self.root
        #self.clean(self.root)
        #self.export_tree('test2.json')

    def clean(self, node):
        for child in node.children:
            keywords =[]
            c_keys = list(set(child.keywords))
            c_keys.sort()
            for keyword in c_keys:
                if len(keyword) >= 2:
                    keywords.append(''.join([i for i in keyword if i.isalpha()]))
            child.keywords = keywords
            self.clean(child)


    def export_tree(self, file_name):
        exporter = JsonExporter(indent=2, sort_keys=True)
        data = exporter.export(self.root)
        with open(file_name, 'w') as json_file:
            json_file.write(data)

    def get_brand_answer(self, brand_array, user_response):
        brand = ''
        print("we are in the brand")
        user_response = user_response.lower()
        tokens = user_response.split()
        for token in tokens:
            if token in brand_array:
                brand = token
                break
        return "What is your maximum budget?", 'brand', brand, self.current_node.name

    def get_child_node(self, current_node, user_keywords, return_node=None):
        for child in current_node.children:
            for user_keyword in user_keywords:
                for token in child.keywords:
                    if token == user_keyword:
                        return self.get_child_node(child, user_keywords, child)
        return return_node

    def get_price(self, answer):
        price = [int(s) for s in answer.split() if s.isdigit()]
        return price[0]

    def get_subcategory_answer(self, user_response):
        parent_name = self.current_node.parent.name
        #self.current_node = None
        if parent_name == 'laptop':
            laptop_brands = ['asus', 'acer', 'dell', 'macbook', 'hp', 'rog', 'lenovo', 'msi']
            return self.get_brand_answer(laptop_brands, user_response)
        elif parent_name == 'clothes':
            clothes_brands = ['adidas', 'nike', 'jeans', 'sweatpants', 'chouyatou', 'dwar', 'lock and love',
                              'ilovesia']
            return self.get_brand_answer(clothes_brands, user_response)
        return 'I am confused'

    def get_answer(self, user_response):

        user_response = user_response.lower()

        if self.current_node is None:
            price = self.get_price(user_response)
            return "Do you like the products suggested?", 'product_price', price, ''

        if self.current_node.name == "question3":
            price = self.get_price(user_response)
            return "check if you like any of the suggested products", 'price_answer', price

        current_node = self.get_child_node(self.current_node, stem_tokens((user_response.lower().split(' '))))

        if current_node == None and len(self.current_node.question) > 1:
            return self.current_node.question[1], self.current_node.degree, 'product'

        if self.current_node.degree == "general_child":
            current_node = self.current_node.children[0]
            names = self.get_tree_leaves(user_response)

            self.current_node = current_node
            return current_node.question[0], 'general_answer', names

        if self.current_node.degree == 'subcategory':
                return self.get_subcategory_answer(user_response)
        else:
            if current_node is not None:
                degree = current_node.degree
                name = current_node.name
                self.current_node = current_node
                return current_node.question[0], degree, name

            else:
                if self.current_node != self.root:
                    self.current_node = self.current_node.parent
                if self.current_node.degree != 'root' \
                        and len(self.current_node.question) > self.current_node.q_idx+1:
                    print("node current idx")
                    self.current_node.q_idx += 1
                    return self.current_node.question[self.current_node.q_idx], self.current_node.degree, 'product'
                return 'Sorry we do not have this product right now, do you have other products you are interested in? ', \
                       self.current_node.degree, 'product'

    def get_tree_leaves(self, user_response):

        root_node = self.root
        user_response = user_response.lower()
        tokens = stem_tokens(user_response.split())
        names = []

        for child in root_node.children:
            if child.name == 'product':
                current_node = child
                leaves = current_node.leaves
                for leaf in leaves:
                    for token in tokens:
                        if token in leaf.keywords:
                            names.append(leaf.name)
        return names

    def print_tree(self, product):
        for pre, fill, node in RenderTree(product):
            print("%s%s question=%s" % (pre, node.name, node.question[0]))

    def reset_tree(self):
        for node in self.root.children:
            node.q_idx = 0
        self.current_node = self.root

def main():
    directory = ''
    chatbot = Chatbot(directory)
    print(chatbot.root.question[0])

    while (True):
        user_response = input()
        response = chatbot.get_answer(user_response)
        print(response[0], response[1], response[2])

if __name__ == '__main__':
    main()
