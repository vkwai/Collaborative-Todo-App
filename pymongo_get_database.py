import pymongo
import json
from pymongo import MongoClient
def get_database():
 
   CONNECTION_STRING = "mongodb+srv://v:7788@1280cluster.cccf8nf.mongodb.net/?retryWrites=true&w=majority"
 
   client = MongoClient(CONNECTION_STRING)
 
   return client['project']
  
if __name__ == "__main__":   
   db = get_database()
  
