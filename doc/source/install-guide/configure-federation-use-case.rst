`Home <index.html>`__ OpenStack Ansible Installation Guide

Identity Service to Identity Service federation example use-case
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This document describes the configuration steps necessary to reproduce the
federation scenario described below:

* Federate Cloud 1 and Cloud 2.
* Create mappings between Cloud 1 Group A and Cloud 2 Project X and Role R.
* Create mappings between Cloud 1 Group B and Cloud 2 Project Y and Role S.
* Create User U in Cloud 1, assign to Group A.
* Authenticate with Cloud 2 and confirm scope to Role R in Project X.
* Assign User U to Group B, confirm scope to Role S in Project Y.

Keystone identity provider (IdP) configuration
----------------------------------------------

The configuration for the keystone IdP instance is as follows::

    keystone_idp:
      certfile: "/etc/keystone/ssl/idp_signing_cert.pem"
      keyfile: "/etc/keystone/ssl/idp_signing_key.pem"
      self_signed_cert_subject: "/C=US/ST=Texas/L=San Antonio/O=IT/CN={{ external_lb_vip_address }}"
      regen_cert: false
      idp_entity_id: "{{ keystone_service_publicurl_v3 }}/OS-FEDERATION/saml2/idp"
      idp_sso_endpoint: "{{ keystone_service_publicurl_v3 }}/OS-FEDERATION/saml2/sso"
      idp_metadata_path: /etc/keystone/saml2_idp_metadata.xml
      service_providers:
        - id: "cloud2"
          auth_url: https://cloud2.com:5000/v3/OS-FEDERATION/identity_providers/cloud1/protocols/saml2/auth
          sp_url: https://cloud2.com:5000/Shibboleth.sso/SAML2/ECP

In the above example, only the last three lines are specific to a particular
installation, as they reference the service provider cloud (referred to as
"Cloud 2" in the original scenario). In the example, it is assumed that this
cloud is located at https://cloud2.com, and the unique ID for this cloud
is "cloud2".

Also note that in the ``auth_url`` there is a reference to the IdP cloud (or
"Cloud 1"), as known by the service provider (SP). The ID used for the IdP
cloud in this example is "cloud1".

Keystone SP configuration
-------------------------

The configuration for the Keystone SP is more complex, as it needs to define
the remote-to-local user mappings. The complete configuration is as follows::

    keystone_sp:
      cert_duration_years: 5
      trusted_dashboard_list:
        - "https://{{ external_lb_vip_address }}/auth/websso/"
      trusted_idp_list:
        - name: "cloud1"
          entity_ids:
            - 'https://cloud1.com:5000/v3/OS-FEDERATION/saml2/idp'
          metadata_uri: 'https://cloud1.com:5000/v3/OS-FEDERATION/saml2/metadata'
          metadata_file: 'metadata-cloud1.xml'
          metadata_reload: 1800
          federated_identities:
            - domain: Default
              project: X
              role: R
              group: federated_group_1
            - domain: Default
              project: Y
              role: S
              group: federated_group_2
          protocols:
            - name: saml2
              mapping:
                name: cloud1-mapping
                rules:
                  - remote:
                      - any_one_of:
                          - A
                        type: openstack_project
                    local:
                      - group:
                          name: federated_group_1
                          domain:
                            name: Default
                  - remote:
                      - any_one_of:
                          - B
                        type: openstack_project
                    local:
                      - group:
                          name: federated_group_2
                          domain:
                            name: Default
              attributes:
                - name: openstack_user
                  id: openstack_user
                - name: openstack_roles
                  id: openstack_roles
                - name: openstack_project
                  id: openstack_project
                - name: openstack_user_domain
                  id: openstack_user_domain
                - name: openstack_project_domain
                  id: openstack_project_domain

The ``cert_duration_years`` is used for the self-signed certificate used by
Shibboleth. The ``trusted_dashboard_list`` is only necessary if Horizon SSO
login is going to be implemented. When given, it works as a security measure,
as keystone will only redirect to these URLs.

The ``trusted_idp_list`` is where the IdPs known to the SP are configured. In
this example there is only one IdP, the "Cloud 1", which is configured with
the ID "cloud1", matching the reference in the IdP configuration shown in the
previous section.

The ``entity_ids`` is given the unique URL that represents the "Cloud 1" IdP,
which for this example is assumed to be hosted at https://cloud1.com.

The three metadata values that follow configure the access to the IdP
metadata. The ``metadata_file`` needs to be different for each IdP, as this is
a filename in the keystone containers of the SP cloud that will hold cached
metadata for each registered IdP.

The ``federated_identities`` list defines the sets of identities that will be
used for federated users. In this example there are two sets, Project X/Role R
and Project Y/Role S. To keep things organized, a user group is created
for each set.

The ``protocols`` section is where the federation protocols are specified. At
this time the only supported protocol is ``saml2``.

The ``mapping`` dictionary is where the actual assignments of remote to local
users is defined. A keystone mapping is given a ``name`` and a set of
``rules`` that keystone applies to determine how to map a given user. Each
mapping rule has a ``remote`` and a ``local`` component.

The ``remote`` part of the mapping rule specifies the criteria for the remote
user, based on the attributes exposed by the IdP in the SAML2 assertion. The
use case for this scenario calls for mapping users in "Group A" and "Group B",
but the group or groups a user belongs to are not exported in the SAML2
assertion. To make the example work, the groups A and B in the use case have
been assumed to be projects, so there are projects A and B, which are exported
in the assertion under the ``openstack_project`` attribute. The two rules
defined above select the corresponding project using the ``any_one_of``
selector.

