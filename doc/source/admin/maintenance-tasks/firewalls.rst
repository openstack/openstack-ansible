Firewalls
=========

OpenStack-Ansible does not configure firewalls for its infrastructure. It is
up to the deployer to define the perimeter and its firewall configuration.

By default, OpenStack-Ansible relies on Ansible SSH connections, and needs
the TCP port 22 to be opened on all hosts internally.

For more information on generic OpenStack firewall configuration, see the
`Firewalls and default ports <https://docs.openstack.org/install-guide/firewalls-default-ports.html>`_

In each of the role's respective documentatione you can find the default
variables for the ports used within the scope of the role. Reviewing the
documentation allow you to find the variable names if you want to use a
different port.

.. note:: OpenStack-Ansible group vars conveniently expose the vars outside of the
   `role scope <https://opendev.org/openstack/openstack-ansible/src/inventory/group_vars/all/all.yml>`_
   in case you are relying on the OpenStack-Ansible groups to
   configure your firewall.

Finding ports for your external load balancer
---------------------------------------------

As explained in the previous section, you can find (in each roles
documentation) the default variables used for the public interface endpoint
ports.

For example, the
`os_glance documentation <https://docs.openstack.org/openstack-ansible-os_glance/latest/#default-variables>`_
lists the variable ``glance_service_publicuri``. This contains
the port used for the reaching the service externally. In
this example, it is equal to ``glance_service_port``, whose
value is 9292.

As a hint, you could find the list of all public URI defaults by executing
the following:

.. code::

   cd /etc/ansible/roles
   grep -R -e publicuri -e port *

.. note::

   `HAProxy <https://opendev.org/openstack/openstack-ansible/src/commit/6520d0bb2c689ed7caa5df581be6a966133cdce0/inventory/group_vars/haproxy/haproxy.yml>`_
   can be configured with OpenStack-Ansible.
   The automatically generated ``/etc/haproxy/haproxy.cfg`` file have
   enough information on the ports to open for your environment.
