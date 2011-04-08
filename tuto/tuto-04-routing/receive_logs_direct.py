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
    channel.exchange_declare(exchange = 'direct_logs', durable = True, type = 'direct',
                             callback = on_exch_declared)

def on_exch_declared(frame):
    channel.queue_declare(callback = on_queue_declared, exclusive = True)

def on_queue_declared(frame):
    global queuename
    queuename = frame.method.queue
    for severity in severities:
        channel.queue_bind(exchange = 'direct_logs', queue = queuename,
                           callback = on_queue_bind, routing_key = severity)

def on_queue_bind(frame):
    channel.basic_consume(handle_delivery, queue = queuename, no_ack = True)

def handle_delivery(channel, method_frame, header_frame, body):
    print "Received %r" % (body,)


if __name__ == '__main__':
    severities = sys.argv[1:]
    if not severities:
        print >> sys.stderr, "Usage: %s [info] [warning] [error]" % \
                             (sys.argv[0],)
        sys.exit(1)

    parameters = pika.ConnectionParameters(host)
    connection = pika.adapters.SelectConnection(parameters, on_connected)
    connection.ioloop.start()

