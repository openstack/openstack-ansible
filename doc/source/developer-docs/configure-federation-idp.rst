`Home <index.html>`__ OpenStack-Ansible Installation Guide

Configure Identity service (keystone) as a federated identity provider
======================================================================

The Identity Provider (IdP) configuration for keystone provides a
dictionary attribute with the key ``keystone_idp``. The following is a
complete example:

.. code::

    keystone_idp:
      certfile: "/etc/keystone/ssl/idp_signing_cert.pem"
      keyfile: "/etc/keystone/ssl/idp_signing_key.pem"
      self_signed_cert_subject: "/C=US/ST=Texas/L=San Antonio/O=IT/CN={{ external_lb_vip_address }}"
      regen_cert: false
      idp_entity_id: "{{ keystone_service_publicurl_v3 }}/OS-FEDERATION/saml2/idp"
      idp_sso_endpoint: "{{ keystone_service_publicurl_v3 }}/OS-FEDERATION/saml2/sso"
      idp_metadata_path: /etc/keystone/saml2_idp_metadata.xml
      service_providers:
        - id: "sp_1"
          auth_url: https://example.com:5000/v3/OS-FEDERATION/identity_providers/idp/protocols/saml2/auth
          sp_url: https://example.com:5000/Shibboleth.sso/SAML2/ECP
      organization_name: example_company
      organization_display_name: Example Corp.
      organization_url: example.com
      contact_company: example_company
      contact_name: John
      contact_surname: Smith
      contact_email: jsmith@example.com
      contact_telephone: 555-55-5555
      contact_type: technical

The following list is a reference of allowed settings:

* ``certfile`` defines the location and filename of the SSL certificate that
  the IdP uses to sign assertions. This file must be in a location that is
  accessible to the keystone system user.

* ``keyfile`` defines the location and filename of the SSL private key that
  the IdP uses to sign assertions. This file must be in a location that is
  accessible to the keystone system user.

* ``self_signed_cert_subject`` is the subject in the SSL signing
  certificate. The common name of the certificate
  must match the hostname configuration in the service provider(s) for
  this IdP.

* ``regen_cert`` by default is set to ``False``. When set to ``True``, the
  next Ansible run replaces the existing signing certificate with a new one.
  This setting is added as a convenience mechanism to renew a certificate when
  it is close to its expiration date.

* ``idp_entity_id`` is the entity ID. The service providers
  use this as a unique identifier for each IdP.
  ``<keystone-public-endpoint>/OS-FEDERATION/saml2/idp`` is the value we
  recommend for this setting.

* ``idp_sso_endpoint`` is the single sign-on endpoint for this IdP.
  ``<keystone-public-endpoint>/OS-FEDERATION/saml2/sso>`` is the value
  we recommend for this setting.

* ``idp_metadata_path`` is the location and filename where the metadata for
  this IdP is cached. The keystone system user must have access to this
  location.

* ``service_providers`` is a list of the known service providers (SP) that
  use the keystone instance as identity provider. For each SP, provide
  three values: ``id`` as a unique identifier,
  ``auth_url`` as the authentication endpoint of the SP, and ``sp_url``
  endpoint for posting SAML2 assertions.

* ``organization_name``, ``organization_display_name``, ``organization_url``,
  ``contact_company``, ``contact_name``, ``contact_surname``,
  ``contact_email``, ``contact_telephone`` and ``contact_type`` are
  settings that describe the identity provider. These settings are all
  optional.

--------------

.. include:: navigation.txt
