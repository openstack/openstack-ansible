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

--------------

#. If using HAProxy, run the playbook to deploy it:

   .. code-block:: shell-session

       # openstack-ansible haproxy-install.yml

.. include:: navigation.txt
