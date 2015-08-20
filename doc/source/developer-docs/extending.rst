Extending os-ansible-deployment
===============================

The os-ansible-deployment project provides a basic OpenStack environment, but
many deployers will wish to extend the environment based on their needs. This
could include installing extra services, changing package versions, or
overriding existing variables.

Using these extension points, deployers can provide a more 'opinionated'
installation of OpenStack that may include their own software.

Including os-ansible-deployment in your project
-----------------------------------------------

Including the os-ansible-deployment repository within another project can be
done in several ways.

    1. A git submodule pointed to a released tag.
    2. A script to automatically perform a git checkout of
       os-ansible-deployment

When including os-ansible-deployment in a project, consider using a parallel
directory structure as shown in the `ansible.cfg files`_ section.

Also note that copying files into directories such as `env.d`_ or
`conf.d`_ should be handled via some sort of script within the extension
project.

ansible.cfg files
-----------------

You can create your own playbook, variable, and role structure while still
including the os-ansible-deployment roles and libaries by putting an
``ansible.cfg`` file in your ``playbooks`` directory.

The relevant options for Ansible 1.9 (included in os-ansible-deployment)
are as follows:

    ``library``
        This variable should point to
        ``os-ansible-deployment/playbooks/library``. Doing so allows roles and
        playbooks to access os-ansible-deployment's included Ansible modules.
    ``roles_path``
        This variable should point to
        ``os-ansible-deployment/playbooks/roles``. This allows Ansible to
        properly look up any os-ansible-deployment roles that extension roles
        may reference.
    ``inventory``
        This variable should point to
        ``os-ansible-deployment/playbooks/inventory``. With this setting,
        extensions have access to the same dynamic inventory that
        os-ansible-deployment uses.

Note that the paths to the ``os-ansible-deployment`` top level directory can be
relative in this file.

Consider this directory structure::

    my_project
    |
    |- custom_stuff
    |  |
    |  |- playbooks
    |- os-ansible-deployment
    |  |
    |  |- playbooks

The variables in ``my_project/custom_stuff/playbooks/ansible.cfg`` would use
``../os-ansible-deployment/playbooks/<directory>``.


env.d
-----

The os-ansible-deployment default environment, including container and host
group mappings, resides in ``/etc/openstack_deploy/openstack_environment.yml``.

The ``/etc/openstack_deploy/env.d`` directory sources all YAML files into the
deployed environment, allowing a deployer to define additional group mappings
without having to edit the ``openstack_environment.yml`` file, which is
controlled by the os-ansible-deployment project itself.

conf.d
------

Common OpenStack services and their configuration are defined by
os-ansible-deployment in the
``/etc/openstack_deploy/openstack_user_config.yml`` settings file.

Additional services should be defined with a YAML file in
``/etc/openstack_deploy/conf.d``, in order to manage file size.


user\_*.yml files
-----------------

Files in ``/etc/openstack_deploy`` beginning with ``user_`` will be automatically
sourced in any ``openstack-ansible`` command. Alternatively, the files can be
sourced with the ``-e`` parameter of the ``ansible-playbook`` command.

``user_variables.yml`` and ``user_secrets.yml`` are used directly by
os-ansible-deployment; adding custom values here is not recommended.

``user_extras_variables.yml`` and ``users_extras_secrets.yml`` are provided
and can contain deployer's custom values, but deployers can add any other
files they wish to include new configuration, or override existing.

Ordering and Precedence
+++++++++++++++++++++++

``user_*.yml`` variables are just YAML variable files. They will be sourced
in alphanumeric order by ``openstack-ansible``.

Adding Galaxy roles
-------------------

Any roles defined in ``os-ansible-deployment/ansible-role-requirements.yml``
will be installed by the
``os-ansible-deployment/scripts/bootstrap-ansible.sh`` script.
