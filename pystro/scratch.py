from config import Config
from api import get_workstations, set_fence, get_workstation_plan_id

def main():
    config = Config.from_json()
    workstation_class = "/AAIS/DF_TEST"

    workstations = get_workstations(config, workstation_class)
    for workstation in workstations:
        print(f"Setting fence for workstation {workstation}")
        workstation_id = get_workstation_plan_id(config, workstation)
        if workstation_id:
            success = set_fence(config, workstation_id, 24)
            if success:
                print(f"Successfully set fence for workstation {workstation} with ID {workstation_id}")
            else:
                print(f"Failed to set fence for workstation {workstation} with ID {workstation_id}")
        else:
            print(f"Could not find workstation ID for {workstation}")

if __name__ == "__main__":
    main()