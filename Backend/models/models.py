from pydantic import BaseModel, Field, UUID4, validator
from typing import Optional, Literal, List, Union, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum
 
SUPPORTED_DB_TYPES = Literal[
    "PostgreSQL",
    "MySQL",
    "SQLite",
    "Oracle",
    "SQL Server",
    "MSSQL",
    "Snowflake",
    "Redshift"
]
 
class ConnectionBase(BaseModel):
    # This model is used for input (Create) and as a base for Update
    project_code: str = Field(..., description="Code identifying the project this connection belongs to")
    connection_name: str = Field(..., description="Name of the database connection")
    connection_description: Optional[str] = Field(None, description="Description of the connection")
    sql_flavor: SUPPORTED_DB_TYPES = Field(..., description=f"Database type/flavor. Select from: {list(SUPPORTED_DB_TYPES.__args__)}")
    project_host: str = Field(..., description="Database Hostname")
    project_port: str = Field(..., description="Database Port (as string)")
    project_user: str = Field(..., description="Database User ID")
    password: str = Field(..., description="Database Password (will be encrypted before saving)") # Password is required for input
    project_db: str = Field(None, description="Database Name")
    max_threads: Optional[int] = Field(4, description="Maximum threads for connection operations")
    max_query_chars: Optional[int] = Field(None, description="Maximum characters for queries")
    url: Optional[str] = Field('', description="Connection URL (if connecting by URL)")
    connect_by_url: Optional[bool] = Field(False, description="Connect using URL")
    connect_by_key: Optional[bool] = Field(False, description="Connect using private key")
    private_key: Optional[str] = Field(None, description="Private Key (if connecting by key)")
    private_key_passphrase: Optional[str] = Field(None, description="Private Key Passphrase (if connecting by key)")
    http_path: Optional[str] = Field(None, description="HTTP Path (if applicable)")
 
 
class DBConnectionCreate(ConnectionBase):
    # Inherits all fields from ConnectionBase, including the required password for creation
    pass
 
class ConnectionAction(str, Enum):
    TEST = "test"
    CREATE = "create"
 
 
class ConnectionActionRequest(BaseModel):
    action: ConnectionAction
 
    # Required for both actions
    sql_flavor: str
    db_hostname: str
    db_port: int
    project_db: str
    user_id: str
    password: str
 
    # Only needed for "create"
    project_code: Optional[str] = None
    connection_name: Optional[str] = None
    connection_description: Optional[str] = None
    max_query_chars: Optional[int] = None
    url: Optional[str] = None
    connect_by_url: Optional[bool] = False
    connect_by_key: Optional[bool] = False
    private_key: Optional[str] = None
    private_key_passphrase: Optional[str] = None
    http_path: Optional[str] = None
 
class DBConnectionUpdate(BaseModel):
    # This model is used for update input. All fields are optional.
    # Password is optional here because it's only sent if the user changes it.
    project_code: Optional[str] = Field(None, description="Code identifying the project this connection belongs to")
    connection_name: Optional[str] = Field(None, description="Name of the database connection")
    connection_description: Optional[str] = Field(None, description="Description of the connection")
    sql_flavor: Optional[SUPPORTED_DB_TYPES] = Field(None, description=f"Database type/flavor. Select from: {list(SUPPORTED_DB_TYPES.__args__)}")
    project_host: Optional[str] = Field(None, description="Database Hostname")
    project_port: Optional[str] = Field(None, description="Database Port (as string)")
    project_user: Optional[str] = Field(None, description="Database User ID")
    password: str = Field(..., description="Database Password (will be encrypted before saving)")
    project_db: Optional[str] = Field(None, description="Database Name (if applicable)")
    max_threads: Optional[int] = Field(None, description="Maximum threads for connection operations")
    max_query_chars: Optional[int] = Field(None, description="Maximum characters for queries")
    url: Optional[str] = Field(None, description="Connection URL (if connecting by URL)")
    connect_by_url: Optional[bool] = Field(None, description="Connect using URL")
    connect_by_key: Optional[bool] = Field(None, description="Connect using private key")
    private_key: Optional[str] = Field(None, description="Private Key (if connecting by key)")
    private_key_passphrase: Optional[str] = Field(None, description="Private Key Passphrase (if connecting by key)")
    http_path: Optional[str] = Field(None, description="HTTP Path (if applicable)")
 
 
# Model for representing a Connection retrieved from the database (Output Model)
# This model does NOT inherit from ConnectionBase and does NOT include the raw password.
class DBConnectionOut(BaseModel):
    # Include fields that are safe to return from the database
    id: Union[UUID, str] # UUID from DB
    connection_id: int # BIGINT PK from DB
    project_code: str
    connection_name: str
    connection_description: Optional[str] = None
    sql_flavor: str # Return as string, not Literal, as DB stores string
    project_host: Optional[Any]
    project_port: Optional[Any]
    project_user: str
    project_pw_encrypted: str
    project_db: str
    max_threads: Optional[int] = None
    max_query_chars: Optional[int] = None
    url: Optional[str] = None
    connect_by_url: Optional[bool] = None
    connect_by_key: Optional[bool] = None
    # private_key and private_key_passphrase are NOT included for security
    http_path: Optional[str] = None
 
    class Config:
        # Allows Pydantic to read from SQLAlchemy model attributes (orm_mode)
        orm_mode = True
        # Allows population by field name or alias (important for mapping SQL column names)
        allow_population_by_field_name = True
 
 
 
class TestConnectionRequest(BaseModel):
    # This model is specifically for the test endpoint input
    sql_flavor: str = Field(
        ..., title="Database Type", description="Select from: PostgreSQL, MSSQL, Oracle, SQL Server, Snowflake, Redshift"
    )
    db_hostname: str = Field(..., title="DB Hostname")
    db_port: int = Field(..., title="DB Port") # Test connection expects integer port
    user_id: str = Field(..., title="User ID")
    password: str = Field(..., title="Password")
    project_db: Optional[str] = Field(None, title="Database Name (if applicable)")
 
 
