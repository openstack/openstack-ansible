========================
Linux Container commands
========================

The following are some useful commands to manage LXC:

-  List containers and summary information such as operational state and
   network configuration:

   .. code-block:: shell-session

       # lxc-ls --fancy

-  Show container details including operational state, resource
   utilization, and ``veth`` pairs:

   .. code-block:: shell-session

       # lxc-info --name container_name

-  Start a container:

   .. code-block:: shell-session

       # lxc-start --name container_name

-  Attach to a container:

   .. code-block:: shell-session

       # lxc-attach --name container_name

-  Stop a container:

   .. code-block:: shell-session

       # lxc-stop --name container_name
