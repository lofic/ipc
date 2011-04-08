#!/usr/bin/env python
host = 'localhost'

import pika
import sys
import uuid

connection = channel = None

def on_connected(connection):
    connection.channel(on_channel_open)

def on_channel_open(channel_):
    global channel
    channel = channel_
    channel.queue_declare(callback = on_queue_declared, exclusive = True)

def on_queue_declared(frame):
    global queuename
    queuename = frame.method.queue
    channel.basic_consume(handle_delivery, queue = queuename, no_ack = True)
    global corr_id
    corr_id = str(uuid.uuid4())
    response = None
    channel.basic_publish(exchange='', routing_key='rpc_queue',
                          properties = pika.BasicProperties(
                                         reply_to = queuename,
                                         correlation_id = corr_id,
                                         ),
                                   body = str(seqnum))

def handle_delivery(channel, method_frame, header_frame, body):
    if header_frame.correlation_id == corr_id:
        print body 
        connection.close()


if __name__ == '__main__':
    try:
        seqnum = int(sys.argv[1])
    except IndexError,ValueError:
        print >> sys.stderr, "Usage: %s [Fibonacci_seq_num]..." % (sys.argv[0],)
        sys.exit(1)
    parameters = pika.ConnectionParameters(host)
    connection = pika.adapters.SelectConnection(parameters, on_connected)
    connection.ioloop.start()

