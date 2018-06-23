import datetime
import logging

from pop.database import Database
from pop.namespaces import Namespaces

LOG = logging.getLogger()

class Engine:
    """
    Provides a standard interface for the popularity operations.
    """
    
    def __init__(self,user="",password="",database=""):
        # not yet using the input parameters
        self.db = Database(user="",password="",database="")
        self.dbhandle = self.db.handle
        self.namespaces = Namespaces()

    def add_open(self,filename,timestamp):

        rc = 0

        # make sure we have the ids
        (namespace_id,file_id) = self._find_ids(filename)

        # get a fresh cursor
        cursor = self.dbhandle.cursor()

        sql = "insert into file_usage values(%d,'%s')"%(file_id,str(timestamp))
        rc = cursor.execute(sql)
        LOG.debug(' Executed: %s (%d)'%(sql,rc))
        
        cursor.close()

        return rc

    def delete_usage(self,filename):
        rc = 0

        # get a fresh cursor
        cursor = self.dbhandle.cursor()

        # get ids (careful they might not exist, so they wil be created if needed)
        (namespace_id,file_id) = self._find_ids(filename)
        if file_id > 0:
            sql = "delete from file_usage where file_id = %d"%(file_id)
            rc = cursor.execute(sql)
            LOG.debug(' Executed: %s (%d)'%(sql,rc))

        cursor.close()

        return rc

    def get_last_update(self):

        # get a fresh cursor
        cursor = self.dbhandle.cursor()

        sql = "select * from updated"
        rc = 0
        try:
            rc = cursor.execute(sql)
            LOG.debug(' Executed: %s (%d)'%(sql,rc))
        except:
            LOG.error(' ERROR  %s (%d)'%(sql,rc))
           
        results = cursor.fetchall()
        for row in results:
            timestamp = row[0]

        cursor.close()

        return timestamp

    def set_last_update(self,timestamp):

        rc = 0
        # get a fresh cursor
        cursor = self.dbhandle.cursor()

        sql = "update updated set last_update = '%s'"%(timestamp)
        rc = cursor.execute(sql)
        LOG.debug(' Executed: %s (%d)'%(sql,rc))

        cursor.close()

        return rc

    def get_namespaces(self):

        # get a fresh cursor
        cursor = self.dbhandle.cursor()

        # prepare sql query to get files with the given filename
        sql  = "select name from namespaces"
        try:
            # Execute the SQL command
            rc = cursor.execute(sql)
            LOG.debug(' Executed: %s (%d)'%(sql,rc))
            results = cursor.fetchall()
        except:
            LOG.error(" ERROR - selecting from namespaces table (%s)."%sql)
            results = []

        cursor.close()

        return results

    def get_namespace_usage_summary(self,namespace):

        # get each access for any given file in the namespace
        file_usages = self._get_namespace_usage(namespace)

        # generate the summary information
        n_accesses = {}
        last_accesses = {}
        for (localname,timestamp) in file_usages:
            if localname not in n_accesses:
                n_accesses[localname] = 1
                last_accesses[localname] = timestamp
            else:
                n_accesses[localname] += 1
                if last_accesses[localname]<timestamp:
                    last_accesses[localname] = timestamp    

        # put it in a simple ntuple
        usage_summary = []
        for localname in n_accesses:
            usage_summary.append((localname,n_accesses[localname],last_accesses[localname]))
        
        return usage_summary

    def _get_namespace_usage(self,namespace):

        # get a fresh cursor
        cursor = self.dbhandle.cursor()

        # prepare sql query to get files with the given filename
        sql  = "select f.name, u.usage_time from file_usage as u"
        sql += " inner join files as f on f.file_id = u.file_id"
        sql += " inner join namespaces as n on n.namespace_id = f.namespace_id"
        sql += " where n.name = '%s'"%(namespace)
        try:
            # Execute the SQL command
            rc = cursor.execute(sql)
            LOG.debug(' Executed: %s (%d)'%(sql,rc))
            results = cursor.fetchall()
        except:
            LOG.error(" ERROR - selecting from files table (%s)."%sql)
            results = []

        cursor.close()

        return results

    def _add_file(self,namespace_id,localname):

        file_id = 0

        # get a fresh cursor
        cursor = self.dbhandle.cursor()

        # add the new file
        sql = "insert into files (namespace_id,name) values(%d,'%s')"%(namespace_id,localname)
        rc = cursor.execute(sql)
        LOG.debug(' Executed: %s (%d)'%(sql,rc))
        # get the generated id
        file_id = cursor.lastrowid
    
        cursor.close()

        return file_id

    def _find_ids(self,filename):

        # initialize
        file_id = 0
        namespace_id = 0

        # find the namespace and local file name
        (namespace_name,namespace_id,localname) = \
            self.namespaces.find_namespace_localname(filename)

        # get a fresh cursor
        cursor = self.dbhandle.cursor()

        # prepare sql query to get files with the given filename
        sql = "select file_id from files where namespace_id = %d and name = '%s'"% \
            (namespace_id,localname)
        try:
            # Execute the SQL command
            rc = cursor.execute(sql)
            LOG.debug(' Executed: %s (%d)'%(sql,rc))
            results = cursor.fetchall()
            for row in results:
                file_id = int(row[0])
        except:
            LOG.error(" ERROR - selecting from files table (%s)."%sql)

        cursor.close()

        if file_id == 0:
            file_id = self._add_file(namespace_id,localname)

        return (namespace_id,file_id)

#if __name__ == '__main__':
#    pass
