`Home <index.html>`_ OpenStack-Ansible Installation Guide

Checking the integrity of your configuration files
==================================================

Execute the following steps before running any playbook:

#. Ensure all files edited in ``/etc/`` are Ansible
   YAML compliant. Guidelines can be found here:
   `<http://docs.ansible.com/ansible/YAMLSyntax.html>`_

#. Check the integrity of your YAML files:

   .. note:: Here is an online linter: `<http://www.yamllint.com/>`_

#. Run your command with ``syntax-check``:

   .. code-block:: shell-session

      # openstack-ansible setup-infrastructure.yml --syntax-check

#. Recheck that all indentation is correct.

   .. note::
      The syntax of the configuration files can be correct
      while not being meaningful for OpenStack-Ansible.

--------------

.. include:: navigation.txt
