#!/bin/bash

# this is a hack
export INSTALL_PATH=/usr
export LOG_PATH=/var/log/pop
export ETC_PATH=/etc
export USER=cmsprod
export PYTHONPATH=/usr/lib/python2.6/site-packages

export SOURCE=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

### Stop the daemons first ###

if [[ $(uname -r) =~ el7 ]]
then
  systemctl stop popd 2>/dev/null
else
  service popd stop 2>/dev/null
fi

echo
echo "Uninstalling pop based on $SOURCE."
echo
echo '#########################'
echo '######  LIBRARIES  ######'
echo '#########################'
echo
echo "-> Uninstalling.."

### Install the python libraries ###

rm -rf $PYTHONPATH/pop

### Install the executable(s) ###

pop_files=`ls -1 $SOURCE/sbin`
for file in $pop_files
do
    rm -f $INSTALL_PATH/sbin/$file
done

pop_files=`ls -1 $SOURCE/bin`
for file in $pop_files
do
    rm -f $INSTALL_PATH/bin/$file
done

echo " Done."
echo

### Install the configs ###

echo
echo '########################'
echo '######  CONFIGS  #######'
echo '########################'
echo
echo "-> Uninstalling.."

rm -f $ETC_PATH/pop.cfg

echo " Done."
echo

echo
echo '#########################'
echo '######  LOGFILES  #######'
echo '#########################'
echo
echo "-> Uninstalling.."

rm -rf $LOG_PATH

echo " Done."
echo

### Install the daemons ###

echo '########################'
echo '######  SERVICES  ######'
echo '########################'
echo
echo "-> Uninstalling.."

if [[ $(uname -r) =~ el7 ]]
then
  # systemd daemon
  rm /usr/lib/systemd/system/popd.service
  systemctl daemon-reload
else
  rm /etc/init.d/popd
fi

echo " Done."
echo
