OpenStack Ansible Deployment
############################
:date: 2015-02-02 22:00
:tags: lxc, openstack, cloud, ansible
:category: \*nix


Building a development stack
----------------------------

If you are wanting to build a development stack for testing or otherwise contributing to this repository you can do so using the
``gate-check-commit.sh`` script in the scripts directory. To execute this script please do so from the ``os-ansible-deployment`` directory that was created when you cloned the repository.

Example AIO build process:

.. code-block:: bash

  # Clone the source code
  git clone https://github.com/stackforge/os-ansible-deployment /opt/os-ansible-deployment

  # Change your directory
  cd /opt/os-ansible-deployment

  # Checkout your desired branch.
  git checkout master

  # Run the script from the root directory of the cloned repository.
  ./scripts/gate-check-commit.sh

Alternatively, you can curl/wget the ``run-aio-build.sh`` script:

.. code-block:: bash

  bash <(curl -s http://git.openstack.org/cgit/stackforge/os-ansible-deployment/plain/scripts/run-aio-build.sh)


To use these scripts successfully please make sure that you have the following:
  * At least **60GB** of available storage on "/" when using local file system containers. Containers are built into ``/var/lib/lxc`` and will consume up-to 40GB on their own.
    * If you would like to test building containers using LVM simply create an **lxc** volume group before executing the script. Be aware that each container will be built with a minimum of 5GB of storage.
  * 2.4GHZ quad-core processor with that is KVM capable is required.
  * You must have at least 4GB of available ram.

This may seem like you need a lot to run the stack, which is partially true, however consider that this simple "All in One" deployment builds a "35" node infrastructure and mimics our reference architecture. Additionally, components like Rabbitmq, MariaDB with Galera, Repository servers, and Keystone will all be clustered. Lastly the "All in One" deployment uses HAProxy for test purposes only. **At this time we do not recommend running HAProxy in production**. At this time you should **NEVER** use the AIO script on a box that you care about. Cloud servers such as Rackspace Cloud server of the flavor *general1-8* variety work really well as development machines, as does Virtual Box of KVM instances.

Using Heat:
  If you would like to use heat to deploy an All in one node there is a heat script which you can use. Simply get and or source the raw script as found here: "https://raw.githubusercontent.com/stackforge/os-ansible-deployment/master/scripts/osad-aio-heat-template.yml"


Rebuilding the stack
^^^^^^^^^^^^^^^^^^^^

Once you have completed your testing and or dev work if you'd like to tear down the stack and restart from a new build there is a play that will assist you in doing just that. Simply change to your playbooks directory and execute the ``lxc-containers-destroy.yml`` play.

Example:

.. code-block:: bash

  # Move to the playbooks directory.
  cd /opt/os-ansible-deployment/playbooks

  # Destroy all of the running containers.
  openstack-ansible lxc-containers-destroy.yml

  # On the host stop all of the services that run locally and not within a container.
  for i in $(ls /etc/init | grep -e nova -e swift -e neutron | awk -F'.' '{print $1}'); do service $i stop; done

  # Uninstall the core services that were installed.
  for i in $(pip freeze | grep -e nova -e neutron -e keystone -e swift); do pip uninstall -y $i; done

  # Remove crusty directories.
  rm -rf /openstack /etc/neutron /etc/nova /etc/swift /var/log/neutron /var/log/nova /var/log/swift


Using the teardown script:
  The ``teardown.sh`` script that will destroy everything known within an environment. You should be aware that this script will destroy whole environments and should be used **WITH CAUTION**.


Notice
^^^^^^

The system uses a number of variables. You should look a the scripts for a full explanation and description of all of the available variables that you can set. At a minimum you should be aware of the default public interface variable as you may be kicking on a box that does not have an ``eth0`` interface. To set the default public interface run the following.

.. code-block:: bash

    export PUBLIC_INTERFACE="<<REPLACE WITH THE NAME OF THE INTERFACE>>" # This is only required if you dont have eth0


This play will destroy all of your running containers and remove items within the ``/openstack`` directory for the container. After the completion of this play you can rerun the ``cloudserver-aio.sh`` or you can run the plays manually to rebuild the stack.


Diagram of stack
^^^^^^^^^^^^^^^^

Here is a basic diagram that attempts to illustrate what the AIO installation job is doing. **NOTICE** This diagram is not to scale and is not even 100% accurate, this diagram was built for informational purposes only and should **ONLY** be used as such.


Diagram::

    ====== ASCII Diagram for AIO infrastructure ======

              ------->[ ETH0 == Public Network ]
              |
              V                        [  *   ] Socket Connections
    [ HOST MACHINE ]                   [ <>v^ ] Network Connections
      *       ^  *
      |       |  |-----------------------------------------------------
      |       |                                                       |
      |       |---------------->[ HAProxy ]                           |
      |                                 ^                             |
      |                                 |                             |
      |                                 V                             |
      |                          (BR-Interfaces)<-----                |
      |                                ^     *      |                 |
      *-[ LXC ]*--*--------------------|-----|------|----|            |
      |           |                    |     |      |  | |            |
      |           |                    |     |      |  | |            |
      |           |                    |     |      |  | |            |
      |           |                    |     |      V  * |            |
      |           *                    |     |   [ Galera x3 ]        |
      |        [ Memcached ]<----------|     |           |            |
      *-------*[ Rsyslog ]<------------|--|  |           *            |
      |        [ Repos Server x3 ]<----|  ---|-->[ RabbitMQ x3 ]      |
      |        [ Horizon ]<------------|  |  |                        |
      |        [ Nova api ec2 ]<-------|--|  |                        |
      |        [ Nova api os ]<--------|->|  |                        |
      |        [ Nova spice console ]<-|  |  |                        |
      |        [ Nova Cert ]<----------|->|  |                        |
      |        [ Cinder api ]<---------|->|  |                        |
      |        [ Glance api ]<---------|->|  |                        |
      |        [ Heat apis ]<----------|->|  | [ Loop back devices ]*-*
      |        [ Heat engine ]<--------|->|  |    \        \          |
      | ------>[ Nova api metadata ]   |  |  |    { LVM }  { XFS x3 } |
      | |      [ Nova conductor ]<-----|  |  |       *         *      |
      | |----->[ Nova scheduler ]------|->|  |       |         |      |
      | |      [ Keystone x3 ]<--------|->|  |       |         |      |
      | | |--->[ Neutron agents ]*-----|--|---------------------------*
      | | |    [ Neutron server ]<-----|->|          |         |      |
      | | | |->[ Swift proxy ]<---------  |          |         |      |
      *-|-|-|-*[ Cinder volume ]*--------------------*         |      |
      | | | |                             |                    |      |
      | | | ---------------------------------------            |      |
      | | --------------------------------------- |            |      |
      | |          -----------------------|     | |            |      |
      | |          |                            | |            |      |
      | |          V                            | |            *      |
      ---->[ Compute ]*[ Neutron linuxbridge ]<-| |->[ Swift storage ]-


    ====== ASCII Diagram for AIO infrastructure ======
