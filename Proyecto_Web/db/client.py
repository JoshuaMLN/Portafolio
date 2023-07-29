from pymongo import MongoClient

# Base de datos local
#db_client = MongoClient().local

#Base de datos remota
db_client = MongoClient("mongodb+srv://knastusml:Jmln_2003@clusterleon.pulrus1.mongodb.net/?retryWrites=true&w=majority").test
