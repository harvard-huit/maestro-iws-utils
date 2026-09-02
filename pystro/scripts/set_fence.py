import argparse
import sys
import logging

from pystro.config import Config, get_logger
from pystro.apis.api import get_workstation_class_members, get_workstations_from_list, set_fence, get_workstation_plan_id
from pystro.models.model import Workstation

def main():
    parser = argparse.ArgumentParser(description='Set the fence for a given workstation class')
    parser.add_argument('-e', '--environment', help='The environment to use from the configuration file', default='test')
    parser.add_argument('-c', '--workstation_class', help='The name of the workstation class to set the fence for')
    parser.add_argument('-w', '--workstation_list', help='A comma-separated list of workstations to set the fence for')
    parser.add_argument('-f', '--fence', help='The fence to set for the workstation class')
    args = parser.parse_args()

    config = Config.from_json(environment=args.environment)
    logger = get_logger(config, __name__)

    workstation_class = args.workstation_class if args.workstation_class else ""
    workstation_list = args.workstation_list.split(',') if args.workstation_list else []
    fence_value = int(args.fence) if args.fence else None

    workstations: list[Workstation] = []

    logger.info(f"Args: workstation_class={workstation_class}, workstations={workstation_list}, fence_value={fence_value}")

    if fence_value is None:
        logger.error("No fence value provided.")
        return 1

    if fence_value < 0 or fence_value > 100:
        logger.error("Fence value must be between 0 and 100.")
        return 1

    if workstation_list:
        logger.info(f"Using provided workstation list: {workstation_list}")
        workstations = get_workstations_from_list(config, workstation_list)
    else:
        logger.warning(f"No workstations provided. Pulling from workstation class members for class {workstation_class}")
        workstations = get_workstation_class_members(config, workstation_class)

        if not workstations:
            logger.error(f"No workstations found for workstation class {workstation_class}")
            return 1

    for workstation in workstations:
        logger.info(f"Setting fence for workstation {workstation}")
        workstation_id = get_workstation_plan_id(config, workstation)
        if workstation_id:
            success = set_fence(config, workstation_id, fence_value)
            if success:
                logger.info(f"Successfully set fence to {fence_value} for workstation {workstation} with ID {workstation_id}")
            else:
                logger.error(f"Failed to set fence for workstation {workstation} with ID {workstation_id}")
        else:
            logger.error(f"Could not find workstation ID for {workstation}")
    return 0

if __name__ == "__main__":
    sys.exit(main())