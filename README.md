# ansible-mikrotik
<h1>Ansible Roles</h1>
mtk-ros-upgrade is a role that when used will check that ROS is updated and if not will get the router upgraded<br>
!<br>
mtk-firmware-upgrade is a role that when used will upgrade the firware on a Mikrotik<br>
!<br>
mtk-ssh-keys is a role that when used will create an RSA keypair on the Ansible host, and install the public key on a MTK device<br>
!<br>
mtk-password is a role that when used will update the password for a supplied user<br>
!<br>
mtk-dude-backup is a role that will backup the database on a router based dude install and FTP it off<br><br>
<h1>Ansible Playbooks</h1><br><br>
mtk-wlan2-ani enables adaptive noise immunity on wlan2(usually the 5ghz radio)<br>
!<br>
mtk-wlan2-power drastically lowers power on wlan2 by setting its dBi on the interface artificially high and setting it to indoor<br>
!<br>
mtk-wlan2-tuning enables a whole host of tweaks for the wlan2 radio<br>
!<br>
mtk-switch-interface-desc loops through a switch looking at the neighbor table.  It filters the table by type ether for copper<br>
interfaces.  It also looks for devices that start with "Room" as their identity.  I set the CPEs in the rooms to be named Room101, <br>
Room205, etc.  So adjust the filters as you need.  It then loops through each neighbor entry and updates the physical interface<br>
description so that it's easy to see which device is connected to which switch port.<br>
!<br>
mtk-probe-tshoot-file.yml - Connects to test probes and pings/traceroutes for a destination IP, then saves it into a single file.<br>
If you also specify a source address it will ping/trace to that also and add it to the file.<br>
!<br>
mtk-probe-tshoot-screen.yml - Connects to test probes and pings/traceroutes for a destination IP, then displays it to the screen.<br>
If you also specify a source address it will ping/trace to that also and add it the screen display.<br>
!<br>
mtk-probe-tshoot-notification-api.yml - Connects to test probes and pings/traceroutes for a destination IP, then displays it to the screen.<br>
If you also specify a source address it will ping/trace to that also and then send the info either via email or slack.  This is picked via the "method" variable by setting it to slack or email.  I'm using this with tower and passing destIP over via extra vars.  While calling this with the tower API be sure to set extra_variables to "prompt on run" otherwise the playbook won't accept variables sent via extra_vars.<br>
