Overview
========

The Juno to Kilo upgrade process contains two major components that make the
upgrade process more complex than previous upgrades.

OpenStack-Ansible was initially based on Rackspace Private Cloud. As such the
original code base (as shown in the Juno branch) contains a number of
references to Rackspace, Rackspace products, and Rackspace naming. These
references have been removed by the community for the release of the Kilo
series.

Because of these changes, the Juno to Kilo upgrade process requires many
adjustments to clean up those references and to ensure that the environment
is prepared for future versions. These steps will ensure that future upgrades
are simpler.
