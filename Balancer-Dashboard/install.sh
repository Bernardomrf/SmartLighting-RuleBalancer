#!/bin/sh

if [ $(id -u) != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi


# Install requirements
apt install -y python3-pip
pip3 install -r requirements.txt


# Add user
# There is no need, has to be root anyway to allow to use port 80
# useradd gw-gui


# Copy code
mkdir -p /opt/balancer-dashboard/
cp -a ./* /opt/balancer-dashboard/
chmod +x /opt/balancer-dashboard/manage.py

# chown -R gw-gui:gw-gui /opt/gw-gui/


# Create pid and log files
touch /var/run/balancer-dashboard.pid /var/log/balancer-dashboard.log
# chown gw-gui:gw-gui /var/run/gw-gui.pid /var/log/gw-gui.log


# Copy service script, add to start up and start it
cp balancer-dashboard /etc/init.d/balancer-dashboard
chmod +x /etc/init.d/balancer-dashboard

update-rc.d balancer-dashboard defaults

systemctl daemon-reload

service balancer-dashboard restart
