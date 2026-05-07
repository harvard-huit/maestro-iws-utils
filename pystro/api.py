import requests
import urllib3
import json

from config import Config

# Suppress only the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_workstations(config: Config, workstation_class: str) -> list[dict]:
    """
    Retrieve a list of workstations for a given workstation class.

    Args:
        workstation_class (str): The name of the workstation class to retrieve workstations for.
    Returns:
        list: A list of workstations for the given workstation class.
    """
    workstations = []
    
    url = f"{config.base_url}/model/workstationclass?oql=name='/AAIS/DF_TEST'"
    headers = {"Authorization": f"Bearer {config.api_token}", "Content-Type": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        class_workstations = response.json().get('results', [])[0].get('def').get('workstationLinks', [])
        
        for workstation in class_workstations:
            full_name = workstation.get('workstation',"")
            folder, name = full_name.rsplit('/', 1)
            workstations.append({"name": name, "folder": folder})
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving workstations: {e}")
    return workstations

def get_workstation_plan_id(config: Config, workstation_data: dict) -> str:
    """
    Retrieve the ID for a given workstation on the current plan.

    Args:
        workstation_data (dict): The data of the workstation to retrieve the plan ID for.

    Returns:
        str: The ID of the workstation, or an empty string if not found.
    """
    oql_query = f"name='{workstation_data['name']}' and folder='{workstation_data['folder']}/'"
    url = f"{config.base_url}/plan/workstation?oql={oql_query}"
    headers = {"Authorization": f"Bearer {config.api_token}", "Content-Type": "application/json"}
    workstation_id = ""
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        workstation_id = response.json().get('results', [])[0].get('id')
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving workstation plan ID: {e}")
    return workstation_id

def set_fence(config: Config, workstation_id: str, fence_value: int) -> bool:
    """
    Set the fence value for a given workstation.

    Args:
        workstation_id (str): The ID of the workstation to set the fence for.
        fence_value (int): The value to set the fence to.

    Returns:
        bool: True if the fence was successfully set, False otherwise.
    """
    url = f"{config.base_url}/plan/workstation/{workstation_id}/action/update-fence"
    headers = {"Authorization": f"Bearer {config.api_token}", "Content-Type": "application/json"}
    query = f"fence={fence_value}"
    
    try:
        response = requests.put(url, params=query, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error setting fence: {e}")
        return False