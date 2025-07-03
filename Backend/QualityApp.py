from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import logging
import os
from datetime import datetime, timedelta
from jose import JWTError, jwt

from sqlalchemy import create_engine, text, func, cast, Date, distinct, case, or_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import uuid
import json

# Get the absolute path to the directory containing backend_services.py
backend_dir = os.path.dirname(os.path.abspath(__file__))
# Get the absolute path to the parent directory (DB_Inspector_App)
parent_dir = os.path.dirname(backend_dir)

# Logging config
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)
LOG.info(f"Backend directory: {backend_dir}")
LOG.info(f"Backend directory: {parent_dir}")
# Add the parent directory to sys.path temporarily
sys.path.insert(0, parent_dir)

from Backend.backend_services import(
    test_connection_service,
    create_connection_service,
    list_connections_service,
    get_connection_service,
    update_connection_service,
    delete_connection_service,
    create_table_group_service,
    get_table_groups_service,
    update_table_group_service,
    get_specific_table_group_service,
    delete_table_group_service,
    trigger_profiling_service,
    # get_profile_results_by_run_id,
    # get_profiling_runs_by_connection,
    get_profile_results_for_run_detail,
    get_profiling_runs_by_table_group,
    get_all_profiling_runs_service,
    get_latest_profiling_run_dashboard_data_service,
    get_all_schedules_service,
    get_schedule_by_id_service,
    create_schedule_service,
    update_schedule_service,
    delete_schedule_service,
    reactivate_schedule_service,
    load_existing_scheduled_jobs,
    get_dashboard_overview_data_service,
    get_table_names_for_run_service,
    get_table_profiling_details_service,
    handle_connection_action,
    create_test_suites,
    list_test_suites,
    delete_test_suite,
    read_test_suite,
    update_test_suite,
    run_test_suites,
    list_table_group_service,
    display_test_results,
    get_anomaly_results,
    get_overall_data_quality_overview_service,
    get_data_quality_trend_service,
    get_recent_test_runs_service,
    get_data_sources_service,
    get_overview_metrics_service,
    get_profile_run_trend_service,
    get_recent_profile_runs_service,
    get_column_stats_distribution_service,
    get_dropdown_options_service,
    get_column_distinct_counts_service,
    get_test_run_status_summary_service,
    get_test_type_summary_by_status_service,
    get_detailed_test_results_service,
    get_test_runs_summary_by_suite_service,
    scheduler
)
from Backend.models.models import (
    DBConnectionUpdate,
    TableGroupCreate, # Use TableGroupCreate for input
    DBConnectionOut, # Use DBConnectionOut for output
    TableGroupOut,
    ProfileResultOut,
    ProfilingRunOut,
    TriggerProfilingRequest,
    DashboardStats,
    LatestProfilingRunDashboardData,
    ScheduleProfilingRequest,
    ScheduleProfilingUpdate,
    ScheduledProfilingJobResponse,
    DashboardData,
    TableDetailsData,
    TableNameItem,
    ConnectionActionRequest,
    Test_Generation,
    Test_Execution,
    TestSuiteMetadata,
    TestSuiteResponse,
    TestResultDetail,
    TestResultsWithConnection,
    TestSuiteSummary,
    TableGroupUpdate,
    
    OverallDataQualityOverviewResponse,
    DataQualityTrendResponse,
    RecentTestRunsTableResponse,
    DataSource,
    ErrorResponse,
    
    
    OverviewMetricsResponse, RecentProfileRunsResponse, 
    ProfileRunTrendResponse, ColumnStatsDistributionResponse,
    DropdownOption, ColumnDistinctCountsResponse, ColumnMetricType,
    
    
    TestDefinition,
    TestSuiteDetailResponse,
    TestDefinitionCreate,
    TestDefinitionUpdate,
    DetailedTestDefinition,
    TestType,TestTypeFormDefinition,
    DynamicFormField,
    ProfileResultOut
    
    
    )
from Backend.Auth.auth import AuthenticationMiddleware, get_current_user
from Backend.helpers.helper import get_latest_successful_run_id, get_time_filter, calculate_success_rate_change, format_duration_display
from pydantic import BaseModel
from typing import List, Dict, Any 
from uuid import UUID


from Backend.db.database import get_db, SessionLocal, TestDefinitionModel, TestTypeModel, TableGroupModel, TestSuiteModel, ProfileResultModel
from Backend.swagger import custom_openapi
from sqlalchemy.orm import Session 
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

