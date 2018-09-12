Firewalls
=========


OpenStack-Ansible does not configure firewalling for its
infrastructure. It is up to the deployer to define the perimeter
and its firewalling configuration.

By default, OpenStack-Ansible relies on Ansible SSH connections,
and needs the TCP port 22 to be opened on all hosts
internally.

For more information on generic OpenStack firewalling, see the
`Firewalls and default ports <https://docs.openstack.org/install-guide/firewalls-default-ports.html>`_

You can find in each of the role's respective documentatione, the
default variables for the ports used within the scope of the role.
Reviewing the documentation allow you to find the variable names
if you want to use a different port.

.. note:: OpenStack-Ansible's group vars conveniently expose the vars outside of the
   `role scope <https://github.com/openstack/openstack-ansible/blob/master/playbooks/inventory/group_vars/all.yml>`_
   in case you are relying on the OpenStack-Ansible groups to
   configure your firewall.

Finding ports for your external load balancer
---------------------------------------------

As explained in the previous section, you can find (in each role
documentation) the default variables used for the public
interface endpoint ports.

For example, the
`os_glance documentation <https://docs.openstack.org/openstack-ansible-os_glance/latest/#default-variables>`_
lists the variable ``glance_service_publicuri``. This contains
the port used for the reaching the service externally. In
this example, it is equal to to ``glance_service_port``, whose
value is 9292.

As a hint, you could find the whole list of public URI defaults
by executing the following:

.. code::

   cd /etc/ansible/roles
   grep -R -e publicuri -e port *

.. note::

   `Haproxy <https://github.com/openstack/openstack-ansible/blob/master/playbooks/vars/configs/haproxy_config.yml>`_
   can be configured with OpenStack-Ansible.
   The automatically generated ``/etc/haproxy/haproxy.cfg`` file have
   enough information on the ports to open for your environment.

