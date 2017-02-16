====================================
Appendix H: Ceph-Ansible integration
====================================

OpenStack-Ansible allows `Ceph storage <https://ceph.com>`_ cluster integration
using the roles maintained by the `Ceph-Ansible`_ project>. Deployers can
enable the ``ceph-install`` playbook by adding hosts to the
``ceph-mon_hosts`` and ``ceph-osd_hosts`` groups in
``openstack_user_config.yml``, and then configuring `Ceph-Ansible specific vars
<https://github.com/ceph/ceph-ansible/blob/master/group_vars/all.yml.sample>`_
in the OpenStack-Ansible ``user_variables.yml`` file.

.. warning::

   Ceph-Ansible integration in OpenStack-Ansible should be considered
   experimental and for testing purposes only.

.. _Ceph-Ansible: https://github.com/ceph/ceph-ansible/
