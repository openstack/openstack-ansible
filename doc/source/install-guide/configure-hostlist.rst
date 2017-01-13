`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring target hosts
========================

Modify the ``/etc/openstack_deploy/openstack_user_config.yml`` file to
configure the target hosts.

Do not assign the same IP address to different target hostnames.
Unexpected results may occur. Each IP address and hostname must be a
matching pair. To use the same host in multiple roles, for example
infrastructure and networking, specify the same hostname and IP in each
section.

Use short hostnames rather than fully-qualified domain names (FQDN) to
prevent length limitation issues with LXC and SSH. For example, a
suitable short hostname for a compute host might be:
``123456-Compute001``.

Unless otherwise stated, replace ``*_IP_ADDRESS`` with the IP address of
the ``br-mgmt`` container management bridge on each target host.

#. Configure a list containing at least three infrastructure target
   hosts in the ``shared-infra_hosts`` section:

   .. code-block:: yaml

      shared-infra_hosts:
        infra01:
          ip: INFRA01_IP_ADDRESS
        infra02:
          ip: INFRA02_IP_ADDRESS
        infra03:
          ip: INFRA03_IP_ADDRESS
        infra04: ...

#. Configure a list containing at least two infrastructure target
   hosts in the ``os-infra_hosts`` section (you can reuse
   previous hosts as long as their name and ip is consistent):

   .. code-block:: yaml

      os-infra_hosts:
        infra01:
          ip: INFRA01_IP_ADDRESS
        infra02:
          ip: INFRA02_IP_ADDRESS
        infra03:
          ip: INFRA03_IP_ADDRESS
        infra04: ...

#. Configure a list of at least one keystone target host in the
   ``identity_hosts`` section:

   .. code-block:: yaml

      identity_hosts:
        infra1:
          ip: IDENTITY01_IP_ADDRESS
        infra2: ...

#. Configure a list containing at least one network target host in the
   ``network_hosts`` section:

   .. code-block:: yaml

      network_hosts:
        network01:
          ip: NETWORK01_IP_ADDRESS
        network02: ...

   Providing more than one network host in the ``network_hosts`` block will
   enable `L3HA support using VRRP`_ in the ``neutron-agent`` containers.

.. _L3HA support using VRRP: http://docs.openstack.org/liberty/networking-guide/scenario-l3ha-lb.html

#. Configure a list containing at least one compute target host in the
   ``compute_hosts`` section:

   .. code-block:: yaml

      compute_hosts:
        compute001:
          ip: COMPUTE001_IP_ADDRESS
        compute002: ...

#. Configure a list containing at least one logging target host in the
   ``log_hosts`` section:

   .. code-block:: yaml

      log_hosts:
        logging01:
          ip: LOGGER1_IP_ADDRESS
        logging02: ...

#. Configure a list containing at least one repository target host in the
   ``repo-infra_hosts`` section:

   .. code-block:: yaml

      repo-infra_hosts:
        repo01:
          ip: REPO01_IP_ADDRESS
        repo02:
          ip: REPO02_IP_ADDRESS
        repo03:
          ip: REPO03_IP_ADDRESS
        repo04: ...

   The repository typically resides on one or more infrastructure hosts.

#. Configure a list containing at least one optional storage host in the
   ``storage_hosts`` section:

   .. code-block:: yaml

      storage_hosts:
        storage01:
          ip: STORAGE01_IP_ADDRESS
        storage02: ...

   Each storage host requires additional configuration to define the back end
   driver.

   The default configuration includes an optional storage host. To
   install without storage hosts, comment out the stanza beginning with
   the *storage_hosts:* line.

--------------

.. include:: navigation.txt
