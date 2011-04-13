#!/usr/bin/env python

    
import ConfigParser as configparser
import glob
import simplejson as json
from multiprocessing import Process
import os
import pika
import socket
import sys

try:
    from bda import daemon
except:
    print 'Install bda.daemon'
    print 'See http://www.kermit.fr/repo/rpm/el6/x86_64/'
    sys.exit(1)

class MqDispatch(object):
    def __init__(self, config):
        self.connection = None
        self.channel = None
        self.kstplfolder = config.get('provi','kstplfolder')
        self.mqhost = config.get('provi','mqhost')
        self.stdin = self.stdout = self.stderr = '/dev/null'
        self.pidfile = '/tmp/dispatch.pid'

    def run(self):
        parameters = pika.ConnectionParameters(self.mqhost)
        try:
            self.connection = pika.adapters.SelectConnection(parameters,
                                                             self.on_connected)
        except socket.error:
            print "Connection failed to the mq server."
            sys.exit(1)
        self.connection.ioloop.start()

    def on_connected(self, connection):
        connection.channel(self.on_channel_open)

    def on_channel_open(self, chan):
        self.channel = chan 
        self.channel.queue_declare(queue = 'provi_request', durable = True,
                                   callback = self.on_queue_declared)

    def on_queue_declared(self, frame):
        self.channel.basic_qos(prefetch_count = 1)
        # ! bug on pika 0.9.4 -> cf https://github.com/pika/pika/pull/46
        self.channel.basic_consume(self.on_request, queue = 'provi_request')

    def on_request(self, chan, method, props, body):
        """Handle the request in a subprocess"""
        try:
            req = json.loads(body)
        except ValueError:
            req = { 'type' : '', 'parameters' : '' }
        if not req.has_key('type'):
            req['type'] = ''
        if req['type'] == 'kstpllist':
            subp = Process(target=self.handle_request,
                           args = (chan, method, props, body))
            subp.start()
            subp.join() 
        else:
            self.handle_garbage(chan, method, props, body) 

    def handle_request(self, chan, method, props, body):
        tpllist = [ os.path.basename(fic).strip('ks.tpl') for fic in
                      glob.glob(self.kstplfolder+'/*.ks.tpl') ]
        message = json.dumps(tpllist)
        chan.basic_publish(exchange = '', routing_key = props.reply_to,
                         properties = pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                         body = message)
        chan.basic_ack(delivery_tag = method.delivery_tag)

    def handle_garbage(self, chan, method, props, body):
        """Handle garbage requests""" 
        chan.basic_ack(delivery_tag = method.delivery_tag)



if __name__ == '__main__':
    BASEPATH = os.path.dirname(os.path.realpath(__file__))
    CONFIGFILE = '%s/%s' % (BASEPATH,'config.txt')
    config = configparser.RawConfigParser()
    config.read(CONFIGFILE)

    mqd = MqDispatch(config)
    
    dispatchdaemon = daemon.Daemon(mqd)

