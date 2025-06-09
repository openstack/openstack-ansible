.. _quickstart-aio:

===============
Quickstart: AIO
===============

All-in-one (AIO) builds are a great way to perform an OpenStack-Ansible build
for:

* a development environment
* an overview of how all of the OpenStack services fit together
* a simple lab deployment

Although AIO builds aren't recommended for large production deployments,
they're great for smaller proof-of-concept deployments.

Absolute minimum server resources (currently used for gate checks):

* 8 vCPU's
* 50GB free disk space on the root partition
* 8GB RAM

Recommended server resources:

* CPU/motherboard that supports `hardware-assisted virtualization`_
* 8 CPU Cores
* 80GB free disk space on the root partition, or 60GB+ on a blank
  secondary disk. Using a secondary disk requires the use of the
  ``bootstrap_host_data_disk_device`` parameter. Please see
  :ref:`building-an-aio` for more details.
* 16GB RAM

It is `possible` to perform AIO builds within a virtual machine for
demonstration and evaluation, but your virtual machines will perform poorly
unless nested virtualization is available. For production workloads, multiple
nodes for specific roles are recommended.

.. _hardware-assisted virtualization: https://en.wikipedia.org/wiki/Hardware-assisted_virtualization

.. _building-an-aio:

Building an AIO
---------------

Overview
~~~~~~~~

There are three steps to running an AIO build, with an optional first step
should you need to customize your build:

* Prepare the host
* Bootstrap Ansible and the required roles
* Bootstrap the AIO configuration
* Run playbooks

Prepare the host
~~~~~~~~~~~~~~~~

When building an AIO on a new server, it is recommended that all
system packages are upgraded and then reboot into the new kernel:

.. note:: Execute the following commands and scripts as the root user.

.. code-block:: shell-session

   ## Ubuntu / Debian
   # apt-get update
   # apt-get dist-upgrade
   # reboot

.. code-block:: shell-session

   ## CentOS Stream / Rocky Linux
   # dnf upgrade
   # dnf install git-core
   # systemctl stop firewalld
   # systemctl mask firewalld
   # reboot

.. note::

   Before rebooting, in ``/etc/sysconfig/selinux``, make sure that
   ``SELINUX=enforcing`` is changed to ``SELINUX=disabled``.
   SELinux enabled is not currently supported in OpenStack-Ansible
   for CentOS Stream or Rocky Linux due to a lack of maintainers for the feature.

.. note::

   If you are installing with limited connectivity, please review :ref:`Installing
   with limited connectivity <limited-connectivity>` before proceeding.

Bootstrap Ansible and the required roles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Start by cloning the OpenStack-Ansible repository and changing into the
repository root directory:

.. code-block:: shell-session

   # git clone https://opendev.org/openstack/openstack-ansible \
       /opt/openstack-ansible
   # cd /opt/openstack-ansible

Next switch the applicable branch/tag to be deployed from. Note that
deploying from the head of a branch may result in an unstable build due to
changes in flight and upstream OpenStack changes. For a test (for example,
not a development) build it is usually best to checkout the latest tagged
version.

.. parsed-literal::

   # # List all existing tags.
   # git tag -l

   # # Checkout the stable branch and find just the latest tag
   # git checkout |current_release_git_branch_name|
   # git describe --abbrev=0 --tags

   # # Checkout the latest tag from either method of retrieving the tag.
   # git checkout |latest_tag|

.. note::
   The |current_release_formal_name| release is only compatible with
   Debian 12 (bookworm) and Ubuntu 24.04 (Noble Numbat).

The next step is to bootstrap Ansible and the Ansible roles for the
development environment.

Run the following to bootstrap Ansible and the required roles:

.. code-block:: shell-session

   # scripts/bootstrap-ansible.sh

.. note::
  You might encounter an error while running the Ansible bootstrap script
  when building some of the Python extensions (like pycrypto) which says:

  .. code-block:: shell-session

     configure: error: cannot run C compiled programs.

  The reason of this failure might be resulting from a noexec mount flag
  used for the filesystem associated with /tmp which you can check by
  running the following command:

  .. code-block:: shell-session

     # mount | grep $(df /tmp | tail -n +2 | awk '{print $1}') | grep noexec

  If this is the case you can specify an alternate path which does not
  have this mount option set:

  .. code-block:: shell-session

     # TMPDIR=/var/tmp scripts/bootstrap-ansible.sh

