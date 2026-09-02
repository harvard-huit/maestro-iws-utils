import argparse

from pystro.config import Config, load_json, get_logger
from pystro.api import get_folders, get_workstations, create_workstation_class, OQLQuery, field

def main():
    parser = argparse.ArgumentParser(description='Create workstation classes for each folder')
    parser.add_argument('-f', '--folder', help='Limit to a specific folder (e.g. "/ADHOC/")')
    parser.add_argument('-d', '--dry-run', action='store_true', help='Perform a dry run without making any changes')
    args = parser.parse_args()

    config = Config.from_json()
    logger = get_logger(config, __name__)

    folders_to_ignore = ["/", "/ADHOC/"]

    filter = {}
    if args.folder:
        filter["folder"] = args.folder
        folders_to_ignore = [f for f in folders_to_ignore if f != args.folder]

    folders = get_folders(config, filter)
    for folder in folders:
        if folder.name in folders_to_ignore:
            continue
        logger.info(f"Found folder: {folder.name}")
        oql = OQLQuery(field('folder') == f"{folder.name}")
        workstations = get_workstations(config, oql)
        class_name = folder.name.strip("/") + "_AGENTS"
        workstation_paths = [ws.workstation_path() for ws in workstations]
        if not args.dry_run:
            create_workstation_class(config, folder.name, class_name, workstation_paths)
        else:
            logger.info(f"Dry run: would create workstation class '{class_name}' in folder '{folder.name}' with members: {workstation_paths}")
            

if __name__ == "__main__":
    main()