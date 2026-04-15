#!/bin/ksh
# daily_dataexport.sh
# Exports Maestro master configuration using dataexport and copies to backup directory.
. /u02/tws/twa_env.sh

set -x
MAESTRO_HOME=/u02/tws/TWS/
MAESTRO_DATA_HOME=/u02/tws/TWSDATA/
CMD="$MAESTRO_HOME/bin/dataexport"
BACKUP_DIR=/u02/daily_backup
set +x
export WA_EXPORT_PWD=$(openssl enc -aes-256-cbc -d -pbkdf2 -iter 100000 -in $MAESTRO_HOME/scripts/.secrets/password.enc -pass file:$MAESTRO_HOME/scripts/.secrets/password.key)
set -x

#########################
# Make backup directory #
#########################
mkdir -p $BACKUP_DIR
TARGET_DIR=$BACKUP_DIR/dataexport_`date +%y%m%d%H%M`
mkdir $TARGET_DIR

#####################
# Cleanup directory #
#####################
find $BACKUP_DIR -ctime +14 -exec rm -rf {} \;

############################
# Create backup flat files #
############################
$CMD $MAESTRO_HOME $TARGET_DIR