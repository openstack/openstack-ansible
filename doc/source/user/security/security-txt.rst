Security.txt
============

security.txt is a proposed `IETF standard`_ to allow independent security
researchers to easily report vulnerabilities. The standard defines that a text
file called ``security.txt`` should be found at "/.well-known/security.txt". For
legacy compatibility reasons the file might also be placed at "/security.txt".

.. _IETF standard: https://datatracker.ietf.org/doc/html/draft-foudil-securitytxt

In OpenStack-Ansible, ``security.txt`` is implemented in haproxy as all public
endpoints reside behind it and the text file is hosted by keystone. It defaults
to directing any request paths that end with ``/security.txt`` to the text
file using an ACL rule in haproxy.

Enabling security.txt
~~~~~~~~~~~~~~~~~~~~~

Use the following process to add a ``security.txt`` file to your deployment
using OpenStack-Ansible:

#. Write the contents of the ``security.txt`` file in accordance with the
   standard.
#. Define the contents of ``security.txt`` in the variable
   ``keystone_security_txt_content`` in the
   ``/etc/openstack_deploy/user_variables.yml`` file:

  .. code-block:: yaml

    keystone_security_txt_content: |
        # This is my example security.txt file
        # Please see https://securitytxt.org/ for details of the specification of this file

#. Update keystone

  .. code-block:: shell-session

    # openstack-ansible os-keystone-install.yml

#. Update haproxy

  .. code-block:: shell-session

    # openstack-ansible haproxy-install.yml

Advanced security.txt ACL
~~~~~~~~~~~~~~~~~~~~~~~~~

In some cases you may need to change the haproxy ACL used to redirect requests
to the ``security.txt`` file, such as adding extra domains.

The haproxy ACL is updated by overriding the variable
``haproxy_security_txt_acl`` in the
``/etc/openstack_deploy/user_variables.yml`` file.
