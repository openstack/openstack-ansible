Federation Questions and Answers
================

Are the procedures to make keystone into a Service Provider (SP) or Identity Provider (IdP) run during the install process or after RPC is installed?

They can be configured beforehand or after the fact. Introduction of SSL certificates to a running deployment can break things. Using SSL certificates is required for an SP using an ADFS IDP, but is not required when the SP is using a Keystone IDP.

Not counting SSL changes, it is perfectly safe to deploy a standard keystone, and then later when you are ready add the config bits for IdP and/or SP and just re-run the keystone play (and the horizon play as well, if you are doing ADFS).


How many SPs and IdPs are necessary/possible? Can Keystone be both?

As many as you like. We haven’t scale tested anything, but any Keystone can be an IDP and an SP.

The configuration allows a list of IdPs to be configured on a keystone SP, and a list of SPs to be configured on a keystone IdP. I believe we still have a limitation that we can only have one ADFS IdP hooked up to a keystone SP (Jesse, correct me if I’m wrong). No such limitation exists when you use keystone IdPs.


What are the differences in process if using AD (besides setting up AD as an IdP)?

Using ADFS as an IDP for a Keystone SP requires the deployment of SSL certificates for the public endpoint, and slightly different keystone_sp settings. 

Any more prerequisites for Keystone to Keystone Federation besides multiple RPC v11.1 installations?

There are no additional requirements besides those installed by the playbook itself, it’s all configuration.


What are the actual steps for the following (Keystone IDP)?

Add the settings to user_variables.yml, then run the os-keystone-install.yml play. I’ve updated the docs to reflect where the settings go.

There are a few examples in the rcbops/rpc-federation-docs repo, and also in the comments of the keystone defaults file at stackforge/os-ansible-deployment/playbooks/roles/os_keystone/defaults/main.yml.


Are the config files manually updated (if so, what do you run to get them incorporated) or do you use commands (like in scenario-kfs006.rst)?

Yes. If the initial settings are right, no other configuration is required via the CLI. The CLI may be used to overwrite configuration put into place by Ansible so they’ve been included for reference.

This is probably a bit confusing if you haven’t been doing this full time for the last few weeks. The keystone playbook is able to apply the full configuration for IdP and SP, but only when it is doing it as an initial configuration. Due to a limitation in the keystone client that the playbook uses, it is currently not possible to make modifications after the initial configuration has been set up. If you need to make modifications, then you can use the docs to learn how to work with the openstack CLI.

Also, at risk of confusing you even more, a trick I’ve been using to partially workaround the limitation in the ansible keystone client, is to just use the openstack CLI to delete whatever entity i want to modify, and then run the playbook, which now will create it again from scratch. This is easier for me than having to remember openstack CLI command lines, specially the one for the mappings.

Note that the domain/project/group/role and attribute mappings only apply to the Keystone SP, not the IDP. The IDP is very simple to setup and only involves the keystone_idp dictionary attribute.