class TestConnectionResponse(BaseModel):
    status: bool
    message: str
    details: Optional[str] = None
 
 
class TableGroupBase(BaseModel):
    # Base model for Table Group input/output fields
    table_groups_name: str = Field(..., description="Name of the table group")
    table_group_schema: Optional[str] = Field(None, description="Database schema for the table group")
    explicit_table_list: Optional[List[str]] = None # List[str] in Pydantic, comma-separated string in DB
    profiling_include_mask: Optional[str] = Field(None, description="Mask for tables to include")
    profiling_exclude_mask: Optional[str] = Field(None, description="Mask for tables to exclude")
    profile_id_column_mask: Optional[str] = Field('%id', description="Mask for ID columns")
    profile_sk_column_mask: Optional[str] = Field('%_sk', description="Mask for surrogate key columns")
    
    # Change these to bool for Pydantic validation if you want 'true'/'false' input
    # Then convert to 'Y'/'N' for DB storage.
    profile_use_sampling: str = Field('N', description="Use sampling (Y/N)") # Changed default to bool
    profile_flag_cdes: bool = Field(True, description="Flag CDEs (True/False)") # Changed default to bool
    profile_do_pair_rules: str = Field('N', description="Do pair rules (Y/N)") # Changed default to bool

    # Change these to actual numeric types for Pydantic validation
    profile_sample_percent: int = Field(30, description="Sample percentage") # Changed default to float
    profile_sample_min_count: int = Field(100000, description="Minimum sample count")
    min_profiling_age_days: int = Field(0, description="Minimum profiling age in days")
    profile_pair_rule_pct: Optional[float] = Field(95.0, description="Pair rule percentage") # Changed default to float/Optional

    description: Optional[str] = Field(None, description="Description of the table group")
    data_source: Optional[str] = Field(None, description="Data source")
    source_system: Optional[str] = Field(None, description="Source system")
    source_process: Optional[str] = Field(None, description="Source process")
    data_location: Optional[str] = Field(None, description="Data location")
    business_domain: Optional[str] = Field(None, description="Business domain")
    stakeholder_group: Optional[str] = Field(None, description="Stakeholder group")
    transform_level: Optional[str] = Field(None, description="Transform level")
    data_product: Optional[str] = Field(None, description="Data product")
    last_complete_profile_run_id: Optional[Union[UUID, str]] = Field(None, description="Last complete profile run ID")
    dq_score_profiling: Optional[float] = Field(None, description="DQ score from profiling")
    dq_score_testing: Optional[float] = Field(None, description="DQ score from testing")


    @validator('explicit_table_list', pre=True, always=True)
    def parse_explicit_table_list(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(',') if item.strip()]
        return v
    
    # # New validator to handle boolean conversions from string 'Y'/'N' on retrieval
    # @validator('profile_use_sampling', 'profile_do_pair_rules', pre=True)
    # def parse_yn_to_bool(cls, v):
    #     if isinstance(v, str):
    #         return v.upper() == 'Y'
    #     return v
    
    
# Re-define based on the updated TableGroupBase
class TableGroupCreate(TableGroupBase):
    pass

class TableGroupUpdate(TableGroupBase):
    # Make all fields optional for update operations
    table_groups_name: Optional[str] = None
    table_group_schema: Optional[str] = None
    explicit_table_list: Optional[List[str]] = None
    profiling_include_mask: Optional[str] = None
    profiling_exclude_mask: Optional[str] = None
    profile_id_column_mask: Optional[str] = None
    profile_sk_column_mask: Optional[str] = None
    profile_use_sampling: Optional[bool] = None # Now Optional[bool]
    profile_sample_percent: Optional[int] = None 
    profile_sample_min_count: Optional[int] = None
    min_profiling_age_days: Optional[int] = None
    profile_flag_cdes: Optional[bool] = None # Now Optional[bool]
    profile_do_pair_rules: Optional[bool] = None # Now Optional[bool]
    profile_pair_rule_pct: Optional[float] = None # Now Optional[float]
    description: Optional[str] = None
    data_source: Optional[str] = None
    source_system: Optional[str] = None
    source_process: Optional[str] = None
    data_location: Optional[str] = None
    business_domain: Optional[str] = None
    stakeholder_group: Optional[str] = None
    transform_level: Optional[str] = None
    data_product: Optional[str] = None
    last_complete_profile_run_id: Optional[Union[UUID, str]] = None
    dq_score_profiling: Optional[float] = None
    dq_score_testing: Optional[float] = None


 
class TableGroupOut(TableGroupBase):
    # Output model for Table Group, includes DB-generated fields
    id: Union[UUID, str] # UUID from DB
    project_code: str
    connection_id: int # BIGINT from DB
 
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
       
class TestSuite_TableGroups(TableGroupBase):
    id: Union[UUID, str]
    table_group_name: str
   
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
 
 
class ConnectionProfilingRequest(BaseModel):
    # This model is specifically for the profiling endpoint input body
    db_type: str # Should map to sql_flavor in backend service
    db_hostname: str # Should map to project_host
    db_port: int # Should map to project_port (str in DB, int in this model)
    user: str # Should map to project_user
    password: str # Should map to password input (encrypted as project_pw_encrypted)
    database: str # Should map to project_db
    project_code: str = "DEFAULT" # Should map to project_code
 
