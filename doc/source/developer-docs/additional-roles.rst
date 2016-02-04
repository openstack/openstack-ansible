`Home <index.html>`_ OpenStack-Ansible Developer Documentation

Adding new Roles and Services
=============================

If you would like to contribute towards a role to introduce an OpenStack
service or an infrastructure service to support an OpenStack deployment, the
OpenStack-Ansible project would welcome that contribution and your assistance
in maintaining it.

Recommended procedure to develop a Role
---------------------------------------

#. Deploy OpenStack-Ansible (possibly using
   `an AIO`_
   deploy) so that you have the rest of an OpenStack cluster to integrate with
   in your testing.
#. Deploy your service on another VM, or possibly directly on the AIO host, by
   hand. Configure the service to coordinate with the OpenStack cluster
   appropriately. When all the related systems are communicating with each
   other you can use the resulting configuration as a reference later.
#. Develop a role for your service. A recommended process is detailed below.

.. _an AIO: quickstart-aio.html

Writing the Role
----------------
Most OpenStack services will follow a common series of stages to install or
update a service deployment. This is apparent when you review `tasks/main.yml`
for existing roles.

#. pre-install: prepare the service user group and filesystem directory paths
   on the host or container
#. install: install system packages, prepare the (optional) service virtual
   environment, install service and requirements (into a virtual environment)
#. post-install: apply all configuration files
#. messaging and db setup: db user and database prepared, message queue vhost
   and user prepared
#. service add: register the service (each of: service type, service project,
   service user, and endpoints) within Keystone's service catalog.
#. service setup: install a service-startup script (init, upstart, etc.) so
   that the service will start up when the container or host next starts.
#. service init/startup: signal to the host or container to start the services

There may be other specialized steps required by some services but most of the
roles will perform all of these at a minimum. Begin by reviewing a role for a
service that has something in common with your service and think about how you
can fit most of the common service setup and configuration steps into that
model.

.. HINT:: Following the patterns you find in other roles can help ensure your role
   is easier to use and maintain.

Steps to writing the role:

#. You can review roles which may be currently in development by checking our
   `specs repository`_ and `unmerged specs`_ on review.openstack.org. If you
   do not find a spec for the role, propose a blueprint/spec `(see also the
   spec template)`_ outlining the new Role. By proposing a draft spec you can
   help the OpenStack-Ansible community keep track of what roles are being
   developed and perhaps connect you with others who may be interested and
   able to help you in the process.
#. Create a source repository (e.g. on Github) to start your work on the Role.
#. Generate the reference directory structure for an Ansible role which is
   the necessary subset of the documented `Best Practice`_. You might use
   Ansible Galaxy tools to do this for you (e.g. ``ansible-galaxy init``).
   You may additionally want to include directories such as ``docs`` and
   ``examples`` and ``tests`` for your role.
#. Generate a meta/main.yml right away. This file is important to Ansible to
   ensure your dependent roles are installed and available and provides others
   with the information they will need to understand the purpose of your role.
#. Develop task files for each of the install stages in turn, creating any
   handlers and templates as needed. Ensure that you notify handlers after any
   task which impacts the way the service would run (such as configuration
   file modifications). Also take care that file ownership and permissions are
   appropriate.

   .. HINT:: Fill in variable defaults, libraries, and prerequisites as you
      discover a need for them. You can also develop documentation for your
      role at the same time.

.. _(see also the spec template): https://github.com/openstack/openstack-ansible-specs/blob/master/specs/template.rst
.. _specs repository: https://github.com/openstack/openstack-ansible-specs
.. _unmerged specs: https://review.openstack.org/#/q/status:+open+project:openstack/openstack-ansible-specs
.. _Best Practice: https://docs.ansible.com/ansible/playbooks_best_practices.html#directory-layout

Deploying the Role
------------------
#. Include your role on the deploy host. See also `Adding Galaxy roles`_.
#. Perform any other host preparation (such as the tasks performed by the
   ``bootstrap-aio.yml`` playbook). This includes any preparation tasks that
   are particular to your service.
#. Generate files to include your service in the Ansible inventory
   using `env.d`_ and `conf.d`_ files for use on your deploy host.

   .. HINT:: You can follow examples from other roles, making the appropriate
      modifications being sure that group labels in ``env.d`` and ``conf.d``
      files are consistent.

#. Generate secrets, if any, `as described in the Install Guide`_. You can
   append your keys to an existing ``user_secrets.yml`` file or add a new file
   to the ``openstack_deploy`` directory to contain them. Provide overrides
   for any other variables you will need at this time as well, either in
   ``user_variables.yml`` or another file. This is explained in more depth
   under `Extending OpenStack-Ansible`_.
#. If your service is installed from source or relies on python packages which
   need to be installed from source, specify a repository for the source
   code of each requirement by adding a file to your deploy host under
   ``playbooks/repo_packages`` in the OpenStack-Ansible source repository
   and following the pattern of files currently in that directory. You could
   also simply add an entry to an existing file there. Be sure to run the
   ``repo-build.yml`` play later so that wheels for your packages will be
   included in the repository infrastructure.
#. Make any required adjustments to the load balancer configuration
   (e.g. modify ``playbooks/vars/configs/haproxy_config.yml`` in the
   OpenStack-Ansible source repository on your deploy host) so that your
   service can be reached through a load balancer, if appropriate, and be sure
   to run the ``haproxy-install.yml`` play later so your changes will be
   applied.
#. Put together a service install playbook file for your role. This can also
   be modeled from any existing service playbook that has similar
   dependencies to your service (database, messaging, storage drivers,
   container mount points, etc.). A common place to keep playbook files in a
   Galaxy role is in an ``examples`` directory off the root of the role.

.. HINT:: If you adhere to the pattern of isolating your role's extra
   deployment requirements (secrets and var files, HAProxy yml fragments,
   repo_package files, etc.) in their own files it makes it easy for you to
   automate these additional steps when testing your role.

.. _Adding Galaxy roles: extending.html#adding-galaxy-roles
.. _env.d: extending.html#env-d
.. _conf.d: extending.html#conf-d
.. _as described in the Install Guide: ../install-guide/configure-creds.html#configuring-service-credentials
.. _Extending OpenStack-Ansible: extending.html#user-yml-files