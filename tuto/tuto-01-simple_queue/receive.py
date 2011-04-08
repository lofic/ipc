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
    channel.basic_consume(handle_delivery, queue = 'hello')
    connection.close()

def handle_delivery(channel, method_frame, header_frame, body):
    print "Received %r" % (body,)
    channel.basic_ack(delivery_tag = method_frame.delivery_tag)


if __name__ == '__main__':
    parameters = pika.ConnectionParameters(host)
    connection = pika.adapters.SelectConnection(parameters, on_connected)
    connection.ioloop.start()

