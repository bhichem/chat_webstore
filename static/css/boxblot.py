import matplotlib.pyplot as plt

import matplotlib.pyplot as plt

x = [[94.8, 66.6, 85.2, 96.1, 78.3, 99.2, 100.3, 130.6, 104.6, 84.3, 86.7, 60.3, 92.0, 46.8, 121, 95, 112,130, 105, 66 ],
        [30.1, 20.8, 35.6,  24.2, 26.5, 28.6, 29.5, 33.5, 45.6, 37.0, 32.6, 42.3, 28.5, 20.0, 32, 40, 37, 55, 42, 38]]

print(len(x[0]), len(x[1]))
plt.boxplot(x, patch_artist=True, labels=['Tranditional navigation','Dialogue based'])
plt.xlabel("Method")
plt.ylabel("Time in seconds")
plt.savefig("time.png")
#plt.title("Time difference between traditional navigation and dialgue based navigation")
plt.show()

# import these modules
from nltk.stem import WordNetLemmatizer


from anytree import Node, RenderTree

from anytree import NodeMixin, RenderTree
from nltk.stem import PorterStemmer
porter = PorterStemmer()
from anytree.exporter import JsonExporter

from nltk.corpus import stopwords
from anytree.importer import JsonImporter
from anytree import RenderTree

import json

lemmatizer = WordNetLemmatizer()


print("browsing", porter.stem(lemmatizer.lemmatize("browsing")))
print("student", porter.stem(lemmatizer.lemmatize("student")))
print("traveling", porter.stem(lemmatizer.lemmatize("traveling")))
print("reading", porter.stem(lemmatizer.lemmatize("reading")))
print("nothing", porter.stem(lemmatizer.lemmatize("nothing")))

