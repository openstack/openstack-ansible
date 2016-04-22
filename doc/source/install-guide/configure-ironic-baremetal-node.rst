`Home <index.html>`_ OpenStack-Ansible Installation Guide

Deploy a baremetal node kicked with Ironic
------------------------------------------

.. important::

   You will not have access unless you have a key set within Nova before
   your Ironic deployment. If you do not have an ssh key readily
   available, set one up with ``ssh-keygen``.

.. code-block:: bash

    nova keypair-add --pub-key ~/.ssh/id_rsa.pub admin

Now boot a node:

.. code-block:: bash

   nova boot --flavor ${FLAVOR_NAME} --image ${IMAGE_NAME} --key-name admin ${NODE_NAME}