class ProfilingRunOut(BaseModel):
    id: UUID
    project_code: str
    connection_id: int
    table_groups_id: UUID
    profiling_starttime: Optional[datetime]
    profiling_endtime: Optional[datetime]
    status: Optional[str]
    log_message: Optional[str]
    table_ct: Optional[int]
    column_ct: Optional[int]
    anomaly_ct: Optional[int]
    anomaly_table_ct: Optional[int]
    anomaly_column_ct: Optional[int]
    dq_affected_data_points: Optional[int]
    dq_total_data_points: Optional[int]
    dq_score_profiling: Optional[float]
    process_id: Optional[int]
 
    class Config:
        orm_mode = True
 
 
class ProfileResultOut(BaseModel):
    id: UUID4
    dk_id: Optional[int]
    column_id: Optional[UUID4]
    project_code: Optional[str]
    connection_id: Optional[int]
    table_groups_id: Optional[UUID4]
    profile_run_id: Optional[UUID4]
    schema_name: Optional[str]
    run_date: Optional[datetime]
    table_name: Optional[str]
    position: Optional[int]
    column_name: Optional[str]
    column_type: Optional[str]
    general_type: Optional[str]
    record_ct: Optional[int]
    value_ct: Optional[int]
    distinct_value_ct: Optional[int]
    distinct_std_value_ct: Optional[int]
    null_value_ct: Optional[int]
    min_length: Optional[int]
    max_length: Optional[int]
    avg_length: Optional[float]
    zero_value_ct: Optional[int]
    zero_length_ct: Optional[int]
    lead_space_ct: Optional[int]
    quoted_value_ct: Optional[int]
    includes_digit_ct: Optional[int]
    filled_value_ct: Optional[int]
    min_text: Optional[str]
    max_text: Optional[str]
    upper_case_ct: Optional[int]
    lower_case_ct: Optional[int]
    non_alpha_ct: Optional[int]
    mixed_case_ct: Optional[int]
    numeric_ct: Optional[int]
    date_ct: Optional[int]
    top_patterns: Optional[str]
    top_freq_values: Optional[str]
    distinct_value_hash: Optional[str]
    min_value: Optional[float]
    min_value_over_0: Optional[float]
    max_value: Optional[float]
    avg_value: Optional[float]
    stdev_value: Optional[float]
    percentile_25: Optional[float]
    percentile_50: Optional[float]
    percentile_75: Optional[float]
    fractional_sum: Optional[float]
    min_date: Optional[datetime]
    max_date: Optional[datetime]
    before_1yr_date_ct: Optional[int]
    before_5yr_date_ct: Optional[int]
    before_20yr_date_ct: Optional[int]
    before_100yr_date_ct: Optional[int]
    within_1yr_date_ct: Optional[int]
    within_1mo_date_ct: Optional[int]
    future_date_ct: Optional[int]
    distant_future_date_ct: Optional[int]
    date_days_present: Optional[int]
    date_weeks_present: Optional[int]
    date_months_present: Optional[int]
    boolean_true_ct: Optional[int]
    datatype_suggestion: Optional[str]
    distinct_pattern_ct: Optional[int]
    embedded_space_ct: Optional[int]
    avg_embedded_spaces: Optional[float]
    std_pattern_match: Optional[str]
    pii_flag: Optional[str]
    functional_data_type: Optional[str]
    functional_table_type: Optional[str]
    sample_ratio: Optional[float]
 
    class Config:
        orm_mode = True
       
       
class TriggerProfilingRequest(BaseModel):
    connection_id: int
    table_group_id: str
   
class RunInfo(BaseModel):
    connection_id: int
    profiling_id: UUID
    status: str
    table_groups_id: UUID
    created_at: datetime
 
class DashboardStats(BaseModel):
    connections: int
    table_groups: int
    profiling_runs: int
    runs: List[RunInfo]
   
   
class LatestProfilingRunDashboardData(BaseModel):
    latest_run: ProfilingRunOut
    profile_results: List[ProfileResultOut]
 
    class Config:
        orm_mode = True
       
       
 
class LatestRunSummary(BaseModel):
    """
    Summary statistics for the latest profiling run, displayed on the dashboard.
    """
    tables: int
    columns: int
    rowCount: int
    missingValues: int
    dqScore: Optional[float] = None
    profilingScore: Optional[float] = None  # Same as dqScore for now
    cdeScore: Optional[float] = None        # Placeholder, always 0.0 in service
    distinctValues: int
    distinctValuesPercentage: Optional[float] = None
    completenessPercentage: Optional[float] = None

    
 
class RecentRunEntry(BaseModel):
    """
    A simplified model for displaying recent profiling runs in a list.
    Maps directly to relevant fields from ProfilingRunOut.
    """
    profiling_id: UUID4 # Corresponds to ProfilingRunOut.id
    profilingTime: datetime # Corresponds to ProfilingRunOut.profiling_starttime
    status: str # Corresponds to ProfilingRunOut.status
    tables: int # Corresponds to ProfilingRunOut.table_ct
 
    class Config:
        # This allows Pydantic to read ORM models directly
        from_attributes = True # Use from_attributes for Pydantic v2+, orm_mode = True for v1
 
class DashboardData(BaseModel):
    """
    The consolidated response model for the dashboard overview endpoint.
    Combines the latest run summary and a list of recent runs.
    """
    summary: LatestRunSummary
    recentRuns: List[RecentRunEntry]
 
# --- New Pydantic Models for Profile Run Details ---
 
class ColumnDataType(BaseModel):
    """
    Represents a column's name, type, and general type for display
    in the "Column Data Types" section.
    """
    columnName: str # Corresponds to ProfileResultOut.column_name
    columnType: str # Corresponds to ProfileResultOut.column_type
    generalType: Optional[str] = None # Corresponds to ProfileResultOut.general_type
 
