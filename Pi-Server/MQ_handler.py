#!/usr/bin/env python3
from msilib.schema import Error
import pika,sys,time
import json
import datetime
import logging
from os.path import dirname, join

class MQ_handler:

    def __init__(self):
        current_dir = dirname(__file__)
        file_path = join(current_dir, "./.config")

        with open(file_path) as json_data_file:
            self.config = json.load(json_data_file)

        logging.basicConfig(level = self.config["logging"]["level"], filename = self.config["logging"]["filename"],
                          format = "%(asctime)s | %(name)s | %(levelname)s | %(funcName)s | %(message)s")
        self.logger = logging.getLogger(__name__)

    def consume(self,queue,callbackfunc):
        credentials = pika.PlainCredentials(self.config["RabbitMQ"]["user"], self.config["RabbitMQ"]["passwd"])
        parameters = pika.ConnectionParameters(self.config["RabbitMQ"]["host"],
                                                self.config["RabbitMQ"]["port"],
                                                '/',
                                                credentials)       
        
        try:
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.queue_declare(queue=queue,
                                        durable=True, #Declare that the queue is durable, I only use durable queues
                                        passive=True  #Check that the queue exists
                                        )
                
            channel.basic_consume(queue=queue,
                                auto_ack=True,
                                on_message_callback=callbackfunc)
            
            channel.start_consuming()
        except Exception as e:
            print(f"Could not consume messages from queue {queue}")

    def produce(self,queue,msg):
            credentials = pika.PlainCredentials(self.config["RabbitMQ"]["user"], self.config["RabbitMQ"]["passwd"])
            parameters = pika.ConnectionParameters(self.config["RabbitMQ"]["host"],
                                            self.config["RabbitMQ"]["port"],
                                            '/',
                                            credentials)

            try:
                connection = pika.BlockingConnection(parameters)
                channel = connection.channel()
                channel.queue_declare(  queue=queue,
                                        durable=True, #Declare that the queue is durable, I only use durable queues
                                        passive=True  #Check that the queue exists
                                        )
                channel.basic_publish(  exchange='',
                                        routing_key=queue,
                                        body=msg
                                        )
                connection.close()
                return True
            except Exception as e:
                return False

def main():
    mq = MQ_handler()
    
    msg = {
            "name": "Air pressure",
            "timestamp": "2022-05-04 12:00:00",
            "value": 1019.5,
            "parameter_key": None,
            "unit": "hPa"}
    r = mq.produce("measurements",json.dumps(msg))

    def callback(ch, method, properties, body):
        print("Received %r" % body)
    mq.consume("meaggsurements",callback)
    

if __name__ == '__main__':
    main()