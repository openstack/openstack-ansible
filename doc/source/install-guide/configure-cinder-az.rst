`Home <index.html>`__ OpenStack Ansible Installation Guide

Availability zones
------------------

Multiple availability zones can be created to manage Block Storage
storage hosts. Edit the
``/etc/openstack_deploy/openstack_user_config.yml`` file to set up
availability zones.

#. For each cinder storage host, configure the availability zone under
   the ``container_vars`` stanza:

   .. code-block:: yaml

       cinder_storage_availability_zone: CINDERAZ

   Replace *``CINDERAZ``* with a suitable name. For example
   *``cinderAZ_2``*

#. If more than one availability zone is created, configure the default
   availability zone for scheduling volume creation:

   .. code-block:: yaml

       cinder_default_availability_zone: CINDERAZ_DEFAULT

   Replace *``CINDERAZ_DEFAULT``* with a suitable name. For example,
   *``cinderAZ_1``*. The default availability zone should be the same
   for all cinder storage hosts.

   If the ``cinder_default_availability_zone`` is not defined, the
   default variable will be used.

--------------

.. include:: navigation.txt
