from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen 
import logging
import pymongo
logging.basicConfig(filename="scrapper.log",level=logging.INFO)

app =  Flask(__name__)

@app.route("/",methods = ['GET'])
@cross_origin()
def homepage():
    return render_template("index.html")

@app.route("/scrap",methods = ['POST','GET'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['search'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = urlopen(flipkart_url)
            flipkart_page = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkart_page,"html.parser")
            bigboxes = flipkart_html.find_all("div",{"class":"_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text,"html.parser")
            print(prod_html)
            commentboxes = prod_html.find_all("div",{'class':'_16PBlm'})

            filename = searchString + ".csv"
            fw = open(filename,"w")
            headers = "Product, Customer name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    name = commentbox.div.div.find_all('p',{'class':'_2sc7ZR _2V5EHH'})[0].text
                
                except:
                    logging.info("name")

                try:
                    rating = commentbox.div.div.div.div.text
                
                except:
                    rating = "no rating"
                    logging.info("rating")
                
                try:
                    commentHead = commentbox.div.div.div.p.text 
                
                except:
                    commentHead = "No comment Heading"
                    logging.info(commentHead)

                try:
                    comtag = commentbox.div.div.find_all('div',{'class':''})
                    custComment = comtag[0].div.text 
                
                except Exception as e:
                    logging.info(e)

                mydict = {
                    "Product":searchString, "Name":name, "Rating": rating, "CommentHead":commentHead,
                    "Comment":custComment
                }

                reviews.append(mydict)
            logging.info("log my final dict{}".format(reviews))

            
            client = pymongo.MongoClient("mongodb+srv://Anirudhra:Anirudhra@cluster0.dls0ufn.mongodb.net/?retryWrites=true&w=majority")
            db =  client['scrapper']
            coll_create = db['product_reviews']
            coll_create.insert_many(reviews)


            return render_template('result.html',reviews=reviews[0:(len(reviews)-1)])
        
        except Exception as e:
            logging.info(e)
            return "Something is wrong"
    
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0")
