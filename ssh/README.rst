Example SSH config file
#######################
:date: 2013-09-05 09:51
:tags: rackspace, lxc, openstack, cloud, ansible
:category: \*nix


Adding the option in your ssh config file will allow ansible to function without verifying host keys.
While this is great for testing and or use where you don't want to be prompted, I **would not** recommend 
using this option in production. 
