`Home <index.html>`_ OpenStack-Ansible Installation Guide

Installing source and dependencies
----------------------------------

Install the source and dependencies for the deployment host.

#. Clone the OSA repository into the ``/opt/openstack-ansible``
   directory:

   .. code-block:: shell-session

       # git clone -b TAG https://github.com/openstack/openstack-ansible.git /opt/openstack-ansible

   Replace *``TAG``* with the current stable release tag.

#. Change to the ``/opt/openstack-ansible`` directory, and run the
   Ansible bootstrap script:

   .. code-block:: shell-session

       # scripts/bootstrap-ansible.sh

--------------

.. include:: navigation.txt
