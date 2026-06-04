#!/bin/ksh
# backup_config_files.sh
# Copies configuration files required for Maestro master.
set -x
BACKUP_DIR=/u02/daily_backup
CONFIG_RETENTION_DAYS=10
MAESTRO_HOME=/u02/tws/
TWSDATA_DIR=$MAESTRO_HOME/TWSDATA/
ENGINE_SERVER_DIR=$TWSDATA_DIR/usr/servers/engineServer/
TAR='/usr/bin/tar -cvf'

#########################
# Make backup directory #
#########################
TARGET_DIR=$BACKUP_DIR/config_`date +%y%m%d%H%M`
mkdir $TARGET_DIR

#####################
# Cleanup directory #
#####################
find $BACKUP_DIR -ctime +$CONFIG_RETENTION_DAYS -exec rm -rf {} \;

##############################
# Copy directories and files #
##############################

FILES_TO_BACKUP=(
    "$TWSDATA_DIR/localopts"
    "$ENGINE_SERVER_DIR"
    "$TWSDATA_DIR/mozart"
    "$TWSDATA_DIR/network"
    "$TWSDATA_DIR/Sinfonia"
    "$TWSDATA_DIR/Symphony"

)

for item in "${FILES_TO_BACKUP[@]}"; do
    if [ -e "$item" ]; then
        cp -R "$item" "$TARGET_DIR"
    else
        echo "WARNING: $item not found, skipping."
    fi
done