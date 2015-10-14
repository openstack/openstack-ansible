# neutron-rootwrap command filters for nodes on which neutron is
# expected to control network
#
# This file should be owned by (and only-writeable by) the root user

# format seems to be
# cmd-name: filter-name, raw-command, user, args

[Filters]

# Filters for the dibbler-based reference implementation of the pluggable
# Prefix Delegation driver. Other implementations using an alternative agent
# should include a similar filter in this folder.

# prefix_delegation_agent
dibbler-client: CommandFilter, dibbler-client, root
