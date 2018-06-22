pop
===

pop is a popularity service which has an engine that agregates file usage data in a database. The
file usage service is running as a system daemon. Any source for file usage can be used to populate
the database. Depending on the filesystem you are working with different implementations could be
useful. As we work with a hadoop implementation the first implementation in this repository is
called hdfs_pop.

**hdfs_pop** is using the logfiles on the namenode of the hadoop storage system to find two tags:
cmd=open and cmd=delete. The open tag will add a file usage to the file_usage table which includes
the file_id and the timestamp when that usage occured. The delete tag will lead to the deletion of
all file usage data for the given file.

The package also has a client which can be used to query the database to present the present file
usage situtation on the system.
