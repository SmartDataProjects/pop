#!/bin/bash

# this is a hack
export INSTALL_PATH=/usr
export LOG_PATH=/var/log/pop
export ETC_PATH=/etc
export USER=cmsprod
export PYTHONPATH=/usr/lib/python2.6/site-packages

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
echo "-> Installing.."

### (Clear &) Make the directories ###

mkdir -p $INSTALL_PATH
mkdir -p $PYTHONPATH/pop
mkdir -p $INSTALL_PATH/sbin
mkdir -p $INSTALL_PATH/bin
mkdir -p $ETC_PATH

### Install python libraries ###

cp -r $SOURCE/python/* $PYTHONPATH/pop/
python -m compileall $PYTHONPATH/pop > /dev/null

### Install the executable(s) ###

pop_files=`ls -1 $SOURCE/sbin`
for file in $pop_files
do
    cp      $SOURCE/sbin/$file $INSTALL_PATH/sbin/$file
    chown root:$(id -gn $USER) $INSTALL_PATH/sbin/$file
    chmod 754                  $INSTALL_PATH/sbin/$file
done

pop_files=`ls -1 $SOURCE/bin`
for file in $pop_files
do
    cp       $SOURCE/bin/$file $INSTALL_PATH/bin/$file
    chown root:$(id -gn $USER) $INSTALL_PATH/bin/$file
    chmod 754                  $INSTALL_PATH/bin/$file
done

echo " Done."
echo

### Install the configs ###

echo
echo '########################'
echo '######  CONFIGS  #######'
echo '########################'
echo
echo "-> Installing.."

cp $SOURCE/etc/pop.cfg $ETC_PATH
sed -i "s|_INSTALLPATH_|$INSTALL_PATH|" $ETC_PATH/pop.cfg

echo " Done."
echo

echo
echo '#########################'
echo '######  LOGFILES  #######'
echo '#########################'
echo
echo "-> Installing.."

mkdir -p $LOG_PATH
chown $USER:$(id -gn $USER) $LOG_PATH

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
  systemctl daemon-reload
else
  cp $SOURCE/daemon/popd.sysv /etc/init.d/popd
  sed -i "s|_INSTALLPATH_|$INSTALL_PATH|" /etc/init.d/popd
  chmod +x /etc/init.d/popd
fi

echo " Done."
echo
