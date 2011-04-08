#!/usr/bin/env python
host = 'localhost'

import os
import pika
import subprocess

if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.\n")

connection = channel = None

def on_connected(connection):
    connection.channel(on_channel_open)

def on_channel_open(channel_):
    global channel
    channel = channel_
    proc = subprocess.Popen(['/usr/sbin/rabbitmqctl','-q','list_queues'],
                            shell = False, stdout = subprocess.PIPE)
    for line in proc.stdout.readlines():
        listedqueue=line.strip().split()[0]
        print "Deleting %s" % (listedqueue)
        channel.queue_delete(queue = listedqueue)
    connection.close()

if __name__ == '__main__':
    parameters = pika.ConnectionParameters(host)
    connection = pika.adapters.SelectConnection(parameters, on_connected)
    connection.ioloop.start()

