pop
===

pop is a popularity service which has an engine that agregates file usage data in a database. The
file usage service is running as a system daemon. The implementation here is for a hadoop storage
installation. In principle any source can be used to populate the database. hdfs_pop is using the
logfiles on the namenode of the hadoop storage system to find two tags: cmd=open and cmd=delete. The
open tag will add a file usage to the file_usage table which includes the file_id and the timestamp
when that usage occured. The delete tag will lead to the deletion of all file usage data for the
given file.