app = FastAPI(title='Covasant Data Quality Tool')
#app.add_middleware(AuthenticationMiddleware)  
app.add_middleware(
    CORSMiddleware,  # <-- CORS last lo pettale because ikkada after authentication cors raavale
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#app.openapi = lambda: custom_openapi(app)

# --- Connection Endpoints ---

@app.post("/api/connections", tags=["Connections"])
def connection_action_route(
    conn_data: ConnectionActionRequest,
    db: Session = Depends(get_db)
):
    return handle_connection_action(conn_data, db)

@app.get("/api/connections", response_model=List[DBConnectionOut], tags=["Connections"])
def list_connections_route(db: Session = Depends(get_db)):
    return list_connections_service(db=db)

# @app.get("/api/connections", response_model=List[DBConnectionOut], tags=["Connections"])
# def list_connections_route(db: Session = Depends(get_db)):
#     return list_connections_service(db=db)

@app.get("/api/connections/{connection_id}", response_model=DBConnectionOut, tags=["Connections"])
def get_connection_route(connection_id: int, db: Session = Depends(get_db)):
    return get_connection_service(conn_id=connection_id, db=db)

@app.put("/api/connections/{connection_id}", response_model=DBConnectionOut, tags=["Connections"])
def update_connection_route(connection_id: int, conn_data: DBConnectionUpdate, db: Session = Depends(get_db)):
    return update_connection_service(conn_id=connection_id, conn_data=conn_data, db=db)

@app.delete("/api/connections/{connection_id}", tags=["Connections"])
def delete_connection_route(connection_id: int, db: Session = Depends(get_db)):
    return delete_connection_service(conn_id=connection_id, db=db)

# --- Table Group Endpoints ---

@app.post("/api/connections/{connection_id}/table-groups/", response_model=TableGroupOut, tags=["Table Groups"])
def create_table_group_route(connection_id: int, table_group_data: TableGroupCreate, db: Session = Depends(get_db)):
    return create_table_group_service(conn_id=connection_id, table_group_data=table_group_data, db=db)

@app.get("/api/connections/{connection_id}/table-groups/", response_model=List[TableGroupOut], tags=["Table Groups"])
def get_table_groups_route(connection_id: int, db: Session = Depends(get_db)):
    return get_table_groups_service(conn_id=connection_id, db=db)

@app.get("/api/connections/{connection_id}/table-groups/{group_id}", response_model=TableGroupOut, tags=["Table Groups"])
def get_specific_table_group_route(connection_id: int, group_id: str, db: Session = Depends(get_db)):
    return get_specific_table_group_service(conn_id=connection_id, group_id=group_id, db=db)


@app.patch("/api/connections/{connection_id}/table-groups/{group_id}", response_model=TableGroupOut, tags=["Table Groups"])
def update_table_group_route(connection_id: int,group_id: str,table_group_data: TableGroupUpdate,db: Session = Depends(get_db)):
    """
    Updates an existing table group by ID for a specific connection.
    Supports partial updates.
    """
    return update_table_group_service(conn_id=connection_id,group_id=group_id,table_group_data=table_group_data,db=db)

@app.delete("/api/connections/{connection_id}/table-groups/{group_id}", tags=["Table Groups"])
def delete_table_group_route(connection_id: int, group_id: str, db: Session = Depends(get_db)):
    return delete_table_group_service(conn_id=connection_id, group_id=group_id, db=db)

# --- Trigger Background Profiling Endpoint ---

@app.post("/api/run-profiling", tags=["Profiling"])
def trigger_profiling_route(request_data: TriggerProfilingRequest):
    return trigger_profiling_service(conn_id=request_data.connection_id, group_id=request_data.table_group_id)


#----------   Profiling Endpoints   ----------

@app.get("/api/connections/{conn_id}/table-groups/{group_id}/profiling-runs", response_model=List[ProfilingRunOut],tags=["Profliing"])
def list_profiling_runs_for_group(conn_id: int, group_id: UUID, db: Session = Depends(get_db)):
    """
    Get a list of all profiling runs for a specific table group within a data connection.
    """
    return get_profiling_runs_by_table_group(conn_id, group_id, db)

@app.get("/api/connections/{conn_id}/table-groups/{group_id}/profiling-runs/{run_id}/profile-results", response_model=List[ProfileResultOut],tags=["Profliing"])
def get_profile_results_detail_for_run(conn_id: int, group_id: UUID, run_id: UUID, db: Session = Depends(get_db)):
    """
    Get a list of all profile results (details) for a specific profiling run,
    ensuring it belongs to the given table group and connection.
    """
    return get_profile_results_for_run_detail(conn_id, group_id, run_id, db)

@app.get("/api/home", response_model=DashboardStats, tags=["Dashboard"])
def get_all_profiling_runs(db: Session = Depends(get_db)):
    return get_all_profiling_runs_service(db)

@app.get("/api/latest-profiling-run", response_model=LatestProfilingRunDashboardData, tags=["Dashboard"])
def get_latest_profiling_run_dashboard_data(db: Session = Depends(get_db)):
    return get_latest_profiling_run_dashboard_data_service(db)


#----------   Profiling Scheduling Endpoints   ----------
 
 
@app.on_event("startup")
def startup_event():
    scheduler.start()
    with SessionLocal() as db:
        load_existing_scheduled_jobs(db)
         
         

@app.get("/api/schedules", response_model=List[ScheduledProfilingJobResponse], tags=["Scheduling"])
def get_schedules(db: Session = Depends(get_db)):
    return get_all_schedules_service(db)

@app.get("/api/schedules/{scheduled_job_id}", response_model=ScheduledProfilingJobResponse, tags=["Scheduling"])
def get_schedule(scheduled_job_id: str, db: Session = Depends(get_db)):
    return get_schedule_by_id_service(scheduled_job_id, db)

@app.post("/api/schedules", response_model=ScheduledProfilingJobResponse, tags=["Scheduling"])
def create_schedule(request: ScheduleProfilingRequest, db: Session = Depends(get_db)):
    return create_schedule_service(request, db)

@app.put("/api/schedules/{scheduled_job_id}", response_model=ScheduledProfilingJobResponse, tags=["Scheduling"])
def update_schedule(scheduled_job_id: str, update: ScheduleProfilingUpdate, db: Session = Depends(get_db)):
    return update_schedule_service(scheduled_job_id, update, db)

@app.delete("/api/schedules/{scheduled_job_id}", tags=["Scheduling"])
def delete_schedule(
    scheduled_job_id: str,
    mode: str = Query(default="deactivate", pattern="^(deactivate|delete_permanent)$"),
    db: Session = Depends(get_db)
):
    return delete_schedule_service(scheduled_job_id, db, mode)

@app.post("/api/schedules/{scheduled_job_id}/reactivate", tags=["Scheduling"])
def reactivate_schedule(scheduled_job_id: str,db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    Reactivates a previously deactivated scheduled profiling job.
    """
    return reactivate_schedule_service(scheduled_job_id, db)

# ---------- New Dashboard & Details Endpoints ----------

@app.get("/api/dashboard-overview", response_model=DashboardData, tags=["New Dashboard"])
def get_dashboard_overview(db: Session = Depends(get_db)):
    """
    Fetches consolidated data for the Profile Run Dashboard:
    - Summary of the latest profiling run (Tables, Columns, Row Count, Missing Values)
    - List of recent profiling runs
    """
    return get_dashboard_overview_data_service(db)


@app.get("/api/profiling-runs/{run_id}/table-names", response_model=List[TableNameItem], tags=["New Profiling Results"])
def get_table_names_for_profiling_run(run_id: UUID, db: Session = Depends(get_db)):
    """
    Fetches a list of table names profiled in a specific profiling run.
    Used for the dropdown in the Profile Run Details section.
    """
    return get_table_names_for_run_service(run_id, db)


@app.get("/api/profiling-runs/{run_id}/tables/{table_name}/details", response_model=TableDetailsData, tags=["New Profiling Results"])
def get_profiling_table_details(run_id: UUID, table_name: str, db: Session = Depends(get_db)):
    """
    Fetches detailed profiling results for a specific table within a given profiling run.
    Includes Column Data Types and Data Distribution.
    """
    return get_table_profiling_details_service(run_id, table_name, db)


# ----------   Testing Endpoints   ----------

@app.get("/api/testsuites/tablegroups", tags=["Test Suites"])      
def test_suites_table_api(db: Session = Depends(get_db)):
    """
    Lists all the table groups that are profiled along with ID
    """
    return list_table_group_service(db)
                                  
@app.post("/api/testsuites/generation", tags=["Test Suites"])
def create_test_suite_endpoint(data: Test_Generation, db: Session = Depends(get_db)):
    """
    Generates test suite and populates metadata like description and severity.
    """
    return create_test_suites(data, db)

@app.get("/api/testsuites/{test_suite_id}", response_model=TestSuiteMetadata, tags=["Test Suites"])
def read_test_suite_endpoint(test_suite_id: str, db: Session = Depends(get_db)):
    """
    Fetch a specific test suite and its metadata.
    """
    return read_test_suite(test_suite_id, db)

@app.get("/api/testsuites", response_model=List[TestSuiteResponse], tags=["Test Suites"])
def list_test_suites_endpoint(db: Session = Depends(get_db)):
    """
    List all test suites with metadata.
    """
    return list_test_suites(db)

@app.put("/api/testsuites/{test_suite_id}", tags=["Test Suites"])
def update_test_suite_endpoint(test_suite_id: str,update_data: TestSuiteMetadata, db: Session = Depends(get_db)):
    """
    Update test suite metadata (partial or full).
    """
    return update_test_suite(test_suite_id, update_data, db)


@app.delete("/api/testsuites/{test_suite_id}", tags=["Test Suites"])
def delete_test_suite_endpoint(test_suite_id: str, db: Session = Depends(get_db)):
    """
    Permanently delete a test suite by its ID.
    """
    return delete_test_suite(test_suite_id, db)


@app.get("/api/testsuites/{test_suite_id}/results", response_model=TestResultsWithConnection,tags=["Test Suites"])
def get_test_suite_results_endpoint(test_suite_id: str, db: Session = Depends(get_db)):
    """
    Fetch the results of a specific test suite.
    """
    return display_test_results(test_suite_id, db)



# def run_execution_steps(project_code: str, test_suite: str, minutes_offset: int=0, spinner: Spinner=None) -> str:
@app.post("/api/testsuite/execution", tags=["Test Suites"])
def execution_test_suite(request_data: Test_Execution):
    return run_test_suites(request_data.strProjectCode, request_data.strTestSuite, minutes_offset=0)


# @app.get("/api/testsuite/execution/status/{execution_id}", tags=["Test Suites"])

# ------------ Anamoly endpoints ------------
@app.get("/api/connections/table-groups/{table_group_id}/anomaly-results",response_model=Dict,tags=["Anomaly Results"])
def get_anomaly_results_for_table_group(table_group_id: UUID,group_by_table: bool = Query(True),group_by_run: bool = Query(False),db: Session = Depends(get_db)):
    return get_anomaly_results(table_group_id, group_by_table, group_by_run, db)



#------------------- Test Dashboard Endpoints -------------------
# @app.get("/api/v1/data-quality/overview",response_model=OverallDataQualityOverviewResponse,tags=["New Test Dashboard"])
# async def get_overall_data_quality_overview(duration: str = Query("Last 30 days", description="Filter data by duration (e.g., 'Last 30 days', 'Last 7 days', 'Today')"),db: Session = Depends(get_db)):
#     """
#     Retrieves an overview of data quality metrics including overall score,
#     test failures, records tested, and test status.
#     """
#     return get_overall_data_quality_overview_service(duration, db)


@app.get("/api/v1/data-quality/overview",response_model=OverallDataQualityOverviewResponse,responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},tags=["New Test Dashboard"])
async def get_overall_data_quality_overview(
    duration: str = Query("Last 30 days", description="Filter data by duration (e.g., 'Last 30 days', 'Last 7 days', 'Today')"),
    db: Session = Depends(get_db)
):
    """
    Retrieves an overview of data quality metrics including overall score,
    test failures, records tested, and test status.
    """
    return get_overall_data_quality_overview_service(duration, db)


@app.get("/api/v1/test-runs/recent",response_model=RecentTestRunsTableResponse,responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},tags=["New Test Dashboard"])
async def get_recent_test_runs(
    limit: int = Query(5, description="Number of recent test runs to fetch"),
    db: Session = Depends(get_db)
):
    """
    Retrieves a list of recent test runs, suitable for both summarized lists
    and detailed tables.
    """
    return get_recent_test_runs_service(limit, db)


