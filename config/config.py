SQLALCHEMY_DATABASE_URI='sqlite:///data/db/imperium.db'
SQLALCHEMY_ECHO = False
SQLALCHEMY_POOL_RECYCLE = 299
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="trnecka",
    password="<the password you set on the 'Databases' tab>",
    hostname="trnecka.mysql.eu.pythonanywhere-services.com",
    databasename="trnecka$imperium",
)