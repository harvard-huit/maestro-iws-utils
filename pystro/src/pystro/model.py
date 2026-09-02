from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Workstation:
    name: str
    folder: str
    os: str = ""
    id: str = ""
    type: str = ""

    @staticmethod
    def fromJson(json: dict) -> 'Workstation':
        name = json.get('name', '')
        folder = json.get('folder', '')
        os = json.get('os', '')
        id = json.get('id', '')
        type = json.get('type', '')
        return Workstation(name, folder, os, id, type)
    
    def workstation_path(self) -> str:
        return f"{self.folder}{self.name}"
    
    def __str__(self) -> str:
        return f"Workstation(name={self.name}, folder={self.folder}, os={self.os}, id={self.id}, type={self.type})"


@dataclass
class WorkstationLink:
    workstation: str
    workstation_id: Optional[str] = None

    @staticmethod
    def fromJson(json: dict) -> 'WorkstationLink':
        workstation = json.get('workstation', '')
        return WorkstationLink(workstation)
    
    def to_json(self) -> dict:
        json_dict = {"workstation": self.workstation}
        if self.workstation_id:
            json_dict["workstation_id"] = self.workstation_id
        return json_dict
    
    def __str__(self) -> str:
        return f"WorkstationLink(workstation={self.workstation})"

@dataclass
class Folder:
    id: str
    name: str
    parent_id: Optional[str] = None

    @staticmethod
    def fromJson(json: dict) -> 'Folder':
        id = json.get('id', '')
        name = json.get('folder', '')
        parent_id = json.get('parentId', None)
        return Folder(id, name, parent_id)

    def to_json(self) -> dict:
        return {
            "kind": "Folder",
            "key": self.name,
            "def": {
                "id": self.id,
                "folder": self.name,
                "parentId": self.parent_id
            }
        }

    def __str__(self) -> str:
        return f"Folder(name={self.name})"

@dataclass
class WorkstationClass:
    name: str
    folder: str
    description: str = ""
    options: list[str] = field(default_factory=list)
    workstation_links: list[WorkstationLink] = field(default_factory=list)

    @staticmethod
    def fromJson(json: dict) -> 'WorkstationClass':
        name = json.get('name', '')
        folder = json.get('folder', '')
        description = json.get('description', '')
        options = json.get('options', ["ignore"])
        workstation_links = [WorkstationLink.fromJson(link) for link in json.get('workstationLinks', [])]
        return WorkstationClass(name, folder, description, options, workstation_links)

    def to_json(self) -> dict:
        return {
            "kind": "WorkstationClass",
            "def": {
                "name": self.name,
                "folder": self.folder,
                "description": self.description,
                "options": self.options,
                "workstationLinks": [link.to_json() for link in self.workstation_links]
            }
        }

    def __str__(self) -> str:
        return f"WorkstationClass(name={self.name}, folder={self.folder})"

@dataclass
class Action:
    key: str
    id: str = ""

    @staticmethod
    def fromJson(json: dict) -> 'Action':
        key = json.get('key', '')
        id = json.get('id', '')
        return Action(key, id)

    def __str__(self) -> str:
        return f"Action(key={self.key})"


@dataclass
class JobDefinition:
    name: str
    workstation: str = ""
    workstation_id: str = ""
    cpu_folder_id: str = ""
    task_type: str = ""
    task: dict = field(default_factory=dict)
    estimated_duration: str = ""
    user_logins: list[str] = field(default_factory=list)
    recovery_option: str = ""
    recovery_repeat_occurrences: int = 0
    recovery_repeat_affinity: bool = False
    command: bool = False

    @staticmethod
    def fromJson(json: dict) -> 'JobDefinition':
        name = json.get('name', '')
        workstation = json.get('workstation', '')
        workstation_id = json.get('workstationId', '')
        cpu_folder_id = json.get('cpuFolderId', '')
        task_type = json.get('taskType', '')
        task = json.get('task', {})
        estimated_duration = json.get('estimatedDuration', '')
        user_logins = json.get('userLogins', [])
        recovery_option = json.get('recoveryOption', '')
        recovery_repeat_occurrences = json.get('recoveryRepeatOccurrences', 0)
        recovery_repeat_affinity = json.get('recoveryRepeatAffinity', False)
        command = json.get('command', False)
        return JobDefinition(name, workstation, workstation_id, cpu_folder_id, task_type, task,
                             estimated_duration, user_logins, recovery_option,
                             recovery_repeat_occurrences, recovery_repeat_affinity, command)

    def task_string(self) -> str:
        """The command line for this job, e.g. the UNIX taskString."""
        return self.task.get(self.task_type, {}).get('taskString', '')

    def __str__(self) -> str:
        return f"JobDefinition(name={self.name}, workstation={self.workstation}, task_type={self.task_type})"


