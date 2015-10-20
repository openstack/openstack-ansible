`Home <index.html>`__ OpenStack Ansible Installation Guide

Configure Identity Service (keystone) Domain-Project-Group-Role mappings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following is an example service provider (SP) mapping configuration
for an ADFS identity provider (IdP):

.. code-block:: yaml

      federated_identities:
        - domain: Default
          project: fedproject
          group: fedgroup
          role: _member_

Each IdP trusted by an SP must have the following configuration:

#. ``project``: The project which federated users will have access to.
   If the project does not already exist then it is created in the
   domain with the name specified by ``domain``.

#. ``group``: The Identity (keystone) group to which the federated users
   will belong. If the group does not already exist then it is created in
   the domain with the name specified by ``domain``.

#. ``role``: The role which federated users will assume in that project.
   If the role does not already exist, it is created.

#. ``domain``: The domain in which the ``project`` lives, and in
   which the role is assigned. If the domain does not already exist,
   it will be created.

With the above information, Ansible implements the equivalent of the
following OpenStack CLI commands:

.. code-block:: shell-session

  # if the domain does not already exist
  openstack domain create Default

  # if the group does not already exist
  openstack group create fedgroup --domain Default

  # if the role does not already exist
  openstack role create _member_

  # if the project does not already exist
  openstack project create --domain Default fedproject

  # map the role to the project and user group in the domain
  openstack role add --project fedproject --group fedgroup _member_

If the deployer wants to add more mappings, additional options can be added to
the list, for example:

.. code-block:: yaml

      federated_identities:
        - domain: Default
          project: fedproject
          group: fedgroup
          role: _member_
        - domain: Default
          project: fedproject2
          group: fedgroup2
          role: _member_

Identity Service federation attribute mapping
---------------------------------------------

Attribute mapping adds a set of rules to map federation attributes to keystone
users and/or groups. An IdP has exactly one mapping specified per
protocol.

Mapping objects can be used multiple times by different combinations of
IdP and protocol.

The details of how the mapping engine works, the schema and various rule
examples are in the `keystone developer documentation <http://docs.openstack.org/developer/keystone/mapping_combinations.html>`_.

Consider an example SP attribute mapping configuration for an ADFS IdP:

.. code-block:: yaml

      mapping:
        name: adfs-IdP-mapping
        rules:
          - remote:
              - type: upn
            local:
              - group:
                  name: fedgroup
                  domain:
                    name: Default
              - user:
                  name: '{0}'
      attributes:
        - name: 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn'
          id: upn

Each IdP for an SP needs to be set up with a mapping. This tells the SP how
to interpret the attributes provided to the SP from the IdP.

In this particular case the IdP is publishing the ``upn`` attribute. As this
is not in the standard Shibboleth attribute attribute map (see
``/etc/shibboleth/attribute-map.xml`` in the keystone containers), this IdP
has been configured with the extra mapping through the ``attributes``
dictionary.

The ``mapping`` dictionary is a yaml representation very similar to the
keystone mapping property which Ansible uploads. The above mapping
produces the following in keystone.

.. code-block:: shell-session

  root@aio1_keystone_container-783aa4c0:~# openstack mapping list
  +------------------+
  | ID               |
  +------------------+
  | adfs-IdP-mapping |
  +------------------+

  root@aio1_keystone_container-783aa4c0:~# openstack mapping show adfs-IdP-mapping
  +-------+---------------------------------------------------------------------------------------------------------------------------------------+
  | Field | Value                                                                                                                                 |
  +-------+---------------------------------------------------------------------------------------------------------------------------------------+
  | id    | adfs-IdP-mapping                                                                                                                      |
  | rules | [{"remote": [{"type": "upn"}], "local": [{"group": {"domain": {"name": "Default"}, "name": "fedgroup"}}, {"user": {"name": "{0}"}}]}] |
  +-------+---------------------------------------------------------------------------------------------------------------------------------------+

  root@aio1_keystone_container-783aa4c0:~# openstack mapping show adfs-IdP-mapping | awk -F\| '/rules/ {print $3}' | python -mjson.tool
  [
      {
          "remote": [
              {
                  "type": "upn"
              }
          ],
          "local": [
              {
                  "group": {
                      "domain": {
                          "name": "Default"
                      },
                      "name": "fedgroup"
                  }
              },
              {
                  "user": {
                      "name": "{0}"
                  }
              }
          ]
      }
  ]

The interpretation of the above mapping rule is that any federated user
authenticated by the IdP is mapped to an ``ephemeral`` (non-existant) user in
keystone. The user is a member of a group named ``fedgroup``, which in turn is
in a domain called ``Default``. The user's ID and Name (federation always uses
the same value for both properties) for all OpenStack services will be
the value of ``upn``.


--------------

.. include:: navigation.txt
