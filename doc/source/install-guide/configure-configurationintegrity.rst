`Home <index.html>`_ OpenStack-Ansible Installation Guide

Checking the integrity of your configuration files
--------------------------------------------------

Here are a few steps to execute before running any playbook:

#. Make sure all the files edited in ``/etc/`` are ansible
   YAML compliant. Guidelines can be found here:
   `<http://docs.ansible.com/ansible/YAMLSyntax.html>`_

#. Check the integrity of your yaml files using a yaml linter.

   .. note:: Here is an online linter: `<http://www.yamllint.com/>`_

#. Run your command with syntax-check, for example,
   in the playbooks directory:

   .. code-block:: shell-session

      # openstack-ansible setup-infrastructure.yml --syntax-check

#. Recheck that all indentation seems correct: the syntax of the
   configuration files can be correct while not being meaningful
   for openstack-ansible.

--------------

.. include:: navigation.txt
