`Home <index.html>`_ OpenStack-Ansible Installation Guide

Availability zones
------------------

Multiple availability zones can be created to manage Block Storage
storage hosts. Edit the
``/etc/openstack_deploy/openstack_user_config.yml`` and
``/etc/openstack_deploy/user_variables.yml`` files to set up
availability zones.

#. For each cinder storage host, configure the availability zone under
   the ``container_vars`` stanza:

   .. code-block:: yaml

       cinder_storage_availability_zone: CINDERAZ

   Replace ``CINDERAZ`` with a suitable name. For example
   ``cinderAZ_2``

#. If more than one availability zone is created, configure the default
   availability zone for all the hosts by creating a
   ``cinder_default_availability_zone`` in your
   ``/etc/openstack_deploy/user_variables.yml``

   .. code-block:: yaml

       cinder_default_availability_zone: CINDERAZ_DEFAULT

   Replace ``CINDERAZ_DEFAULT`` with a suitable name. For example,
   ``cinderAZ_1``. The default availability zone should be the same
   for all cinder hosts.

   If the ``cinder_default_availability_zone`` is not defined, the
   default variable will be used (nova). This could make horizon's
   volume creation fail.

--------------

.. include:: navigation.txt
