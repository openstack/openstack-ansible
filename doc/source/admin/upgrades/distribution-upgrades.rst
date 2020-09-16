=====================
Distribution upgrades
=====================

This guide provides information about upgrading from one distribution
release to the next.

.. note::

   The information provided here goes from ubuntu xenial to ubuntu bionic

Introduction
============

From stein, support for xenial is dropped, so rocky is the transition point for
upgrading the ubuntu distribution version from xenial to bionic. The only
supported way for such a transition is a reinstall of the operating system,
then running openstack-ansible to install services on this new host.

Here's a checklist of what to do when upgrading.

Checklist
=========

#. Identifying your "primary" haproxy/galera/rabbitmq/repo infrastructure_host

   In a "simple" 3 _infrastructure_hosts setup, these services/containers
   usually end up being all on the the same host.

   This will be the LAST box you'll want to reinstall.

   #. haproxy/keepalived

       Finding your haproxy/keepalived primary is as easy as

       .. code:: console

          ssh {{ external_lb_vip_address }}

       Or preferably if you've installed haproxy with stats, like so;

       .. code-block:: yaml

          haproxy_stats_enabled: true
          haproxy_stats_bind_address: "{{ external_lb_vip_address }}"

       and can visit https://admin:password@external_lb_vip_address:1936/ and read
       "Statistics Report for pid # on infrastructure_host

   #. repo_container

       Check all your repo_containers and look for /etc/lsyncd/lsyncd.conf.lua

#. Disable your non-primary repo_all-back

   Log into your primary haproxy/keepalived and run something similar to
   .. code:: console

      echo "disable server repo_all-back/<infrahost>_repo_container-<hash>" | socat /var/run/haproxy.stat stdio

   for each repo_container that's non-primary.

   Or if you've enabled haproxy_stats as described above, you can visit
   https://admin:password@external_lb_vip_address:1936/ and select them and
   "Set state to MAINT"

   .. note::

      This is because the lsync process is already running on your primary
      repo_container, and will only send updates of files it receives back to
      your new repo_container. So xenial packages aren't getting updated and
      synced out to your new repo_container. And requests for xenial packages
      could go to this new bionic backend.

      You can optionally solve this by triggering a restart of the lsyncd
      process on the primary repo_container each time the repo_build.yml finishes.

      (Also check that your pypiserver.service is getting refreshed/restarted on
      your new repo_container)

#. Update openstack_deploy/user_variables.yml

   .. code-block:: yaml

      repo_build_global_links_path: "{{ repo_build_base_path }}/links/{{ repo_build_os_distro_version }}"

#. ceph luminous for bionic

   Luminous packages for bionic from ceph.com aren't available, so you'll
   default to getting them from uca, which is using mimic. We fix the pinning
   by altering two places in openstack-ansible/playbooks/ceph-install.yml and
   once in openstack-ansible/playbooks/ceph-rgw-install.yml

   .. code-block:: yaml

      apt_pinned_packages: [{ package: '*', release: "{{ (ansible_distribution_release == 'bionic') | ternary('Ubuntu', 'ceph.com') }}" }]

   This fix was merged in the latest stable/rocky on 2020-03-11.

Actually deploying
==================

#. Reinstall a server that has a repo-container with ubuntu bionic

   You'll want to avoid doing this on your primary.
   Typically an _infrastructure_host, unless you've customized repo-infra_hosts

#. Clearing out stale information

   #. Removing stale ansible-facts

      .. code:: console

         rm /etc/openstack_deploy/ansible-facts/reinstalled_host*

      (* because we're deleting all container facts for the host aswell.)

   #. If rabbitmq container was running on this host

      we forget it by running these commands on another rabbitmq host.

      .. code:: console

         rabbitmqctl cluster_status
         rabbitmqctl forget_cluster_node rabbit@removed_host_rabbitmq_container

#. If it's not a "primary", install everything on the new node

   .. code:: console

      openstack-ansible setup-everything.yml

#. If it IS a "primary", do these steps

   .. code:: console

      openstack-ansible setup-hosts.yml

   Temporarily set your primary-galera in MAINT in haproxy

   .. code:: console

      openstack-ansible galera-install.yml

   You'll get a errors about some haproxy handlers, no need to worry.
   You'll now have mariadb running, but it's not synced info from the
   non-primaries. To fix this we ssh to the primary galera, and restart the
   mariadb.service and verify everything is in order.

   .. code:: console

      systemctl restart mariadb.service
      mysql
      mysql> SHOW STATUS LIKE "wsrep_cluster_%";
      mysql> SHOW DATABASES;

   Everything should be sync'ed and in order now. You can take your
   primary-galera from MAINT to READY

   We can move on to rabbitmq-primary

   .. code:: console

      openstack-ansible rabbitmq-install.yml

   rabbitmq-primary will also be in a weird cluster of it's own state. You fix
   this by doing these commands on it.

   .. code:: console

      rabbitmqctl stop_app
      rabbitmqctl join_cluster rabbit@some_operational_rabbitmq_container
      rabbitmqctl start_app
      rabbitmqctl cluster_status

   Everything should now be in a working state and we can finish it off with

   .. code:: console

      openstack-ansible setup-infrastructure.yml
      setup-openstack.yml
