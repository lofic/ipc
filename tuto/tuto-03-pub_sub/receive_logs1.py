#!/usr/bin/env python
host = 'localhost'

import pika

connection = channel = None

def on_connected(connection):
    connection.channel(on_channel_open)

def on_channel_open(channel_):
    global channel
    channel = channel_
    channel.exchange_declare(exchange = 'logs', durable = True, type = 'fanout',
                             callback = on_exch_declared)

def on_exch_declared(frame):
    channel.queue_declare(callback = on_queue_declared, exclusive = True)

def on_queue_declared(frame):
    global queuename
    queuename = frame.method.queue
    channel.queue_bind(exchange = 'logs', queue = queuename,
                       callback = on_queue_bind)

def on_queue_bind(frame):
    channel.basic_consume(handle_delivery, queue = queuename, no_ack = True)

def handle_delivery(channel, method_frame, header_frame, body):
    print "Received %r" % (body,)


if __name__ == '__main__':
    parameters = pika.ConnectionParameters(host)
    connection = pika.adapters.SelectConnection(parameters, on_connected)
    connection.ioloop.start()

