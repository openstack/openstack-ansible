`Home <index.html>`__ OpenStack Ansible Installation Guide

Installing source and dependencies
----------------------------------

Install the source and dependencies for the deployment host.

#. Clone the OSAD repository into the ``/opt/os-ansible-deployment``
   directory:

   .. code-block:: bash

       # git clone -b TAG https://github.com/stackforge/os-ansible-deployment.git /opt/os-ansible-deploymemt
               

   Replace *``TAG``* with the current stable release tag.

#. Change to the ``/opt/os-ansible-deployment`` directory, and run the
   Ansible bootstrap script:

   .. code-block:: bash

       # scripts/bootstrap-ansible.sh

--------------

.. include:: navigation.txt
