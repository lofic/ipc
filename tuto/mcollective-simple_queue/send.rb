#!/usr/bin/ruby

require 'mcollective'

oparser = MCollective::Optionparser.new
options = oparser.parse

config = MCollective::Config.instance

# set the config file with --config at the cmd line
config.loadconfig(options[:config])

client = MCollective::Client.new(config)
client.options = MCollective::Util.default_options

msgpayload = "Louis was here"
message = MCollective::Message.new(msgpayload, nil,
    {:agent => "foo", :type => :direct_request, :collective => "mcollective"})

message.discovered_hosts = ["queuereceiver"]

message.ttl = 1000

client.sendreq(message, nil)
