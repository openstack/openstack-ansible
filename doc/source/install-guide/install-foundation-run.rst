`Home <index.html>`_ OpenStack-Ansible Installation Guide

Running the foundation playbook
-------------------------------

.. seealso:: Before continuing, the configuration files may be validated using the guidance in "`Checking the integrity of your configuration files`_".

   .. _Checking the integrity of your configuration files: ../install-guide/configure-configurationintegrity.html

#. Change to the ``/opt/openstack-ansible/playbooks`` directory.

#. Run the host setup playbook, which runs a series of sub-playbooks:

   .. code-block:: shell-session

       # openstack-ansible setup-hosts.yml

   Confirm satisfactory completion with zero items unreachable or
   failed:

   .. code-block:: shell-session

       PLAY RECAP ********************************************************************
       ...
       deployment_host                :  ok=18   changed=11   unreachable=0    failed=0

#. If using HAProxy:

   .. note::

     If you plan to run haproxy on multiple hosts, you'll need keepalived
     to make haproxy highly-available. The keepalived role should have
     been downloaded during the bootstrap-ansible stage. If not, you should
     rerun the following command before running the haproxy playbook:

     .. code-block:: shell-session

        # ../scripts/bootstrap-ansible.sh

     or

     .. code-block:: shell-session

        # ansible-galaxy install -r ../ansible-role-requirements.yml

  Run the playbook to deploy haproxy:

  .. code-block:: shell-session

     # openstack-ansible haproxy-install.yml

--------------

.. include:: navigation.txt
