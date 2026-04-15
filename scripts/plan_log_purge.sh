#!/bin/ksh
# log_purge.sh
# Purges old log files for Maestro master.

# Function to display usage and exit
usage() {
    print "Usage: $0 [-h] [-e environment] [-v]"
    print "  -h               Display this help message"
    print "  -e environment   Specify the environment (uses OPTARG)"
    print "  -v               Enable verbose mode"
    exit 1
}

while getopts "he:" opt; do
    case $opt in
        h)
            usage
            ;;
        e)
            IWS_ENV=$OPTARG
            ;;
        \?) # Handles invalid options
            print "Invalid option: -${OPTARG}" >&2
            usage
            ;;
        :) # Handles missing arguments for options that require them
            print "Option -${OPTARG} requires an argument." >&2
            usage
            ;;
    esac
done
shift $((OPTIND - 1)) # Remove processed flags from positional parameters

set -x
MAESTRO_DATA_HOME=/u02/tws/TWSDATA/
if [ "$IWS_ENV" = "PROD" ]; then
    PLAN_RETENTION_DAYS=1100
    FORECAST_PLAN_RETENTION_DAYS=3
elif [ "$IWS_ENV" = "TEST" ]; then
    PLAN_RETENTION_DAYS=370
    FORECAST_PLAN_RETENTION_DAYS=3
else
    print "Invalid environment specified: $IWS_ENV. Use 'PROD' or 'TEST'."
    exit 1
fi

#######################
# Cleanup directories #
#######################
find $MAESTRO_DATA_HOME/schedlog -ctime +$PLAN_RETENTION_DAYS -exec rm -rf {} \;
find $MAESTRO_DATA_HOME/schedForecast -ctime +$FORECAST_PLAN_RETENTION_DAYS -exec rm -rf {} \;

