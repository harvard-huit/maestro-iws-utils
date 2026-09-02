from typing import Optional

import requests
import urllib3
import json
import logging

from pystro.config import Config, get_logger
from pystro.models.model import Folder, PlanJob, Workstation, WorkstationClass
from pystro.helpers.oql import OQLQuery, field, And, Or, Not

# Suppress only the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Default for how the API token is sent. Apigee expects it in the "x-api-key"
# header; "bearer" sends "Authorization: Bearer <token>" instead.
AUTH_SCHEME = "x-api-key"


def get_headers(config: Config, auth_scheme: Optional[str] = None) -> dict:
    """
    Build the request headers for an API call.

    Args:
        config (Config): The config holding the API token.
        auth_scheme (Optional[str]): "x-api-key" or "bearer". Defaults to AUTH_SCHEME.
    Returns:
        dict: The auth header for the given scheme, plus the content type.
    """
    scheme = auth_scheme or AUTH_SCHEME
    if scheme == "bearer":
        auth = {"Authorization": f"Bearer {config.api_token}"}
    else:
        auth = {"x-api-key": f"{config.api_token}"}
    return {**auth, "Content-Type": "application/json"}


def get_engine_master(config: Config) -> str:
    """
    Retrieve the master engine for the current plan.

    Returns:
        str: The name of the master engine, or an empty string if not found.
    """
    logger = get_logger(config, __name__)
    oql_query = f"folder='/'"
    url = f"{config.base_url}/model/workstation?oql={oql_query}"
    headers = get_headers(config)
    logger.info(f"Retrieving master engine with OQL query: {oql_query}")
    master_engine = ""
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        results = response.json().get('results', [])
        for result in results:
            definition = result.get('def',"")
            if definition.get('type') == 'MANAGER':
                master_engine = definition.get('name', "")
                break
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error retrieving master engine: {e}")
    return master_engine


def get_workstation_class_members(config: Config, workstation_class: str) -> list[Workstation]:
    """
    Retrieve a list of workstations for a given workstation class.

    Args:
        workstation_class (str): The name of the workstation class to retrieve workstations for.
    Returns:
        list: A list of Workstation objects in the given workstation class.
    """
    logger = get_logger(config, __name__)
    if workstation_class == "":
        return []

    workstations: list[Workstation] = []
    
    url = f"{config.base_url}/model/workstationclass?oql=name='{workstation_class}'"
    headers = get_headers(config)
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        class_workstations = response.json().get('results', [])[0].get('def').get('workstationLinks', [])
        
        for workstation in class_workstations:
            full_name = workstation.get('workstation',"")
            folder, name = full_name.rsplit('/', 1)
            workstations.append(Workstation(name, f"{folder}/"))
    except requests.exceptions.RequestException as e:
        logger.error(f"Error retrieving workstations: {e}")
    return workstations
    
def get_workstation_class(config: Config, workstation_class_name: str) -> Optional[WorkstationClass]:
    """
    Retrieve a workstation class.

    Args:
        workstation_class_name (str): The name of the workstation class to retrieve workstations for.
    Returns:
        WorkstationClass: The workstation class object.
    """
    logger = get_logger(config, __name__)
    if workstation_class_name == "":
        return None

    url = f"{config.base_url}/model/workstationclass?oql=name='{workstation_class_name}'"
    headers = get_headers(config)
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        results = response.json().get('results', [])
        if results:
            definition = results[0].get('def', {})
            name = definition.get('name', "")
            folder = definition.get('folder', "")
            description = definition.get('description', "")
            options = definition.get('options', [])
            return WorkstationClass(name, folder, description, options)        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error retrieving workstations: {e}")
    return None

def get_workstations_from_list(config: Config, workstation_list: list[str]) -> list[Workstation]:
    """
    Retrieve a list of workstations for a given list of workstation names.

    Args:
        workstation_list (list[str]): A list of workstation names to retrieve workstations for.
    Returns:
        list: A list of workstations in the given workstation class.
    """
    logger = get_logger(config, __name__)
    if not workstation_list:
        return []

    workstations: list[Workstation] = []
    
    for workstation_def in workstation_list:
        workstation_folder, workstation_name = workstation_def.rsplit('/', 1)
        oql = OQLQuery((field('name') == workstation_name) & (field('folder') == f"{workstation_folder}/"))
        workstations.extend(get_workstations(config, oql))
    return workstations
    