Bootstrap the AIO configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order for all the services to run, the host must be prepared with the
appropriate disks partitioning, packages, network configuration and
configurations for the OpenStack Deployment.

By default the AIO bootstrap scripts deploy a base set of OpenStack services
with sensible defaults for the purpose of a gate check, development or testing
system.

Review the `bootstrap-host role defaults`_ file to see various configuration
options. Deployers have the option to change how the host is bootstrapped.
This is useful when you wish the AIO to make use of a secondary data disk,
or when using this role to bootstrap a multi-node development environment.

.. _bootstrap-host role defaults: https://opendev.org/openstack/openstack-ansible/src/tests/roles/bootstrap-host/defaults/main.yml

The bootstrap script is pre-set to pass the environment variable
``BOOTSTRAP_OPTS`` as an additional option to the bootstrap process. For
example, if you wish to set the bootstrap to re-partition a specific
secondary storage device (``/dev/sdb``), which will erase all of the data
on the device, then execute:

.. code-block:: shell-session

   # export BOOTSTRAP_OPTS="bootstrap_host_data_disk_device=sdb"

Additional options may be implemented by simply concatenating them with
a space between each set of options, for example:

.. code-block:: shell-session

   # export BOOTSTRAP_OPTS="bootstrap_host_data_disk_device=sdb"
   # export BOOTSTRAP_OPTS="${BOOTSTRAP_OPTS} bootstrap_host_data_disk_fs_type=xfs"

If you are installing with limited connectivity, or you don't have default
route set, you will need to define interface for outgoing connections manually

.. code-block:: shell-session

   # export BOOTSTRAP_OPTS="bootstrap_host_public_interface=eth1"

For the default AIO scenario, the AIO configuration preparation is completed by
executing:

.. code-block:: shell-session

   # scripts/bootstrap-aio.sh

To add OpenStack Services over and above the bootstrap-aio default services
for the applicable scenario, copy the ``conf.d`` files with the ``.aio`` file
extension into ``/etc/openstack_deploy`` and rename then to ``.yml`` files.
For example, in order to enable the OpenStack Telemetry services, execute the
following:

.. code-block:: shell-session

   # cd /opt/openstack-ansible/
   # cp etc/openstack_deploy/conf.d/{aodh,gnocchi,ceilometer}.yml.aio /etc/openstack_deploy/conf.d/
   # for f in $(ls -1 /etc/openstack_deploy/conf.d/*.aio); do mv -v ${f} ${f%.*}; done

It is possible to also do this (and change other defaults) during the bootstrap
script initial execution by changing the SCENARIO environment variable before
running the script. The key word 'aio' will ensure that a basic set of
OpenStack services (cinder, glance, horizon, neutron, nova) will be deployed.
The key words 'lxc' can be used to set the container back-end,
while the key word 'metal' will deploy all services without containers. In
order to implement any other services, add the name of the conf.d file name
without the `.yml.aio` extension into the SCENARIO environment variable. Each
key word should be delimited by an underscore. For example, the following will
implement an AIO with barbican, cinder, glance, horizon, neutron, and nova. It
will set the cinder storage back-end to ceph and will make use of LXC as the
container back-end.

.. code-block:: shell-session

   # export SCENARIO='aio_lxc_barbican_ceph_ovs'
   # scripts/bootstrap-aio.sh

To add any global overrides, over and above the defaults for the applicable
scenario, edit ``/etc/openstack_deploy/user_variables.yml``. In order to
understand the various ways that you can override the default behaviour
set out in the roles, playbook and group variables, see :ref:`user-overrides`.

See the :deploy_guide:`Deployment Guide <index.html>` for a more detailed break
down of how to implement your own configuration rather than to use the AIO
bootstrap.

Run playbooks
~~~~~~~~~~~~~

Finally, run the playbooks by executing:

