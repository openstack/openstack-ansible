`Home <index.html>`_ OpenStack-Ansible Installation Guide

Adding a compute host
---------------------

Use the following procedure to add a compute host to an operational
cluster.

#. Configure the host as a target host. See `Chapter 4, *Target
   hosts* <ch-hosts-target.html>`_ for more information.

#. Edit the ``/etc/openstack_deploy/openstack_user_config.yml`` file and
   add the host to the ``compute_hosts`` stanza.

   If necessary, also modify the ``used_ips`` stanza.

#. Run the following commands to add the host. Replace
   *``NEW_HOST_NAME``* with the name of the new host.

   .. code-block:: shell-session

       # cd /opt/openstack-ansible/playbooks
       # openstack-ansible setup-everything.yml --limit NEW_HOST_NAME

--------------

.. include:: navigation.txt
