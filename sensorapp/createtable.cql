/**
 * A keyspace is analoguous to a schema in a relational database.
 * They contain groups of tables (a.k.a, column families), and most 
 * applications use a single keyspace. 
 *
 * Keyspaces also control the replication policy. There are two elements
 * to this: the "strategy" and "factor". The strategy defines how the
 * replicas get placed within the cluster. The replication factor controls 
 * how many replicas you want.
 **/
CREATE KEYSPACE sensorapp WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };
USE sensorapp;

/**
 * A table in Cassandra is analoguous to a table in a relational database. 
 * Older versions of Cassandra referred to table as "column families". 
 *
 * In our table we want to sort by the timestamp, so we'll need to create
 * a composite key. 
 **/
CREATE TABLE sensor_data (
  sensor_id text,
  time timeuuid,
  reading float, 
  PRIMARY KEY(sensor_id, time)
);