.. code-block:: shell-session

   # openstack-ansible openstack.osa.setup_hosts
   # openstack-ansible openstack.osa.setup_infrastructure
   # openstack-ansible openstack.osa.setup_openstack

The installation process will take a while to complete, but here are some
general estimates:

* Bare metal systems with SSD storage: ~ 30-50 minutes
* Virtual machines with SSD storage: ~ 45-60 minutes
* Systems with traditional hard disks: ~ 90-120 minutes

Once the playbooks have fully executed, it is possible to experiment with
various settings changes in ``/etc/openstack_deploy/user_variables.yml`` and
only run individual playbooks. For example, to run the playbook for the
Keystone service, execute:

.. code-block:: shell-session

   # cd /opt/openstack-ansible/playbooks
   # openstack-ansible os-keystone-install.yml

Interacting with an AIO
-----------------------

Once an AIO has been deployed, you most likely want to interact with it. You
can do this via the web interface or one of the many clients or libraries that
exist for OpenStack.

Using a GUI
~~~~~~~~~~~

The Horizon web interface provides a graphical interface for interacting with
the AIO deployment. By default, the Horizon API is available on port 443 of the
host (or port 80, if SSL certificate configuration was disabled). As such, to
interact with Horizon, simply browse to the IP of the host.

.. note::

   If the AIO was deployed in a cloud VM, you may need to configure security
   groups or firewall rules to allow access to the HTTP(S) ports. For example,
   if the AIO was deployed in an OpenStack VM, you can create and apply a
   suitable security group for interacting with Horizon like so:

   .. code-block:: shell-session

      $ openstack security group create http \
          --description 'Allow HTTP and HTTPS access'
      $ openstack security group rule create http \
          --protocol tcp --dst-port 80 --remote-ip 0.0.0.0/0
      $ openstack security group rule create http \
          --protocol tcp --dst-port 443 --remote-ip 0.0.0.0/0
      $ openstack server add security group $SERVER http

   A list of service ports can be found in the `OpenStack Install Guide`__.

   .. __: https://docs.openstack.org/install-guide/firewalls-default-ports.html

This will present a login page. By default, OpenStack-Ansible create a user
called ``admin``. The password will be the value of the
``keystone_auth_admin_password`` variable. If you did not configure this
variable, OpenStack-Ansible auto-generates one. You can view the configured
password in the ``/etc/openstack_deploy/user_secrets.yml`` file.

.. code-block:: shell-session

   # grep admin_pass /etc/openstack_deploy/user_secrets.yml
   heat_stack_domain_admin_password: <redacted>
   keystone_auth_admin_password: <redacted>
   radosgw_admin_password: <redacted>

Using this username and password combination, log in to Horizon.

Using a client or library
~~~~~~~~~~~~~~~~~~~~~~~~~

There are a variety of clients and libraries available for interacting with an
OpenStack deployment, including as `openstackclient`__, `openstacksdk`__, or
`gophercloud`__. These are typically configured using either environment
variables sourced from an ``openrc`` file or the newer ``clouds.yaml`` file.

.. __: https://opendev.org/openstack/python-openstackclient
.. __: https://opendev.org/openstack/openstacksdk
.. __: https://github.com/gophercloud/gophercloud

OpenStack-Ansible provides the ``openstack_openrc`` role for creating these
configuration files as well as a number of utilities such as *openstackclient*.
If the AIO deployment using the ``lxc`` scenario (the default), these will be
availably in the utility container.

.. code-block:: shell-session

   $ lxc-attach -n `lxc-ls -1 | grep utility`

   # ls /root/openrc
   /root/openrc

   # ls /root/.config/openstack/clouds.yaml
   /root/.config/openstack/clouds.yaml

   # export OS_CLOUD=default
   # openstack project list -c Name -f value
   service
   admin

Alternatively, if the AIO was deployed using the ``metal`` scenario, these
files will be available on the host itself.

.. code-block:: shell-session

   # ls /root/openrc
   /root/openrc

   # ls /root/.config/openstack/clouds.yaml
   /root/.config/openstack/clouds.yaml

