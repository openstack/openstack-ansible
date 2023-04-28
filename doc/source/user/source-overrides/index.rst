==========================
Source overriding examples
==========================

There are situations where a deployer want to override sources with
its own fork.

This chapter gives case-by-case examples on how to override the
default sources.

Overriding Ansible version
==========================

Overriding the default Ansible version is not recommended, as
each branch of OpenStack-Ansible has been built with the a specific
Ansible version in mind, and many Ansible changes are neither backwards
nor forward compatible.

The ``bootstrap-ansible.sh`` script installs Ansible, and uses
a variable ``ANSIBLE_PACKAGE`` to describe which version to install.

For example to install ansible version 2.5.0:

.. code:: bash

   $ export ANSIBLE_PACKAGE="ansible==2.5.0"


Installing directly from git is also supported. For example, from the tip of
Ansible development branch:

.. code:: bash

   $ export ANSIBLE_PACKAGE="git+https://github.com/ansible/ansible@devel#egg=ansible"


Overriding the roles
====================

Overriding the role file has been explained in the reference guide,
on the :ref:`extend_osa_roles` section.

.. _override_openstack_sources:

Overriding other upstream projects source code
==============================================

All the upstream repositories used are defined in the
``openstack-ansible`` integrated repository, in the
``inventory/group_vars/<service_group>/source_git.yml`` file.

For example, if you want to override ``glance`` repository with your
own, you need to define the following:

::

    glance_git_repo: https://<your git repo>
    glance_git_install_branch: <your git branch or commit SHA>
    glance_git_project_group: glance_all

Please note, for this glance example, that you do not need to edit the
``inventory/group_vars/glance_all/source_git.yml`` file.

Instead, the usual overrides mechanism can take place, and you
can define these 3 variables in a ``user_*.yml`` file.
See also the :ref:`user-overrides` page.

.. note::

   These variables behave a little differently than standard ansible
   precedence, because they are also consumed by a custom lookup plugin.

   The ``py_pkgs lookup`` will ignore all _git_ variables unless the
   ``_git_repo`` variable is present.

   So even if you only want to override the ``_git_install_branch`` for
   a repository, you should also define the ``_git_repo`` variable
   in your user variables.