class DataDistributionEntry(BaseModel):
    """
    Represents a single row in the "Data Distribution" table for a column.
    """
    column: str # Corresponds to ProfileResultOut.column_name
    dataType: str # Corresponds to ProfileResultOut.column_type
    distinctValues: int # Corresponds to ProfileResultOut.distinct_value_ct
    missingValues: int # Corresponds to ProfileResultOut.null_value_ct
    emptyValues: int # Derived from ProfileResultOut.null_value_ct + zero_length_ct (or zero_value_ct)
 
    class Config:
        # This allows Pydantic to read ORM models directly
        from_attributes = True # Use from_attributes for Pydantic v2+, orm_mode = True for v1
 
class TableNameItem(BaseModel):
    """
    A simple model for a table name, used in dropdowns or lists.
    """
    tableName: str # Corresponds to ProfileResultOut.table_name
 
    class Config:
        from_attributes = True
 
class TableDQScoreHistory(BaseModel):
    profiling_id: UUID
    profilingTime: datetime
    dqScore: Optional[float] = None # The DQ score for this specific table in this run
 
 
class TableDetailsData(BaseModel):
    """
    The consolidated response model for the specific table details endpoint.
    Includes overall run info, column data types, and data distribution for the selected table.
    """
    profilingTime: datetime
    status: str
    tableName: str
    columnDataTypes: List[ColumnDataType]
    dataDistribution: List[DataDistributionEntry]
    tableDQScoreHistory: List[TableDQScoreHistory]
    profilingScore: Optional[float] = None
    distinctValuePercentage: Optional[float] = None
    completenessPercentage: Optional[float] = None

 
 
 
class ScheduleProfilingRequest(BaseModel):
    conn_id: int
    group_id: UUID
    cron_expression: str
 
class ScheduleProfilingUpdate(BaseModel):
    conn_id: Optional[int] = None
    group_id: Optional[UUID] = None
    cron_expression: Optional[str] = None
    is_active: Optional[bool] = None
 
class ScheduledProfilingJobResponse(BaseModel):
    id: int
    conn_id: int
    connection_name : Optional[str]
    group_id: UUID
    table_group_name: Optional[str]
    cron_expression: str = Field(..., alias="schedule_cron_expression")
    scheduled_job_id: str
    is_active: bool
 
    class Config:
        orm_mode = True
       
   
   
class Test_Execution(BaseModel):
    strProjectCode: str
    strTableGroupsID: Optional[str]
    strTestSuite: str
    strGenerationSet: Optional[str] = None
    strTestSet: Optional[str] = None
   
 
class Severity(str, Enum):
    INHERIT = "Inherit"
    FAILED = "Fail"
    WARNING = "Warning"
 
 
class Test_Generation(BaseModel):
    strTableGroupsID: str
    strTestSuite: Optional[str]
    strGenerationSet: Optional[str] = None
    description: Optional[str]
    severity: Optional[Severity]
   
 
   

class TestSuiteMetadata(BaseModel):
    test_suite_description: Optional[str] = Field(None, alias="description") # Maps 'description' from request
    severity: Optional[str]
    export_to_observability: Optional[str]
    test_suite_schema: Optional[str]
    component_key: Optional[str]
    component_type: Optional[str]
    component_name: Optional[str]
    test_suite: Optional[str] = Field(None, alias="strTestSuite") # Maps 'strTestSuite' from request
    table_groups_id: Optional[UUID] = Field(None, alias="strTableGroupsID") # Maps 'strTableGroupsID' from request
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True # Allows you to use either alias or field name
   
 
 
class GenerateTestSuiteRequest(BaseModel):
    table_group_name: str = Field(..., description="The user-friendly name of the table group.")
    test_suite_name: str = Field(..., description="The name of the test suite to create or update.")
    generation_set: Optional[str] = Field(None, description="Optional generation set identifier.")
    test_suite_description: Optional[str] = Field(None, description="Description for the test suite.")
    test_action: Optional[str] = Field(None, description="Action for the test suite (e.g., 'Inherit', 'Run').") # Adjust based on actual enum if exists
    severity: Optional[Severity] = Field(Severity.INHERIT, description="Severity for the test suite.")
    export_to_observability: Optional[bool] = Field(False, description="Whether to export results to observability.")
    test_suite_schema: Optional[str] = Field(None, description="Schema for the test suite (often derived from table group).")
    component_key: Optional[str] = Field(None, description="Component key for the test suite.")
    component_type: Optional[str] = Field(None, description="Component type (e.g., 'dataset').")
    component_name: Optional[str] = Field(None, description="Component name for the test suite.")
    dq_score_exclude: Optional[bool] = Field(False, description="Whether to exclude from DQ score.")
   
   
 
# New model for TestResult

class TestResultWithDetails(BaseModel):
    id: UUID4
    result_id: int
    test_type: str
    test_suite_id: UUID4
    test_definition_id: Optional[UUID4]
    auto_gen: Optional[bool]
    test_time: Optional[datetime]
    starttime: Optional[datetime]
    endtime: Optional[datetime]
    schema_name: Optional[str]
    table_name: Optional[str]
    column_names: Optional[str]
    skip_errors: Optional[int]
    input_parameters: Optional[str]
    result_code: Optional[int]
    severity: Optional[str]
    result_status: Optional[str]
    result_message: Optional[str]
    result_measure: Optional[str]
    threshold_value: Optional[str]
    result_error_data: Optional[str]
    test_action: Optional[str]
    disposition: Optional[str]
    subset_condition: Optional[str]
    result_query: Optional[str]
    test_description: Optional[str] #This is present in both the test results and test types
    test_run_id: UUID4
    table_groups_id: Optional[UUID4]
    dq_prevalence: Optional[float]
    dq_record_ct: Optional[int]
    observability_status: Optional[str]

    # Fields from TestTypeModel
    test_name_short: Optional[str]
    test_name_long: Optional[str]
    test_type_description: Optional[str] # Renamed to avoid clash with test_results.test_description
    
    

    class Config:
        orm_mode = True
        # For UUID and datetime handling
        json_encoders = {
            UUID4: lambda v: str(v),
            datetime: lambda v: v.isoformat()
        }
 
 
 