If you wish to access the AIO deployment from another host - perhaps your local
workstation - you will need either an ``openrc`` file or ``clouds.yaml`` file.
You can download an ``openrc`` file from Horizon: simply click the User
dropdown in the top-right corner and select ``OpenStack RC File``.

.. important::

   You may be tempted to copy the ``openrc`` or ``clouds.yaml`` files created
   by the ``openstack_openrc`` role. However, these files use the ``internal``
   `interface`__ by default. This interface use the management network
   (``172.29.236.0/22``) , which is not routable from outside the host. If you
   wish to use these files, you will need to change the interface to
   ``public``.

   .. __: https://docs.openstack.org/keystone/latest/contributor/service-catalog.html#endpoints

.. note::

   If the AIO was deployed in a cloud VM, you may need to configure security
   groups or firewall rules to allow access to the various sevice ports. For
   example, if the AIO was deployed in an OpenStack VM, you can create and
   apply a suitable security group for interacting the core services like so:

   .. code-block:: shell-session

      $ openstack security group create openstack-apis \
          --description 'Allow access to various OpenStack services'
      $ for port in 8774 8776 9292 9696 5000 8780; do
          openstack security group rule create openstack-apis \
            --protocol tcp --dst-port ${port}:${port} --remote-ip 0.0.0.0/0
        done
      $ openstack server add security group $SERVER openstack-apis

   A list of service ports can be found in the `OpenStack Install Guide`__.

   .. __: https://docs.openstack.org/install-guide/firewalls-default-ports.html

.. note::

   If you have enabled SSL certificate configuration (default), all services
   will use self-signed certificates. While the host is configured to trust
   these certificates, this is not the case for other hosts. This will result
   in HTTPS errors when attempting to interact with the cloud. To resolve this
   issue, you will need to manually configure certificates on other hosts or
   ignore SSL issues. To use the self-signed certificate, first copy it to the
   other hosts. The name and location of the generated certificate are
   configured by the ``pki_authorities`` and ``pki_trust_store_location``
   variables respectively, which are used by the ``pki`` role provided by
   `ansible-role-pki`__. On an Ubuntu 24.04 host, these will default to
   ``ExampleCorpRoot`` and ``/usr/local/share/ca-certificates``, respectively.
   For example:

   .. code-block:: shell-session

      $ scp aio:/usr/local/share/ca-certificates/ExampleCorpRoot.crt ~/.config/openstack/aio.crt

   .. __: https://opendev.org/openstack/ansible-role-pki

   Once this is done, configure the ``cacert`` value in the the definition for
   your cloud in ``clouds.yaml``. For example:

   .. code-block:: yaml

      clouds:
        aio:
          # ...
          cacert: /home/<username>/.config/openstack/aio.crt

   Alternatively, you can simply ignore SSL issues by setting ``verify: false``
   in the definition for your cloud in ``clouds.yaml``. This will disable SSL
   verification entirely for this cloud. For example:

   .. code-block:: yaml

      clouds:
        aio:
          # ...
          verify: false

   Finally, you can also opt to disable SSL certificate configuration during
   initial deployment or opt to use an external certificate authority for
   signing, such as Let's Encrypt. Both topics are outside the scope of this
   document.

   More information about SSL certificate configuration can be found in the
   :ref:`securing-services-with-ssl-certificates`.

Once one of these files have been created, you can use it to interact with your
deployment using most standard clients and libraries. For example, to list
available projects using *openstackclient*:

.. code-block:: shell-session

   $ export OS_CLOUD=aio
   $ openstack project list -c Name -f value
   service
   admin

Rebooting an AIO
----------------

As the AIO includes all three cluster members of MariaDB/Galera, the cluster
has to be re-initialized after the host is rebooted.

This is done by executing the following:

.. code-block:: shell-session

   # cd /opt/openstack-ansible/playbooks
   # openstack-ansible -e galera_ignore_cluster_state=true galera-install.yml

If this fails to get the database cluster back into a running state, then
please make use of the :ref:`galera-cluster-recovery`
section in the :ref:`operations-guide`.

Rebuilding an AIO
-----------------

Sometimes it may be useful to destroy all the containers and rebuild the AIO.
While it is preferred that the AIO is entirely destroyed and rebuilt, this
isn't always practical. As such the following may be executed instead:

