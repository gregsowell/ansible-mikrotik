Role Name
=========

This performs a database backup of a router based dude server via FTP.

Role Variables
--------------

# what to name the backup file
    bup_file: home-dude
#increase the timeout for larger dude directories
    ansible_command_timeout: 120
#ftp username/password details
    ftp_user: ftp
    ftp_pass: ftp
#where to save the file on the local server
    ftp_dest: /etc/ansible/backups/

Dependencies
------------

This utilizes the FTP module found here: https://github.com/melmorabity/ansible-ftp

Example Playbook
----------------

    - hosts: My_Dude
      roles:
         - role: mtk-dude-backup
           bup_file: home-dude
           ansible_command_timeout: 120
           ftp_user: ftp
           ftp_pass: ftp
           ftp_dest: /etc/ansible/backups/
           
License
-------

BSD

Author Information
------------------

Greg Sowell - GregSowell.com - TheBrothersWISP.com
