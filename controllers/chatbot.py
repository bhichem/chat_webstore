
import io
import random
import string  # to process standard python strings
import warnings
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
import threading

warnings.filterwarnings('ignore')

import nltk
from nltk.stem import WordNetLemmatizer

nltk.download('popular', quiet=True)  # for downloading packages

# uncomment the following only the first time
# nltk.download('punkt') # first-time use only
# nltk.download('wordnet') # first-time use only

class Chatbot():
    def __init__(self):

        # Reading in the corpus
        with open('controllers/chatbot.txt', 'r', encoding='utf8', errors='ignore') as fin:
            raw = fin.read().lower()

        # TOkenisation
        self.sent_tokens = nltk.sent_tokenize(raw)  # converts to list of sentences
        self.word_tokens = nltk.word_tokenize(raw)  # converts to list of words

        # Preprocessing
        self.lemmer = WordNetLemmatizer()
        self.remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

        # Keyword Matching
        self.GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up", "hey",)
        self.GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]


    def Lem_tokens(self, tokens):
        return [self.lemmer.lemmatize(token) for token in tokens]


    def Lem_normalize(self, text):
        return self.LemTokens(nltk.word_tokenize(text.lower().translate(self.remove_punct_dict)))


    def greeting(self, sentence):
        """If user's input is a greeting, return a greeting response"""
        for word in sentence.split():
            if word.lower() in self.GREETING_INPUTS:
                return random.choice(self.GREETING_RESPONSES)


    # Generating response
    def response(self, user_response):
        robo_response = ''
        self.sent_tokens.append(user_response)
        TfidfVec = TfidfVectorizer(tokenizer=self.LemNormalize, stop_words='english')
        tfidf = TfidfVec.fit_transform(self.sent_tokens)
        vals = cosine_similarity(tfidf[-1], tfidf)
        idx = vals.argsort()[0][-2]
        flat = vals.flatten()
        flat.sort()
        req_tfidf = flat[-2]
        if (req_tfidf == 0):
            robo_response = robo_response + "I am sorry! I don't understand you"
            return robo_response
        else:
            robo_response = robo_response + self.sent_tokens[idx]
            return robo_response

    def get_answer(self,user_response):

        user_response = user_response.lower()
        if (user_response != 'bye'):
            if (user_response == 'thanks' or user_response == 'thank you'):
                return "John: You are welcome.."
            else:
                if (self.greeting(user_response) != None):
                    return "John: " + self.greeting(user_response)
                else:

                    response = self.response(user_response)
                    self.sent_tokens.remove(user_response)
                    return response

        else:
            return "John: Bye! take care.."


def main():
    flag = True
    chatbot = Chatbot()
    print("ROBO: My name is Robo. I will answer your queries about Chatbots. If you want to exit, type Bye!")

    while (flag == True):
        user_response = input()
        user_response = user_response.lower()
        print(chatbot.get_answer(user_response))


if __name__ == '__main__':
    main()



