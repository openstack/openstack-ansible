.. _security_hardening:

==================
Security hardening
==================

OpenStack-Ansible automatically applies host security hardening configurations
using the `openstack-ansible-security`_ role. The role uses a version of the
`Security Technical Implementation Guide (STIG)`_ that has been adapted for
Ubuntu 14.04 and OpenStack.

The role is applicable to physical hosts within an OpenStack-Ansible deployment
that are operating as any type of node, infrastructure or compute. By
default, the role is enabled. You can disable it by changing a variable
within ``user_variables.yml``:

.. code-block:: yaml

    apply_security_hardening: false

When the variable is set to ``true``, the ``setup-hosts.yml`` playbook applies
the role during deployments.

You can apply security configurations to an existing environment or audit
an environment using a playbook supplied with OpenStack-Ansible:

.. code-block:: bash

    # Perform a quick audit using Ansible's check mode
    openstack-ansible --check security-hardening.yml

    # Apply security hardening configurations
    openstack-ansible security-hardening.yml

Refer to the `openstack-ansible-security`_ documentation for more details on
the security configurations. Review the `Configuration`_
section of the openstack-ansible-security documentation to find out how to
fine-tune certain security configurations.

.. _openstack-ansible-security: http://docs.openstack.org/developer/openstack-ansible-security/
.. _Security Technical Implementation Guide (STIG): https://en.wikipedia.org/wiki/Security_Technical_Implementation_Guide
.. _Configuration: http://docs.openstack.org/developer/openstack-ansible-security/configuration.html
.. _Appendix H: ../install-guide/app-custom-layouts.html
