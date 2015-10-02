`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the hypervisor (optional)
-------------------------------------

By default, the KVM hypervisor is used. If you are deploying to a host
that does not support KVM hardware acceleration extensions, select a
suitable hypervisor type such as ``qemu`` or ``lxc``. To change the
hypervisor type, uncomment and edit the following line in the
``/etc/openstack_deploy/user_variables.yml`` file:

.. code-block:: yaml

    # nova_virt_type: kvm

--------------

.. include:: navigation.txt
