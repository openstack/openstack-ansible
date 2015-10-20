`Home <index.html>`_ OpenStack-Ansible Installation Guide

Add to existing deployment
--------------------------

Complete the following procedure to deploy Object Storage on an
existing deployment.

#. `the section called "Configure and mount storage
   devices" <configure-swift-devices.html>`_

#. `the section called "Configure an Object Storage
   deployment" <configure-swift-config.html>`_

#. Optionally, allow all Identity users to use Object Storage by setting
   ``swift_allow_all_users`` in the ``user_variables.yml`` file to
   ``True``. Any users with the ``_member_`` role (all authorized
   Identity (keystone) users) can create containers and upload objects
   to Object Storage.

   If this value is ``False``, then by default, only users with the
   admin or swiftoperator role are allowed to create containers or
   manage tenants.

   When the backend type for the Image Service (glance) is set to
   ``swift``, the Image Service can access the Object Storage cluster
   regardless of whether this value is ``True`` or ``False``.

#. Run the Object Storage play:

   .. code-block:: shell-session

       # cd /opt/openstack-ansible/playbooks
       # openstack-ansible os-swift-install.yml

--------------

.. include:: navigation.txt
