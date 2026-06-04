#!/bin/ksh
# set_fence.sh
# Sets the fence value for specified workstations or all members of a workstation class.
. /u02/tws/twa_env.sh

set -x
/u02/maestro-iws-utils/.venv/bin/python /u02/maestro-iws-utils/pystro/set_fence.py "$@"