#---------------------------------




@app.get("/api/v1/data-quality/trend",response_model=DataQualityTrendResponse,responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},tags=["New Test Dashboard"])
async def get_data_quality_trend(
    duration: str = Query("Last 30 days", description="Defines the X-axis range (e.g., 'Last 30 days', 'Last 7 days', 'Today')"),
    metric: str = Query("dq_score", description="Metric for the trend chart (e.g., 'dq_score', 'test_failures_count')"),
    db: Session = Depends(get_db)
):
    """
    Retrieves data quality trend data for charting.
    """
    return get_data_quality_trend_service(duration, metric, db)



@app.get("/api/v1/data-sources",response_model=List[DataSource],tags=["New Test Dashboard"])
async def get_data_sources(db: Session = Depends(get_db)):
    """
    Retrieves a list of data sources with aggregated data quality scores.
    """
    return get_data_sources_service(db)

########################################################################################################################################################################
#--------------------------The profile dashboard endpoints

@app.get("/api/v1/overview_metrics", response_model=OverviewMetricsResponse, tags=["New Profile Dashboard"])
async def get_overview_metrics(
    db: Session = Depends(get_db),
    database_connection_id: Optional[int] = Query(None, description="Filter by database connection ID"),
    schema_table_group_uuid: Optional[uuid.UUID] = Query(None, description="Filter by table group (schema) UUID")
):
    """
    Retrieves aggregated key metrics for the data profiling dashboard overview.
    """
    return get_overview_metrics_service(db, database_connection_id, schema_table_group_uuid)
   


