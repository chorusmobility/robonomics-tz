Robonomics on Tezos
===================

Robonomics network proof of concept for Tezos platform.

Install and run
---------------

Install Nix

    curl https://nixos.org/nix/install | sh

Be sure that user added to trusted users in /etc/nix/nix.conf

    trusted-users = username

Launch build process in repository core

    nix build -f release.nix --option sandbox false
    source result/setup.bash

Launch Turtle simulator
-----------------------

    roslaunch robonomics_tz turtle_sim.launch

Launch 3DR Solo drone
---------------------

    roslaunch robonomics_tz solo_drone.launch

Useful links
------------

* Factory smart-contract: [KT1KspVr8U7QL7EyLYqTf5AomnQB6a9jZ1hs](https://alphanet.tzscan.io/KT1KspVr8U7QL7EyLYqTf5AomnQB6a9jZ1hs)
* Smart-contract interaction [demo video](https://cloud.mail.ru/public/5siR/wi9S3BjHa)
* ROS listener node [demo video](https://cloud.mail.ru/public/3vFt/43w88DGoL)
* Turtlesim robot launch [demo video](https://cloud.mail.ru/public/2qxp/4f8ZLGXTS)
* 3DR Solo drone launch [demo video](https://cloud.mail.ru/public/23Wx/2D9fzRrB9)

**Notice: this repo use code parts of projects:**

* [pytezos](https://github.com/murbard/pytezos)
* [netstruct](https://pypi.org/project/netstruct/)
