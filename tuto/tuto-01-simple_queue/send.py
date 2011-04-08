#!/usr/bin/env python
host = 'localhost'

import pika

connection = channel = None

def on_connected(connection):
    connection.channel(on_channel_open)

def on_channel_open(channel_):
    global channel
    channel = channel_ 
    channel.queue_declare(queue = 'hello', durable = True,
                          callback = on_queue_declared)

def on_queue_declared(frame):
    message = 'Hello World !'
    channel.basic_publish(exchange = '', routing_key = 'hello', body = message)
    connection.close()

if __name__ == '__main__':
    parameters = pika.ConnectionParameters(host)
    connection = pika.adapters.SelectConnection(parameters, on_connected)
    connection.ioloop.start()

