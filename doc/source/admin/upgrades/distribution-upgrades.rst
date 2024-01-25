=====================
Distribution upgrades
=====================

This guide provides information about upgrading from one distribution
release to the next.

.. note::

   This guide was written when upgrading from Ubuntu Bionic to Focal during the
   Victoria release cycle.

Introduction
============

OpenStack Ansible supports operating system distribution upgrades during
specific release cycles. These can be observed by consulting the operating
system compatibility matrix, and identifying where two versions of the same
operating system are supported.

Upgrades should be performed in the order specified in this guide to minimise
the risk of service interruptions. Upgrades must also be carried out by
performing a fresh installation of the target system's operating system, before
running openstack-ansible to install services on this host.

Ordering
========

This guide includes a suggested order for carrying out upgrades. This may need
to be adapted dependent on the extent to which you have customised your
OpenStack Ansible deployment.

Critically, it is important to consider when you upgrade 'repo'
hosts/containers. At least one 'repo' host should be upgraded before you
upgrade any API hosts/containers. The last 'repo' host to be upgraded should be
the 'primary', and should not be carried out until after the final service
which does not support '--limit' is upgraded.

If this order is adapted, it will be necessary to restore some files to the
'repo' host from a backup part-way through the process. This will be necessary
if no 'repo' hosts remain which run the older operating system version, which
prevents older packages from being built.

Beyond these requirements, a suggested order for upgrades is a follows:

#. Infrastructure services (Galera, RabbitMQ, APIs, HAProxy)

   In all cases, secondary or backup instances should be upgraded first

#. Compute nodes

#. Network nodes

Pre-Requisites
==============

*  Ensure that all hosts in your target deployment have been installed and
   configured using a matching version of OpenStack Ansible. Ideally perform a
   minor upgrade to the latest version of the OpenStack release cycle which you
   are currently running first in order to reduce the risk of encountering
   bugs.

*  Check any OpenStack Ansible variables which you customise to ensure that
   they take into account the new and old operating system version (for example
   custom package repositories and version pinning).

*  Perform backups of critical data, in particular the Galera database in case
   of any failures. It is also recommended to back up the '/var/www/repo'
   directory on the primary 'repo' host in case it needs to be restored
   mid-upgrade.

*  Identify your 'primary' HAProxy/Galera/RabbitMQ/repo infrastructure host

   In a simple 3 infrastructure hosts setup, these services/containers
   usually end up being all on the the same host.

   The 'primary' will be the LAST box you'll want to reinstall.

   *  HAProxy/keepalived

      Finding your HAProxy/keepalived primary is as easy as

      .. code:: console

         ssh {{ external_lb_vip_address }}

      Or preferably if you've installed HAProxy with stats, like so;

      .. code-block:: yaml

         haproxy_stats_enabled: true
         haproxy_stats_bind_address: "{{ external_lb_vip_address }}"

      and can visit https://admin:password@external_lb_vip_address:1936/ and read
      'Statistics Report for pid # on infrastructure_host'

Warnings
========

*  During the upgrade process, some OpenStack services cannot be deployed by
   using Ansible's '--limit'. As such, it will be necessary to deploy some
   services to mixed operating system versions at the same time.

   The following services are known to lack support for '--limit':

   * RabbitMQ
   * Repo Server
   * Keystone

*  In the same way as OpenStack Ansible major (and some minor) upgrades, there
   will be brief interruptions to the entire Galera and RabbitMQ clusters
   during the upgrade which will result in brief service interruptions.

*  When taking down 'memcached' instances for upgrades you may encounter
   performance issues with the APIs.

Deploying Infrastructure Hosts
==============================

#. Drain RabbitMQ connections (optional)

   In order to cleanly hand over connections from one member of the RabbitMQ
   cluster to another, the instance being reinstalled should be drained.
   This can be achieved by running the following from the instance to be
   reinstalled and waiting for the RabbitMQ admin interface to indicate that
   socket descriptors have reduced to zero.

   .. code:: console

      rabbitmq-upgrade drain

#. Disable HAProxy back ends (optional)

   If you wish to minimise error states in HAProxy, services on hosts which are
   being reinstalled can be set in maintenance mode (MAINT).

   Log into your primary HAProxy/keepalived and run something similar to

   .. code:: console

      echo "disable server repo_all-back/<infrahost>_repo_container-<hash>" | socat /var/run/haproxy.stat stdio

   for each API or service instance you wish to disable.

   You can also use a playbook from `OPS repository`_ like this:

   .. code:: console

      openstack-ansible set-haproxy-backends-state.yml -e hostname=<infrahost> -e backend_state=disabled

   Or if you've enabled haproxy_stats as described above, you can visit
   https://admin:password@external_lb_vip_address:1936/ and select them and
   'Set state to MAINT'

#. Reinstall an infrastructure host's operating system

   As noted above, this should be carried out for non-primaries first, ideally
   starting with a 'repo' host.