@app.get("/api/v1/profile_run_trend", response_model=ProfileRunTrendResponse, tags=["New Profile Dashboard"])
async def get_profile_run_trend(
    db: Session = Depends(get_db),
    database_connection_id: Optional[int] = Query(None, description="Filter by database connection ID"),
    schema_table_group_uuid: Optional[uuid.UUID] = Query(None, description="Filter by table group (schema) UUID"),
    start_date: Optional[datetime] = Query(None, description="Start date for trend (YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="End date for trend (YYYY-MM-DD)"),
    interval: str = Query("day", description="Aggregation interval: 'day', 'week', 'month'"),
    metric: str = Query("total_runs", description="Metric for trend: 'total_runs', 'successful_runs', 'avg_dq_score'")
):
    """
    Provides historical data for the 'Profile Run Trend' chart.
    """
    return get_profile_run_trend_service(
            db, database_connection_id, schema_table_group_uuid, start_date, end_date, interval, metric
        )
    

@app.get("/api/v1/recent_profile_runs", response_model=RecentProfileRunsResponse, tags=["New Profile Dashboard"])
async def get_recent_profile_runs(
    db: Session = Depends(get_db),
    database_connection_id: Optional[int] = Query(None, description="Filter by database connection ID"),
    schema_table_group_uuid: Optional[uuid.UUID] = Query(None, description="Filter by table group (schema) UUID"),
    limit: int = Query(10, ge=1, le=100, description="Number of runs to return"),
    offset: int = Query(0, ge=0, description="Number of runs to skip"),
    sort_by: str = Query("profiling_starttime", description="Column to sort by"),
    sort_order: str = Query("desc", description="Sort order: 'asc' or 'desc'")
):
    """
    Retrieves a paginated list of recent profiling runs.
    """
    return get_recent_profile_runs_service(
            db, database_connection_id, schema_table_group_uuid, limit, offset, sort_by, sort_order
        )
    
    
@app.get("/api/v1/column_stats_distribution", response_model=ColumnStatsDistributionResponse, tags=["New Profile Dashboard"])
async def get_column_stats_distribution(
    db: Session = Depends(get_db),
    metric_type: ColumnMetricType = Query(..., description="Type of distribution metric"),
    database_connection_id: Optional[int] = Query(None, description="Filter by database connection ID"),
    schema_table_group_uuid: Optional[uuid.UUID] = Query(None, description="Filter by table group (schema) UUID"),
    bucket_size: float = Query(10.0, ge=0.1, le=100.0, description="Size of the percentage buckets (e.g., 10 for 10%)")
):
    """
    Provides data for column statistics distribution charts.
    """
    return get_column_stats_distribution_service(
            db, metric_type, database_connection_id, schema_table_group_uuid, bucket_size
        )
    
    
@app.get("/api/v1/dropdown_options", response_model=List[DropdownOption], tags=["New Profile Dashboard"])
async def get_dropdown_options(
    db: Session = Depends(get_db),
    type: str = Query(..., description="Type of options: 'database' or 'table_group'"),
    database_connection_id: Optional[int] = Query(None, description="Filter schemas by database connection ID")
):
    """
    Retrieves options for the Database and Schema dropdowns.
    """
    return get_dropdown_options_service(db, type, database_connection_id)
    
    
@app.get("/api/v1/column_distinct_counts", response_model=ColumnDistinctCountsResponse, tags=["New Profile Dashboard"])
async def get_column_distinct_counts(
    db: Session = Depends(get_db),
    database_connection_id: Optional[int] = Query(None, description="Filter by database connection ID"),
    schema_table_group_uuid: Optional[uuid.UUID] = Query(None, description="Filter by table group (schema) UUID"),
    table_name: Optional[str] = Query(None, description="Filter by specific table name"),
    column_name: Optional[str] = Query(None, description="Filter by specific column name")
):
    """
    Retrieves distinct value counts for columns based on the 'distinct_value_ct' field.
    """
    return get_column_distinct_counts_service(
            db, database_connection_id, schema_table_group_uuid, table_name, column_name
        )
    
@app.get("/test_runs/status_summary", response_model=Dict[str, int], summary="Get Test Run Status Summary for Main Pie Chart", tags=["Test Summary"])
async def get_test_run_status_summary(db: Session = Depends(get_db)):
    """
    Returns the aggregated `result_status` (e.g., "Passed", "Failed", "Warning")
    and their counts from the `test_results` table to populate the main pie chart.
    """
    return get_test_run_status_summary_service(db)
    
    
@app.get("/test_results/test_type_summary", response_model=Dict[str, int], summary="Get Test Type Summary by Result Status for Second Pie Chart", tags=["Test Summary"])
async def get_test_type_summary_by_status(
    result_status: str = Query(..., description="Result Status to filter test types (e.g., 'Passed', 'Failed', 'Warning')"),
    db: Session = Depends(get_db)
):
    """
    Returns the aggregated `test_type` and their counts from the `test_results` table,
    filtered by a specific `result_status`. This will populate the second pie chart.
    """
    return get_test_type_summary_by_status_service(result_status, db)    


@app.get("/test_results/detailed", response_model=List[TestResultDetail], summary="Get Detailed Test Results", tags=["Test Summary"])
async def get_detailed_test_results(
    result_status: str = Query(..., description="Result Status to filter detailed results (e.g., 'Passed', 'Failed', 'Warning')"),
    test_type: str = Query(..., description="Test Type to filter detailed results (e.g., 'Missing_Pct', 'Avg_Shift')"),
    db: Session = Depends(get_db)
):
    """
    Returns detailed `test_results` data, filtered by `result_status` and `test_type`.
    This will populate the table underneath.
    """
    return get_detailed_test_results_service(result_status, test_type, db)
    
    
@app.get("/test_runs_summary_by_suite",response_model=TestSuiteSummary,summary="Get Test Run Counts by Test Suite", tags=["Test Summary"])
async def get_test_runs_summary_by_suite(db: Session = Depends(get_db)):
    """
    Returns aggregated counts of passed, failed, warning, and error tests
    for each distinct test suite, along with their percentages.
    """
    try:
        return get_test_runs_summary_by_suite_service(db)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@app.get("/test_runs_summary_by_suite",response_model=TestSuiteSummary,summary="Get Test Run Counts by Test Suite", tags=["Test Summary"])
async def get_test_runs_summary_by_suite(db: Session = Depends(get_db)):
    """
    Returns aggregated counts of passed, failed, warning, and error tests
    for each distinct test suite, along with their percentages.
    """
    return get_test_runs_summary_by_suite_service(db)



#------------------------------------- Test Case CRUD ---------------------------------------------------------------


# --- Test Definition Endpoints ---


@app.get(
    "/test-suites/{test_suite_id}/test-definitions",
    response_model=TestSuiteDetailResponse, # <--- Changed this line
    summary="Get All Test Definitions for a Test Suite"
)
async def get_all_test_definitions_for_suite(
    test_suite_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieves all test definitions associated with a given test suite ID.
    """
    try:
        test_suite = db.query(TestSuiteModel).filter(TestSuiteModel.id == test_suite_id).first()
        if not test_suite:
            raise HTTPException(status_code=404, detail="Test suite not found")
        
        test_definitions = db.query(TestDefinitionModel).filter(
            TestDefinitionModel.test_suite_id == test_suite_id
        ).all()
        
        
        return TestSuiteDetailResponse(
            test_suite=TestSuiteResponse.from_orm(test_suite),
            test_definitions=[TestDefinition.from_orm(td) for td in test_definitions]
        )

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    

@app.get(
    "/test-definitions/{test_definition_id}",
    response_model=TestDefinition, # Using the enhanced TestDefinition model
    summary="Get a Single Test Definition (for Editing Form)"
)
async def get_test_definition_by_id(
    test_definition_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieves a single test definition by its ID for editing purposes.
    The response includes all relevant test definition data and associated
    Test Type metadata to dynamically render the edit form.
    """
    try:
        # Join TestDefinition with TestType to fetch all necessary data
        result = db.query(TestDefinitionModel, TestTypeModel).join(
            TestTypeModel, TestDefinitionModel.test_type == TestTypeModel.test_type
        ).filter(
            TestDefinitionModel.id == test_definition_id
        ).first()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test Definition not found"
            )

        td, tt = result # Unpack the tuple of model instances

        # Create a dictionary from the TestDefinitionModel instance
        test_def_dict = td.__dict__.copy()

        # Add the relevant TestTypeModel attributes to the dictionary
        test_def_dict['test_type_long_name'] = tt.test_name_long
        test_def_dict['test_type_description_full'] = tt.test_description
        test_def_dict['usage_notes'] = tt.usage_notes
        test_def_dict['test_scope'] = tt.test_scope
        test_def_dict['column_name_prompt'] = tt.column_name_prompt
        test_def_dict['column_name_help'] = tt.column_name_help
        test_def_dict['default_parm_columns'] = tt.default_parm_columns
        test_def_dict['default_parm_prompts'] = tt.default_parm_prompts
        test_def_dict['default_parm_help'] = tt.default_parm_help

        # Convert UUID fields to str for Pydantic to pick them up correctly if not handled by from_orm
        # Pydantic's from_orm should handle UUIDs, but explicit conversion can sometimes prevent issues
        if 'id' in test_def_dict: test_def_dict['id'] = str(test_def_dict['id'])
        if 'test_suite_id' in test_def_dict: test_def_dict['test_suite_id'] = str(test_def_dict['test_suite_id'])
        if 'table_groups_id' in test_def_dict and test_def_dict['table_groups_id'] is not None: test_def_dict['table_groups_id'] = str(test_def_dict['table_groups_id'])
        if 'profile_run_id' in test_def_dict and test_def_dict['profile_run_id'] is not None: test_def_dict['profile_run_id'] = str(test_def_dict['profile_run_id'])
        if 'last_run_id' in test_def_dict and test_def_dict['last_run_id'] is not None: test_def_dict['last_run_id'] = str(test_def_dict['last_run_id'])
        
        # Pydantic's from_orm will handle dates, but if you're constructing from dict, ensure isoformat
        if 'create_ts' in test_def_dict and test_def_dict['create_ts'] is not None: test_def_dict['create_ts'] = test_def_dict['create_ts'].isoformat()
        if 'run_ts' in test_def_dict and test_def_dict['run_ts'] is not None: test_def_dict['run_ts'] = test_def_dict['run_ts'].isoformat()
        if 'end_ts' in test_def_dict and test_def_dict['end_ts'] is not None: test_def_dict['end_ts'] = test_def_dict['end_ts'].isoformat()
        if 'last_manual_update' in test_def_dict and test_def_dict['last_manual_update'] is not None: test_def_dict['last_manual_update'] = test_def_dict['last_manual_update'].isoformat()


        # Return the TestDefinition instance populated with combined data
        return TestDefinition(**test_def_dict)

    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")
    
@app.patch(
"/test-definitions/{test_definition_id}",
response_model=TestDefinition,
summary="Update a Test Definition"
)
async def update_test_definition(
    test_definition_id: UUID,
    updates: TestDefinitionUpdate,
    db: Session = Depends(get_db)
):
    try:
        test_definition = db.query(TestDefinitionModel).filter(
            TestDefinitionModel.id == test_definition_id
        ).first()

        if not test_definition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test Definition not found"
            )

        update_data = updates.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(test_definition, field, value)

        test_definition.last_manual_update = datetime.now()

        db.commit()
        db.refresh(test_definition)

        return TestDefinition.from_orm(test_definition)

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error during update: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@app.get(
    "/test-definitions/{test_definition_id}/details",
    response_model=DetailedTestDefinition,
    summary="Get Detailed Test Definition Info (On Click)"
)
async def get_detailed_test_definition_info(
    test_definition_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieves detailed information for a test definition, combining data from
    `test_definitions` and `test_types` tables.
    """
    try:
        result = db.query(TestDefinitionModel, TestTypeModel).join(
            TestTypeModel, TestDefinitionModel.test_type == TestTypeModel.test_type
        ).filter(
            TestDefinitionModel.id == test_definition_id
        ).first()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test Definition details not found"
            )

        td, tt = result # Unpack the tuple of model instances
        summary_info: Dict[str, Any] = {
            "Schema Name": td.schema_name,
            "Table Name": td.table_name,
            "Column Name": td.column_name,
            "Profile Run ID": td.profile_run_id,
            "Test Type": td.test_type,
            "Severity": td.severity,
            "Threshold Value": td.threshold_value
        }
        detailed_info: Dict[str, Any] = {
            "Test Type(name)": tt.test_name_long,
            "Description": tt.test_description,
            "Measure UOM": tt.measure_uom,
            "Threshold": td.threshold_value, # From test_definitions
            "Default Test Severity": tt.default_severity,
            "Test Run Type": tt.test_scope,
            "Constant Info": [
                "COLUMN tests are consolidated into aggregate queries and execute faster.",
                "TABLE, REFERENTIAL and CUSTOM tests are executed individually and may take longer to run."
            ],
            "Data Quality Dimension": tt.dq_dimension
        }
        return DetailedTestDefinition(summary_info=summary_info, detailed_info=detailed_info)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@app.get(
    "/test-definitions/{test_definition_id}/profile-results",
    response_model=ProfileResultOut,
    summary="Get Profile Results for a Test Definition's Column"
)
async def get_profile_results_for_test_definition(
    test_definition_id: UUID,
    db: Session = Depends(get_db)
):
    try:
        test_definition = db.query(TestDefinitionModel).filter(
            TestDefinitionModel.id == test_definition_id
        ).first()

        if not test_definition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test Definition not found"
            )
        
        profile_result = db.query(ProfileResultModel).filter(
            ProfileResultModel.profile_run_id == test_definition.profile_run_id,
            ProfileResultModel.table_name == test_definition.table_name,
            (ProfileResultModel.column_name == test_definition.column_name) if test_definition.column_name else True
        ).first()

        if not profile_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile results not found for this test definition."
            )
        
        return ProfileResultOut.from_orm(profile_result)

    except HTTPException as e:
        raise e
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")

@app.get("/get-tables-in-table-group", summary='Get list of tables in the table group')
async def get_tables_in_table_group(table_groups_id: str, db: Session = Depends(get_db)) -> list:
    schema = 'tgapp'
    sql = f"""
    SELECT profiling_table_set
    FROM {schema}.table_groups
    WHERE id = '{table_groups_id}'   
    """
    result = db.execute(text(sql))
    table_names = result.fetchone().profiling_table_set
    table_names_list = [name.strip() for name in table_names.split(',')]
    return table_names_list
    
    
@app.get("/get-column-names", summary="Get Column Names for a Table")
async def get_column_names(table_groups_id: str, table_name: str, db: Session = Depends(get_db)) -> list:
    schema = 'tgapp'
    sql = f"""
    SELECT column_name
    FROM {schema}.data_column_chars
    WHERE table_groups_id = '{table_groups_id}'
        AND table_name = '{table_name}'
        AND drop_date IS NULL
    ORDER BY column_name
    """
    result = db.execute(text(sql))

    # Fetch all results and then extract column_name
    column_names = [row.column_name for row in result.all()]

    return column_names
    
    
    
@app.post(
    "/test-definitions",
    response_model=TestDefinition,
    status_code=status.HTTP_201_CREATED,
    summary="Create a New Test Definition"
)
async def create_test_definition(
    test_definition_data: TestDefinitionCreate,
    db: Session = Depends(get_db)
):
    """
    Creates a new test definition, handling inherited properties and uniqueness validation.
    """
    try:
        # 1. Fetch related entities to get inherited values and derived data
        test_suite = db.query(TestSuiteModel).filter(
            TestSuiteModel.id == test_definition_data.test_suite_id
        ).first()
        if not test_suite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test Suite not found."
            )

        table_group = db.query(TableGroupModel).filter(
            TableGroupModel.id == test_suite.table_groups_id
        ).first()
        if not table_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Table Group associated with Test Suite not found."
            )

        test_type_details = db.query(TestTypeModel).filter(
            TestTypeModel.test_type == test_definition_data.test_type
        ).first()
        if not test_type_details:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid test_type: {test_definition_data.test_type}"
            )

        # 2. Populate derived/default values for the database model
        new_test_definition_dict = test_definition_data.dict(exclude_unset=True)

        # Derived from related objects
        new_test_definition_dict["table_groups_id"] = test_suite.table_groups_id
        # new_test_definition_dict["project_code"] = table_group.project_code
        new_test_definition_dict["schema_name"] = table_group.db_schema # As per UI code
        new_test_definition_dict["profile_run_id"] = table_group.last_complete_profile_run_id

        # Handle boolean to 'Y'/'N' conversion
        new_test_definition_dict["test_active"] = 'Y' if new_test_definition_dict.get("test_active", True) else 'N'
        new_test_definition_dict["lock_refresh"] = 'Y' if new_test_definition_dict.get("lock_refresh", False) else 'N'

        
        if test_definition_data.custom_query is not None:
            new_test_definition_dict["custom_query"] = test_definition_data.custom_query
        # Inherited values if not explicitly provided
        if test_definition_data.severity is None:
            new_test_definition_dict["severity"] = test_suite.severity if test_suite.severity else test_type_details.default_severity
        # Convert "Yes"/"No" to "Y"/"N" and apply inheritance
        if test_definition_data.export_to_observability is None or test_definition_data.export_to_observability == "Inherited":
            new_test_definition_dict["export_to_observability"] = test_suite.export_to_observability
        else:
            new_test_definition_dict["export_to_observability"] = 'Y' if test_definition_data.export_to_observability == "Yes" else 'N'

        # Default for check_result and test_definition_status (backend managed)
        new_test_definition_dict["test_definition_status"] = "OK" # Or initial status
        new_test_definition_dict["check_result"] = None # No check result on creation

        # Set creation timestamp
        new_test_definition_dict["last_manual_update"] = datetime.now()

        # 3. Handle conditional 'column_name' requirement based on test_scope
        test_scope = test_type_details.test_scope
        if test_scope in ["column", "referential", "custom"] and not test_definition_data.column_name:
            # Replicate your UI's validation logic for required column_name
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"For test_scope '{test_scope}', 'column_name' is a required field."
            )
        elif test_scope == "table":
            # As per UI, column_name should be None for 'table' scope
            new_test_definition_dict["column_name"] = None

        # --- New: Validate presence of mandatory dynamic parameters based on test_type_details ---
        required_dynamic_fields = [
            col.strip() for col in test_type_details.default_parm_columns.split(',')
        ] if test_type_details.default_parm_columns else []

        for field_name in required_dynamic_fields:
            # We assume if a field is listed in default_parm_columns, it's generally required.
            # If some fields can be optional even if listed there, you'd need more granular logic
            # (e.g., another column in test_types to indicate optionality).
            if getattr(test_definition_data, field_name, None) is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required parameter '{field_name}' for test type '{test_definition_data.test_type}'. Please provide all necessary fields."
                )
        # --- End of New Validation ---

        # 4. Perform uniqueness validation
        # The logic from `validate_test_definition_uniqueness` needs to be in a service function
        # or directly here using SQLAlchemy.

        # Temporarily create a dict for uniqueness check to match `test_definition` structure in UI's `validate_test_definition_uniqueness`
        uniqueness_check_data = {
            "test_suite_id": test_definition_data.test_suite_id,
            "table_name": new_test_definition_dict["table_name"],
            "column_name": new_test_definition_dict["column_name"],
            "test_type": test_definition_data.test_type
        }
        existing_test_def_count = db.query(TestDefinitionModel).filter(
            TestDefinitionModel.test_suite_id == uniqueness_check_data["test_suite_id"],
            TestDefinitionModel.table_name == uniqueness_check_data["table_name"],
            TestDefinitionModel.test_type == uniqueness_check_data["test_type"],
            # Special handling for column_name which can be NULL
            (TestDefinitionModel.column_name == uniqueness_check_data["column_name"]) if uniqueness_check_data["column_name"] else (TestDefinitionModel.column_name.is_(None))
        ).count()

        if existing_test_def_count > 0:
            message_bit = ""
            match test_scope:
                case "column":
                    message_bit = "and Column Name "
                case "referential":
                    message_bit = "and Column Names "
                case "custom":
                    message_bit = "and Test Focus "
                case "table":
                    message_bit = ""
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, # 409 Conflict for resource already existing
                detail=f"Validation error: the combination of Table Name, Test Type {message_bit}must be unique within a Test Suite."
            )

        # 5. Create the SQLAlchemy model instance
        new_test_definition = TestDefinitionModel(**new_test_definition_dict)

        # 6. Add to DB, commit, and refresh
        db.add(new_test_definition)
        db.commit()
        db.refresh(new_test_definition)

        return TestDefinition.from_orm(new_test_definition)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error during creation: {e}")
    except HTTPException:
        # Re-raise HTTPExceptions directly to maintain specific error codes
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")


@app.delete(
    "/test-definitions/{test_definition_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Test Definition"
)
async def delete_test_definition(
    test_definition_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Deletes an existing test definition.
    """
    try:
        test_definition = db.query(TestDefinitionModel).filter(
            TestDefinitionModel.id == test_definition_id
        ).first()

        if not test_definition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test Definition not found"
            )

        db.delete(test_definition)
        db.commit()
        return # FastAPI automatically handles 204 No Content for empty return
    except SQLAlchemyError as e:
        db.rollback() # Rollback on error
        raise HTTPException(status_code=500, detail=f"Database error during deletion: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@app.get(
    "/test-types",
    response_model=List[TestType],
    summary="Get Available Test Types"
)
async def get_available_test_types(
    db: Session = Depends(get_db),
    # Optional filters for test_scope, matching UI checkboxes
    show_referential: bool = Query(True, alias="scope_referential", description="Include Referential test types"),
    show_table: bool = Query(True, alias="scope_table", description="Include Table test types"),
    show_column: bool = Query(True, alias="scope_column", description="Include Column test types"),
    show_custom: bool = Query(True, alias="scope_custom", description="Include Custom test types")
):
    """
    Retrieves a list of available test types, optionally filtered by their scope (column, table, referential, custom).
    This can be used by the frontend to populate test type dropdowns and retrieve associated details.
    """
    try:
        query = db.query(TestTypeModel)
        scope_filters = []
        if show_referential:
            scope_filters.append(TestTypeModel.test_scope == "referential")
        if show_table:
            scope_filters.append(TestTypeModel.test_scope == "table")
        if show_column:
            scope_filters.append(TestTypeModel.test_scope == "column")
        if show_custom:
            scope_filters.append(TestTypeModel.test_scope == "custom")

        if scope_filters:
            query = query.filter(or_(*scope_filters))

        test_types = query.order_by(TestTypeModel.test_name_short).all()

        return [TestType.from_orm(tt) for tt in test_types]
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

