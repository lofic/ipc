#!/usr/bin/ruby

require 'mcollective'

def publish(msg, security, connector, config)
   target = "/queue/message.example"
   reqid = Digest::MD5.hexdigest("#{config.identity}-#{Time.now.to_f.to_s}-#{target}")
   if MCollective.version.split('.').first.to_i > 1
     req = security.encoderequest(config.identity, msg, reqid, "", "customqueue", "mcollective")
   else
     req = security.encoderequest(config.identity, target, msg, reqid, {}, "customqueue", "mcollective")
   end

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

# default mcollective client options like --config etc will be valid
oparser = MCollective::Optionparser.new
options = oparser.parse

config = MCollective::Config.instance
# We read client.cfg (readable for a standard user) :
config.loadconfig(options[:config])
# We override the mcollective keys to use a new pair specific to the queue
# !!!!DON'T!!!! really put the q-public.pem in the ssl/clients/ folder on the
# sending nodes. 
# We just need this to send the name of the decoding key to the receiver
config.pluginconf['ssl_client_public']='/etc/mcollective/ssl/clients/q-public.pem'
# This key is used to encode and needed on the nodes in ssl/clients/ :
config.pluginconf['ssl_client_private']='/etc/mcollective/ssl/clients/q-private.pem'
# !!!!DON'T!!!! put the q-private.pem key on the receiver node.

security = MCollective::PluginManager["security_plugin"]
security.initiated_by = :client

connector = MCollective::PluginManager["connector_plugin"]
connector.connect


data = "Louis was here"
publish(data, security, connector, config)

