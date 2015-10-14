`Home <index.html>`__ OpenStack Ansible Installation Guide

Identity Service (keystone) service provider background
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In openstack-ansible (OSA) the Identity Service (keystone) is set up to
use Apache with mod_wsgi. The additional configuration of
keystone as a federation service provider adds Apache mod_shib
and configures it to respond to specific locations requests
from a client.

.. note::
   There are alternative methods of implementing
   federation, but at this time only SAML2-based federation using
   the Shibboleth SP is instrumented in OA.

When requests are sent to those locations, Apache hands off the
request to the ``shibd`` service. Only requests pertaining to
authentication are handed off.

The ``shibd`` service configuration is primarily handled through
the following files in ``/etc/shibboleth/`` within the keystone
containers:

* ``sp-cert.pem``, ``sp-key.pem``: These files are generated on the
  first keystone container and replicated to the other keystone
  containers by the ``os-keystone-install.yml`` playbook. They are
  used as signing credentials in communications between the SP
  and the IdP.
* ``shibboleth2.xml``: This file's contents are written by the
  ``os-keystone-install.yml`` playbook based on the configuration
  of the ``keystone_sp`` structured attribute in the
  ``/etc/openstack_deploy/user_variables.yml`` file. It contains
  the list of trusted IdP's, the entityID by which the SP will
  be known and some other facilitating configuration.
* ``attribute-map.xml``: This file's contents are written by the
  ``os-keystone-install.yml`` playbook based on the configuration
  of the ``keystone_sp`` structured attribute in the
  ``/etc/openstack_deploy/user_variables.yml`` file. It contains
  some default attribute mappings which will work for any basic
  Shibboleth-type IDP setup, but also contains any additional
  attribute mappings which were set out in the ``keystone_sp``
  structured attribute.
* ``shibd.logger``: This file is left alone by Ansible, but is useful
  when troubleshooting issues with federated authentication or
  when trying to discover what attributes published by an IdP
  are not currently being understood by your SP's attribute map.
  To enable debug logging, change ``log4j.rootCategory=INFO`` to
  ``log4j.rootCategory=DEBUG`` at the top of the file. The
  log file is output to ``/var/log/shibboleth/shibd.log``.

References
----------
* http://docs.openstack.org/developer/keystone/configure_federation.html
* http://docs.openstack.org/developer/keystone/extensions/shibboleth.html
* https://wiki.shibboleth.net/confluence/display/SHIB2/NativeSPConfiguration

--------------

.. include:: navigation.txt