# @app.get(
#     "/test-types/{test_type_id}", # Using test_type as ID, assuming it's unique
#     response_model=TestType,
#     summary="Get Details for a Specific Test Type"
# )
# async def get_test_type_details(
#     test_type_id: str,
#     db: Session = Depends(get_db)
# ):
#     """
#     Retrieves detailed information for a specific test type.
#     """
#     try:
#         test_type = db.query(TestTypeModel).filter(TestTypeModel.id == test_type_id).first()
#         if not test_type:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"Test Type '{test_type_id}' not found"
#             )
#         return TestType.from_orm(test_type)
#     except SQLAlchemyError as e:
#         raise HTTPException(status_code=500, detail=f"Database error: {e}")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    
    
    

@app.get(
    "/test-types/{test_type_id}/form-fields",
    response_model=TestTypeFormDefinition,
    summary="Get Dynamic Form Fields for a Specific Test Type"
)
async def get_test_type_form_fields(
    test_type_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves the dynamic input fields (prompts and help texts) required for a specific test type.
    The frontend should use this to render the appropriate form for test definition creation.
    """
    try:
        test_type_details = db.query(TestTypeModel).filter(
            TestTypeModel.id == test_type_id
        ).first()

        if not test_type_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test Type '{test_type_id}' not found."
            )

        dynamic_parameters: List[DynamicFormField] = []

        # Parse default_parm_columns, default_parm_prompts, and default_parm_help
        # Ensure all are not None before splitting
        columns = test_type_details.default_parm_columns.split(',') if test_type_details.default_parm_columns else []
        prompts = test_type_details.default_parm_prompts.split(',') if test_type_details.default_parm_prompts else []
        help_texts = test_type_details.default_parm_help.split('|') if test_type_details.default_parm_help else []

        # Ensure lists are of equal length or handle discrepancies
        # For simplicity, we'll iterate based on 'columns' and fallback if prompts/help are missing
        for i, col_name in enumerate(columns):
            col_name = col_name.strip() # Clean up any whitespace
            param_prompt = prompts[i].strip() if i < len(prompts) else col_name # Use column name if prompt missing
            param_help = help_texts[i].strip() if i < len(help_texts) else None

            dynamic_parameters.append(
                DynamicFormField(
                    field_name=col_name,
                    prompt=param_prompt,
                    help_text=param_help
                )
            )

        return TestTypeFormDefinition(
            test_type=test_type_details.test_type,
            test_name_short=test_type_details.test_name_short,
            test_description=test_type_details.test_description,
            usage_notes=test_type_details.usage_notes,
            test_scope=test_type_details.test_scope,
            column_name_prompt=test_type_details.column_name_prompt,
            column_name_help=test_type_details.column_name_help,
            severity = test_type_details.default_severity,
            dynamic_parameters=dynamic_parameters
        )

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
