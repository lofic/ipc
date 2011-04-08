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
    channel.exchange_declare(exchange = 'topic_logs', durable = True,
                             type = 'topic', callback = on_exch_declared)

def on_exch_declared(frame):
    channel.queue_declare(callback = on_queue_declared, exclusive = True)

def on_queue_declared(frame):
    global queuename
    queuename = frame.method.queue
    for binding_key in binding_keys:
        channel.queue_bind(exchange = 'topic_logs', queue = queuename,
                           callback = on_queue_bind, routing_key = binding_key)

def on_queue_bind(frame):
    channel.basic_consume(handle_delivery, queue = queuename, no_ack = True)

def handle_delivery(channel, method_frame, header_frame, body):
    print "Received %r:%r" % (method_frame.routing_key,body,)


if __name__ == '__main__':
    binding_keys = sys.argv[1:]
    if not binding_keys:
        print >> sys.stderr, "Usage: %s [binding_key]..." % (sys.argv[0],)
        sys.exit(1)

    parameters = pika.ConnectionParameters(host)
    connection = pika.adapters.SelectConnection(parameters, on_connected)
    connection.ioloop.start()

