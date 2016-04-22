`Home <index.html>`_ OpenStack-Ansible Installation Guide

Virtual Private Network Service (Optional)
------------------------------------------

The following procedure describes how to modify the
``/etc/openstack_deploy/user_variables.yml`` file to enable VPNaaS.

#. Override the default list of Neutron plugins to include
   ``vpnaas``:

   .. code-block:: yaml

      neutron_plugin_base:
        - router
        - metering

#. The complete `neutron_plugin_base`, at the time of this writing, is as follows:

   .. code-block:: yaml

      neutron_plugin_base:
         - router
         - metering
         - vpnaas

#. Execute the Neutron install playbook in order to update the configuration:

   .. code-block:: shell-session

       # cd /opt/openstack-ansible/playbooks
       # openstack-ansible os-neutron-install.yml

#. Execute the Horizon install playbook in order to update the Horizon
   configuration to show the VPNaaS panels:

   .. code-block:: shell-session

       # cd /opt/openstack-ansible/playbooks
       # openstack-ansible os-horizon-install.yml

The VPNaaS default configuration options may be changed through the
`conf override`_ mechanism using the ``neutron_neutron_conf_overrides``
dict.

.. _conf override: http://docs.openstack.org/developer/openstack-ansible/install-guide/configure-openstack.html

--------------

.. include:: navigation.txt