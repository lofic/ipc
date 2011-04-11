#!/usr/bin/env python
host = 'localhost'

import pika
import sys

connection = channel = None

def on_connected(connection):
    connection.channel(on_channel_open)

def on_channel_open(channel_):
    global channel
    channel = channel_ 
    channel.exchange_declare(exchange = 'logs', durable = True, type = 'fanout',
                             callback = on_exch_declared)

def on_exch_declared(frame):
    message = ' '.join(sys.argv[1:]) or "info: Hello World!"
    for i in range(10): 
        channel.basic_publish(exchange = 'logs', routing_key = '',
                              body = message)
    connection.close()

if __name__ == '__main__':
    parameters = pika.ConnectionParameters(host)
    connection = pika.adapters.SelectConnection(parameters, on_connected)
    connection.ioloop.start()

