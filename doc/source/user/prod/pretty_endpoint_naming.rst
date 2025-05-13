============================================================
Using domain (or path) based endpoints instead of port-based
============================================================

By default, OpenStack-Ansible uses port-based endpoints. This means, that
each service will be served on its own unique port for both public and internal
endpoints. For example, Keystone will be added as
``https://domain.com:5000/v3``, Nova as ``https://domain.com:8774/v2.1`` and so
on.

While this is the simplest approach, as it does not require any extra
configuration and is easy to start with, it also has some disadvantages.
For example, some clients or organizations might not be allowed to connect
to custom ports which completely disables the ability to use them in such deployments.

In order to work around such limitations, starting from 2023.1 (Antelope) release,
it is possible to have domain-based or path-based endpoints instead.


Configuring domain-based endpoints (recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Domain-based endpoints do separate direct requests to specific services based
on FQDNs. Usually for this purpose subdomains are used. For example, Keystone
endpoint may look like ``https://identity.domain.com`` while Nova endpoint
can be like ``https://compute.domain.com``.

As a prerequisite for this type of setup you need to ensure that corresponding
`A` or `CNAME` records are present for your domain. Also, you need to ensure
having a valid wildcard or SAN certificates for public/internal endpoints.


HAProxy configuration
---------------------

In order for HAProxy to pass specific FQDN to it's own backend we will leverage
`map files <https://www.haproxy.com/documentation/haproxy-configuration-tutorials/core-concepts/map-files/>`_
functionality.

We need to make adjustments to each HAProxy service definition to:

* Prevent creation of a front-end per service. As we are now expecting traffic
  to come only on default `80` and `443` ports there is no need to have a
  separate frontend per service. A HAProxy map file is attached to a "base"
  frontend which is deployed with the ``haproxy_server`` role and is
  independent of any service definitions. The map file can be used to direct
  incoming requests to specific backends by using rules defined in the map
  file to match against host request headers.

  .. note::

    In case of any changes to ``haproxy_base_service_overrides`` variable you
    need to re-run
    ``openstack-ansible openstack.osa.haproxy --tags haproxy-service-config``.

  .. code:: yaml

    haproxy_base_service_overrides:
      haproxy_maps:
        - 'use_backend %[req.hdr(host),map_dom(/etc/haproxy/base_domain.map)]'
      haproxy_map_entries:
        - name: base_domain
          entries:
            - "# Domain map file - this comment is defined in the base frontend config"

* Populate a "base" map file with search patterns per service backend. As each
  service is going to use its own FQDN we need to inform HAProxy which backend
  should be used when request is coming to the FQDN.

  Sample configuration for Keystone and Nova will look like this:

  .. note::

    With changes made to ``haproxy_<service>_service_overrides`` variable you
    need to re-run a service-specific playbook with `haproxy-service-config`
    tag, for example
    ``openstack-ansible openstack.osa.keystone --tags haproxy-service-config``.

  .. code:: yaml

      haproxy_keystone_service_overrides:
        haproxy_backend_only: True
        haproxy_map_entries:
          - name: base_domain
            entries:
              - "identity.{{ external_lb_vip_address }} keystone_service-back"
              - "identity.{{ internal_lb_vip_address }} keystone_service-back"

      haproxy_nova_api_compute_service_overrides:
        haproxy_backend_only: True
        haproxy_map_entries:
          - name: base_domain
            entries:
              - "compute.{{ external_lb_vip_address }} nova_api_os_compute-back"
              - "compute.{{ internal_lb_vip_address }} nova_api_os_compute-back"

      haproxy_nova_novnc_console_service_overrides:
        haproxy_backend_only: True
        haproxy_map_entries:
          - name: base_domain
            entries:
              - "novnc.{{ external_lb_vip_address }} nova_novnc_console-back"


Service configuration
---------------------

Along with HAProxy configuration we also need to ensure that the endpoint catalog
will be populated with correct URIs. Each service has a set of variables that
needs to be overridden. Usually such variables have the following format:

* `<service>_service_publicuri`
* `<service>_service_internaluri`
* `<service>_service_adminuri`

Below you can find an example for defining endpoints for Keystone and Nova:

.. code:: yaml

    keystone_service_publicuri: "{{ openstack_service_publicuri_proto }}://identity.{{ external_lb_vip_address }}"
    keystone_service_internaluri: "{{ openstack_service_internaluri_proto }}://identity.{{ internal_lb_vip_address }}"
    keystone_service_adminuri: "{{ openstack_service_adminuri_proto }}://identity.{{ internal_lb_vip_address }}"

    nova_service_publicuri: "{{ openstack_service_publicuri_proto }}://compute.{{ external_lb_vip_address }}"
    nova_service_internaluri: "{{ openstack_service_internaluri_proto }}://compute.{{ internal_lb_vip_address }}"
    nova_service_adminuri: "{{ openstack_service_adminuri_proto }}://compute.{{ internal_lb_vip_address }}"
    nova_novncproxy_base_uri: "{{ nova_novncproxy_proto }}://novnc.{{ external_lb_vip_address }}"


Using Let's Encrypt
-------------------

While you can consider having a wildcard or SAN TLS certificate for the
domain to cover all service endpoints in this setup, it is still possible
to use Let's Encrypt certificates with dns-01 authentication or by supplying
a list of subdomains which issued certificate will cover.

So your Let's Encrypt configuration may look like this:

.. code:: yaml

    haproxy_ssl_letsencrypt_enable: True
    haproxy_ssl_letsencrypt_email: "root@{{ external_lb_vip_address }}"
    haproxy_ssl_letsencrypt_domains:
      - "{{ external_lb_vip_address }}"
      - "identity.{{ external_lb_vip_address }}"
      - "compute.{{ external_lb_vip_address }}"

.. note::

    Please mention, that Internal FQDNs are still going to be covered with
    self-signed certificates as in most use-cases Let's Encrypt should not be
    able to verify domain ownership for internal VIPs, unless dns-01 auth is used.

You also might need to take care of expanding CN names for issued SAN certificate
by the PKI role.
For that you will have to override ``haproxy_vip_binds`` variable like in
example below:

.. code:: yaml

  haproxy_vip_binds:
    - address: "{{ haproxy_bind_external_lb_vip_address }}"
      interface: "{{ haproxy_bind_external_lb_vip_interface }}"
      type: external
    - address: "{{ haproxy_bind_internal_lb_vip_address }}"
      interface: "{{ haproxy_bind_internal_lb_vip_interface }}"
      type: internal
      pki_san_records:
        - "{{ internal_lb_vip_address }}"
        - "identity.{{ internal_lb_vip_address }}"
        - "compute.{{ internal_lb_vip_address }}"


You also might want to adjust HSTS headers defined by
``haproxy_security_headers_csp`` variable. While default rules do allow
subdomains out of the box, you might want to restrict records a bit more to
disallow access on arbitrary ports.

.. note::

    Variables ``haproxy_security_child_src_records`` and
    ``haproxy_security_connect_src_records`` are only available staring with
    2024.2 (Dalmatian) version.
    You need to override ``haproxy_security_headers_csp`` as a whole for
    earlier releases

.. code::

    haproxy_security_child_src_records:
      - "novnc.{{ external_lb_vip_address }}"
    haproxy_security_connect_src_records:
      - "{{ external_lb_vip_address }}
    haproxy_security_frame_ancestors_records:
      - "{{ external_lb_vip_address }}


Configuring path-based endpoints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Path-based endpoints imply serving services on the same FQDN but
differentiating them based on URI.

For example, Keystone can be configured as ``https://domain.com/identity/v3``
while Nova as ``https://domain.com/compute/v2.1``

.. warning::

    Please note, that Horizon does utilize `/identity` for its Keystone
    panel, so if you're serving Horizon on `/` (default) and using
    `/identity` to forward traffic to Keystone backend, management of
    users, roles, projects inside the Horizon will be broken due to
    a conflict.

While path-based endpoints might look tempting due to using FQDN and
thus not having the need for wildcard TLS, they are harder to maintain and more
complex to set up. Also worth mentioning, that not all services are ready
to support path-based endpoints, despite this approach being used in devstack.

Good example of exceptions which do not support path-based endpoints at the moment
are VNC consoles for VMs (to be implemented with
`blueprint <https://blueprints.launchpad.net/nova/+spec/novnc-base-url-respect-extra-params>`_),
Magnum (`bug report <https://launchpad.net/bugs/2083168>`) and Ceph Rados Gateway.


HAProxy configuration
---------------------

Similar to domain-based endpoints we rely on HAProxy maps functionality. But instead of
``map_dom`` we will be using ``map_reg``.

So we need to define a map file to be used and a way to parse it. For that we
need to apply an override for the `base` service.

.. code:: yaml

    haproxy_base_service_overrides:
      haproxy_maps:
        - 'use_backend %[path,map_reg(/etc/haproxy/base_regex.map)]'

In case you do need to have a Ceph RGW or want to combine domain-based with
path-based approach - you can do that by defining two map files:

.. note::

    In case of any changes to ``haproxy_base_service_overrides`` variable you
    need to re-run
    ``openstack-ansible openstack.osa.haproxy --tags haproxy-service-config``.

.. code:: yaml

    haproxy_base_service_overrides:
      haproxy_maps:
        - 'use_backend %[req.hdr(host),map_dom(/etc/haproxy/base_domain.map)] if { req.hdr(host),map_dom(/etc/haproxy/base_domain.map) -m found }'
        - 'use_backend %[path,map_reg(/etc/haproxy/base_regex.map)]'

If no domain will be matched HAProxy will proceed with path-based endpoints.

Next, we need to ensure a HAProxy configuration for each service does contain
HAProxy map population with a respective condition, for example:

.. note::

    With changes made to ``haproxy_<service>_service_overrides`` variable you
    need to re-run a service-specific playbook with `haproxy-service-config`
    tag, for example
    ``openstack-ansible openstack.osa.keystone --tags haproxy-service-config``.

.. code:: yaml

    haproxy_keystone_service_overrides:
      haproxy_backend_only: True
      haproxy_map_entries:
        - name: base_regex
          entries:
            - "^/identity keystone_service-back"

    haproxy_nova_api_compute_service_overrides:
      haproxy_backend_only: True
      haproxy_map_entries:
        - name: base_regex
          entries:
            - "^/compute nova_api_os_compute-back"


Service configuration
---------------------

Similar to the domain-based endpoints we need to override endpoints definition
for each service. Endpoints are usually defined with following variables:

* `<service>_service_publicuri`
* `<service>_service_internaluri`
* `<service>_service_adminuri`

Below you can find an example for defining endpoints for Keystone and Nova:

.. code:: yaml

    keystone_service_publicuri: "{{ openstack_service_publicuri_proto }}://{{ external_lb_vip_address }}/identity"
    keystone_service_internaluri: "{{ openstack_service_internaluri_proto }}://{{ internal_lb_vip_address }}/identity"
    keystone_service_adminuri: "{{ openstack_service_adminuri_proto }}://{{ internal_lb_vip_address }}/identity"

    nova_service_publicuri: "{{ openstack_service_publicuri_proto }}://{{ external_lb_vip_address }}/compute"
    nova_service_internaluri: "{{ openstack_service_internaluri_proto }}://{{ internal_lb_vip_address }}/compute"
    nova_service_adminuri: "{{ openstack_service_adminuri_proto }}://{{ internal_lb_vip_address }}/compute"

However, there is another important part of the configuration required per service which
is not a case for domain-based setup.
All services assume that they've been served on root path (i.e. `/`) while in path-based
approach we use a unique path for each service.

So we now need to make service respect the path and respond correctly on it.
One way of doing that could be using rewrite mechanism in uWSGI, for example:

.. warning::

    Example below does not represent a correct approach on how to
    configure path-based endpoint for most services

.. code:: yaml

    keystone_uwsgi_ini_overrides:
      uwsgi:
        route: '^/identity(.*)$ rewrite:$1'

But this approach is not correct and will result in issues in some clients
or use cases, despite the service appearing completely functional.
The problem with the approach above is related to how services return the `self`
URL when it's asked for. Most services will reply with their
current micro-version and URI to this micro-version in reply.

If you are to use uWSGI rewrites like shown above, you will result in
response like that:

.. code-block:: console

    curl https://cloud.com/identity/ | jq
    {
    "versions": {
        "values": [
        {
            "id": "v3.14",
            "status": "stable",
            "updated": "2020-04-07T00:00:00Z",
            "links": [
            {
                "rel": "self",
                "href": "https://cloud.com/v3/"
            }
            ],
            "media-types": [
            {
                "base": "application/json",
                "type": "application/vnd.openstack.identity-v3+json"
            }
            ]
        }
        ]
    }
    }

As you might see, `href` is pointing not to the expected location. While
some clients may not refer to href link provided by service, others might
use it as source of truth and which will result in failures.

Some services, like keystone, have a configuration options which may
control how `href` is being defined. For instance, keystone does have
`[DEFAULT]/public_endpoint` option, but this approach is not consistent
across services. Moreover, keystone will return provided `public_endpoint`
for all endpoints, including admin and internal.

With that, the only correct approach here would be to adjust ``api-paste.ini``
for each respective service. But, Keystone specifically, does not support
api-paste.ini files. So the only way around it is actually a uWSGI rewrite
and to define a `public_endpoint` in `keystone.conf`:

.. code:: yaml

    keystone_keystone_conf_overrides:
      DEFAULT:
        public_endpoint: "{{ keystone_service_publicuri }}"

For other services applying ``api-paste.ini`` can be done with variables,
but each service have quite a unique content there, so approach can't be
easily generalized. Below you can find overrides made for some services
as an example:

.. code:: yaml

    _glance_api_paste_struct:
        /: {}
        /healthcheck: {}
        /image: api
        /image/healthcheck: healthcheck
    glance_glance_api_paste_ini_overrides:
      composite:glance-api: "{{ _glance_api_paste_struct }}"
      composite:glance-api-caching: "{{ _glance_api_paste_struct }}"
      composite:glance-api-cachemanagement: "{{ _glance_api_paste_struct }}"
      composite:glance-api-keystone: "{{ _glance_api_paste_struct }}"
      composite:glance-api-keystone+caching: "{{ _glance_api_paste_struct }}"
      composite:glance-api-keystone+cachemanagement: "{{ _glance_api_paste_struct }}"

    neutron_api_paste_ini_overrides:
      composite:neutron:
        /: {}
        /v2.0: {}
        /network/: neutronversions_composite
        /network/v2.0: neutronapi_v2_0

    nova_api_paste_ini_overrides:
      composite:osapi_compute:
        /: {}
        /v2: {}
        /v2.1: {}
        /v2/+: {}
        /v2.1/+: {}
        /compute: oscomputeversions
        /compute/v2: oscomputeversion_legacy_v2
        /compute/v2.1: oscomputeversion_v2
        /compute/v2/+: openstack_compute_api_v21_legacy_v2_compatible
        /compute/v2.1/+: openstack_compute_api_v21


We suggest referring to each service api-paste.ini for more details
on how to properly configure overrides.
