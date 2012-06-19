#!/usr/bin/ruby

require 'mcollective'
require 'pp'

oparser = MCollective::Optionparser.new
options = oparser.parse

config = MCollective::Config.instance

# set the config file with --config at the cmd line
config.loadconfig(options[:config])

# You need to set a special identity
# Because otherwise the mcollectived, when running in direct adressing mode,
# will also get some of these messages
# Can also bet set in the config file with identity = ...
config.instance_variable_set("@identity", "queuereceiver")

security = MCollective::PluginManager["security_plugin"]
security.initiated_by = :node

connector = MCollective::PluginManager["connector_plugin"]
connector.connect

MCollective::Util.subscribe(MCollective::Util.make_subscriptions("foo", :directed))

loop do
  msg = connector.receive
  msg.type = :request
  msg.decode!
  msg.validate
  pp msg.payload[:body]
end
