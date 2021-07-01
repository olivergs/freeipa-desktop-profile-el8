# freeipa-desktop-profile-el8
FreeIPA desktop profile plugin reworked for building it in CentOS/RHEL8

For building you should have installed the idm:DL1 module and the following packages:

* rpm-build
* python3-devel
* python3-ipaserver

Then just run the script and it will build the RPMs for the version 0.0.8

It will basicly downloads the sources from https://github.com/abbra/freeipa-desktop-profile/ and then uses the freeipa-desktop-profile.spec to generate the packages
