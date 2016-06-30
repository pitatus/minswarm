# minswarm

minswarm (salt-minion swarm) is a testing tool for starting multiple salt-minions on a single host to aid in the testing for scale, or for whatever reason you need to have extra minions connected to your salt-master (don't do this in production).  The host could be a VM, container, or a bare-metal install.  minswarm has been tested on Linux, FreeBSD, & OpenBSD.

minswarm will use the default grains (characteristics of the OS/Distro) for the OS it is running on.  Although modifying grains to emulate a different OS and version are possible, this is not the intended functionality of minswarm.  minswarm is intended to allow most standard Salt functions and modules to run. ...however, remember doing 'package' calls to mulitiple minions that are running on the same host will not result in normal success.

Although minswarm does not modify OS/Distro related grains, it does allow you to report different versions of the salt-minion.  This is done via the saltver.yaml file, a sample is provided.  You can change the versions in this file to report the salt-minion versions that are important to you.  You can also add a lot more versions to this file if you choose.  minswarm will randomly select a version from this file for each salt-minion it starts.

## Setup

minswarm requires salt-minion to be pre-installed and available via the standard ``$PATH`` environment.

Both minswarm.py and saltver.yaml need to be in the same directory.  minswarm.py execution defaults to the python2 environment, if you do not have a link for python2 you may need to modify the first line of the minswarm.py file.  For example, the default python2 binary is python2.7 for OpenBSD.

Set minswarm to executable if it is not already:
```
chmod 750 minswarm.py
```
## Executing

To start a swarm of salt-minions:
```
./minswarm.py -n 50 -m 192.168.1.100 -i 1
```
this will start 50 salt-minions connecting to the salt-master at ``192.168.1.100``, with a source network of ``10.1.0.0``  Each salt-minion will report an IP address from the ``10.1.0.0`` network, randomly selecting an address from the 3rd and 4th octet.  Starting multiple smaller sessions for different networks is also possible.

Minion names (ID's) are generated using the following template:

``<OS>-<id>-<type>-<rand>``

where:
* OS is the OS grain of the host
* id is the '-i' arg, or network ID
* type is taken from an internal list at random ('bld','dev','eng','mgnt', etc)
* rand is a 4 digit string to further make the name unique

For example:
``Fedora-01-sales-q5mw``

Help is available
```
./minswarm.py -h
```
Watch your memory and cpu useage, leave room for these minions to operate.


## Example

You are wanting to connect 500 minions to your salt-master to test the configuration of your salt-master.  Your salt-master is located at ``10.12.9.3`` and you have 5 VM's with different Distro/versions setup to test with.

Copy ``minswarm.py`` and ``saltver.yaml`` to each VM.  Start minswarm on each VM as root:

__VM #1__
```
./minswary.py -n 100 -m 10.12.9.3 -i 1
```
__VM #2__
```
./minswary.py -n 100 -m 10.12.9.3 -i 2
```
__VM #3__
```
./minswary.py -n 100 -m 10.12.9.3 -i 3
```
__VM #4__
```
./minswary.py -n 100 -m 10.12.9.3 -i 4
```
__VM #5__
```
./minswary.py -n 100 -m 10.12.9.3 -i 5
```

## Cleanup

When you are finished with your testing, the salt-minions can be stopped with ``pkill``, ``killall``, or similar:
```
pkill salt-master
```

* __Note__: minswarm creates its operating environment for each salt-minion in /tmp/minswarm, completely cleaning up after your testing can/should include removing these temporary directories.  Log file for each salt-minion are found in these directories.  (don't forget to delete the minions in your master too)