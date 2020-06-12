Role Name
=========

This role reaches out to remote mikrotik routers and updates the specified user name with the supplied password.
The combo can be supplied with prompting or directly.

Requirements
------------

NA

Role Variables
--------------

usr_name = username on the Mikrotik to be changed
pword = new password to be used

Dependencies
------------

NA

Example Playbook
----------------

## Example 1 propts for username and password

---
- name: Utilize role to change Mikrotik passwords
  hosts: mtk1
  gather_facts: false

  vars_prompt:
    - name: usr_name
      prompt: "what is the username?"
      private: no

    - name: pword
      prompt: "what is the new password"
      confirm: yes


  roles:
    - mtk-password

## Example 2 specifies username and password

---
- name: Utilize role to change Mikrotik passwords
  hosts: mtk1
  gather_facts: false

  vars:
    usr_name: testUser
    pword: testPassword

  roles:
    - mtk-password


License
-------

BSD

Author Information
------------------

Greg Sowell 2020 - GregSowell.com TheBrothersWISP.com
