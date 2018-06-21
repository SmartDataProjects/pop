#!/bin/bash

# this is a hack
export INSTALL_PATH=/usr/local/pop
export LOG_PATH=/var/log/pop
export USER=cmsprod

### Where we are installing from (i.e. this directory) ###

export SOURCE=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

### Stop the daemons first ###

if [[ $(uname -r) =~ el7 ]]
then
  systemctl stop popd 2>/dev/null
else
  service popd stop 2>/dev/null
fi

echo
echo "Uninstalling pop."
echo
echo '#########################'
echo '######  LIBRARIES  ######'
echo '#########################'
echo

### Clear the directories ###

if [ -d $INSTALL_PATH ]
then
  echo "Target directory $INSTALL_PATH exists. Removing!"
  rm -rf $INSTALL_PATH
fi
echo

rm -rf $LOG_PATH

### Install python libraries ###

echo "-> Uninstalling.."

### Install the executable(s) ###

echo " Done."
echo

### Install the configs ###

# Init script

echo " Done."
echo

### Install the daemons ###

echo '########################'
echo '######  SERVICES  ######'
echo '########################'
echo
echo "-> Uninstalling popd.."

if [[ $(uname -r) =~ el7 ]]
then
  # systemd daemon
  rm -f /usr/lib/systemd/system/popd.service

  # environment file for the daemon
  rm -f /etc/sysconfig/popd
else
  rm -f /etc/init.d/popd
fi

echo "Pop uninstallation completed."
