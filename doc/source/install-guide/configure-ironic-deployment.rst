`Home <index.html>`_ OpenStack-Ansible Installation Guide

OpenStack-Ansible deployment
----------------------------

#. Modify the environment files and force ``nova-compute`` to run from
   within a container:

   .. code-block:: bash

      sed -i '/is_metal.*/d' /etc/openstack_deploy/env.d/nova.yml

