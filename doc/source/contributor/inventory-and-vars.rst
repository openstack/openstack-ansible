=======================
Inventory and variables
=======================

Our dynamic Inventory
^^^^^^^^^^^^^^^^^^^^^

OpenStack-Ansible ships with its own dynamic inventory. You can
find more explanations on the `inventory`_.

Variable precedence
^^^^^^^^^^^^^^^^^^^

Role defaults
-------------

Every role has a file, ``defaults/main.yml`` which holds the
usual variables overridable by a deployer, like a regular Ansible
role. This defaults are the closest possible to OpenStack standards.

Group vars and host vars
------------------------

OpenStack-Ansible provides safe defaults for deployers in its
group_vars folder. They take care of the wiring between different
roles, like for example storing information on how to reach
RabbitMQ from nova role.

You can override the existing group vars (and host vars) by creating
your own folder in /etc/openstack_deploy/group_vars (and
/etc/openstack_deploy/host_vars respectively).

If you want to change the location of the override folder, you
can adapt your openstack-ansible.rc file, or export
``GROUP_VARS_PATH`` and ``HOST_VARS_PATH`` during your shell session.

Role vars
---------

Because OpenStack-Ansible is following Ansible precedence, every role
``vars/`` will take precedence over group vars. This is intentional.
You should avoid overriding these variables.

User variables
--------------

If you want to override a playbook or a role variable, you can define
the variable you want to override in a
``/etc/openstack_deploy/user_*.yml`` file.

.. _Inventory: inventory.html