.. code-block:: shell-session

   # # Move to the playbooks directory.
   # cd /opt/openstack-ansible/playbooks

   # # Destroy all of the running containers.
   # openstack-ansible lxc-containers-destroy.yml

   # # On the host stop all of the services that run locally and not
   # #  within a container.
   # for i in \
          $(ls /etc/init \
            | grep -e "nova\|swift\|neutron\|cinder" \
            | awk -F'.' '{print $1}'); do \
       service $i stop; \
     done

   # # Uninstall the core services that were installed.
   # for i in $(pip freeze | grep -e "nova\|neutron\|keystone\|swift\|cinder"); do \
       pip uninstall -y $i; done

   # # Remove crusty directories.
   # rm -rf /openstack /etc/{neutron,nova,swift,cinder} \
            /var/log/{neutron,nova,swift,cinder}

   # # Remove the pip configuration files on the host
   # rm -rf /root/.pip

   # # Remove the apt package manager proxy
   # rm /etc/apt/apt.conf.d/00apt-cacher-proxy

Should an existing AIO environment need to be reinstalled, the most efficient
method is to destroy the host operating system and start over. For this reason,
AIOs are best run inside of some form of virtual machine or cloud guest.

Reference Diagram for an AIO Build
----------------------------------

Here is a basic diagram that attempts to illustrate what the resulting AIO
deployment looks like.

This diagram is not to scale and is not even 100% accurate, this diagram was
built for informational purposes only and should **ONLY** be used as such.

.. code-block:: text

              ------->[ ETH0 == Public Network ]
              |
              V                        [  *   ] Socket Connections
    [ HOST MACHINE ]                   [ <>v^ ] Network Connections
      *       ^  *
      |       |  |-------------------------------------------------------
      |       |                                                         |
      |       |---------------->[ HAProxy ]                             |
      |                                 ^                               |
      |                                 |                               |
      |                                 V                               |
      |                          (BR-Interfaces)<------                 |
      |                                  ^     *      |                 |
      *-[ LXC ]*--*----------------------|-----|------|----|            |
      |           |                      |     |      |  | |            |
      |           |                      |     |      |  | |            |
      |           |                      |     |      |  | |            |
      |           |                      |     |      V  * |            |
      |           *                      |     |   [ Galera x3 ]        |
      |        [ Memcached ]<------------|     |           |            |
      *-------*[ Rsyslog ]<--------------|--|  |           *            |
      |        [ Repos Server x3 ]<------|  ---|-->[ RabbitMQ x3 ]      |
      |        [ Horizon x2 ]<-----------|  |  |                        |
      |        [ Nova api ec2 ]<---------|--|  |                        |
      |        [ Nova api os ]<----------|->|  |                        |
      |        [ Nova console ]<---------|  |  |                        |
      |        [ Nova Cert ]<------------|->|  |                        |
      |        [ Cinder api ]<-----------|->|  |                        |
      |        [ Glance api ]<-----------|->|  |                        |
      |        [ Heat apis ]<------------|->|  | [ Loop back devices ]*-*
      |        [ Heat engine ]<----------|->|  |    \        \          |
      | ------>[ Nova api metadata ]     |  |  |    { LVM }  { XFS x3 } |
      | |      [ Nova conductor ]<-------|  |  |       *         *      |
      | |----->[ Nova scheduler ]--------|->|  |       |         |      |
      | |      [ Keystone x3 ]<----------|->|  |       |         |      |
      | | |--->[ Neutron agents ]*-------|--|---------------------------*
      | | |    [ Neutron server ]<-------|->|          |         |      |
      | | | |->[ Swift proxy ]<-----------  |          |         |      |
      *-|-|-|-*[ Cinder volume ]*----------------------*         |      |
      | | | |                               |                    |      |
      | | | -----------------------------------------            |      |
      | | ----------------------------------------- |            |      |
      | |          -------------------------|     | |            |      |
      | |          |                              | |            |      |
      | |          V                              | |            *      |
      ---->[ Compute ]*[ Neutron OpenvSwitch ]<---| |->[ Swift storage ]-
