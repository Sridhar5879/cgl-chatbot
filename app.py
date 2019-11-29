import pandas as pd
import nltk
nltk.data.path.append('/app/nltk_data') 
#nltk.download("wordnet","/app/nltk_data/")
#nltk.download("stopwords","/app/nltk_data/")
import warnings
warnings.filterwarnings("ignore")
from fuzzywuzzy import fuzz
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.stem.porter import *
import stemming
from textblob import TextBlob, Word
from stemming.porter2 import stem
stop_words=set(stopwords.words('english'))

# Method to convert a series into a String
def convert(s):
  # initialization of string to ""
  new = ""
  # traverse in the string
  for x in s:
    new += x+' '
    # return string
  return new


# Basic code required to run the app on heroku
from flask import Flask, render_template, request, json, jsonify, make_response
import requests
import pdb
app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def order_status():
  if request.method == 'POST':
    #Reading the document and the relevant fields
    df=pd.read_excel("chatbot - CGL.xlsx")
    dfq=df['Question']
    dfa=df['Answer']
    dfq.head()
    dfa.head()
    #Lemmatization of "Questions"
    from textblob import Word
    dfq1 = dfq.apply(lambda x: " ".join([Word(word).lemmatize() for word in x.split()]))
    dfq1.head()
    #Removal of stop words
    from nltk.corpus import stopwords
    stop = stopwords.words('english')
    dfq1 = dfq1.apply(lambda x: " ".join(x for x in x.split() if x not in stop))
    dfq1.head()
  
    # Changing the "Questions" to lower case
    dfq_1 = [w.lower() for w in dfq1]
    # "Answers" have been converted to a list
    dfa1=[w for w in dfa]
      
    #Taking the input query from user and converting it to an usable string
    query = request.form.get('ui_query')
    #query = input('Hello, How can i assist you:\n')
    query1 = pd.Series(query)
    query2 = query1.apply(lambda x: " ".join([Word(word).lemmatize() for word in x.split()]))
    query2=  [w for w in query2 if not w in stop]
    
    # Converting query2 into a string
    k=convert(query2)
    #Implementation fuzzywuzzy algorithm to find the closest match
    from fuzzywuzzy import process
    ## To Get Related questions based on ratio
    choices_dict = {idx: el for idx, el in enumerate(dfq_1)}
    Ratios = process.extract(k,choices_dict,limit=3)
    ChatReply=(tuple(Ratios[0]))
    j=(tuple(Ratios[1]))
    l=(tuple(Ratios[2]))
    if ChatReply[1]<70:
      aa = {}
      aa['input'] = request.form.get('ui_query')
      aa['result'] = "Sorry but your query did not match with any of our records, please try with another query"
      print('Sorry but your query did not match with any of our records, please try with another query')
    elif ChatReply[1]>=70 and ChatReply[2] <= 48:
      aa = {}
      aa['input'] = request.form.get('ui_query')
      aa['result'] = dfa[ChatReply[2]]
      print('\n',ChatReply[0],'\n',dfa[ChatReply[2]],'\n')
    else:
      aa = {}
      aa['input'] = request.form.get('ui_query')
      aa['result'] = dfa[k[2]]
      print('\n','NEAREST MATCH','\n''\n',dfq[ChatReply[2]],'\n',dfa[ChatReply[2]],'\n','\n','DO YOU MEAN?','\n',dfq[j[2]],'\n',dfq[l[2]])
    return aa
  else:
      return render_template('chat.html')

if __name__ == "__main__":
  #from waitress import serve
  #serve(app, host="127.0.0.1", port=8081)
  app.run(host='127.0.0.1')