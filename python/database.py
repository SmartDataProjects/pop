import MySQLdb

class Database:
    """
    Provides interface for the database interactions. It is really about the connection parameters
    to be in one place.
    """
    
    def __init__(self,user="",password="",database=""):
        self.handle = MySQLdb.connect(read_default_file="/etc/my.cnf",
                                      read_default_group="mysql-pop",
                                      db="pop")
        #self.handle = MySQLdb.connect(user=user,
        #                              password=password,
        #                              db=database)
