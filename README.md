# ansible-mikrotik
<h1>Ansible Roles</h1>
mtk-ros-upgrade is a role that when used will check that ROS is updated and if not will get the router upgraded<br>
!<br>
mtk-firmware-upgrade is a role that when used will upgrade the firware on a Mikrotik<br>
!<br>
mtk-ssh-keys is a role that when used will create an RSA keypair on the Ansible host, and install the public key on a MTK device<br>
!<br>
mtk-password is a role that when used will update the password for a supplied user<br><br>
<h1>Ansible Playbooks</h1><br><br>
mtk-wlan2-ani enables adaptive noise immunity on wlan2(usually the 5ghz radio)<br>
!<br>
mtk-wlan2-power drastically lowers power on wlan2 by setting its dBi on the interface artifically high and setting it to indoor<br>
!<br>
mtk-wlan2-tuning enables a whole host of tweaks for the wlan2 radio<br>
!<br>
mtk-switch-interface-desc loops through a switch looking at the neighbor table.  It filters the table by type ether for copper<br>
interfaces.  It also looks for devices that start with "Room" as their identity.  I set the CPEs in the rooms to be named Room101, <br>
Room205, etc.  So adjust the filters as you need.  It then loops through each neighbor entry and updates the physical interface<br>
description so that it's easy to see which device is connected to which switch port.