class TestResultsWithConnection(BaseModel):
    connection_name: Optional[str]
    db_type:Optional[str]
    results: List[TestResultWithDetails]
    
    
    
# You can also add a response model for the list of results
class TestResultsResponse(BaseModel):
    results: List[TestResultWithDetails]
    total_results: int
 
class TestSuiteResponse(BaseModel):
    id: UUID
    test_suite: str
    table_groups_id: UUID
    test_suite_description: Optional[str]
    severity: Optional[str]
    export_to_observability: Optional[str]
    test_suite_schema: Optional[str]
    component_key: Optional[str]
    component_type: Optional[str]
    component_name: Optional[str]
    has_test_results: bool = False
 
    class Config:
        orm_mode = True
 
class AnomalyResultOut(BaseModel):
    id: UUID
    table_groups_id: UUID
    profile_run_id: UUID
    table_name: str
    column_name: str
    anomaly_id: str # Keep as str for consistency with ProfileAnomalyTypeModel.id lookup
    anomaly_name: Optional[str] = None
    anomaly_description: Optional[str] = None
    issue_likelihood: Optional[str] = None
    suggested_action: Optional[str] = None
    dq_dimension: Optional[str] = None
    detail: str
    dq_prevalence: Optional[float]
    created_at: Optional[datetime]
    
    # NEW FIELD: Add profiling_starttime to the Pydantic output model
    profiling_starttime: datetime 

    class Config:
        orm_mode = True # This will allow direct mapping from SQLAlchemy models
        
        
class AnomalyGroupedByTable(BaseModel):
    table_group: TableGroupOut
    anomaly_results_by_table: Dict[str, List[AnomalyResultOut]]
 
class AnomalyGroupedByRun(BaseModel):
    table_group: TableGroupOut
    anomaly_results_by_run: Dict[str, Dict[str, List[AnomalyResultOut]]]
 
class AnomalyUngrouped(BaseModel):
    table_group: TableGroupOut
    all_anomaly_results: List[AnomalyResultOut]
    
class LatestTestRunSummary(BaseModel):
    totalTests: int
    passed: int
    failed: int
    warnings: int
    errors: int
    duration: str
    dqScore: float  # If you compute some kind of test quality score

class RecentTestRunEntry(BaseModel):
    test_run_id: UUID
    testTime: datetime
    status: str
    tests: int

class TestDashboardData(BaseModel):
    summary: LatestTestRunSummary
    recentRuns: List[RecentTestRunEntry]

class IndividualTestResult(BaseModel):
    status: str
    errorMessage: Optional[str]
    startTime:Optional[datetime]
    endTime: Optional[datetime]
    duration: Optional[str]
    metrics: Dict[str, Any]  # optional metrics per test

class TestDetailsData(BaseModel):
    test_suite: str
    testRunId: UUID
    results: List[IndividualTestResult]
    status: str
    startTime: datetime
    endTime: datetime
    dqScore: Optional[float]


class TestNameItem(BaseModel):
    testSuiteName: str
    
    
#------------------------------------------------

class StatusSummary(BaseModel):
    status: str
    count: int

class TestTypeSummary(BaseModel):
    test_type: str
    count: int

class TestResultDetail(BaseModel):
    id: UUID4
    result_id: int
    test_type: str
    test_suite_id: UUID4
    test_definition_id: UUID4
    auto_gen: bool
    test_time: datetime
    starttime: Optional[datetime]
    endtime: Optional[datetime]
    schema_name: str
    table_name: str
    column_names: str
    skip_errors: int
    input_parameters: str
    result_code: int
    severity: str
    result_status: str
    result_message: str
    result_measure: str
    threshold_value: str
    result_error_data: Optional[str]
    test_action: Optional[str]
    disposition: Optional[str]
    subset_condition: Optional[str]
    result_query: Optional[str]
    test_description: str
    test_run_id: UUID4
    table_groups_id: UUID4
    dq_prevalence: float
    dq_record_ct: int
    observability_status: str

    class Config:
        from_attributes = True # updated from orm_mode = True
        orm_mode = True
        
class TestSuiteCounts(BaseModel):
    """
    Pydantic model for the counts within a single test suite.
    """
    test_suite_id: UUID4
    passed_ct: int
    failed_ct: int
    warning_ct: int
    error_ct: int
    total_tests_executed: int
    percentages: Dict[str, float]

class TestSuiteSummary(BaseModel):
    """
    Pydantic model for the overall summary grouped by test suite.
    """
    test_suite_summaries: List[TestSuiteCounts]
    
    

class ErrorResponse(BaseModel):
    detail: str

# --- 1. Overall Data Quality Overview (Top Section) ---

class OverallDataQualityOverviewResponse(BaseModel):
    data_quality_score: Optional[float]
    test_failures: Dict[str, Any] # Using Dict[str, Any] for flexibility for now, can be refined
    columns_tested: Optional[Any]
    records_tested: Optional[Any]
    test_status: Dict[str, Any] # Using Dict[str, Any] for flexibility for now, can be refined

# --- 2. Data Quality Trend (Chart) ---

class TrendDataPoint(BaseModel):
    day: int
    value: float

class DataQualityTrendResponse(BaseModel):
    trend_data: List[TrendDataPoint]
    metric_label: str
    
class DailyTrendDataPoint(BaseModel):
    date: datetime
    dq_score: float
    total_tests: int
    passed_tests: int
    failed_tests: int
    warning_tests: int
    error_tests: int
    # Health Dimension specific failures (counts)
    schema_drift_failures: int = 0
    data_drift_failures: int = 0
    volume_failures: int = 0
    recency_failures: int = 0

# --- 3. Recent Test Runs (Left-Hand Panel & Table) ---

class RecentTestRunSummary(BaseModel):
    test_suite_name: str
    test_suite_id: UUID
    table_group_name: str
    table_group_id: UUID
    status: str