def get_workstations(config: Config, oql_query: OQLQuery) -> list[Workstation]:
    """
    Retrieve a list of workstations filtered by the given criteria.

    Args:
        oql_query (OQLQuery): The OQL query to apply to the workstations.
    Returns:
        list: A list of workstations that match the given filter criteria.
    """
    logger = get_logger(config, __name__)

    workstations = []
    
    url = f"{config.base_url}/model/workstation?oql={oql_query}"
    headers = get_headers(config)
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        results = response.json().get('results', [])
        for result in results:
            definition = result.get('def', {})
            workstations.append(Workstation.fromJson(definition))
    except requests.exceptions.RequestException as e:
        logger.error(f"Error retrieving workstations: {e}")
    return workstations

def get_folders(config: Config, filter: dict[str, str] = {}) -> list[Folder]:
    """
    Retrieve a list of folders filtered by the given criteria.

    Args:
        filter (dict[str, str]): A dictionary of filter criteria to apply to the folders.
    Returns:
        list: A list of folders that match the given filter criteria.
    """
    logger = get_logger(config, __name__)
    oql_query: OQLQuery = OQLQuery()
    if filter is None:
        filter = {}
    for key, value in filter.items():
        if value and value != "/":
            oql_query.filter(field(key) == value)

    folders = []
    
    url = f"{config.base_url}/model/folder?oql={str(oql_query)}"
    headers = get_headers(config)
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        results = response.json().get('results', [])
        for result in results:
            definition = result.get('def', {})
            folders.append(Folder.fromJson(definition))
    except requests.exceptions.RequestException as e:
        logger.error(f"Error retrieving folders: {e}")
    return folders

def get_workstation_plan_id(config: Config, workstation_data: Workstation) -> str:
    """
    Retrieve the ID for a given workstation on the current plan.

    Args:
        workstation_data (Workstation): The data of the workstation to retrieve the plan ID for.

    Returns:
        str: The ID of the workstation, or an empty string if not found.
    """
    logger = get_logger(config, __name__)
    oql_query: OQLQuery = OQLQuery()
    if workstation_data.name != "":
        oql_query.filter(field("name") == workstation_data.name)
    if workstation_data.folder != "/":
        oql_query.filter(field("folder") == f"{workstation_data.folder}")

    url = f"{config.base_url}/plan/workstation?oql={str(oql_query)}"
    logger.debug(f"Getting workstation plan ID with OQL query: {str(oql_query)}")
    headers = get_headers(config)
    workstation_id = ""
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        workstation_id = response.json().get('results', [])[0].get('id')
    except requests.exceptions.RequestException as e:
        logger.error(f"Error retrieving workstation plan ID: {e}")
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
    logger = get_logger(config, __name__)
    logger.info(f"Setting fence for workstation ID={workstation_id} to {fence_value}")
    url = f"{config.base_url}/plan/workstation/{workstation_id}/action/update-fence"
    headers = get_headers(config)
    query = f"fence={fence_value}"
    
    try:
        response = requests.put(url, params=query, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error setting fence: {e}")
        return False
    
def create_workstation_class(config: Config, folder: str, name: str, members: list[str]) -> bool:
    """
    Create a new workstation class with the given name and members.

    Args:
        class_name (str): The name of the workstation class to create.
        members (list[str]): A list of workstation names to include in the class.

    Returns:
        bool: True if the workstation class was successfully created, False otherwise.
    """
    logger = get_logger(config, __name__)
    method = "POST"
    url = f"{config.base_url}/model/workstationclass"
    headers = get_headers(config)
    data = {
        "kind": "WorkstationClass",
        "def": {
            "folder": folder,
            "name": name,
            "workstationLinks": [{"workstation": member} for member in members]
        }
    }
    
    try:
        workstation_class = get_workstation_class_members
        response = requests.post(url, json=data, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating workstation class: {e}")
        return False
    
def get_plan_jobs(config: Config, plan_id: Optional[str] = None, oql: Optional[OQLQuery] = None) -> list[PlanJob]:
    """
    Retrieve a list of all plan jobs, optionally filtered by plan ID or OQL query.

    Args:
        config (Config): The configuration object containing API details.
        plan_id (str, optional): The ID of the plan to filter jobs by.
        oql (OQLQuery, optional): An OQL query to filter the plan jobs.

    Returns:
        list[PlanJob]: A list of plan jobs that match the given filter criteria.
    """
    logger = get_logger(config, __name__)
    url = f"{config.base_url}/plan/job"
    query_params = {}
    if plan_id is not None:
        query_params['planId'] = plan_id
    if oql is not None:
        query_params['oql'] = str(oql)
    headers = get_headers(config)

    plan_jobs = []

    try:
        response = requests.get(url, headers=headers, params=query_params, timeout=10, verify=False)
        response.raise_for_status()
        results = response.json().get('results', [])
        for result in results:
            plan_jobs.append(PlanJob.fromJson(result))
    except requests.exceptions.RequestException as e:
        logger.error(f"Error retrieving plan jobs: {e}")
    return plan_jobs