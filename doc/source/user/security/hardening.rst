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
      openstack-ansible security-hardening.yml

    # Perform a quick audit by using Ansible's check mode
      openstack-ansible --check security-hardening.yml

For more information about the security configurations, see the
`security hardening role`_ documentation.

.. _security hardening role: https://docs.openstack.org/ansible-hardening/
