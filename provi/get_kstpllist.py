#!/usr/bin/env python
import ConfigParser as configparser
import os
import simplejson as json
import pika
import socket
import sys
import uuid

class Request(object):
    """Defines a class 'Request', to handle requests and request attributes."""
    def __init__(self, confighandler, service):
        """Sets the initial values of some request attributes."""
        self.service = service
        self.mqhost = confighandler.get(service,'mqhost')
        self.timeout =  confighandler.getint(service,'timeout')
        self.status = 'new'
        self.result = None


class MqRequest(object):
    def __init__(self, req ):
        self.connection = None
        self.channel = None
        self.queuename = None
        self.corr_id = None
        self.req = req

    def connect(self):
        parameters = pika.ConnectionParameters(self.req.mqhost)
        try:
            self.connection = pika.adapters.SelectConnection(parameters,
                                                             self.on_connected)
        except socket.error:
            print "Connection failed to the mq server."
            sys.exit(1)
        self.connection.add_timeout(self.req.timeout, self.on_timeout)
        self.connection.ioloop.start()

    def on_connected(self, connection):
        connection.channel(self.on_channel_open)

    def on_channel_open(self, chan):
        self.channel = chan
        self.channel.queue_declare(callback = self.on_queue_declared,
                                   exclusive = True)

    def on_queue_declared(self, frame):
        self.queuename = frame.method.queue
        self.channel.basic_consume(self.handle_delivery,
                                   queue = self.queuename, no_ack = True)
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='', routing_key=self.req.key,
                                   properties = pika.BasicProperties(
                                            reply_to = self.queuename,
                                            correlation_id = self.corr_id,),
                                   body = json.dumps(
                                            {'type' : self.req.type, 
                                            'parameters': self.req.parameters}))

    def handle_delivery(self, channel, method_frame, header_frame, body):
        if header_frame.correlation_id == self.corr_id:
            self.req.result = json.loads(body) 
            self.req.status = 'ok'
            self.connection.close()

    def on_timeout(self):
        self.req.status = 'timeout'
        self.connection.close()


if __name__ == '__main__':
    BASEPATH = os.path.dirname(os.path.realpath(__file__))
    CONFIGFILE = '%s/%s' % (BASEPATH,'config.txt')
    config = configparser.RawConfigParser()
    config.read(CONFIGFILE)

    request = Request(config,'provi')
    request.key = 'provi_request'
    request.type = 'kstpllist'
    request.parameters = None

    mqreq = MqRequest(request)
    mqreq.connect()

    result = { 'type' : mqreq.req.type,
               'status' : mqreq.req.status , 
               'result' : mqreq.req.result }

    print json.dumps(result, indent=4)