class RecentTestRunDetail(BaseModel):
    test_run_id: UUID
    test_suite_name: str
    test_suite_id: UUID
    status: str
    records_tested: str # Formatted for display
    duration_display: str # Formatted for display
    table_group_name: str
    table_group_id: UUID
    connection_id: int
    connection_name: str
    db_type: str
    explicit_tables_list: Any

class RecentTestRunsTableResponse(BaseModel):
    total_count: int
    test_runs: List[RecentTestRunDetail]

# --- 4. Data Sources (Right-Hand Panel) ---

class DataSource(BaseModel):
    connection_name: str
    connection_id: int
    data_quality_score: Optional[float]
    #status: str


    
# --- General Schemas ---
class DropdownOption(BaseModel):
    display_name: str
    value: str # Can be str for UUID or int for connection_id

# --- Overview Metrics Schemas ---
class OverviewMetricsResponse(BaseModel):
    total_profiles: int
    rows_profiled: Optional[Any]
    columns_profiled: int
    success_rate: float
    success_rate_change: Optional[str] = None
    failed_profiles: int

# --- Profile Run Trend Schemas ---
class ProfileRunTrendDataPoint(BaseModel):
    date: str # YYYY-MM-DD or YYYY-MM-DD (week start) or YYYY-MM-01
    total_runs: int
    successful_runs: int
    avg_dq_score: Optional[float] = None

class ProfileRunTrendResponse(BaseModel):
    trend_data: List[ProfileRunTrendDataPoint]

# --- Recent Profile Runs Schemas ---
class RecentProfileRun(BaseModel):
    run_display_id: str
    run_uuid: UUID4
    database_name: str
    database_connection_id: int
    schema_name: str
    schema_table_group_uuid: UUID4
    table_group_name: str
    status: str
    columns_profiled: int
    start_time: datetime

class RecentProfileRunsResponse(BaseModel):
    total_runs: int
    runs: List[RecentProfileRun]

# --- Column Stats Distribution Schemas ---
class DistributionDataPoint(BaseModel):
    range: str # e.g., "0-10%"
    column_count: int

class ColumnStatsDistributionResponse(BaseModel):
    chart_title: str
    x_axis_label: str
    y_axis_label: str
    distribution_data: List[DistributionDataPoint]

# --- Top Distinct Values (now Distinct Value Counts) Schemas ---
# Renaming for clarity based on new logic
class ColumnDistinctCountDetail(BaseModel):
    table_name: str
    column_name: str
    distinct_value_count: int # Changed to show the count directly

class ColumnDistinctCountsResponse(BaseModel):
    column_distinct_counts: List[ColumnDistinctCountDetail]
    
    
class ColumnMetricType(str, Enum):
    NULL_PERCENTAGE = "null_percentage"
    DISTINCT_PERCENTAGE = "distinct_percentage"
    AVG_LENGTH = "avg_length"
    
    

# Base model for test_definitions, matching the database schema
class TestDefinitionBase(BaseModel):
    table_groups_id: Optional[UUID] = None
    profile_run_id: Optional[UUID] = None
    test_type: str = Field(..., max_length=200)
    test_suite_id: UUID
    test_description: Optional[str] = Field(None, max_length=1000)
    test_action: Optional[str] = Field(None, max_length=100)
    schema_name: Optional[str] = Field(None, max_length=100)
    table_name: Optional[str] = Field(None, max_length=100)
    column_name: Optional[str] = Field(None, max_length=500)
    skip_errors: Optional[int] = None
    baseline_ct: Optional[str] = Field(None, max_length=1000)
    baseline_unique_ct: Optional[str] = Field(None, max_length=1000)
    baseline_value: Optional[str] = Field(None, max_length=1000)
    baseline_value_ct: Optional[str] = Field(None, max_length=1000)
    threshold_value: Optional[str] = Field(None, max_length=1000)
    baseline_sum: Optional[str] = Field(None, max_length=1000)
    baseline_avg: Optional[str] = Field(None, max_length=1000)
    baseline_sd: Optional[str] = Field(None, max_length=1000)
    subset_condition: Optional[str] = Field(None, max_length=500)
    groupby_names: Optional[str] = Field(None, max_length=200)
    having_condition: Optional[str] = Field(None, max_length=500)
    window_date_column: Optional[str] = Field(None, max_length=100)
    window_days: Optional[int] = None
    match_schema_name: Optional[str] = Field(None, max_length=100)
    match_table_name: Optional[str] = Field(None, max_length=100)
    match_column_names: Optional[str] = Field(None, max_length=200)
    match_subset_condition: Optional[str] = Field(None, max_length=500)
    match_groupby_names: Optional[str] = Field(None, max_length=200)
    match_having_condition: Optional[str] = Field(None, max_length=500)
    test_mode: Optional[str] = Field(None, max_length=20)
    custom_query: Optional[str] = None
    test_active: str = Field('Y', max_length=10)
    test_definition_status: Optional[str] = Field(None, max_length=200)
    severity: Optional[str] = Field(None, max_length=10)
    watch_level: str = Field('WARN', max_length=10)
    check_result: Optional[str] = Field(None, max_length=500)
    lock_refresh: str = Field('N', max_length=10)
    last_auto_gen_date: Optional[datetime] = None
    profiling_as_of_date: Optional[datetime] = None
    last_manual_update: Optional[datetime] = None
    export_to_observability: Optional[str] = Field(None, max_length=5)
    
    
    class Config:
        from_attributes = True
        from_orm = True


