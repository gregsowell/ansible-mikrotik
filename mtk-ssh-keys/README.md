Role Name
=========

This generates an RSA key on the ansible server.  It will then FTP(FTP needs to be enabled on the router) the public key to the MTK device.
It will then create a specific user(unless it already exists) and then import the key for them.

Requirements
------------

NA

Role Variables
--------------

remote_ssh_user = This is the username that will be created/updated with the key.

Dependencies
------------

FTP module is required, but is included in the role.
# https://github.com/melmorabity/ansible-ftp is the ansible module used

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: username.rolename, x: 42 }
---
- name: create and install RSA key on routers
  hosts: mtk1
  gather_facts: false

  vars:
    # This is the user on the Mikrotik that will be created/have the key applied to.
    remote_ssh_user: admin-ssh

  roles:
    - mtk-ssh-keys

License
-------

BSD

Author Information
------------------

Greg Sowell 2020 - GregSowell.com TheBrothersWISP.com
