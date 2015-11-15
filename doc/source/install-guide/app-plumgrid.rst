`Home <index.html>`__ OpenStack Ansible Installation Guide

Appendix E. Using PLUMgrid Neutron Plugin
-----------------------------------------

Installing Source and Host Networking
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Clone the PLUMgrid ansible repository into the ``/opt`` directory:

   .. code-block:: shell-session

       # git clone -b TAG https://github.com/plumgrid/plumgrid-ansible.git /opt

   Replace *``TAG``* with the current stable release tag.

#. PLUMgrid will take over networking for the entire cluster; therefore the
   bridges br-vxlan and br-vlan will only need to be present to avoid
   relevant containers from erroring out on infra hosts. They do not
   need to be attached to any host interface or a valid network.

#. PLUMgrid requires two networks, a Management and a Fabric network.
   Management is typically shared via the standard br-mgmt and Fabric
   must be specified in the PLUMgrid configuration file described below.
   Furthermore the Fabric interface must be untagged and unbridged.

Neutron Configurations
~~~~~~~~~~~~~~~~~~~~~~

To setup the neutron configuration to install PLUMgrid as the
core neutron plugin, create a user space variable file
``/etc/openstack_deploy/user_pg_neutron.yml`` and insert the following
parameters:

#. Set the ``neutron_plugin_type`` parameter to ``plumgrid`` in this file:

   .. code-block:: yaml

      # Neutron Plugins
      neutron_plugin_type: plumgrid

#. Also in the same file, disable the installation of all neutron-agents
   in the ``neutron_services`` dictionary, by setting their ``service_en``
   keys to ``False``

   .. code-block:: yaml

      # Neutron Services
      neutron_services:
       neutron-dhcp-agent:
         service_name: neutron-dhcp-agent
         service_en: False
         service_conf: dhcp_agent.ini
         service_group: neutron_agent
         service_rootwrap: rootwrap.d/dhcp.filters
         config_options: --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/dhcp_agent.ini
         config_overrides: "{{ neutron_dhcp_agent_ini_overrides }}"
         config_type: "ini"
       neutron-linuxbridge-agent:
         service_name: neutron-linuxbridge-agent
         service_en: False
         service_conf: plugins/ml2/ml2_conf.ini
         service_group: neutron_linuxbridge_agent
         service_rootwrap: rootwrap.d/linuxbridge-plugin.filters
         config_options: --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini
         config_overrides: "{{ neutron_ml2_conf_ini_overrides }}"
         config_type: "ini"
       neutron-metadata-agent:
         service_name: neutron-metadata-agent
         service_en: False
         service_conf: metadata_agent.ini
         service_group: neutron_agent
         config_options: --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/metadata_agent.ini
         config_overrides: "{{ neutron_metadata_agent_ini_overrides }}"
         config_type: "ini"
       neutron-metering-agent:
         service_name: neutron-metering-agent
         service_en: False
         service_conf: metering_agent.ini
         service_group: neutron_agent
         config_options: --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/metering_agent.ini
         config_overrides: "{{ neutron_metering_agent_ini_overrides }}"
         config_type: "ini"
       neutron-l3-agent:
         service_name: neutron-l3-agent
         service_en: False
         service_conf: l3_agent.ini
         service_group: neutron_agent
         service_rootwrap: rootwrap.d/l3.filters
         config_options: --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/l3_agent.ini
         config_overrides: "{{ neutron_l3_agent_ini_overrides }}"
         config_type: "ini"
       neutron-lbaas-agent:
         service_name: neutron-lbaas-agent
         service_en: False
         service_conf: lbaas_agent.ini
         service_group: neutron_agent
         service_rootwrap: rootwrap.d/lbaas-haproxy.filters
         config_options: --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/lbaas_agent.ini
         config_overrides: "{{ neutron_lbaas_agent_ini_overrides }}"
         config_type: "ini"
       neutron-server:
         service_name: neutron-server
         service_en: True
         service_group: neutron_server
         config_options: "--config-file /etc/neutron/neutron.conf --config-file /etc/neutron/{{ neutron_plugins[neutron_plugin_type].plugin_ini }}"


PLUMgrid Cofigurations
~~~~~~~~~~~~~~~~~~~~~~

On the Deployment Host create a PLUMgrid user variables file, using the sample in
``../playbooks/plumgrid-ansible/etc/user_pg_vars.yml.example`` and place it under
``/etc/openstack_deploy/``. The following paremeters must be configured:

#. Replace ``PG_REPO_HOST`` with a valid repo URL hosting PLUMgrid
   packages.

   .. code-block:: yaml

      plumgrid_repo: PG_REPO_HOST

#. Replace ``INFRA_IPs`` with comma seperated Infrastructure Node IPs and
   ``PG_VIP`` with an anallocated IP on the management network, this will
   be used to access the PLUMgrid UI.

   .. code-block:: yaml

      plumgrid_ip: INFRA_IPs
      pg_vip: PG_VIP

#. Replace ``FABRIC_IFC`` with the name of the interface that will be used
   for PLUMgrid Fabric. [Note: PLUMgrid Fabric must be an untagged unbridged
   raw inteface such as eth0]

   .. code-block:: yaml

      fabric_interface: FABRIC_IFC

#. To override the default interface names with another name for any
   particular node fill in the ``fabric_ifc_override`` and ``mgmt_override``
   dicts with node ``hostname: interface_name`` as shown in the example file.

#. Obtain a PLUMgrid License file, rename to ``pg_license`` and place it under
   ``/var/lib/plumgrid/pg_license`` on the Deployment Host.

Gateway Hosts
~~~~~~~~~~~~~

PLUMgrid enabled OpenStack clusters contain one or more Gateway Nodes
that are used for providing connectivity with external resources such as
external networks (Internet), bare-metal servers or network service
appliances. In addition to the Management and Fabric networks required
by PLUMgrid nodes, Gateways require dedicated external interfaces referred
to as gateway_devs in the confgiuration files.

#. To add Gateways Hosts, add a ``gateway_hosts`` section to
   ``/etc/openstack_deploy/openstack_user_config.yml`` as shown below:

   .. code-block:: yaml

      gateway_hosts:
        gateway1:
          ip: GW01_IP_ADDRESS
        gateway2:
          ip: GW02_IP_ADDRESS

   Replace ``*_IP_ADDRESS`` with the IP address of the ``br-mgmt`` container management
   bridge on each Gateway host.

#. Also add a ``gateway_hosts`` section to the end of the PLUMgrid ``user_pg_vars.yml``
   file described in the section above. This must contain hostnames and gateway_dev
   names for each Gateway in the cluster.

   .. code-block:: yaml

      gateway_hosts:
       - hostname: gateway1
         gateway_devs:
         - eth3
         - eth4

Installation
~~~~~~~~~~~~

#. Run the PLUMgrid playbooks with (do this before the openstack-setup.yml
   playbook is run):

.. code-block:: yaml

   cd /opt/plumgrid-ansible
   openstack-ansible plumgrid_playbooks/plumgrid_all.yml

Note: Contact PLUMgrid for an Installation Pack info@plumgrid.com
(includes full/trial license, packages, deployment documentation and
automation scripts for the entire workflow described above)

--------------

.. include:: navigation.txt

