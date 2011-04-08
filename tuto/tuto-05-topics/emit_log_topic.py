#!/usr/bin/env python
host = 'localhost'

import pika
import sys
import time

connection = channel = None

def on_connected(connection):
    connection.channel(on_channel_open)

def on_channel_open(channel_):
    global channel
    channel = channel_ 
    channel.exchange_declare(exchange = 'topic_logs', durable = True,
                             type = 'topic', callback = on_exch_declared)

def on_exch_declared(frame):
    routing_key = sys.argv[1] if len(sys.argv) > 1 else 'anonymous.info'
    message = ' '.join(sys.argv[2:]) or "Hello World!"
    channel.basic_publish(exchange = 'topic_logs', routing_key = routing_key,
                          body = message)
    connection.close()

if __name__ == '__main__':
    parameters = pika.ConnectionParameters(host)
    connection = pika.adapters.SelectConnection(parameters, on_connected)
    connection.ioloop.start()

