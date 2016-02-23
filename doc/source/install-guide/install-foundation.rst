`Home <index.html>`_ OpenStack-Ansible Installation Guide

Chapter 5. Foundation playbooks
-------------------------------

**Figure 5.1. Installation work flow**

.. image:: figures/workflow-foundationplaybooks.png

The main Ansible foundation playbook prepares the target hosts for
infrastructure and OpenStack services and performs the following
operations:

-  Perform deployment host initial setup

-  Build containers on target hosts

-  Restart containers on target hosts

-  Install common components into containers on target hosts

Running the foundation playbook
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. seealso:: Before continuing, the configuration files may be validated using the
   guidance in "`Checking the integrity of your configuration files`_".

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

        # pushd /opt/openstack-ansible; scripts/bootstrap-ansible.sh; popd

     or

     .. code-block:: shell-session

        # ansible-galaxy install -r ../ansible-role-requirements.yml

  Run the playbook to deploy haproxy:

  .. code-block:: shell-session

     # openstack-ansible haproxy-install.yml


--------------

.. include:: navigation.txt
