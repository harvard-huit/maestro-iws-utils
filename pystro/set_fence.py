import argparse

from config import Config
from api import get_workstations, set_fence, get_workstation_plan_id

def main():
    parser = argparse.ArgumentParser(description='Set the fence for a given workstation class')
    parser.add_argument('workstation_class', help='The name of the workstation class to set the fence for')
    parser.add_argument('fence', help='The fence to set for the workstation class')
    args = parser.parse_args()

    config = Config.from_json()
    workstation_class = args.workstation_class
    fence_value = int(args.fence)

    workstations = get_workstations(config, workstation_class)
    for workstation in workstations:
        print(f"Setting fence for workstation {workstation}")
        workstation_id = get_workstation_plan_id(config, workstation)
        if workstation_id:
            success = set_fence(config, workstation_id, fence_value)
            if success:
                print(f"Successfully set fence to {fence_value} for workstation {workstation} with ID {workstation_id}")
            else:
                print(f"Failed to set fence for workstation {workstation} with ID {workstation_id}")
        else:
            print(f"Could not find workstation ID for {workstation}")

if __name__ == "__main__":
    main()