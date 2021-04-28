================================================
Using radosgw as a drop-in replacement for Swift
================================================

OpenStack-Ansible gives you the option of deploying radosgw as a
drop-in replacement for native OpenStack Swift.

In particular, the ``ceph-rgw-install.yml`` playbook (which includes
``ceph-rgw-keystone-setup.yml``) will deploy radosgw to any
``ceph-rgw`` hosts, and create a corresponding Keystone
``object-store`` service catalog entry. The service endpoints do
contain the ``AUTH_%(tenant_id)s`` prefix just like in native Swift,
so public read ACLs and temp URLs will work just like they do in
Swift.

By default, OSA enables *only* the Swift API in radosgw.


Adding S3 API support
~~~~~~~~~~~~~~~~~~~~~

You may want to enable the default radosgw S3 API, in addition to the
Swift API. In order to do so, you need to override the
``ceph_conf_overrides_rgw`` variable in ``user_variables.yml``. Below
is an example configuration snippet:

.. note::

   Mentioned below overrides are default ones and will be applied to `ceph-rgw` group

.. literalinclude:: ../../../../inventory/group_vars/ceph-rgw.yml

You may also want to add the ``rgw_dns_name`` option if you want to
enable bucket hostnames with the S3 API.