The ``local`` part of the mapping rule specifies how keystone should represent
the remote user in the local SP cloud. Since the two federated identities were
configured with their own user group, this part simply maps the user to the
corresponding group, which in turn will expose the correct domain, project and
role. Note that a user name is not specified, so keystone creates an
ephemeral user in the specified group.

The final setting of the configuration defines the SAML2 ``attributes`` that
are exported by the IdP. For a keystone IdP these are the five attributes
shown above. The attributes given in this section are configured into the
Shibboleth service, making them available to use in the mappings.

Reviewing or modifying the configuration with the Openstack client
------------------------------------------------------------------

Use OpenStack command line client to review or make modifications to an
existing federation configuration. The following commands can be used for
the previous configuration.

Service providers on the identity provider
------------------------------------------

To see the list of known SPs::

    $ openstack service provider list
    +--------+---------+-------------+-----------------------------------------------------------------------------------------+
    | ID     | Enabled | Description | Auth URL                                                                                |
    +--------+---------+-------------+-----------------------------------------------------------------------------------------+
    | cloud2 | True    | None        | https://cloud2.com:5000/v3/OS-FEDERATION/identity_providers/cloud1/protocols/saml2/auth |
    +--------+---------+-------------+-----------------------------------------------------------------------------------------+

To view the information for a specific SP::

    $ openstack service provider show cloud2
    +--------------------+----------------------------------------------------------------------------------------------+
    | Field              | Value                                                                                        |
    +--------------------+----------------------------------------------------------------------------------------------+
    | auth_url           | http://cloud2.com:5000/v3/OS-FEDERATION/identity_providers/keystone-idp/protocols/saml2/auth |
    | description        | None                                                                                         |
    | enabled            | True                                                                                         |
    | id                 | cloud2                                                                                       |
    | relay_state_prefix | ss:mem:                                                                                      |
    | sp_url             | http://cloud2.com:5000/Shibboleth.sso/SAML2/ECP                                              |
    +--------------------+----------------------------------------------------------------------------------------------+

To make modifications, the ``set`` command is used. Below are the available
options for this command::

    $ openstack service provider set
    usage: openstack service provider set [-h] [--auth-url <auth-url>]
                                          [--description <description>]
                                          [--service-provider-url <sp-url>]
                                          [--enable | --disable]
                                          <service-provider>

Identity providers on the service provider
------------------------------------------

To see the list of known IdPs::

    $ openstack identity provider list
    +----------------+---------+-------------+
    | ID             | Enabled | Description |
    +----------------+---------+-------------+
    | cloud1         | True    | None        |
    +----------------+---------+-------------+

To view the information for a specific IdP::

    $ openstack identity provider show keystone-idp
    +-------------+--------------------------------------------------------+
    | Field       | Value                                                  |
    +-------------+--------------------------------------------------------+
    | description | None                                                   |
    | enabled     | True                                                   |
    | id          | cloud1                                                 |
    | remote_ids  | [u'http://cloud1.com:5000/v3/OS-FEDERATION/saml2/idp'] |
    +-------------+--------------------------------------------------------+

To make modifications, the ``set`` command is used. Below are the available
options for this command::

    $ openstack identity provider set
    usage: openstack identity provider set [-h]
                                           [--remote-id <remote-id> | --remote-id-file <file-name>]
                                           [--enable | --disable]
                                           <identity-provider>

Federated identities on the service provider
--------------------------------------------

The domain, project, role, group and user entities created for the purpose of
federation are regular keystone entities that can be viewed or modified with
the OpenStack command client. For example::

    $ openstack domain list
    $ openstack project list
    $ openstack role list
    $ openstack group list
    $ openstack user list

When using a domain other than the default, the ``--domain`` option must be
added to all the commands above except the first. The ``set`` option is used
to modify these entities.

Federation mappings
-------------------

To view the list of mappings::

    $ openstack mapping list
    +------------------+
    | ID               |
    +------------------+
    | cloud1-mapping   |
    +------------------+

To view a mapping in detail::

    $ openstack mapping show cloud1-mapping
    +-------+--------------------------------------------------------------------------------------------------------------------------------------------------+
    | Field | Value                                                                                                                                            |
    +-------+--------------------------------------------------------------------------------------------------------------------------------------------------+
    | id    | keystone-idp-mapping-2                                                                                                                           |
    | rules | [{"remote": [{"type": "openstack_project", "any_one_of": ["A"]}], "local": [{"group": {"domain": {"name": "Default"}, "name":                    |
    |       | "federated_group_1"}}]}, {"remote": [{"type": "openstack_project", "any_one_of": ["B"]}], "local": [{"group": {"domain": {"name": "Default"},    |
    |       | "name": "federated_group_2"}}]}]                                                                                                                 |
    +-------+--------------------------------------------------------------------------------------------------------------------------------------------------+

To edit a mapping, use an auxiliary file. Save the JSON mapping shown above
and make the necessary modifications, then use the``set`` command to trigger
an update. For example:

    $ openstack mapping show cloud1-mapping -c rules -f value | python -m json.tool > rules.json
    $ vi rules.json  # <--- make any necessary changes
    $ openstack mapping set cloud1-mapping --rules rules.json

Federation protocols
--------------------

It is also possible to view or change the association between a federation
protocol and a mapping::

    $ openstack federation protocol list --identity-provider keystone-idp
    +-------+----------------+
    | id    | mapping        |
    +-------+----------------+
    | saml2 | cloud1-mapping |
    +-------+----------------+

--------------

.. include:: navigation.txt
