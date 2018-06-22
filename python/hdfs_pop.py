import os
import re
import time
import datetime
import logging
import ConfigParser

from pop.engine import Engine

LOG = logging.getLogger()

# main object
class Hdfs_pop(object):
    """
    Main daemon class.
    """

    def __init__(self, config=0):
        """
        constructor
        """

        LOG.info('Initializing hdfs-pop server %s.', __file__)

        # reading detailed configurations
        #--------------------------------
        LOG.info('Loading the configuration: %s.'%(os.environ.get('POP_CONFIG')))
        config_file = os.environ.get('POP_CONFIG')
        config = ConfigParser.RawConfigParser()
        config.read(config_file)

        self.namenode_log = config.get('hdfs_pop','namenode_log')

        self.engine_user = config.get('engine','user')
        self.engine_password = config.get('engine','password')
        self.engine_database = config.get('engine','database')

        self.last_update_time = 0

    def run(self):
        """
        Infinite-loop main body of the daemon.
         - execute one pass
         - sleep for specified number of seconds
        """
        LOG.info('Started hdfs-pop daemon.')
        LOG.info('Starting the loop to analyze log files.')
        sleep_time = 60

        while True:

            self._run_one()
            time.sleep(sleep_time)

    def _find_tag(self,tag,line):

        # initialize
        rc = -1
        value = ""
        
        # find the command and source tags in the line
        m = re.findall(r"%s=(\S*)"%tag,line)

        # print if we have something
        if len(m)==1:
            rc = 0
            value = m[0]

        return (rc,value)

    def _run_one(self):
        """
        This is one complete run over the existing logfiles
        Step 1: Find last update of the database
        Step 2: Read logfiles starting ignoring everything before the last update
        Step 3: Parse new information and update the database
                - chronologically go through new transactions
                - for cmd=delete -> remove full access record from db
                - for cmd=open  -> enter file in db, add new access entry
        Step 4: Enter last access stamp
        """

        ## STEP 1

        # make a database interface
        pop_engine = Engine(self.engine_user,self.engine_password,self.engine_database)

        # find the time when the database was last updated
        last_update = pop_engine.get_last_update()

        ## STEP 2

        LOG.info(" Parsing log file: %s"%(self.namenode_log))
        with open(self.namenode_log,"r") as fH:
            data = fH.read()

        ## STEP 3

        # now loop through all log entries
        last_log = datetime.datetime.strptime("2000-01-01 00:00:00,000","%Y-%m-%d %H:%M:%S,%f")
        for line in data.split("\n")[:-1]:        # dropping the last line that could be corrupted

            # grab the time of the entry
            date_string = " ".join(line.split(" ")[0:2])
            try:
                log_time = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S,%f")
            except:
                warn = " WARNING -- datestring corrupt: %s\n    FROM: %s"%(date_string,line)
                LOG.warning(warn)
                continue

            # if this is before the last_update no more action required
            if log_time<last_update:
                continue

            (rc,cmd) = self._find_tag("cmd",line)
            if rc != 0:
                continue

            (rc,src) = self._find_tag("src",line)
            if rc != 0:
                continue

            LOG.debug(" LINE:%s"%(line))
            LOG.debug(" DATE:%s  CMD:%s  SRC:%s"%(str(log_time),cmd,src))

            if    cmd == 'open':
                LOG.info(" Adding Access - DATE:%s  CMD:%s  SRC:%s"%(str(log_time),cmd,src))
                pop_engine.add_open(src,log_time)
            elif  cmd == 'delete':
                LOG.info(" Removing entries - DATE:%s  CMD:%s  SRC:%s"%(str(log_time),cmd,src))
                pop_engine.delete_usage(src)

            # make sure we remember the last log time we see
            if log_time>last_log:
                last_log = log_time

        ## STEP 4

        if last_log>last_update:
            pop_engine.set_last_update(last_log)
                    
        return 0

if __name__ == '__main__':
    pop = hdfs_pop()
    print ' Start running'
    pop.run()
