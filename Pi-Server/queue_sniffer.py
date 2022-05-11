from MQ_handler import MQ_handler
import json
import mysql.connector

def write_measurement_to_db(ch, method, properties, body):
    body = json.loads(body)

    messages = body["Sensor values"]
    with open(".config") as json_data_file:
        config = json.load(json_data_file)
            
    # --- Connecting to Database ---
    con = mysql.connector.connect(
        host= config["mysql"]["host"],
        user= config["mysql"]["user"],
        password= config["mysql"]["passwd"],
        database= config["mysql"]["db"]
    )

    cur = con.cursor()
    for msg in messages:
        # Get Id for specific measurement
        select_id = ("SELECT measurement_id FROM measurement_ids WHERE name = %(name)s")
        cur.execute(select_id, msg)

        # Should only return one value. write it to the msg dict.
        for (measurement_id) in cur:    
            msg["id"] = measurement_id[0]

        # Write measurement value to db
        add_measurement =   ("INSERT INTO measurements"
                            "(timestamp, value, measurement_id) "
                            "VALUES (%(timestamp)s, %(value)s, %(id)s)")
        cur.execute(add_measurement, msg)

    # Commit and close connection
    con.commit()
    cur.close()
    con.close()

mq = MQ_handler()
mq.consume("measurements",write_measurement_to_db)