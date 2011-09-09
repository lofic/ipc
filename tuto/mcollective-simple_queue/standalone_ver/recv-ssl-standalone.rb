#!/usr/bin/ruby

# You may need to set ACLs for the resource
# Check :
# rabbitmqctl list_user_permissions -p '/' mcollective 
# rabbitmqctl set_permissions -p '/' mcollective ".*" ".*" ".*"

require 'mcollective'
require 'inifile'
require 'pp'

# Kermit parameters
SECTION = 'amqpqueue'
MAINCONF = '/etc/kermit/kermit.cfg'
ini=IniFile.load(MAINCONF, :comment => '#')
params = ini[SECTION]
amqpcfg = params['amqpcfg']
source = params['queuename']

oparser = MCollective::Optionparser.new
options = oparser.parse
options[:config] = amqpcfg 

config = MCollective::Config.instance
config.loadconfig(options[:config])

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


