Robonomics on Tezos
===================

Robonomics network proof of concept for Tezos platform.

Install and run
---------------

    nix build -f release.nix
    source result/setup.bash
    roslaunch robonomics_tz listener.launch

Useful links
------------

* Factory smart-contract: [KT1KspVr8U7QL7EyLYqTf5AomnQB6a9jZ1hs](https://alphanet.tzscan.io/KT1KspVr8U7QL7EyLYqTf5AomnQB6a9jZ1hs)
* Smart-contract interaction: [demo video](https://cloud.mail.ru/public/5siR/wi9S3BjHa)
* ROS listener node: [demo video](https://cloud.mail.ru/public/3vFt/43w88DGoL)

**Notice: this repo use code parts of projects:**

* [pytezos](https://github.com/murbard/pytezos)
* [netstruct](https://pypi.org/project/netstruct/)
