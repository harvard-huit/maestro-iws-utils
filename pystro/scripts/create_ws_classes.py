import argparse

from pystro.config import Config, load_json, get_logger
from pystro.apis.api import get_workstation_plan_id, get_workstations

def main():
    parser = argparse.ArgumentParser(description='Create a new workstation class')
    parser.add_argument('-f', '--workstation_class_data_file', help='The path to the configuration file to use', default='data/workstation_classes.json')
    parser.add_argument('-c', '--workstation_class', help='Limit to a specific workstation class defined in the configuration file')
    parser.add_argument('-e', '--environment', help='The environment to use from the configuration file', default='test')
    args = parser.parse_args()

    config = Config.from_json(environment=args.environment)
    logger = get_logger(config, __name__)

    workstation_class_data = load_json(args.workstation_class_data_file)
    if args.workstation_class:
        workstation_class_data = [wc for wc in workstation_class_data if wc['name'] == args.workstation_class]

    for wcd in workstation_class_data:
        logger.info(f"Processing workstation class: {wcd['name']}")
        try:
            wc_definition = wcd['definition']
        except KeyError:
            logger.warning(f"Workstation class {wcd['name']} is missing a definition. Skipping.")
            continue

        workstations = get_workstations(config, wc_definition)
        for workstation in workstations:
            logger.info(f"Found workstation: {workstation}")
            workstation_id = get_workstation_plan_id(config, workstation)
            if workstation_id:
                logger.info(f"Workstation ID for {workstation.name} in folder {workstation.folder}: {workstation_id}")
            else:
                logger.warning(f"Could not find workstation ID for {workstation.name} in folder {workstation.folder}")
            
            

if __name__ == "__main__":
    main()