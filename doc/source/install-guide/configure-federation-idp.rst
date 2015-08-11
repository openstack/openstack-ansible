`Home <index.html>`__ OpenStack Ansible Installation Guide

Configure Identity Service (keystone) as a federated identity provider
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The identity provider (IdP) configuration for Keystone must be provided in a
dictionary attribute with the key ``keystone_idp``. The following is a
complete example::

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

The following list is a reference of all the allowed settings:

* ``certfile`` defines the location and filename of the SSL certificate that
  the IdP uses to sign assertions. This file must be in a location that is
  accessible to the keystone system user.

* ``keyfile`` defines the location and filename of the SSL private key that
  the IdP uses to sign assertions. This file must be in a location that is
  accessible to the keystone system user.

* ``self_signed_cert_subject`` is the subject used in the SSL signing
  certificate. It is important to note that the common name of the certificate
  must match the hostname that is configured in the service provider(s) for
  this IdP.

* ``regen_cert`` should normally be set to ``False``. When set to ``True``,
  the existing signing certificate will be replaced with a new one. This
  setting is added as a convenience mechanism to renew a certificate when it
  is close to its expiration date.

* ``idp_entity_id`` is the entity ID. The service providers will
  use this as a unique identifier for each IdP. The recommended value for this
  setting is ``<keystone-public-endpoint>/OS-FEDERATION/saml2/idp``

* ``idp_sso_endpoint`` is the single sign-on endpoint for this IdP. The
  recommended value for this setting is
  ``<keystone-public-endpoint>/OS-FEDERATION/saml2/sso>``

* ``idp_metadata_path`` is the location and filename where the metadata for
  this IdP will be cached. The keystone system user must have access to this
  location.

* ``service_providers`` is a list of the known service providers that will be
  using this keystone instance as identity provider. For each SP there are
  three values that need to be provided: ``id`` is a unique identifier,
  ``auth_url`` is the authentication endpoint of the SP, and ``sp_url`` is the
  endpoint where SAML2 assertions need to be posted.

* ``organization_name``, ``organization_display_name``, ``organization_url``,
  ``contact_company``, ``contact_name``, ``contact_surname``,
  ``contact_email``, ``contact_telephone`` and ``contact_type`` are all
  settings that describe the identity provider. These settings are all optional.

--------------

.. include:: navigation.txt
