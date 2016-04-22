`Home <index.html>`_ OpenStack-Ansible Installation Guide

Firewall Service (Optional)
---------------------------

The following procedure describes how to modify the
``/etc/openstack_deploy/user_variables.yml`` file to enable FWaaS.

#. Override the default list of Neutron plugins to include
   ``firewall``:

   .. code-block:: yaml

      neutron_plugin_base:
        - firewall
        - ...

#. The complete `neutron_plugin_base`, at the time of this writing, is as follows:

   .. code-block:: yaml

      neutron_plugin_base:
         - router
         - firewall
         - lbaas
         - vpnaas
         - metering
         - qos

#. Execute the Neutron install playbook in order to update the configuration:

   .. code-block:: shell-session

       # cd /opt/openstack-ansible/playbooks
       # openstack-ansible os-neutron-install.yml

#. Execute the Horizon install playbook in order to update the Horizon
   configuration to show the FWaaS panels:

   .. code-block:: shell-session

       # cd /opt/openstack-ansible/playbooks
       # openstack-ansible os-horizon-install.yml

The FWaaS default configuration options may be changed through the
`conf override`_ mechanism using the ``neutron_neutron_conf_overrides``
dict.

.. _conf override: http://docs.openstack.org/developer/openstack-ansible/install-guide/configure-openstack.html

--------------

.. include:: navigation.txt