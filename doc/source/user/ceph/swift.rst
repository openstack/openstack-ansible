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

.. code-block:: yaml

    ceph_conf_overrides_rgw:
      "client.rgw.{{ hostvars[inventory_hostname]['ansible_hostname'] }}":
        # OpenStack integration with Keystone
        rgw_keystone_url: "{{ keystone_service_adminuri }}"
        rgw_keystone_api_version: 3
        rgw_keystone_admin_user: "{{ radosgw_admin_user }}"
        rgw_keystone_admin_password: "{{ radosgw_admin_password }}"
        rgw_keystone_admin_tenant: "{{ radosgw_admin_tenant }}"
        rgw_keystone_admin_domain: default
        rgw_keystone_accepted_roles: 'member, _member_, admin, swiftoperator'
        rgw_keystone_implicit_tenants: 'true'
        rgw_swift_account_in_url: true
        rgw_swift_versioning_enabled: 'true'
        # Add S3 support, in addition to Swift
        rgw_enable_apis: 'swift, s3'
        rgw_s3_auth_use_keystone: 'true'

You may also want to add the ``rgw_dns_name`` option if you want to
enable bucket hostnames with the S3 API.
