`Home <index.html>`_ OpenStack-Ansible Installation Guide

Running the foundation playbook
-------------------------------

#. Change to the ``/opt/openstack-ansible/playbooks`` directory.

#. Run the host setup playbook, which runs a series of sub-playbooks:

   .. code-block:: bash

       $ openstack-ansible setup-hosts.yml
               

   Confirm satisfactory completion with zero items unreachable or
   failed:

   .. code-block:: bash

       PLAY RECAP ********************************************************************
       ...
       deployment_host                :  ok=18   changed=11   unreachable=0    failed=0

#. If using HAProxy:

   .. note::

     If you plan to run haproxy on multiple hosts, you'll need keepalived
     to make haproxy highly-available. The keepalived role should have
     been downloaded during the bootstrap-ansible stage. If not, you should
     rerun the following command before running the haproxy playbook:

     .. code-block:: shell

        $ ../scripts/bootstrap-ansible.sh

     or

     .. code-block:: shell

        $ ansible-galaxy install -r ../ansible-role-requirements.yml

  Run the playbook to deploy haproxy:

  .. code-block:: bash

     $ openstack-ansible haproxy-install.yml

--------------

.. include:: navigation.txt
