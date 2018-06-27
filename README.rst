pop
===

pop is a popularity service which has an engine that agregates file usage data in a database. The
file usage service is running as a system daemon. Any source for file usage can be used to populate
the database. Depending on the filesystem you are working with different implementations could be
useful.

Namespaces
----------

pop allows to define namespaces using regular expressions. When file usage is recorded, the accessed
file names are analyzed and namespaces are generated automatically according to the given patterns
and stored in the database. The recorded namespaces are kept and changing namespaces during the
operations need to be carefully tested to avoid clashes that can occur. So keep it saimple and think
:-)

Implementation
--------------

As we work with a hadoop implementation the first implementation in this repository is called
hdfs_pop.

**hdfs_pop** is using the logfiles on the namenode of the hadoop storage system by scanning the
lates version for information. The basic operation is to find two tags: cmd=open and cmd=delete.

The *open* tag will add a file usage to the 'file_usage' table which includes the file_id and the
timestamp when that usage occured. The *delete* tag will lead to the deletion of all file usage data
for the given file.

To ensure that freshly copied file will show some usage and the time of arrival can be deduced the
completion of the file copy will count as one usage and added as an entry into the 'file_usage'
table of the database. This is based on finding the *completedFile* tag.

Client
------

The package also has a client which can be used to query the database to present the present file
usage situtation on the system. Use popc or for the local MIT implementation: popc-mit. This will
assume a scheme for how the dataset name is encoded.
