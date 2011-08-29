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
#configfile = "/etc/mcollective/server.cfg"
#config.loadconfig(configfile)
config.loadconfig(options[:config])
# Override the mcollective keys to use a new pair specific to the queue
config.pluginconf['ssl_client_private']='/etc/mcollective/ssl/clients/q-private.pem'
config.pluginconf['ssl_client_public']='/etc/mcollective/ssl/clients/q-public.pem'
config.pluginconf['ssl_client_cert_dir']='/etc/mcollective/ssl/clients/'

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


