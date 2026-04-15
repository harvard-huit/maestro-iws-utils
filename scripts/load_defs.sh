#!/bin/ksh
# load_defs.sh
# Loads job and schedule definitions into Maestro using 

# Function to display usage and exit
usage() {
    print "Usage: $0 [-h] [-e environment] [-v] [-j | -s | -b]"
    print "  -h               Display this help message"
    print "  -e environment   Specify the environment (uses OPTARG)"
    print "  -v               Validate job definitions without loading"
    print "  -j               Load only job definitions"
    print "  -s               Load only schedule definitions"
    print "  -b               Load both job and schedule definitions"
    exit 1
}

while getopts "he:vjsb" opt; do
    case $opt in
        h)
            usage
            ;;
        e)
            IWS_ENV=$OPTARG
            ;;
        v)
            VALIDATE_ONLY=true
            ;;
        j)
            LOAD_JOBS=true
            ;;
        s)
            LOAD_SCHEDULES=true
            ;;
        b)
            LOAD_JOBS=true
            LOAD_SCHEDULES=true
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

. /u02/tws/twa_env.sh
TWS_HOME=/u02/tws/TWS/

if [ -z "$IWS_ENV" ]; then
    print "Environment not specified. Use -e option to specify the environment."
    usage
elif [ "$IWS_ENV" != "PROD" ] && [ "$IWS_ENV" != "TEST" ]; then
    print "Invalid environment specified: $IWS_ENV. Use 'PROD' or 'TEST'."
    usage
elif [ "$IWS_ENV" = "PROD" ]; then
    WORKSTATION="MSTRO-PRD-APP_XA"
elif [ "$IWS_ENV" = "TEST" ]; then
    WORKSTATION="MSTRO-TST-APP_XA"
fi

cd ../definitions

if [ "$LOAD_JOBS" = true ]; then
    print "Update job definitions with workstation: $WORKSTATION"
    rm -f jobs.def
    sed "s/WORKSTATION_DEF/$WORKSTATION/g" jobs.def.template > jobs.def
    if [ "$VALIDATE_ONLY" = true ]; then
        ${TWS_HOME}/bin/composer validate jobs.def
    else
        print "Loading job definitions..."
        ${TWS_HOME}/bin/datamigrate -jobs "jobs.def" $VALIDATE_FLAG -switchdb
        if [ ${?} -ne 0 ]; then exit 1; fi
    fi
fi  

if [ "$LOAD_SCHEDULES" = true ]; then
    print "Update schedule definitions with workstation: $WORKSTATION"
    rm -f scheds.def
    sed "s/WORKSTATION_DEF/$WORKSTATION/g" scheds.def.template > scheds.def
    if [ "$VALIDATE_ONLY" = true ]; then
        ${TWS_HOME}/bin/composer validate scheds.def
    else
        print "Loading schedule definitions..."
        ${TWS_HOME}/bin/datamigrate -scheds "scheds.def" -switchdb
        if [ ${?} -ne 0 ]; then exit 1; fi
    fi
fi