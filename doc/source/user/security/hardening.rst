Apply ansible-hardening
=======================

The ``ansible-hardening`` role is applicable to physical hosts within
an OpenStack-Ansible deployment
that are operating as any type of node, infrastructure or compute. By
default, the role is enabled. You can disable it by changing the value of
the ``apply_security_hardening`` variable in the ``user_variables.yml`` file
to ``false``:

.. code-block:: yaml

    apply_security_hardening: false

You can apply security hardening configurations to an existing environment or
audit an environment by using a playbook supplied with OpenStack-Ansible:

.. code-block:: bash

    # Apply security hardening configurations
      openstack-ansible openstack.osa.security_hardening

    # Perform a quick audit by using Ansible's check mode
      openstack-ansible --check openstack.osa.security_hardening

For more information about the security configurations, see the
`security hardening role`_ documentation.

.. _security hardening role: https://docs.openstack.org/ansible-hardening/latest/

Deployment Host Hardening
-------------------------

You can extend security hardening to the deployment host by defining the
``security_host_group`` variable in your ``openstack_user_variables`` file.
Include ``localhost`` along with your other hosts, like this:

.. code-block:: yaml

   security_host_group: localhost, hosts

Then apply the hardening with:

.. code-block:: shell-session

   openstack-ansible openstack.osa.security_hardening

Or alternatively, you can also supply this variable as extra variable
during runtime, for example:

.. code-block:: shell-session

   openstack-ansible openstack.osa.security_hardening -e security_host_group=localhost

.. warning::

   After applying security hardening, root login via password will be
   disabled. Make sure you configure SSH key authentication or set up
   a non-root user with sudo privileges before applying the changes,
   otherwise you may lose access to the host.

Including the deployment host can be useful to reduce its attack surface
and ensure that the host running OpenStack-Ansible follows the same security
best practices as your other nodes.
