# Changelog

## 9.0.2 - 2014-11-06

- Increase delay and retries for lxc cache download [#449]
- Updated cinder.conf to allow for AZ setup [#458]
- Create empty 'authorized_keys' file [#478]
- Fix limit_container_types typo [#480]
- Use {{ ansible_fqdn }} for service checks [#452]
- Allow for more galera/mysql tuning [#410,#429]
- Increase ssh timeout in ansible.cfg [#358]
- Updated pip installation/wheel building process
- Created lxc-system-manage script for common operational tasks [#434]
- Added missing comma which caused Kibana dashboard to not load
- Updated rpc_release/maas_repo_version versions [#370]
- Ensure that rsyslog state files are unique [#205]
- Changed release version to match the branch [#421]
- Changed maas_notification_plan to npManaged [#402]
- Added galera alarms [#403]
- Added repo_package variable file to nova-spice-console [#347]
- Resolved issue with neutron HA failover cron clobbering other crons [#383,#378]

## 9.0.1 - 2014-10-17

- Ensure temptest installs a bootable cirros image [#333]
- Reference updated rpc-maas repo tag
- Templated out iscsi options in the cinder.conf [#328]
- AggregateDiskFilter should not be included in Icehouse default filters [#326]
- HAproxy memcached acl line too long on big cluster [#142]
- Set holland backup to minute based on container IP [#136]
- Idempotency for LXC cloning [#312]
- No time units for haproxy timeouts [#320]
- Allow maas agent to create agent token [#263]
- Ensure nova_virt_type default is used [#242]
- Change default threading for logstash [#207]
- Horizon logs not being parsed [#204]
- Swap default/fallback repo urls [#188]
- Add appropriate aggregate filters [#315]
- Adds a simple to use and cron script for python packages [#252]
- Add CDM checks and alarms [#306]
- Change the help URL in Horizon so that it can be overriden [#105]
- Increase haproxy client/server timeouts for galera service [#259]
- Updates to remove uses of ">" that cause errors [#192]
- Fixed an issue where a lookup would fail due to recursive children [#300]
- Create users within tempest tenants [#253]
- Install Tempest in utility container [#227]
- Make container networking timeout slightly less aggressive [#208]
- Add missing dependency [#261]
- Unnecessary rackspace_cloudfiles_tenant_id variable [#281]
- Disable query_cache to reduce deadlocks in Galera [#290]
- Removed unused FWaaS plugin [#196]
- Fix template name ircbalance -> irqbalance [#199]
- IRQbalance needs to have hints ignored [#161]
- Galera Needs to have limits set [#160]
- RabbitMQ needs to have the ulimit set [#159]
- Rabbitmq not clustering correctly when 'rpc' in hostname [#256]
- Add a better check to see if the cinder api is actually up [#261]
- Remove verbose logging from logstash [#206]
- Missing logs on logging server [#130]
- Add limits config to galera [#285]
- Added sane Nova scheduler settings [#156]
- Removed duplicate scheduler_driver from nova.conf
- Changed default hypervisor to KVM [#147]
- Fix heat domain configuration [#195]
- Added check to make sure that the volume group variable exists [#231]
- Changed ansible install from the package name to a URL as a tarball [#148]
- Offline compress CSS and JS files [#176]
- Added heat template for use with RPC9.0.0 and RAX
- Added heat template for use with RPC9.0.0 and OpenStack

## 9.0.0 - 2014-09-25

- Initial Release
