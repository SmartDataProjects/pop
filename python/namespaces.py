import re
import logging

from pop.database import Database

LOG = logging.getLogger()

class Namespaces:
    'Describe a namespace.'
    
    def __init__(self):
        ## inialize out namespaces

        # get access to the database
        self.db = Database()
        self.dbhandle = self.db.handle

        # load all namespace patterns
        self.patterns = []
        self._load_patterns()

        # load all known namespace ids
        self.namespace_ids = {}
        self._load_namespaces()

    def find_namespace_localname(self,filename):

        # default is no namespace, global filename
        namespace = ""
        namespace_id = -1
        localname = filename

        # try to find a namespace
        for pattern in self.patterns:
            matches = re.findall(pattern,filename)
            if len(matches)==1:
                namespace = matches[0]
                localname = re.sub("^%s"%namespace,'',filename)
                # we take the first match - order of patterns might matter
                break

        # add namespace to the hash and the database
        if namespace not in self.namespace_ids:
            namespace_id = self._add_namespace(namespace)
        else:
            namespace_id = self.namespace_ids[namespace]
            

        return (namespace,namespace_id,localname)

    def _add_namespace_pattern(self,pattern):
        # this needs a test whether the patterns overlap

        if pattern in self.patterns:
            return -1
        else:
            self.patterns.append(pattern)

        return 0

    def _add_namespace(self,namespace):
        # first add to database and then to hash but only if it works

        # initialize
        namespace_id = -1

        # get a fresh cursor
        cursor = self.dbhandle.cursor()

        # add the new namespace to the database
        sql = "insert into namespaces (name) values('%s')"%(namespace)
        rc = 0
        try:
            rc = cursor.execute(sql)
            LOG.debug(' Executed: %s (%d)'%(sql,rc))
            # get the generated id
            namespace_id = cursor.lastrowid
        except:
            LOG.error(' ERROR  %s (%d)'%(sql,rc))
    
        cursor.close()

        # make sure to update our local cache
        if namespace not in self.namespace_ids:
            self.namespace_ids[namespace] = namespace_id

        return namespace_id

    def _load_namespaces(self):

        # get a fresh cursor
        cursor = self.dbhandle.cursor()


        # prepare sql query to load all known namespaces
        sql = "select namespace_id,name from namespaces"
        rc = 0 
        try:
            # Execute the SQL command
            rc = cursor.execute(sql)
            LOG.debug(' Executed: %s (%d)'%(sql,rc))
            results = cursor.fetchall()
            for row in results:
                namespace_id = int(row[0])
                name = row[1]
                self.namespace_ids[name] = namespace_id

        except:
            LOG.error(" ERROR - selecting from namespaces table (%s,%d)."%(sql,rc))

        cursor.close()
        
        return rc

    def _load_patterns(self):
        # this is hard coded for now, to be determined later

        # this needs a test whether the patterns overlap
        self.patterns.append(re.compile('(/cms/store/data)'))
        self.patterns.append(re.compile('(/cms/store/mc)'))
        self.patterns.append(re.compile('(/cms/store/test)'))
        self.patterns.append(re.compile('(/cms/store/unmerged)'))

        # this needs a test whether the patterns overlap
        self.patterns.append(re.compile('^(/scratch/[^/]*)/.*'))
        self.patterns.append(re.compile('^(/cms/store/user/[^/]*)/.*'))

        return

#if __name__ == '__main__':
#    namespaces = namespaces()
#
#    fn = "/scratch/dghsu/abc/test.root"
#    n,nid,l = namespaces.find_namespace_localname(fn)
#    print " FILENAME: %s\n N: %s  LN: %s"%(fn,n,l)
#
#    fn = "/cms/store/user/dghsu/dbaswd/loop/test.root"
#    n,nid,l = namespaces.find_namespace_localname(fn)
#    print " FILENAME: %s\n N: %s  LN: %s"%(fn,n,l)
