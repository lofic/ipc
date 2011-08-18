#!/usr/bin/ruby

require 'mcollective'
require 'json'

def publish(msg, security, connector, config)
   target = "/queue/message.example"
   reqid = Digest::MD5.hexdigest("#{config.identity}-#{Time.now.to_f.to_s}-#{target}")
   req = security.encoderequest(config.identity, target, msg, reqid, {}, "custominventory", "mcollective")

   Timeout.timeout(2) do
      # Newer stomp rubygem :
      # connector.connection.publish(target, req)
      # Older stomp rubygem :
      connector.connection.send(target, req)
   end
end

# default mcollective client options like --config etc will be valid
oparser = MCollective::Optionparser.new
options = oparser.parse

config = MCollective::Config.instance
config.loadconfig(options[:config])

security = MCollective::PluginManager["security_plugin"]
security.initiated_by = :client

connector = MCollective::PluginManager["connector_plugin"]
connector.connect


data = "Louis was here"
publish(data, security, connector, config)