@dataclass
class CompositeStatus:
    status: str = ""
    canceled: bool = False
    error: bool = False
    started: bool = False
    cancel_pending: bool = False
    dont_run: bool = False

    @staticmethod
    def fromJson(json: dict) -> 'CompositeStatus':
        status = json.get('status', '')
        canceled = json.get('canceled', False)
        error = json.get('error', False)
        started = json.get('started', False)
        cancel_pending = json.get('cancelPending', False)
        dont_run = json.get('dontRun', False)
        return CompositeStatus(status, canceled, error, started, cancel_pending, dont_run)

    def __str__(self) -> str:
        return f"CompositeStatus(status={self.status}, error={self.error})"


@dataclass
class TimeInfo:
    estimated_duration: str = ""
    actual_start_time: Optional[str] = None
    actual_end_time: Optional[str] = None
    elapsed_time: Optional[str] = None

    @staticmethod
    def fromJson(json: dict) -> 'TimeInfo':
        estimated_duration = json.get('estimatedDuration', '')
        actual_start_time = json.get('actualStartTime', None)
        actual_end_time = json.get('actualEndTime', None)
        elapsed_time = json.get('elapsedTime', None)
        return TimeInfo(estimated_duration, actual_start_time, actual_end_time, elapsed_time)

    def __str__(self) -> str:
        return f"TimeInfo(estimated_duration={self.estimated_duration}, elapsed_time={self.elapsed_time})"


@dataclass
class JobRun:
    id: str
    name: str = ""
    job_id: str = ""
    job_key: str = ""
    job_number: Optional[int] = None
    common_status: str = ""
    composite_status: Optional[CompositeStatus] = None
    job_definition: Optional[JobDefinition] = None
    time_info: Optional[TimeInfo] = None
    step: str = ""
    return_code: Optional[int] = None
    rerun_job: bool = False
    rerun_type: str = ""
    released: bool = False
    last_in_rerun_chain: bool = False
    min_duration_not_reached: bool = False
    max_duration_gone: bool = False
    output_conditions: list[dict] = field(default_factory=list)
    actions: list[Action] = field(default_factory=list)

    @staticmethod
    def fromJson(json: dict) -> 'JobRun':
        id = json.get('id', '')
        name = json.get('name', '')
        job_id = json.get('jobId', '')
        job_key = json.get('jobKey', '')
        job_number = json.get('jobNumber', None)
        common_status = json.get('commonStatus', '')
        composite_status = CompositeStatus.fromJson(json.get('compositeStatus', {}))
        job_definition = JobDefinition.fromJson(json.get('jobDefinition', {}))
        time_info = TimeInfo.fromJson(json.get('timeInfo', {}))
        step = json.get('step', '')
        return_code = json.get('returnCode', None)
        rerun_job = json.get('rerunJob', False)
        rerun_type = json.get('rerunType', '')
        released = json.get('released', False)
        last_in_rerun_chain = json.get('lastInRerunChain', False)
        min_duration_not_reached = json.get('minDurationNotReached', False)
        max_duration_gone = json.get('maxDurationGone', False)
        output_conditions = json.get('outputConditions', [])
        actions = [Action.fromJson(action) for action in json.get('actions', [])]
        return JobRun(id, name, job_id, job_key, job_number, common_status, composite_status,
                      job_definition, time_info, step, return_code, rerun_job, rerun_type,
                      released, last_in_rerun_chain, min_duration_not_reached, max_duration_gone,
                      output_conditions, actions)

    def status(self) -> str:
        """The detailed status of this run, e.g. HOLD or ABEND."""
        return self.composite_status.status if self.composite_status else ""

    def __str__(self) -> str:
        return f"JobRun(name={self.name}, common_status={self.common_status}, status={self.status()})"