# Assuming the structure of your DB models is similar to these
class TestDefinition(BaseModel):
    id: UUID
    test_suite_id: UUID
    table_groups_id: Optional[UUID] = None
    project_code: Optional[str] = None
    schema_name: Optional[str] = None
    table_name: str
    column_name: Optional[str] = None
    test_type: str
    test_action: Optional[str] = None # e.g., "REVIEW", "REJECT", "FAIL"
    test_mode: Optional[str] = None # e.g., "PROD", "DEV", "TEST"
    severity: Optional[str] = None # e.g., "INFO", "WARN", "CRITICAL"
    export_to_observability: Optional[str] = None # 'Y' or 'N'
    watch_level: Optional[str] = None # e.g., 0-9
    test_active: Optional[str] = 'Y' # 'Y' or 'N'
    lock_refresh: Optional[str] = 'N' # 'Y' or 'N'
    test_name_short: Optional[str] = None # This is from TestTypeModel, will be populated on read
    test_description: Optional[str] = None # This is from TestTypeModel, will be populated on read
    check_result: Optional[str] = None # Last check result (e.g., "OK", "FAIL")
    test_definition_status: Optional[str] = None # e.g., "OK", "REVIEW", "REJECT"

    # Dynamic/Parameter Fields (actual values for the test definition)
    threshold_value: Optional[float] = None
    baseline_value_ct: Optional[int] = None
    baseline_value_str: Optional[str] = None
    custom_query: Optional[str] = None
    # Add other dynamic parameter fields that exist in your TestDefinitionModel
    # Example:
    # other_param_1: Optional[str] = None
    # other_param_2: Optional[float] = None


    # Timestamps and Run Info
    create_ts: Optional[datetime] = None
    run_ts: Optional[datetime] = None
    end_ts: Optional[datetime] = None
    last_manual_update: Optional[datetime] = None
    profile_run_id: Optional[UUID] = None
    last_run_id: Optional[UUID] = None

    # --- New fields added to TestDefinition for dynamic UI rendering ---
    # These will be populated from the TestTypeModel when fetched for editing
    test_type_long_name: Optional[str] = Field(None, description="Long name of the Test Type from TestTypeModel.")
    test_type_description_full: Optional[str] = Field(None, description="Full description of the Test Type from TestTypeModel.")
    usage_notes: Optional[str] = Field(None, description="Usage notes for the Test Type from TestTypeModel.")
    test_scope: Optional[str] = Field(None, description="Scope of the Test Type (column, table, referential, custom) from TestTypeModel.")
    column_name_prompt: Optional[str] = Field(None, description="Prompt for column_name specific to this Test Type.")
    column_name_help: Optional[str] = Field(None, description="Help text for column_name specific to this Test Type.")
    default_parm_columns: Optional[str] = Field(None, description="Comma-separated list of dynamic parameter column names from TestTypeModel.")
    default_parm_prompts: Optional[str] = Field(None, description="Comma-separated list of prompts for dynamic parameters from TestTypeModel.")
    default_parm_help: Optional[str] = Field(None, description="Pipe-separated list of help texts for dynamic parameters from TestTypeModel.")


    class Config:
        from_attributes = True # for Pydantic V2, use 
        orm_mode = True 
        


class TestSuiteDetailResponse(BaseModel):
    test_suite: TestSuiteResponse
    test_definitions: List[TestDefinition]

    class Config:
        from_attributes = True 
        orm_mode = True       
        
        
        
class TestType(BaseModel):
    id: int 
    test_type: str = Field(..., max_length=200) # Unique identifier, like 'COLUMN_AVG'
    test_name_short: str = Field(..., max_length=200) # Short display name, like 'Column Average'
    test_description: Optional[str] = Field(None, max_length=1000)
    test_name_long: str = Field(..., max_length=200) # Longer description, like 'Average of a column'
    usage_notes: Optional[str] = None # Assuming this can be longer, or text type
    measure_uom: Optional[str] = Field(None, max_length=50)
    measure_uom_description: Optional[str] = Field(None, max_length=1000)
    threshold_description: Optional[str] = Field(None, max_length=1000)
    default_severity: Optional[str] = Field(None, max_length=10)
    run_type: str = Field(..., max_length=20) # e.g., 'QUERY', 'CAT'
    test_scope: str = Field(..., max_length=20) # e.g., 'column', 'table', 'referential', 'custom'
    dq_dimension: Optional[str] = Field(None, max_length=100)
    default_parm_columns: Optional[str] = Field(None, max_length=500) # Comma-separated list of dynamic parameters
    default_parm_prompts: Optional[str] = Field(None, max_length=500) # Comma-separated list of display labels
    default_parm_help: Optional[str] = Field(None, max_length=1000) # Pipe-separated list of help texts
    column_name_prompt: Optional[str] = Field(None, max_length=200)
    column_name_help: Optional[str] = Field(None, max_length=1000)

    class Config:
        orm_mode = True

