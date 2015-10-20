`Home <index.html>`_ OpenStack-Ansible Installation Guide

Integrate with the Image Service
--------------------------------

Optionally, the images created by the Image Service (glance) can be
stored using Object Storage.

If there is an existing Image Service (glance) backend (for example,
cloud files) but want to add Object Storage (swift) to use as the Image
Service back end, re-add any images from the Image Service after moving
to Object Storage. If the Image Service variables are changed (as
described below) and begin using Object storage, any images in the Image
Service will no longer be available.

**Procedure 5.3. Integrating Object Storage with Image Service**

This procedure requires the following:

-  OSA Kilo (v11)

-  Object Storage v 2.2.0

#. Update the glance options in the
   ``/etc/openstack_deploy/user_variables.yml`` file:

   .. code-block:: yaml

       # Glance Options
       glance_default_store: swift
       glance_swift_store_auth_address: '{{ auth_identity_uri }}'
       glance_swift_store_container: glance_images
       glance_swift_store_endpoint_type: internalURL
       glance_swift_store_key: '{{ glance_service_password }}'
       glance_swift_store_region: RegionOne
       glance_swift_store_user: 'service:glance'


   -  ``glance_default_store``: Set the default store to ``swift``.

   -  ``glance_swift_store_auth_address``: Set to the local
      authentication address using the
      ``'{{ auth_identity_uri }}'`` variable.

   -  ``glance_swift_store_container``: Set the container name.

   -  ``glance_swift_store_endpoint_type``: Set the endpoint type to
      ``internalURL``.

   -  ``glance_swift_store_key``: Set the Image Service password using
      the ``{{ glance_service_password }}`` variable.

   -  ``glance_swift_store_region``: Set the region. The default value
      is ``RegionOne``.

   -  ``glance_swift_store_user``: Set the tenant and user name to
      ``'service:glance'``.

#. Rerun the Image Service (glance) configuration plays.

#. Run the Image Service (glance) playbook:

   .. code-block:: shell-session

       # cd /opt/openstack-ansible/playbooks
       # openstack-ansible os-glance-install.yml --tags "glance-config"

--------------

.. include:: navigation.txt