#. Clearing out stale information

   #. Removing stale ansible-facts

      .. code:: console

         rm /etc/openstack_deploy/ansible-facts/reinstalled_host*

      (* because we're deleting all container facts for the host as well.)

   #. If RabbitMQ was running on this host

      We forget it by running these commands on another RabbitMQ host.

      .. code:: console

         rabbitmqctl cluster_status
         rabbitmqctl forget_cluster_node rabbit@removed_host_rabbitmq_container

#. Do generic preparation of reinstalled host

   .. code:: console

      openstack-ansible setup-hosts.yml --limit localhost,reinstalled_host*

#. This step should be executed when you are re-configuring one of haproxy
   hosts

   Since configuration of haproxy backends happens during individual service
   provisioning, we need to ensure that all backends are configured before
   enabling keepalived to select this host.

   Commands below will configure all required backends on haproxy nodes:

   .. code:: console

      openstack-ansible haproxy-install.yml --limit localhost,reinstalled_host --skip-tags keepalived
      openstack-ansible repo-install.yml --tags haproxy-service-config
      openstack-ansible galera-install.yml --tags haproxy-service-config
      openstack-ansible rabbitmq-install.yml --tags haproxy-service-config
      openstack-ansible setup-openstack.yml --tags haproxy-service-config

   Once this is done, you can deploy keepalived again:

   .. code:: console

      openstack-ansible haproxy-install.yml --tags keepalived --limit localhost,reinstalled_host

   After that you might want to ensure that "local" backends remain disabled.
   You can also use a playbook from `OPS repository`_ for this:

   .. code:: console

      openstack-ansible set-haproxy-backends-state.yml -e hostname=<infrahost> -e backend_state=disabled --limit reinstalled_host

#. If it is NOT a 'primary', install everything on the new host

   .. code:: console

      openstack-ansible setup-infrastructure.yml --limit localhost,repo_all,rabbitmq_all,reinstalled_host*
      openstack-ansible setup-openstack.yml --limit localhost,keystone_all,reinstalled_host*

   (* because we need to include containers in the limit)

#. If it IS a 'primary', do these steps

   #. Temporarily set your primary Galera in MAINT in HAProxy.

      In order to prevent role from making your primary Galera
      as UP in haproxy, create an empty file ``/var/tmp/clustercheck.disabled``
      . You can do this with ad-hoc:

      .. code:: console

         cd /opt/openstack-ansible
         ansible -m file -a "path=/var/tmp/clustercheck.disabled state=touch" 'reinstalled-host*:&galera_all'

      Once it's done you can run playbook to install MariaDB to the destination

      .. code:: console

         openstack-ansible galera-install.yml --limit localhost,reinstalled_host* -e galera_server_bootstrap_node="{{ groups['galera_all'][-1] }}"

      You'll now have mariadb running, and it should be synced with
      non-primaries.

      To check that verify MariaDB cluster status by executing from
      host running primary MariaDB following command:

      .. code:: console

         mysql -e 'SHOW STATUS LIKE "wsrep_cluster_%";'


      In case node is not getting synced you might need to restart the
      mariadb.service and verify everything is in order.

      .. code:: console

         systemctl restart mariadb.service
         mysql
         mysql> SHOW STATUS LIKE "wsrep_cluster_%";
         mysql> SHOW DATABASES;

      Once MariaDB cluster is healthy you can remove the file that disables
      backend from being used by HAProxy.

      .. code:: console

         ansible -m file -a "path=/var/tmp/clustercheck.disabled state=absent" 'reinstalled-host_containers:&galera_all'

   #. We can move on to RabbitMQ primary

      .. code:: console

         openstack-ansible rabbitmq-install.yml -e rabbitmq_primary_cluster_node="{{ hostvars[groups['rabbitmq_all'][-1]]['ansible_facts']['hostname'] }}"

   #. Everything should now be in a working state and we can finish it off with

      .. code:: console

         openstack-ansible setup-infrastructure.yml --limit localhost,repo_all,rabbitmq_all,reinstalled_host*
         openstack-ansible setup-openstack.yml --limit localhost,keystone_all,reinstalled_host*

#. Adjust HAProxy status

   If HAProxy was set into MAINT mode, this can now be removed for services
   which have been restored.

   For the 'repo' host, it is important that the freshly installed hosts are
   set to READY in HAProxy, and any which remain on the old operating system
   are set to 'MAINT'.

   You can also use a playbook from `OPS repository`_ to re-enable all backends from the host:

   .. code:: console

      openstack-ansible set-haproxy-backends-state.yml -e hostname=<infrahost> -e backend_state=enabled


Deploying Compute & Network Hosts
=================================

#. Disable the hypervisor service on compute hosts and migrate any VMs to
   another available hypervisor.

#. Reinstall a host's operating system

#. Clear out stale ansible-facts

   .. code:: console

      rm /etc/openstack_deploy/ansible-facts/reinstalled_host*

   (* because we're deleting all container facts for the host as well.)

#. Execute the following:

   .. code:: console

      openstack-ansible setup-hosts.yml --limit localhost,reinstalled_host*
      openstack-ansible setup-infrastructure.yml --limit localhost,reinstalled_host*
      openstack-ansible setup-openstack.yml --limit localhost,reinstalled_host*

   (* because we need to include containers in the limit)

.. note::

   During this upgrade cycle it was noted that network nodes required a restart
   to bring some tenant interfaces online after running setup-openstack.
   Additionally, BGP speakers (used for IPv6) had to be re-initialised from the
   command line. These steps were necessary before reinstalling further network
   nodes to prevent HA Router interruptions.

.. _OPS repository: https://opendev.org/openstack/openstack-ansible-ops/src/branch/master/ansible_tools/playbooks/set-haproxy-backends-state.yml
