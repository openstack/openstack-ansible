`Home <index.html>`_ OpenStack-Ansible Installation Guide

Setup a Neutron network for use Ironic
--------------------------------------

In the general case, the Neutron network can be a simple flat network. However,
in a complex case, this can be whatever you need and want. Ensure
you adjust the deployment accordingly. The following is an example:


.. code-block:: bash

    neutron net-create cleaning-net --shared \
                                    --provider:network_type flat \
                                    --provider:physical_network ironic-net

    neutron subnet-create ironic-net 172.19.0.0/22 --name ironic-subnet
                                                   --ip-version=4 \
                                                   --allocation-pool start=172.19.1.100,end=172.19.1.200 \
                                                   --enable-dhcp \
                                                   --dns-nameservers list=true 8.8.4.4 8.8.8.8