class TestDefinitionCreate(BaseModel):
    # Core identifying fields (required for creation)
    test_type: str
    test_suite_id: UUID

    # Fields directly settable by the user (matching show_test_form inputs)
    # These often have default values or inherit from test_suite/test_type,
    # but the API payload should allow explicit override.
    test_description: Optional[str] = Field(None, max_length=1000) # Override for test type description
    test_action: Optional[str] = Field(None, max_length=100)
    test_mode: Optional[str] = Field(None, max_length=20)
    lock_refresh: bool = False # UI toggle (boolean maps to 'Y'/'N' in backend)
    test_active: bool = True # UI toggle (boolean maps to 'Y'/'N' in backend)
    severity: Optional[str] = None # 'Warning', 'Fail' or None (for inherited)
    export_to_observability: Optional[str] = None # 'Yes', 'No' or None (for inherited)
    watch_level: Optional[str] = 'WARN' # Default as per UI

    # Table/Column specific fields
    table_name: str = Field(..., max_length=100) # Required
    column_name: Optional[str] = Field(None, max_length=500) # Conditional based on test_scope

    # Dynamic Attributes from test_types.default_parm_columns (all optional, can be null)
    custom_query: Optional[str] = None
    baseline_ct: Optional[str] = Field(None, max_length=1000)
    baseline_unique_ct: Optional[str] = Field(None, max_length=1000)
    baseline_value: Optional[str] = Field(None, max_length=1000)
    baseline_value_ct: Optional[str] = Field(None, max_length=1000)
    threshold_value: Optional[str] = Field(None, max_length=1000) # Now string as per show_test_form
    baseline_sum: Optional[str] = Field(None, max_length=1000)
    baseline_avg: Optional[str] = Field(None, max_length=1000)
    baseline_sd: Optional[str] = Field(None, max_length=1000)
    subset_condition: Optional[str] = Field(None, max_length=500)
    groupby_names: Optional[str] = Field(None, max_length=200)
    having_condition: Optional[str] = Field(None, max_length=500)
    window_date_column: Optional[str] = Field(None, max_length=100)
    window_days: Optional[int] = None
    match_schema_name: Optional[str] = Field(None, max_length=100)
    match_table_name: Optional[str] = Field(None, max_length=100)
    match_column_names: Optional[str] = Field(None, max_length=200)
    match_subset_condition: Optional[str] = Field(None, max_length=500)
    match_groupby_names: Optional[str] = Field(None, max_length=200)
    match_having_condition: Optional[str] = Field(None, max_length=500)

    # Fields that might be set by the UI but are internal/derived on backend
    # These should typically NOT be in the Create payload, unless you explicitly want
    # the client to provide them, even if derived.
    # project_code: Optional[str] = None # Derived from table_group_id
    # table_groups_id: Optional[UUID] = None # Derived from test_suite_id
    # profile_run_id: Optional[UUID] = None # Backend will link this if applicable
    skip_errors: Optional[int] = 0 # UI provides this as default
    # test_definition_status: Optional[str] = None # Backend status
    # check_result: Optional[str] = None # Backend result

class TestDefinitionUpdate(BaseModel):
    test_description: Optional[str] = Field(None, max_length=1000)
    severity: Optional[str] = Field(None, max_length=10)
    threshold_value: Optional[str] = Field(None, max_length=1000)
    table_groups_id: Optional[UUID] = None
    profile_run_id: Optional[UUID] = None
    test_type: Optional[str] = Field(None, max_length=200)
    test_suite_id: Optional[UUID] = None
    test_action: Optional[str] = Field(None, max_length=100)
    schema_name: Optional[str] = Field(None, max_length=100)
    table_name: Optional[str] = Field(None, max_length=100)
    column_name: Optional[str] = Field(None, max_length=500)
    skip_errors: Optional[int] = None
    baseline_ct: Optional[str] = Field(None, max_length=1000)
    baseline_unique_ct: Optional[str] = Field(None, max_length=1000)
    baseline_value: Optional[str] = Field(None, max_length=1000)
    baseline_value_ct: Optional[str] = Field(None, max_length=1000)
    baseline_sum: Optional[str] = Field(None, max_length=1000)
    baseline_avg: Optional[str] = Field(None, max_length=1000)
    baseline_sd: Optional[str] = Field(None, max_length=1000)
    subset_condition: Optional[str] = Field(None, max_length=500)
    groupby_names: Optional[str] = Field(None, max_length=200)
    having_condition: Optional[str] = Field(None, max_length=500)
    window_date_column: Optional[str] = Field(None, max_length=100)
    window_days: Optional[int] = None
    match_schema_name: Optional[str] = Field(None, max_length=100)
    match_table_name: Optional[str] = Field(None, max_length=100)
    match_column_names: Optional[str] = Field(None, max_length=200)
    match_subset_condition: Optional[str] = Field(None, max_length=500)
    match_groupby_names: Optional[str] = Field(None, max_length=200)
    match_having_condition: Optional[str] = Field(None, max_length=500)
    test_mode: Optional[str] = Field(None, max_length=20)
    custom_query: Optional[str] = None
    test_active: Optional[str] = Field(None, max_length=10)
    test_definition_status: Optional[str] = Field(None, max_length=200)
    watch_level: Optional[str] = Field(None, max_length=10)
    check_result: Optional[str] = Field(None, max_length=500)
    lock_refresh: Optional[str] = Field(None, max_length=10)
    last_auto_gen_date: Optional[datetime] = None
    profiling_as_of_date: Optional[datetime] = None
    export_to_observability: Optional[str] = Field(None, max_length=5)

class DetailedTestDefinition(BaseModel):
    summary_info: Dict[str, Any]
    detailed_info: Dict[str, Any]
    

class DynamicFormField(BaseModel):
    """Represents a single dynamic input field required for a test type."""
    field_name: str = Field(..., description="The internal name of the field (maps to TestDefinitionCreate attribute)")
    prompt: str = Field(..., description="The user-friendly label to display for the field")
    help_text: Optional[str] = Field(None, description="Detailed help text for the user input")

class TestTypeFormDefinition(BaseModel):
    """Defines the dynamic input fields required for a specific test type."""
    test_type: str = Field(..., description="The identifier of the test type")
    test_name_short: str = Field(..., description="The short name of the test type")
    test_description: Optional[str] = Field(None, description="General description of the test")
    usage_notes: Optional[str] = Field(None, description="Usage notes for the test")
    test_scope: str = Field(..., description="The scope of the test (column, table, referential, custom)")
    severity: Optional[str] = Field(None, description="Severity level of the test")

    # Information for the 'column_name' field
    column_name_prompt: Optional[str] = Field(None, description="Custom prompt for the column name field")
    column_name_help: Optional[str] = Field(None, description="Custom help text for the column name field")

    # List of additional dynamic parameters
    dynamic_parameters: List[DynamicFormField] = Field([], description="List of dynamic input fields for this test type")

    class Config:
        from_attributes = True # Or orm_mode = True for Pydantic V1