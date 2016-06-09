`Home <index.html>`__ OpenStack-Ansible Installation Guide

=========================================
Appendix E: Using PLUMgrid Neutron plugin
=========================================

Installing source and host networking
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Clone the PLUMgrid ansible repository under the ``/opt/`` directory:

   .. code-block:: shell-session

       # git clone -b TAG https://github.com/plumgrid/plumgrid-ansible.git /opt/plumgrid-ansible

   Replace *``TAG``* with the current stable release tag.

#. PLUMgrid will take over networking for the entire cluster. The
   bridges ``br-vxlan`` and ``br-vlan`` only need to be present to avoid
   relevant containers from erroring out on infra hosts. They do not
   need to be attached to any host interface or a valid network.

#. PLUMgrid requires two networks: a `Management` and a `Fabric` network.
   Management is typically shared via the standard ``br-mgmt`` and Fabric
   must be specified in the PLUMgrid configuration file described below.
   The Fabric interface must be untagged and unbridged.

Neutron configurations
~~~~~~~~~~~~~~~~~~~~~~

To setup the neutron configuration to install PLUMgrid as the
core neutron plugin, create a user space variable file
``/etc/openstack_deploy/user_pg_neutron.yml`` and insert the following
parameters.

#. Set the ``neutron_plugin_type`` parameter to ``plumgrid``:

   .. code-block:: yaml

      # Neutron Plugins
      neutron_plugin_type: plumgrid

#. In the same file, disable the installation of unnecessary ``neutron-agents``
   in the ``neutron_services`` dictionary, by setting their ``service_en``
   parameters to ``False``:

   .. code-block:: yaml

         neutron_metering: False
         neutron_l3: False
         neutron_lbaas: False
         neutron_lbaasv2: False
         neutron_vpnaas: False


PLUMgrid configurations
~~~~~~~~~~~~~~~~~~~~~~~

On the deployment host, create a PLUMgrid user variables file using the sample in
``/opt/plumgrid-ansible/etc/user_pg_vars.yml.example`` and copy it to
``/etc/openstack_deploy/user_pg_vars.yml``. You must configure the
following parameters.

#. Replace ``PG_REPO_HOST`` with a valid repo URL hosting PLUMgrid
   packages:

   .. code-block:: yaml

      plumgrid_repo: PG_REPO_HOST

#. Replace ``INFRA_IPs`` with comma separated Infrastructure Node IPs and
   ``PG_VIP`` with an unallocated IP on the management network. This will
   be used to access the PLUMgrid UI:

   .. code-block:: yaml

      plumgrid_ip: INFRA_IPs
      pg_vip: PG_VIP

#. Replace ``FABRIC_IFC`` with the name of the interface that will be used
   for PLUMgrid Fabric. 
   
   .. note::
   
      PLUMgrid Fabric must be an untagged unbridged raw interface such as ``eth0``.

   .. code-block:: yaml

      fabric_interface: FABRIC_IFC

#. Fill in the ``fabric_ifc_override`` and ``mgmt_override`` dicts with
   node ``hostname: interface_name`` to override the default interface
   names.

#. Obtain a PLUMgrid License file, rename to ``pg_license`` and place it under
   ``/var/lib/plumgrid/pg_license`` on the deployment host.

Gateway Hosts
~~~~~~~~~~~~~

PLUMgrid-enabled OpenStack clusters contain one or more gateway nodes
that are used for providing connectivity with external resources, such as
external networks, bare-metal servers, or network service
appliances. In addition to the `Management` and `Fabric` networks required
by PLUMgrid nodes, gateways require dedicated external interfaces referred
to as ``gateway_devs`` in the configuration files.

#. Add a ``gateway_hosts`` section to
   ``/etc/openstack_deploy/openstack_user_config.yml``:

   .. code-block:: yaml

      gateway_hosts:
        gateway1:
          ip: GW01_IP_ADDRESS
        gateway2:
          ip: GW02_IP_ADDRESS

   Replace ``*_IP_ADDRESS`` with the IP address of the ``br-mgmt`` container management
   bridge on each Gateway host.

#. Add a ``gateway_hosts`` section to the end of the PLUMgrid ``user_pg_vars.yml``
   file:
   
   .. note::
      
      This must contain hostnames and ``gateway_dev`` names for each
      gateway in the cluster.

   .. code-block:: yaml

      gateway_hosts:
       - hostname: gateway1
         gateway_devs:
         - eth3
         - eth4

Installation
~~~~~~~~~~~~

#. Run the PLUMgrid playbooks (do this before the ``openstack-setup.yml``
   playbook is run):

   .. code-block:: shell-session

       # cd /opt/plumgrid-ansible/plumgrid_playbooks
       # openstack-ansible plumgrid_all.yml

.. note::

   Contact PLUMgrid for an Installation Pack: info@plumgrid.com
   This includes a full trial commercial license, packages, deployment documentation,
   and automation scripts for the entire workflow described above.

--------------

.. include:: navigation.txt
