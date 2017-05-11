.. _limited-connectivity-appendix:

================================================
Appendix G: Installing with limited connectivity
================================================

Many playbooks and roles in OpenStack-Ansible retrieve dependencies from the
public Internet by default. Many deployers block direct outbound connectivity
to the Internet when implementing network security measures. We recommend a
set of practices and configuration overrides deployers can use when running
OpenStack-Ansible in network environments that block Internet connectivity.

The options below are not mutually exclusive and may be combined if desired.

Example internet dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Software packages
- LXC container images
- Source code repositories
- GPG keys for package validation

Practice A: Mirror internet resources locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may choose to operate and maintain mirrors of OpenStack-Ansible and
OpenStack dependencies. Mirrors often provide a great deal of risk mitigation
by reducing dependencies on resources and systems outside of your direct
control. Mirrors can also provide greater stability, performance and security.

Software package repositories
-----------------------------

Many packages used to run OpenStack are installed using `pip`. We advise
mirroring the PyPi package index used by `pip`.

Many software packages are installed on the target hosts using `.deb`
packages. We advise mirroring the repositories that host these packages.

Ubuntu repositories to mirror:

- xenial
- xenial-updates

Galera-related repositories to mirror:

- https://mirror.rackspace.com/mariadb/repo/10.0/ubuntu
- https://repo.percona.com/apt

These lists are intentionally not exhaustive. Consult the OpenStack-Ansible
playbooks and role documentation for further repositories and the variables
that may be used to override the repository location.

LXC container images
--------------------

OpenStack-Ansible relies upon community built LXC images when building
containers for OpenStack services. Deployers may choose to create, maintain,
and host their own container images. Consult the
``openstack-ansible-lxc_container_create`` role for details on configuration
overrides for this scenario.

Source code repositories
------------------------

OpenStack-Ansible relies upon Ansible Galaxy to download Ansible roles when
bootstrapping a deployment host. Deployers may wish to mirror the dependencies
that are downloaded by the ``bootstrap-ansible.sh`` script.

Deployers can configure the script to source Ansible from an alternate Git
repository by setting the environment variable ``ANSIBLE_GIT_REPO``.

Deployers can configure the script to source Ansible role dependencies from
alternate locations by providing a custom role requirements file and specifying
the path to that file using the environment variable ``ANSIBLE_ROLE_FILE``.

Practice B: Proxy access to internet resources
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configure target and deployment hosts to reach public internet resources via
HTTP or SOCKS proxy server(s). OpenStack-Ansible may be used to configure
target hosts to use the proxy server(s). OpenStack-Ansible does not provide
automation for creating the proxy server(s).

.. note::

   We recommend you set your ``/etc/environment`` variables with proxy
   settings before launching any scripts or playbooks to avoid failure.

Basic proxy configuration
-------------------------

The following configuration configures most network clients on the target
hosts to connect via the specified proxy. For example, these settings
affect:

- Most Python network modules
- `curl`
- `wget`
- `openstack`

Use the ``no_proxy`` environment variable to specify hosts that you cannot
reach through the proxy. These often are the hosts in the management network.
In the example below, ``no_proxy`` is set to localhost only, but the default
configuration file suggests using variables to list all the hosts/containers'
management addresses as well as the load balancer internal/external addresses.

Configuration changes are made in ``/etc/openstack_deploy/user_variables.yml``.

.. code-block:: yaml

      # Used to populate /etc/environment
      global_environment_variables:
         HTTP_PROXY: "http://proxy.example.com:3128"
         HTTPS_PROXY: "http://proxy.example.com:3128"
         NO_PROXY: "localhost,127.0.0.1"
         http_proxy: "http://proxy.example.com:3128"
         https_proxy: "http://proxy.example.com:3128"
         no_proxy: "localhost,127.0.0.1"

``apt-get`` proxy configuration
-------------------------------

See `Setting up apt-get to use a http-proxy`_

.. _Setting up apt-get to use a http-proxy: https://help.ubuntu.com/community/AptGet/Howto#Setting_up_apt-get_to_use_a_http-proxy

Deployment host proxy configuration for bootstrapping Ansible
-------------------------------------------------------------

Configure the ``bootstrap-ansible.sh`` script used to install Ansible and
Ansible role dependencies on the deployment host to use a proxy by setting the
environment variables ``HTTPS_PROXY`` or ``HTTP_PROXY``.

Considerations when proxying TLS traffic
----------------------------------------

Proxying TLS traffic often interferes with the clients ability to perform
successful validation of the certificate chain. Various configuration
variables exist within the OpenStack-Ansible playbooks and roles that allow a
deployer to ignore these validation failures. Find an example
``/etc/openstack_deploy/user_variables.yml`` configuration below:

.. code-block:: yaml

      pip_validate_certs: false
      galera_package_download_validate_certs: false

The list above is intentionally not exhaustive. Additional variables may exist
within the project and will be named using the `*_validate_certs` pattern.
Disable certificate chain validation on a case by case basis and only after
encountering failures that are known to only be caused by the proxy server(s).
