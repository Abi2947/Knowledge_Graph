# !pip install BeautifulSoup4
# !pip install newspaper3k
# !pip install pymongo
# !pip install nltk
# !pip install networkx
# !pip install spacy
# !pip install py2neo

# python -m spacy download en_core_web_sm


import requests
from bs4 import BeautifulSoup
import spacy
import networkx as nx

# Step 1: Scraping text data from selected articles
url = "https://english.onlinekhabar.com/"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
articles = soup.select("article")[:3]  # Selecting first 3 articles for example

text = ""
for article in articles:
    title = article.select_one("h2 a").text.strip()
    content = article.select_one(".entry-summary").text.strip()
    text += f"{title}. {content}\n"

# Step 2: Applying necessary NLP processing
nlp = spacy.load("en_core_web_sm")
doc = nlp(text)

# Step 3: Extracting subject, object, and relationship from each sentence
edges = []
for sent in doc.sents:
    for token in sent:
        if token.dep_ == "nsubj" and token.head.pos_ == "VERB":
            subject = token.text
            for child in token.children:
                if child.dep_ == "amod":
                    subject = child.text + " " + subject
            for child in token.head.children:
                if child.dep_ == "dobj":
                    obj = child.text
                    for grandchild in child.children:
                        if grandchild.dep_ == "amod":
                            obj = grandchild.text + " " + obj
                    edges.append((subject, obj, token.head.text))

# Step 4: Building a directed graph from the above data
G = nx.DiGraph()
for edge in edges:
    G.add_edge(edge[0], edge[1], relation=edge[2])

# Step 5: Geting an answer to the given question
question = "What is the latest news on politics?"
parsed_question = nlp(question)

query = ""
for token in parsed_question:
    if token.pos_ == "NOUN":
        query += f"{token.text.title()} "
    elif token.pos_ == "PROPN":
        query += f"{token.text} "

if query:
    answers = []
    for edge in G.edges(data=True):
        if query.strip() in (edge[0], edge[1]):
            answers.append(edge[2]["relation"])
    if answers:
        print(f"The latest news on {query.strip()} is: {max(answers)}")
    else:
        print(f"No news found on {query.strip()}.")
else:
    print("Invalid question format.")
