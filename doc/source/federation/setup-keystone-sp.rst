Keystone Service Provider Deployment Configuration
====================================

The following settings must be set:

#. ``keystone_public_endpoint`` automatically set by default
   to the public endpoint's URI. This is essential to ensure that
   the redirections performed and token references all refer to the
   public endpoint which is accessible to clients and the trusted
   IDP.

#. ``horizon_keystone_endpoint`` automatically set by default
   to the public v3 API endpoint URL for Keystone. Web-based single
   sign-on for Horizon requires the use of the Keystone v3 API.
   The value for this must use the same DNS name or IP address which
   is registered in the SSL certificate used for the endpoint.

#. If ADFS is to be used as the IdP, the Keystone endpoint is
   **required** to have an HTTPS public endpoint. The endpoint may
   either be provided by Keystone itself, or by an SSL offloading
   load balancer.

#. ``keystone_service_publicuri_proto`` must be set to https in order
   to ensure that the public endpoint is registered with https in the
   URL, to ensure that keystone publishes https in its references
   and to ensure that Shibboleth is configured to know that it should
   expect SSL URL's in the assertions (otherwise it will invalidate
   the assertions).

#. ADFS **requires** that a trusted SP have a trusted certificate that
   is not self-signed. This means that the certificate used for
   Keystone must either be signed by a public CA, or an enterprise CA.

#. When using SSL for the Keystone endpoint, the endpoint URI and the
   certificate must match. For example, if the certificate doesn’t have 
   the IP address of the endpoint, then the endpoint must be published with
   the appropriate name registered on the certificate. When 
   using a DNS name for the Keystone endpoint, both
   ``keystone_public_endpoint`` and ``horizon_keystone_endpoint`` must
   be set to use the DNS name.

#. At the time of writing this, `fernet tokens do not fully support
   federation <https://bugs.launchpad.net/keystone/+bug/1471289>`_.
   The following settings are therefore required to be set in the
   ``user_variables.yml`` file:

   .. code-block:: yaml

      keystone_token_provider: "keystone.token.providers.uuid.Provider"
      keystone_token_driver: "keystone.token.persistence.backends.sql.Token"

#. ``horizon_endpoint_type`` must be set to ``publicURL`` to ensure that
   Horizon makes use of the public endpoint for all its references and
   queries.

#. ``keystone_sp`` is a dictionary attribute which contains various
   settings that describe both the SP and the IDP's it trusts. For example:

   .. code-block:: yaml

      keystone_sp:
        cert_duration_years: 5
        trusted_dashboard_list:
          - "https://{{ external_lb_vip_address }}/auth/websso/"
        trusted_idp_list:
          - name: 'testshib-idp'
            entity_ids:
              - 'https://idp.testshib.org/idp/shibboleth'
            metadata_uri: 'http://www.testshib.org/metadata/testshib-providers.xml'
            metadata_file: 'metadata-testshib-idp.xml'
            metadata_reload: 1800
            federated_identities:
              - domain: Default
                project: fedproject
                group: fedgroup
                role: _member_
            protocols:
              - name: saml2
                mapping:
                  name: testshib-idp-mapping
                  rules:
                    - remote:
                        - type: eppn
                    local:
                        - group:
                            name: fedgroup
                            domain:
                              name: Default
                        - user:
                            name: '{0}'

#. ``cert_duration_years`` designates the valid duration for the SP's
   signing certificate (for example, ``/etc/shibboleth/sp-key.pem``).

#. ``trusted_dashboard_list`` designates the list of trusted URLs from which
   Keystone will accept redirects for Web Single-Sign. This
   list should contain all URLs that Horizon is presented on,
   suffixed by ``/auth/websso/`` which is the path for Horizon's WebSSO
   component.

#. ``trusted_idp_list`` is a dictionary attribute containing the list
   of settings which pertain to each trusted IdP for the SP.

#. ``trusted_idp_list.name`` is the name by which the IDP is known, is
   configured in Keystone and is listed in Horizon's login selection.

#. ``entity_ids`` is a list of reference entity IDs which specify where
   the login request to the SP will be redirected to in order to
   authenticate to the IdP.

#. ``metadata_uri`` is the location of the IdP's metadata which provides
   the SP with the signing key and all the IdP's supported endpoints.

#. ``metadata_file`` is the file name of the local cached version of
   the metadata which will be stored in ``/var/cache/shibboleth/``.

#. ``metadata_reload`` is the number of seconds between metadata
   refresh polls.

#. ``federated_identities`` is a list of domain, project, group and users
   which are to be mapped. See federation-mapping.rst for more information.

#. ``protocols`` is a list of protocols supported for the IdP and the set
   of mappings and attributes for each protocol. Only the protocol with the
   name ``saml2`` is supported at this time.

#. ``mapping`` is the local to remote mapping configuration for federated
   users. See federation-mapping.rst for more information.
