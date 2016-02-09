`Home <index.html>`_ OpenStack-Ansible Installation Guide

Cached Ansible facts issues
---------------------------

At the beginning of a playbook run, information about each host, such as its
Linux distribution, kernel version, and network interfaces, is gathered. To
improve performance, particularly in larger deployments, these facts can be
cached.

OpenStack-Ansible enables fact caching by default. The facts are cached in
JSON files within ``/etc/openstack_deploy/ansible_facts``.

Fact caching can be disabled by commenting out the ``fact_caching``
parameter in ``playbooks/ansible.cfg``.  Refer to Ansible's documentation on
`fact caching`_ for more details.

.. _fact caching: http://docs.ansible.com/ansible/playbooks_variables.html#fact-caching

Forcing regeneration of cached facts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a host's kernel is upgraded or additional network interfaces or bridges are
created on the host, its cached facts may be incorrect. This can lead to
unexpected errors while running playbooks, and require that the cached facts be
regenerated.

Run the following command to remove all currently cached facts for all hosts:

.. code-block:: shell-session

   # rm /etc/openstack_deploy/ansible_facts/*

New facts will be gathered and cached during the next playbook run.

To clear facts for a single host, find its file within
``/etc/openstack_deploy/ansible_facts/`` and remove it.  Each host has a JSON
file that is named after its hostname.  The facts for that host will be
regenerated on the next playbook run.

--------------

.. include:: navigation.txt
