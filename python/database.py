import MySQLdb

class database:
    """
    Provides interface for the database interactions. It is really about the connection parameters
    to be in one place.
    """
    
    def __init__(self):
        self.handle = MySQLdb.connect(read_default_file="/etc/my.cnf",
                                      read_default_group="mysql",
                                      db="pop")
