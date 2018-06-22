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
echo "Installing pop from $SOURCE."
echo
echo '#########################'
echo '######  LIBRARIES  ######'
echo '#########################'
echo

### (Clear &) Make the directories ###

if [ -d $INSTALL_PATH ]
then
  echo "Target directory $INSTALL_PATH exists. Removing!"
  rm -rf $INSTALL_PATH
fi
echo

mkdir -p $INSTALL_PATH
mkdir -p $INSTALL_PATH/python/site-packages/pop
mkdir -p $INSTALL_PATH/sbin
mkdir -p $INSTALL_PATH/bin
mkdir -p $INSTALL_PATH/etc

mkdir -p $LOG_PATH
chown $USER:$(id -gn $USER) $LOG_PATH

### Install python libraries ###

echo "-> Installing.."

cp -r $SOURCE/python/* $INSTALL_PATH/python/site-packages/pop/
python -m compileall $INSTALL_PATH/python/site-packages/pop > /dev/null

### Install the executable(s) ###

cp $SOURCE/sbin/* $INSTALL_PATH/sbin/
chown root:$(id -gn $USER) $INSTALL_PATH/sbin/*
chmod 754 $INSTALL_PATH/sbin/*

cp $SOURCE/bin/* $INSTALL_PATH/bin/
chown root:$(id -gn $USER) $INSTALL_PATH/bin/*
chmod 754 $INSTALL_PATH/bin/*

### Install the configs ###

echo '########################'
echo '######  CONFIGS  #######'
echo '########################'
echo
echo "-> Installing.."

cp $SOURCE/etc/pop.cfg $INSTALL_PATH/etc/
sed -i "s|_INSTALLPATH_|$INSTALL_PATH|"  $INSTALL_PATH/etc/pop.cfg

echo " Done."
echo

# Init script

echo "-> Writing $INITSCRIPT.."

INITSCRIPT=$INSTALL_PATH/etc/profile.d/init.sh
mkdir -p $INSTALL_PATH/etc/profile.d
echo "## GENERATED -- DO NOT EDIT" > $INITSCRIPT
echo "export POP_CONFIG=$INSTALL_PATH/etc/pop.cfg" >> $INITSCRIPT
echo "export PYTHONPATH="$INSTALL_PATH/python/site-packages:$(echo $PYTHONPATH | sed "s|$INSTALL_PATH/python/site-packages:||") >> $INITSCRIPT
echo "export PATH="$INSTALL_PATH/bin:$INSTALL_PATH/sbin:$(echo $PATH | sed "s|$INSTALL_PATH/bin:$INSTALL_PATH/sbin:||") >> $INITSCRIPT

echo " Done."
echo

### Install the daemons ###

echo '########################'
echo '######  SERVICES  ######'
echo '########################'
echo
echo "-> Installing popd.."

if [[ $(uname -r) =~ el7 ]]
then
  # systemd daemon
  cp $SOURCE/daemon/popd.systemd /usr/lib/systemd/system/popd.service
  sed -i "s|_INSTALLPATH_|$INSTALL_PATH|" /usr/lib/systemd/system/popd.service

  # environment file for the daemon
  ENV=/etc/sysconfig/popd
  echo "PYTHONPATH=$INSTALL_PATH/python/site-packages" > $ENV

  systemctl daemon-reload
else
  cp $SOURCE/daemon/popd.sysv /etc/init.d/popd
  sed -i "s|_INSTALLPATH_|$INSTALL_PATH|" /etc/init.d/popd
  chmod +x /etc/init.d/popd
fi

echo "Pop installation completed."
