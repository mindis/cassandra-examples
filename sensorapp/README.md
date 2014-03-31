Simple Time Series Sensor Data in Cassandra with Python and Flask
=================================================================

This application illustrates how to store simple time series data in Cassandra. Examples of time series data includes sensors, machine logs, and tweets. Our application will do two things:

* Store time-stamped sensor data in a Cassandra table
* Provide a simple REST API to interact with the Cassandra cluster

While simple, this application should give you an idea of how to construct more complicated web applications. 

Version
-------

This example was tested against Cassandra version 2.0.6, CQL version 3.1.1, and the DataStax [Python driver](https://github.com/datastax/python-driver).

Getting started
---------------

If you already have access to a Cassandra cluster, you should be able to start running this example application right away. All you have to do is set an environment variable on your client indicating where your cluster is located:

```bash
   $ export BACKEND_STORAGE_IP='mycluster_ip'
```

However, if you don't have access to a Cassandra cluster, you can get started by installing [Ferry](http://ferry.opencore.io). Ferry is an open-source tool that helps developers provision virtual clusters on a local machine. Ferry supports Cassandra (and other "big data" tools) and doesn't require that you actually know how to configure Cassandra to get started. 

Assuming that you are using Ferry, you should run all these commands in a Cassandra client. The first thing to do is install all the prerequisite packages. They can be found in `requirements.txt`. Here's a simple way to do it from the command line using `pip`.

```bash
   $ pip install -r requirements.txt
```

Afterwards, you'll want to set up the Cassandra keyspace and table for our application.

```bash
   $ cqlsh -f createtable.cql
```

After creating the table, you should be able to start the web server by typing:

```bash
   $ python rest.py &
```

Afterwards, insert some data into Cassandra by typing:

```bash
   $ python client.py post 
```

Finally, let's see what data got inserted.

```bash
   $ python client.py fetch  
```

You can filter the results as well. Try:

```bash
   $ python client.py fetch FA-1 sensor-0 2
```

Schema layout
-------------

If you take a peek inside `createtable.cql`, you'll find various CQL commands. CQL is an interface for Cassandra that emulates the feel of SQL. While there are other Cassandra interfaces (such as Thrift), CQL is the preferred method for new applications.

Our schema looks like this: 

```sql
CREATE TABLE sensor_data (
  sensor_id text,
  time timeuuid,
  reading float, 
  PRIMARY KEY(sensor_id, time)
)
```

The sensor values are stored as ``float`` and has an associated timestamp (``timeuuid`` is a timestamp combined with a UUID). Since we'll want to view the sensor data sorted by time, we'll need to use a "compound key" consisting of the sensor ID and timestamp. Basically we're telling Cassandra to first store all the data from a single sensor together on a single node, and then to store the values sorted by time. 

REST API
--------

To demonstrate how a Python application might interact with Cassandra, we've implemented a simple web service using Flask. If you take a peek inside `rest.py`, you'll see a method to insert data and another to fetch data. Inserting data into a Cassandra cluster consists of creating an `INSERT` statement with the values that we want. Here's the relevant section:

```python
query = """INSERT INTO sensor_data 
           (sensor_id, time, reading)
           VALUES (%(sensor_id)s, %(time)s, %(reading)s)"""
values = { 'sensor_id':sensor_id,
           'time': time_uuid.TimeUUID(time]),
           'reading': float(reading) }
session.execute(query, values)
```

This should look pretty familiar to most SQL programmers. Fetching data from a Cassandra cluster is similiar and consists of creating a `SELECT` query. 

REST client
-----------

We've also implemented a small REST client to interact with our server in `client.py`. To insert data into the cluster, it executes an HTTP `post` with a stringified JSON object.

```python
values = {'value': json.dumps( { 'sensor':str(sensor_id),
                                 'time': str(ts),
                                 'reading': sensor_value} ) }
requests.post(REST_SERVER + '/api/sensors', data=values)
```

Similarly, in order to fetch data from the REST server, it executes an HTTP `get` with some parameters to filter the results. 

```python
values = { 'sensor' : sensor, 
           'days'   : days }
res = requests.get(REST_SERVER + '/api/sensors', params=values)
```
