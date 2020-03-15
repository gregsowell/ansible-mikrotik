Role Name
=========

When a new version of ROS is installed on a mikrotik device it will also include a new routerboard firmware.  This firmware isn't installed by default, though.
This role will check if the device has a newer firmware version available and if it is it will mark it for upgrade, then reboot the device.

Requirements
------------

NA

Role Variables
--------------

NA

Dependencies
------------

NA

Example Playbook
----------------

---
- name: Check routerboard firmware and upgrade if needed
  hosts: mtk1
  gather_facts: no
  strategy: free

  roles:
    - mtk-firmware-upgrade

License
-------

BSD

Author Information
------------------

Greg Sowell 2020 - GregSowell.com / TheBrothersWISP.com
