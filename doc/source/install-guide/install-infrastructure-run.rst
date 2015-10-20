`Home <index.html>`_ OpenStack-Ansible Installation Guide

Running the infrastructure playbook
-----------------------------------

.. seealso:: Before continuing, the configuration files may be validated using the guidance in "`Checking the integrity of your configuration files`_".

   .. _Checking the integrity of your configuration files: ../install-guide/configure-configurationintegrity.html

#. Change to the ``/opt/openstack-ansible/playbooks`` directory.

#. Run the infrastructure setup playbook, which runs a series of
   sub-playbooks:

   .. code-block:: shell-session

       # openstack-ansible setup-infrastructure.yml

   Confirm satisfactory completion with zero items unreachable or
   failed:

   .. code-block:: shell-session

       PLAY RECAP ********************************************************************
       ...
       deployment_host                : ok=27   changed=0    unreachable=0    failed=0

--------------

.. include:: navigation.txt
