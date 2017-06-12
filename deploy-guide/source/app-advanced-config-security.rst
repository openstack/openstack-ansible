.. _security_hardening:

==================
Security hardening
==================

OpenStack-Ansible automatically applies host security hardening configurations
by using the `ansible-hardening`_ role. The role uses a version of the
`Security Technical Implementation Guide (STIG)`_ that has been adapted for
Ubuntu 14.04 and OpenStack.

The role is applicable to physical hosts within an OpenStack-Ansible deployment
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
`OpenStack-Ansible host security`_ hardening documentation.

.. _ansible-hardening: http://docs.openstack.org/developer/ansible-hardening/
.. _Security Technical Implementation Guide (STIG): https://en.wikipedia.org/wiki/Security_Technical_Implementation_Guide
.. _OpenStack-Ansible host security: http://docs.openstack.org/developer/ansible-hardening/
