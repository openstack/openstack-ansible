Security Headers
================

Security headers are HTTP headers that can be used to increase the security of
a web application by restricting what modern browsers are able to run.

In OpenStack-Ansible, security headers are implemented in haproxy as all the
public endpoints reside behind it.

The following headers are enabled by default on all the haproxy interfaces
that implement TLS, but only for the Horizon service. The security headers can
be implemented on other haproxy services, but only services used by
browsers will make use of the headers.

HTTP Strict Transport Security
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The `OpenStack TLS Security Guide`_ recommends that all production deployments use
HTTP strict transport security (HSTS).

.. _OpenStack TLS Security Guide: https://docs.openstack.org/security-guide/secure-communication/tls-proxies-and-http-services.html#http-strict-transport-security

By design, this header is difficult to disable once set. It is recommended that
during testing you set a short time of 1 day and after testing increase the time
to 1 year.

To change the default max age to 1 day, override the variable
``haproxy_security_headers_max_age`` in the
``/etc/openstack_deploy/user_variables.yml`` file:

.. code-block:: yaml

    haproxy_security_headers_max_age: 86400

If you would like your domain included in the HSTS preload list, which is built
into browsers, before submitting your request to be added to the HSTS preload
list you must add the ``preload`` token to your response header. The ``preload``
token indicates to the maintainers of HSTS preload list that you are happy to
have your site included.

.. code-block:: yaml

    - "http-response set-header Strict-Transport-Security \"max-age={{ haproxy_security_headers_max_age }}; includeSubDomains; preload;\""

X-Content-Type-Options
~~~~~~~~~~~~~~~~~~~~~~

The ``X-Content-Type-Options`` header prevents MIME type sniffing.

This functionality can be changed by overriding the list of headers in
``haproxy_security_headers`` variable in the
``/etc/openstack_deploy/user_variables.yml`` file.

Referrer Policy
~~~~~~~~~~~~~~~

The ``Referrer-Policy`` header controls how much referrer information is sent
with requests. It defaults to ``same-origin``, which does not send the origin
path for cross-origin requests.

This functionality can be changed by overriding the list of headers in
``haproxy_security_headers`` variable in the
``/etc/openstack_deploy/user_variables.yml`` file.

Permission Policy
~~~~~~~~~~~~~~~~~

The ``Permissions-Policy`` header allows you to selectively enable, disable or
modify the use of browser features and APIs, previously known as Feature Policy.

By default this header is set to block access to all features apart from the
following from the same origin; fullscreen, clipboard read, clipboard
write and spatial navigation.

This functionality can be changed by overriding the list of headers in
``haproxy_security_headers`` variable in the
``/etc/openstack_deploy/user_variables.yml`` file.


Content Security Policy (CSP)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``Content-Security-Policy`` header allows you to control what resources a
browser is allowed to load for a given page, which helps to mitigate the risks
from Cross-Site Scripting (XSS) and data injection attacks.

By default, the Content Security Policy (CSP) enables a minimum set of resources
to allow Horizon to work, which includes access the Nova console. If you require
access to other resources these can be set by overriding the
``haproxy_security_headers_csp`` variable in the
``/etc/openstack_deploy/user_variables.yml`` file.

Report Only
-----------

Implementing CSP could lead to broken content if a browser is blocked from
accessing certain resources, therefore it is recommended that when testing CSP
you use the ``Content-Security-Policy-Report-Only`` header, instead of
``Content-Security-Policy``, this reports CSP violations to the browser console,
but does not enforce the policy.

To set the CSP policy to report only by overriding the
``haproxy_security_headers_csp_report_only`` variable to ``True`` in the
``/etc/openstack_deploy/user_variables.yml`` file:

.. code-block:: yaml

   haproxy_security_headers_csp_report_only: True


Reporting Violations
--------------------

It is recommended that you monitor attempted CSP violations in production, this
is achieved by setting the ``report-uri`` and ``report-to`` tokens.

Federated Login
---------------

When using federated login you will need to override the default Content
Security Policy to allow access to your authorisation server by overriding the
``haproxy_horizon_csp`` variable in the
``/etc/openstack_deploy/user_variables.yml`` file:

.. code-block:: yaml

    haproxy_horizon_csp: >
      http-response set-header Content-Security-Policy "
      default-src 'self';
      frame-ancestors 'self';
      form-action 'self' {{ external_lb_vip_address }}:5000 <YOUR-AUTHORISATION-SERVER-ORIGIN>;
      upgrade-insecure-requests;
      style-src 'self' 'unsafe-inline';
      script-src 'self' 'unsafe-inline' 'unsafe-eval';
      child-src 'self' {{ external_lb_vip_address }}:{{ nova_console_port }};
      frame-src 'self' {{ external_lb_vip_address }}:{{ nova_console_port }};
      "
