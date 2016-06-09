`Home <index.html>`_ OpenStack-Ansible Installation Guide

Add to existing deployment
==========================

Complete the following procedure to deploy swift on an
existing deployment.

#. `The section called "Configure and mount storage
   devices" <configure-swift-devices.html>`_

#. `The section called "Configure an Object Storage
   deployment" <configure-swift-config.html>`_

#. Optionally, allow all keystone users to use swift by setting
   ``swift_allow_all_users`` in the ``user_variables.yml`` file to
   ``True``. Any users with the ``_member_`` role (all authorized
   keystone users) can create containers and upload objects
   to swift.

   If this value is ``False``, by default only users with the
   ``admin`` or ``swiftoperator`` role can create containers or
   manage tenants.

   When the backend type for the glance is set to
   ``swift``, glance can access the swift cluster
   regardless of whether this value is ``True`` or ``False``.

#. Run the swift play:

   .. code-block:: shell-session

       # cd /opt/openstack-ansible/playbooks
       # openstack-ansible os-swift-install.yml

--------------

.. include:: navigation.txt
