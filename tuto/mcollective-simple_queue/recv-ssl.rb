#!/usr/bin/ruby

# You may need to set ACLs for the resource
# Check :
# rabbitmqctl list_user_permissions -p '/' mcollective 
# rabbitmqctl set_permissions -p '/' mcollective ".*" ".*" ".*"

require 'mcollective'
require 'pp'

source = "/queue/message.example"

oparser = MCollective::Optionparser.new
options = oparser.parse

config = MCollective::Config.instance
config.loadconfig(options[:config])
# We need this to be able to pick the key to decode what's sent : 
config.pluginconf['ssl_client_cert_dir']='/etc/mcollective/ssl/clients/'
# !!!DON'T!!! put the private key used to encode the sent message on this node.
# Only the public key, to decode the message.

security = MCollective::PluginManager["security_plugin"]
security.initiated_by = :node

connector = MCollective::PluginManager["connector_plugin"]
connector.connect
connector.connection.subscribe(source)

loop do
    msg = connector.receive
    msg = security.decodemsg(msg)
    pp msg
end


