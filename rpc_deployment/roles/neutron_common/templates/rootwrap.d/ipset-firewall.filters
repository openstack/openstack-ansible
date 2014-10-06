# neutron-rootwrap command filters for nodes on which neutron is
# expected to control network
#
# This file should be owned by (and only-writeable by) the root user

# format seems to be
# cmd-name: filter-name, raw-command, user, args

[Filters]
# neutron/agent/linux/iptables_firewall.py
#   "ipset", "-A", ...
ipset: CommandFilter, ipset, root
