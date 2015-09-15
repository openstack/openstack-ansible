`Home <index.html>`_ OpenStack-Ansible Installation Guide

Running the infrastructure playbook
-----------------------------------

#. Change to the ``/opt/openstack-ansible/playbooks`` directory.

#. Run the infrastructure setup playbook, which runs a series of
   sub-playbooks:

   .. code-block:: bash

       $ openstack-ansible setup-infrastructure.yml
               

   Confirm satisfactory completion with zero items unreachable or
   failed:

   .. code-block:: bash

       PLAY RECAP ********************************************************************
       ...
       deployment_host                : ok=27   changed=0    unreachable=0    failed=0

--------------

.. include:: navigation.txt