@dataclass
class DependenciesStats:
    number_of_dependencies: int = 0
    number_of_job_dependencies: int = 0
    number_of_job_stream_dependencies: int = 0
    number_of_internetwork_dependencies: int = 0
    number_of_prompt_dependencies: int = 0
    number_of_resource_dependencies: int = 0
    number_of_file_dependencies: int = 0
    number_of_unresolved_dependencies: int = 0
    number_of_non_resource_unresolved_dependencies: int = 0
    number_of_completed_dependencies: int = 0
    number_of_successors: int = 0

    @staticmethod
    def fromJson(json: dict) -> 'DependenciesStats':
        return DependenciesStats(
            json.get('numberOfDependencies', 0),
            json.get('numberOfJobDependencies', 0),
            json.get('numberOfJobStreamDependencies', 0),
            json.get('numberOfInternetworkDependencies', 0),
            json.get('numberOfPromptDependencies', 0),
            json.get('numberOfResourceDependencies', 0),
            json.get('numberOfFileDependencies', 0),
            json.get('numberOfUnresolvedDependencies', 0),
            json.get('numberOfNonResourceUnresolvedDependencies', 0),
            json.get('numberOfCompletedDependencies', 0),
            json.get('numberOfSuccessors', 0),
        )

    def __str__(self) -> str:
        return (f"DependenciesStats(total={self.number_of_dependencies}, "
                f"unresolved={self.number_of_unresolved_dependencies})")


@dataclass
class PlanJob:
    id: str
    name: str = ""
    folder: str = ""
    folder_id: str = ""
    plan_id: str = ""
    flow_node_type: str = ""
    workstation: str = ""
    workstation_id: str = ""
    cpu_folder_id: str = ""
    job_stream_name: str = ""
    job_stream_id: str = ""
    job_stream_workstation: str = ""
    job_stream_workstation_id: str = ""
    position: int = 0
    key: str = ""
    priority: int = 0
    orig_priority: int = 0
    job_definition: Optional[JobDefinition] = None
    job_runs: list[JobRun] = field(default_factory=list)
    sched_time: str = ""
    end_time: Optional[str] = None
    confidence_interval: str = ""
    dependencies: Optional[list[dict]] = None
    dependencies_stats: Optional[DependenciesStats] = None
    time_restrictions: dict = field(default_factory=dict)
    job_definition_flags: dict = field(default_factory=dict)
    job_status_flags: dict = field(default_factory=dict)
    job_options: dict = field(default_factory=dict)
    actions: list[Action] = field(default_factory=list)
    archived: bool = False

    @staticmethod
    def fromJson(json: dict) -> 'PlanJob':
        id = json.get('id', '')
        name = json.get('name', '')
        folder = json.get('folder', '')
        folder_id = json.get('folderId', '')
        plan_id = json.get('planId', '')
        flow_node_type = json.get('flowNodeType', '')
        workstation = json.get('workstation', '')
        workstation_id = json.get('workstationId', '')
        cpu_folder_id = json.get('cpuFolderId', '')
        job_stream_name = json.get('jobStreamName', '')
        job_stream_id = json.get('jobStreamId', '')
        job_stream_workstation = json.get('jobStreamWorkstation', '')
        job_stream_workstation_id = json.get('jobStreamWorkstationId', '')
        position = json.get('position', 0)
        key = json.get('key', '')
        priority = json.get('priority', 0)
        orig_priority = json.get('origPriority', 0)
        job_definition = JobDefinition.fromJson(json.get('jobDefinition', {}))
        job_runs = [JobRun.fromJson(run) for run in json.get('jobruns', []) or []]
        sched_time = json.get('schedTime', '')
        end_time = json.get('endTime', None)
        confidence_interval = json.get('confidenceInterval', '')
        dependencies = json.get('dependencies', None)
        dependencies_stats = DependenciesStats.fromJson(json.get('dependenciesStats', {}))
        time_restrictions = json.get('timeRestrictions', {})
        job_definition_flags = json.get('jobDefinitionFlags', {})
        job_status_flags = json.get('jobStatusFlags', {})
        job_options = json.get('jobOptions', {})
        actions = [Action.fromJson(action) for action in json.get('actions', [])]
        archived = json.get('archived', False)
        return PlanJob(id, name, folder, folder_id, plan_id, flow_node_type, workstation,
                       workstation_id, cpu_folder_id, job_stream_name, job_stream_id,
                       job_stream_workstation, job_stream_workstation_id, position, key,
                       priority, orig_priority, job_definition, job_runs, sched_time, end_time,
                       confidence_interval, dependencies, dependencies_stats, time_restrictions,
                       job_definition_flags, job_status_flags, job_options, actions, archived)

    def job_path(self) -> str:
        return f"{self.folder}{self.name}"

    def latest_run(self) -> Optional[JobRun]:
        return self.job_runs[-1] if self.job_runs else None

    def status(self) -> str:
        """The detailed status of the latest run, e.g. HOLD or ABEND."""
        run = self.latest_run()
        return run.status() if run else ""

    def has_error(self) -> bool:
        run = self.latest_run()
        return bool(run and run.composite_status and run.composite_status.error)

    def __str__(self) -> str:
        return f"PlanJob(name={self.name}, folder={self.folder}, status={self.status()})"
