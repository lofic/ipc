#!/usr/bin/ruby

require 'mcollective'
require 'inifile'

def publish(msg, security, connector, config, queuename)
   target = queuename 
   reqid = Digest::MD5.hexdigest("#{config.identity}-#{Time.now.to_f.to_s}-#{target}")
   req = security.encoderequest(config.identity, target, msg, reqid, {}, "custominventory", "mcollective")

   Timeout.timeout(2) do
      begin
          # Newer stomp rubygem :
          connector.connection.publish(target, req)
      rescue
          # Older stomp rubygem :
          connector.connection.send(target, req)
      end
   end
end

# Kermit parameters
SECTION = 'amqpqueue'
MAINCONF = '/etc/kermit/kermit.cfg'
ini=IniFile.load(MAINCONF, :comment => '#')
params = ini[SECTION]
amqpcfg = params['amqpcfg']
queuename = params['queuename'] 

# default mcollective client options like --config etc will be valid
oparser = MCollective::Optionparser.new
options = oparser.parse
options[:config] = amqpcfg 

config = MCollective::Config.instance
config.loadconfig(options[:config])

security = MCollective::PluginManager["security_plugin"]
security.initiated_by = :client

connector = MCollective::PluginManager["connector_plugin"]
connector.connect

data = "Louis was here"
publish(data, security, connector, config, queuename)
