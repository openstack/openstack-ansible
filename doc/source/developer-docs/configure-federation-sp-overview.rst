`Home <index.html>`__ OpenStack-Ansible Installation Guide

Identity Service (keystone) service provider background
=======================================================

In OpenStack-Ansible, the Identity Service (keystone) is set up to
use Apache with ``mod_wsgi``. The additional configuration of
keystone as a federation service provider adds Apache ``mod_shib``
and configures it to respond to specific locations requests
from a client.

.. note::

   There are alternative methods of implementing
   federation, but at this time only SAML2-based federation using
   the Shibboleth SP is instrumented in OA.

When requests are sent to those locations, Apache hands off the
request to the ``shibd`` service.

.. note::
   
   Handing off happens only with requests pertaining to authentication.

Handle the ``shibd`` service configuration through
the following files in ``/etc/shibboleth/`` in the keystone
containers:

* ``sp-cert.pem``, ``sp-key.pem``: The ``os-keystone-install.yml`` playbook
   uses these files generated on the first keystone container to replicate
   them to the other keystone containers. The SP and the IdP use these files
   as signing credentials in communications.
* ``shibboleth2.xml``: The ``os-keystone-install.yml`` playbook writes the
  file's contents, basing on the structure of the configuration
  of the ``keystone_sp`` attribute in the
  ``/etc/openstack_deploy/user_variables.yml`` file. It contains
  the list of trusted IdP's, the entityID by which the SP is known,
  and other facilitating configurations.
* ``attribute-map.xml``: The ``os-keystone-install.yml`` playbook writes
  the file's contents, basing on the structure of the configuration
  of the ``keystone_sp`` attribute in the
  ``/etc/openstack_deploy/user_variables.yml`` file. It contains
  the default attribute mappings that work for any basic
  Shibboleth-type IDP setup, but also contains any additional
  attribute mappings set out in the structure of the ``keystone_sp``
  attribute.
* ``shibd.logger``: This file is left alone by Ansible. It is useful
  when troubleshooting issues with federated authentication, or
  when discovering what attributes published by an IdP
  are not currently being understood by your SP's attribute map.
  To enable debug logging, change ``log4j.rootCategory=INFO`` to
  ``log4j.rootCategory=DEBUG`` at the top of the file. The
  log file is output to ``/var/log/shibboleth/shibd.log``.

References
----------
* `http://docs.openstack.org/developer/keystone/configure_federation.html`_
* `http://docs.openstack.org/developer/keystone/extensions/shibboleth.html`_
* `https://wiki.shibboleth.net/confluence/display/SHIB2/NativeSPConfiguration`_

--------------

.. include:: navigation.txt
