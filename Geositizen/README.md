# Geo citizen

![Main image](img/index.jpg?raw=true)

**Table of Contents**  

* [Manual installation](#Manual-installation)  
* [Task](#Task)
* [Steps for task complition](#Steps-for-task-complition)
* * [Requirements](#Requirements)
* [Possible problem in Centos with second network adapter](#Possible-problem-in-Centos-with-second-network-adapter)
* [Centos: initial system settings and database installing&configuration](#Centos:-initial-system-settings-and-database-installing&configuration)

## Manual installation
### Task
**Install [project](https://github.com/mentorchita/Geocit134) using Ubuntu for web and Centos for database.**

### Steps for task complition

#### Requirements

We will use Virtualbox (can be downloaded [here](https://www.virtualbox.org/wiki/Downloads) as hypervisor for Ubuntu and Centos virtual machines.
For Ubuntu we will use next version - [Ubuntu Server 20.04.3 LTS](https://releases.ubuntu.com/20.04/ubuntu-20.04.3-live-server-amd64.iso.torrent?_ga=2.115100164.244318738.1644355101-915704212.1643474286) and for Centos - [CentOS 7.9.2009](http://ftp.rz.uni-frankfurt.de/pub/mirrors/centos/7.9.2009/isos/x86_64/CentOS-7-x86_64-DVD-2009.torrent) or you can choose another source from Centos [mirrors](http://isoredirect.centos.org/centos/7/isos/x86_64/).
Donwload images, create two virtual machines. One setting we want to mention - network. As we want our virtual machines to communicate with each other and we need internet for package installing and so on, we have several options, but we recommend the next one: two virtual adapters, one configured as NAT (for internet access, but host and guest machines can't communicate through it) and another - as Host-only Adapter.

![Virtualbox_manual](img/Virtualbox_network_variants.jpg?raw=true "https://www.virtualbox.org/manual/ch06.html")

You may check the settings last adapter in Virtualbox menu (File/Host Network Manager) It should be one or more adapters created, must be present ip addresses and DHCP server enabled.

For example:

![Adapter](img/Host_Network_Manager1.jpg?raw=true)

![Dhcp server](img/Host_Network_Manager2.jpg?raw=true)


#### Possible problem in Centos with second network adapter

After Centos installation you may face one problem - only one network adapter is working.
1. Instruct the system to **list your network devices** with the command:
```
sudo nmcli d
```
![nmcli](img/nmcli.jpg?raw=true)

*(you may see one of the adapters is in "red" state, like disconnected)*

Find the network you want to configure for DHCP and copy its name.

2. Then, **open the appropriate configuration file**. Use the following command and paste the device name at the end:
```
sudo vi /etc/sysconfig/network-scripts/ifcfg-[network_device_name]
```
3. A text editor with the network configuration opens.
4. The `BOOTPROTO` line should have the value **"dhcp"** and change the `ONBOOT` line to **"yes"** to enable the network. `DEFROUTE` should be set to **"no"** in case this is the **Virtualbox Host-only Adapter's** interface, you should recognize it by ip address you set.

![interfece](img/interface.jpg?raw=true)

5. **Save** the file and exit to return to the command line.

6. Finally, **restart the network** with:

```
sudo systemctl restart
```

#### Centos: initial system settings and database installing&configuration