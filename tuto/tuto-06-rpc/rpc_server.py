#!/usr/bin/env python
host = 'localhost'

import pika

connection = channel = None

def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n-1) + fib(n-2)

def on_connected(connection):
    connection.channel(on_channel_open)

def on_channel_open(channel_):
    global channel
    channel = channel_ 
    channel.queue_declare(queue = 'rpc_queue', durable = True,
                          callback = on_queue_declared)

def on_queue_declared(frame):
    channel.basic_qos(prefetch_count = 1)
    # ! bug on pika 0.9.4 -> cf https://github.com/pika/pika/pull/46
    channel.basic_consume(on_request, queue = 'rpc_queue')

def on_request(ch, method, props, body):
    n = int(body)
    print "fib(%s)"  % (n,)
    response = fib(n)

    ch.basic_publish(exchange = '', routing_key = props.reply_to,
                     properties = pika.BasicProperties(correlation_id = \
                                                     props.correlation_id),
                     body = str(response))
    ch.basic_ack(delivery_tag = method.delivery_tag)


if __name__ == '__main__':
    parameters = pika.ConnectionParameters(host)
    connection = pika.adapters.SelectConnection(parameters, on_connected)
    connection.ioloop.start()

