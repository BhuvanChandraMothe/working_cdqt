from typing import List, Dict, Any, Optional, Union
import collections
from uuid import uuid4, UUID
import base64
from sqlalchemy import create_engine, desc, func, distinct, case, exists, and_
from sqlalchemy import create_engine, text, func, cast, Date, distinct, case
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import uuid
import json
from fastapi import Depends
from sqlalchemy.orm import sessionmaker, Session 
from fastapi import HTTPException
from Backend.models.models import (
    DBConnectionCreate,
    DBConnectionUpdate,
    TestConnectionRequest,
    TestConnectionResponse,
    TableGroupCreate, 
    TableGroupUpdate,
    DBConnectionOut, 
    TableGroupOut, 
    ProfileResultOut,
    ProfilingRunOut,
    LatestProfilingRunDashboardData,
    ScheduleProfilingRequest,
    ScheduledProfilingJobResponse,
    ScheduleProfilingUpdate,
    LatestRunSummary,
    LatestProfilingRunDashboardData,
    DashboardData,
    TableDetailsData,
    TableNameItem,
    RecentRunEntry,
    DataDistributionEntry,
    ColumnDataType,
    TableDQScoreHistory,
    ConnectionActionRequest,
    TestSuiteResponse,
    Test_Generation,
    TestSuiteMetadata,
    AnomalyGroupedByRun,
    AnomalyGroupedByTable,
    AnomalyUngrouped,
    AnomalyResultOut,
    TestResultWithDetails,
    ScheduledProfilingJobResponse,
    
    
    
    OverallDataQualityOverviewResponse,
    DataQualityTrendResponse,
    RecentTestRunSummary,
    RecentTestRunsTableResponse,
    DataSource,
    ErrorResponse,
    RecentTestRunDetail,
    
    OverviewMetricsResponse, RecentProfileRunsResponse, RecentProfileRun,
    ProfileRunTrendResponse, ProfileRunTrendDataPoint, ColumnStatsDistributionResponse,
    DistributionDataPoint, DropdownOption, ColumnDistinctCountDetail, ColumnDistinctCountsResponse, ColumnMetricType,
    
    
    TestResultDetail,
    TestSuiteCounts,
    TestSuiteSummary,
    
    
    
    
    
)
from Backend.helpers.helper import get_latest_successful_run_id, get_time_filter, calculate_success_rate_change, format_duration_display,format_large_number
from Backend.db.database import TableGroupModel, Connection, ProfileResultModel, ProfilingRunModel, ScheduledProfilingJob, TestSuiteModel, TestResultModel, AnomalyResultModel,ProfileAnomalyTypeModel, TestRunModel, TestTypeModel
from testgen.common.encrypt import EncryptText, DecryptText
from testgen.commands.queries.profiling_query import CProfilingSQL
import testgen.commands.run_profiling_bridge as rpb
import testgen.commands.run_generate_tests as rgt
import testgen.commands.run_execute_tests as ret
from apscheduler.schedulers.background import BackgroundScheduler

from apscheduler.triggers.cron import CronTrigger
from testgen.ui.views.connections import ConnectionsPage
import logging

# Logging config
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)
 
# SQLAlchemy setup
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:bhuvan@localhost:5432/postgres"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
 
# Utility functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
 
 
# API logic functions
 
#----------------------------test connection-----------------------------------
 

def is_encrypted(password: str) -> bool:
    try:
        decoded = base64.b64decode(password)
        
        return len(decoded) > 16
    except Exception:
        return False
   

def test_connection_service(conn: ConnectionActionRequest) -> TestConnectionResponse:
    try:
        con = ConnectionsPage()
        password = conn.password
        
        if is_encrypted(password):
            password = DecryptText(password)
 
        
        connection_dict = {
            "sql_flavor": conn.sql_flavor.lower(),
            "project_host": conn.db_hostname,
            "project_port": conn.db_port, # TestConnectionRequest expects int port
            "project_db": conn.project_db,
            "project_user": conn.user_id,
            "password": password,
            "url": None,
            "connect_by_url": False,
            "connect_by_key": False,
            "private_key": None,
            "private_key_passphrase": None,
            "http_path": None,
        }
        status = con.test_connection(connection_dict)
        
        return TestConnectionResponse(
            status=status.successful,
            message=status.message,
            details=status.details,
        )
    except Exception as e:
        LOG.error(f"Connection test failed: {e}")
        
        return TestConnectionResponse(
            status=False,
            message=f"Connection test failed: {str(e)}",
            details=None,
        )
 


def handle_connection_action(conn_data: ConnectionActionRequest, db: Session):
    if conn_data.action == "test":
        return test_connection_service(conn_data)
    elif conn_data.action == "create":
        return create_connection_service(conn_data, db)
    else:
        raise HTTPException(status_code=400, detail="Unsupported action.")
    

def create_connection_service(conn_data: ConnectionActionRequest, db: Session = next(get_db())) -> DBConnectionOut:
    try:
        db_conn = Connection(
            project_code=conn_data.project_code,
            connection_name=conn_data.connection_name,
            connection_description=conn_data.connection_description,
            sql_flavor=conn_data.sql_flavor.lower(),
            project_host=conn_data.db_hostname,
            project_port=conn_data.db_port,
            project_user=conn_data.user_id,
            project_db = conn_data.project_db,
            project_pw_encrypted = EncryptText(conn_data.password).encode('utf-8'),
            max_query_chars= 5000,#conn_data.max_query_chars,
            url=conn_data.url,
            connect_by_url=conn_data.connect_by_url,
            connect_by_key=conn_data.connect_by_key,
            private_key=conn_data.private_key,
            private_key_passphrase=conn_data.private_key_passphrase,
            http_path=conn_data.http_path,
        )
        db.add(db_conn)
        db.commit()
        db.refresh(db_conn)
        
        return DBConnectionOut.from_orm(db_conn)
    except Exception as e:
        db.rollback()
        LOG.error(f"Error creating connection: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating connection: {str(e)}")
 
 


def list_connections_service(db: Session = next(get_db())):
    try:
        connections = db.query(Connection).order_by(desc(Connection.connection_id)).all()
        
        return [DBConnectionOut.from_orm(conn) for conn in connections]
    except Exception as e:
        LOG.error(f"Error listing connections: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing connections: {str(e)}")
 
 
#--------------------get one connection---------------------------------


def get_connection_service(conn_id: int, db: Session = next(get_db())):
    try:
        conn = db.query(Connection).filter(Connection.connection_id == conn_id).first()
        if not conn:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        return DBConnectionOut.from_orm(conn)
    except Exception as e:
        LOG.error(f"Error getting connection {conn_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting connection: {str(e)}")
 
 
 
#----------------------------update a connection---------------------------------
# Uses DBConnectionUpdate Pydantic model for input and updates Connection SQLAlchemy model
def update_connection_service(conn_id: int, conn_data: DBConnectionUpdate, db: Session = next(get_db())):
    try:
        conn = db.query(Connection).filter(Connection.connection_id == conn_id).first()
        if not conn:
            raise HTTPException(status_code=404, detail="Connection not found")
 
        
        update_data = conn_data.dict(exclude_unset=True)
 
        
        for key, value in update_data.items():
            
            if key == "password" and value is not None:
                    setattr(conn, "project_pw_encrypted", EncryptText(value).encode('utf-8'))
            
            elif key == "private_key" and value is not None:
                    setattr(conn, "private_key", value)
            
            elif key == "private_key_passphrase" and value is not None:
                    setattr(conn, "private_key_passphrase", value)
            
            elif hasattr(conn, key):
                    setattr(conn, key, value)
            else:
                    LOG.warning(f"Attempted to update non-existent attribute on Connection model: {key}")
 
 
        db.commit()
        db.refresh(conn)
        
        return DBConnectionOut.from_orm(conn)
    except Exception as e:
        db.rollback()
        LOG.error(f"Error updating connection {conn_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating connection: {str(e)}")
 
 
#-------------------------------delete a connection---------------------------------
# Queries and deletes a Connection SQLAlchemy object by connection_id (BIGINT PK)
def delete_connection_service(conn_id: int, db: Session = next(get_db())):
    try:
        conn = db.query(Connection).filter(Connection.connection_id == conn_id).first()
        if not conn:
            raise HTTPException(status_code=404, detail="Connection not found")
        db.delete(conn)
        db.commit()
        return {"message": "Connection deleted successfully"}
    except Exception as e:
        db.rollback()
        LOG.error(f"Error deleting connection {conn_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting connection: {str(e)}")
 
 
#--------------------create table groups for a connection---------------------------------
def create_table_group_service(conn_id: int, table_group_data: TableGroupCreate, db: Session = next(get_db())):
    try:
        connection = db.query(Connection).filter(Connection.connection_id == conn_id).first()
        if not connection:
            raise HTTPException(status_code=404, detail=f"Connection with id {conn_id} not found")

        project_code = connection.project_code

        # Serialize the list to a comma-separated string for database storage
        serialized_explicit_table_list = None
        if table_group_data.explicit_table_list is not None:
            serialized_explicit_table_list = ",".join(table_group_data.explicit_table_list)
        # If you prefer JSON:
        # if table_group_data.explicit_table_list is not None:
        #     serialized_explicit_table_list = json.dumps(table_group_data.explicit_table_list)


        db_group = TableGroupModel(
            project_code=project_code,
            connection_id=conn_id,
            table_groups_name=table_group_data.table_groups_name,
            db_schema=table_group_data.table_group_schema,
            explicit_table_list=serialized_explicit_table_list, # Use the serialized string here
            tables_to_include_mask=table_group_data.profiling_include_mask,
            profiling_exclude_mask=table_group_data.profiling_exclude_mask,
            profiling_id_column_mask=table_group_data.profile_id_column_mask,
            profiling_surrogate_key_column_mask=table_group_data.profile_sk_column_mask,
            profile_use_sampling=str(table_group_data.profile_use_sampling),
            profile_sample_percent=str(table_group_data.profile_sample_percent),
            profile_sample_min_count=table_group_data.profile_sample_min_count,
            min_profiling_age_days=str(table_group_data.min_profiling_age_days),
            profile_flag_cdes=table_group_data.profile_flag_cdes,
            profile_do_pair_rules=str(table_group_data.profile_do_pair_rules),
            profile_pair_rule_pct=table_group_data.profile_pair_rule_pct,
            description=table_group_data.description,
            data_source=table_group_data.data_source,
            source_system=table_group_data.source_system,
            source_process=table_group_data.source_process,
            data_location=table_group_data.data_location,
            business_domain=table_group_data.business_domain,
            stakeholder_group=table_group_data.stakeholder_group,
            transform_level=table_group_data.transform_level,
            data_product=table_group_data.data_product,
            last_complete_profile_run_id=table_group_data.last_complete_profile_run_id,
            dq_score_profiling=table_group_data.dq_score_profiling,
            dq_score_testing=table_group_data.dq_score_testing,
        )
        db.add(db_group)
        db.commit()
        db.refresh(db_group)

        # Deserialize the string back to a list for the response
        deserialized_explicit_table_list = []
        if db_group.explicit_table_list:
            deserialized_explicit_table_list = [item.strip() for item in db_group.explicit_table_list.split(',')]
            # If you used JSON:
            # deserialized_explicit_table_list = json.loads(db_group.explicit_table_list)


        return TableGroupOut(
            id=db_group.id,
            project_code=db_group.project_code,
            connection_id=db_group.connection_id,
            table_groups_name=db_group.table_groups_name,
            table_group_schema=db_group.db_schema,
            explicit_table_list=deserialized_explicit_table_list, # Return as a list
            profiling_include_mask=db_group.tables_to_include_mask,
            profiling_exclude_mask=db_group.profiling_exclude_mask,
            profile_id_column_mask=db_group.profiling_id_column_mask,
            profiling_surrogate_key_column_mask=db_group.profiling_surrogate_key_column_mask,
            profile_use_sampling=db_group.profile_use_sampling,
            profile_sample_percent=db_group.profile_sample_percent,
            profile_sample_min_count=db_group.profile_sample_min_count,
            min_profiling_age_days=int(db_group.min_profiling_age_days) if db_group.min_profiling_age_days else 0,
            profile_flag_cdes=db_group.profile_flag_cdes,
            profile_do_pair_rules=db_group.profile_do_pair_rules,
            profile_pair_rule_pct=db_group.profile_pair_rule_pct,
            description=db_group.description,
            data_source=db_group.data_source,
            source_system=db_group.source_system,
            source_process=db_group.source_process,
            data_location=db_group.data_location,
            business_domain=db_group.business_domain,
            stakeholder_group=db_group.stakeholder_group,
            transform_level=db_group.transform_level,
            data_product=db_group.data_product,
            last_complete_profile_run_id=db_group.last_complete_profile_run_id,
            dq_score_profiling=db_group.dq_score_profiling,
            dq_score_testing=db_group.dq_score_testing,
        )
    except Exception as e:
        db.rollback()
        LOG.error(f"Error creating table group for connection {conn_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating table group: {str(e)}")
 
 
#--------------------get all table groups for a connection---------------------------------
# Queries the TableGroupModel SQLAlchemy model by connection_id and returns a list of TableGroupOut
def get_table_groups_service(conn_id: int, db: Session = next(get_db())):
    try:
        groups = db.query(TableGroupModel).filter(TableGroupModel.connection_id == conn_id).all()

        result_groups = []
        for group in groups:
            # Deserialize the string back to a list
            deserialized_explicit_table_list = []
            if group.explicit_table_list:
                deserialized_explicit_table_list = [item.strip() for item in group.explicit_table_list.split(',')]
                # If you used JSON:
                # deserialized_explicit_table_list = json.loads(group.explicit_table_list)

            result_groups.append(
                TableGroupOut(
                    id=group.id,
                    project_code=group.project_code,
                    connection_id=group.connection_id,
                    table_groups_name=group.table_groups_name,
                    table_group_schema=group.db_schema,
                    explicit_table_list=deserialized_explicit_table_list, # Return as a list
                    profiling_include_mask=group.tables_to_include_mask,
                    profiling_exclude_mask=group.profiling_exclude_mask,
                    profile_id_column_mask=group.profiling_id_column_mask,
                    profiling_surrogate_key_column_mask=group.profiling_surrogate_key_column_mask,
                    profile_use_sampling=group.profile_use_sampling,
                    profile_sample_percent=group.profile_sample_percent,
                    profile_sample_min_count=group.profile_sample_min_count,
                    min_profiling_age_days=int(group.min_profiling_age_days) if group.min_profiling_age_days else 0,
                    profile_flag_cdes=group.profile_flag_cdes,
                    profile_do_pair_rules=group.profile_do_pair_rules,
                    profile_pair_rule_pct=group.profile_pair_rule_pct,
                    description=group.description,
                    data_source=group.data_source,
                    source_system=group.source_system,
                    source_process=group.source_process,
                    data_location=group.data_location,
                    business_domain=group.business_domain,
                    stakeholder_group=group.stakeholder_group,
                    transform_level=group.transform_level,
                    data_product=group.data_product,
                    last_complete_profile_run_id=group.last_complete_profile_run_id,
                    dq_score_profiling=group.dq_score_profiling,
                    dq_score_testing=group.dq_score_testing,
                )
            )
        return result_groups
    except Exception as e:
        LOG.error(f"Error getting table groups for connection {conn_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting table groups: {str(e)}")
 
 
#--------------------get specific table group---------------------------------
def get_specific_table_group_service(conn_id: int, group_id: str, db: Session = next(get_db())):
    try:
        group = db.query(TableGroupModel).filter(TableGroupModel.connection_id == conn_id, TableGroupModel.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Table group not found")

        # Deserialize the string back to a list
        deserialized_explicit_table_list = []
        if group.explicit_table_list:
            deserialized_explicit_table_list = [item.strip() for item in group.explicit_table_list.split(',')]
            # If you used JSON:
            # deserialized_explicit_table_list = json.loads(group.explicit_table_list)

        return TableGroupOut(
            id=group.id,
            project_code=group.project_code,
            connection_id=group.connection_id,
            table_groups_name=group.table_groups_name,
            table_group_schema=group.db_schema,
            explicit_table_list=deserialized_explicit_table_list, # Return as a list
            profiling_include_mask=group.tables_to_include_mask,
            profiling_exclude_mask=group.profiling_exclude_mask,
            profile_id_column_mask=group.profiling_id_column_mask,
            profiling_surrogate_key_column_mask=group.profiling_surrogate_key_column_mask,
            profile_use_sampling=group.profile_use_sampling,
            profile_sample_percent=group.profile_sample_percent,
            profile_sample_min_count=group.profile_sample_min_count,
            min_profiling_age_days=int(group.min_profiling_age_days) if group.min_profiling_age_days else 0,
            profile_flag_cdes=group.profile_flag_cdes,
            profile_do_pair_rules=group.profile_do_pair_rules,
            profile_pair_rule_pct=group.profile_pair_rule_pct,
            description=group.description,
            data_source=group.data_source,
            source_system=group.source_system,
            source_process=group.source_process,
            data_location=group.data_location,
            business_domain=group.business_domain,
            stakeholder_group=group.stakeholder_group,
            transform_level=group.transform_level,
            data_product=group.data_product,
            last_complete_profile_run_id=group.last_complete_profile_run_id,
            dq_score_profiling=group.dq_score_profiling,
            dq_score_testing=group.dq_score_testing,
        )
    except Exception as e:
        LOG.error(f"Error getting table group {group_id} for connection {conn_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting table group: {str(e)}")
 

#--------------------update table groups for a connection---------------------------------
# In your service file (e.g., backend_services.py)

def update_table_group_service(conn_id: int, group_id: str, table_group_data: TableGroupUpdate, db: Session = next(get_db())):
    """
    Updates an existing table group for a given connection.
    Supports partial updates via the TableGroupUpdate Pydantic model.
    """
    try:
        db_group = db.query(TableGroupModel).filter(
            TableGroupModel.connection_id == conn_id,
            TableGroupModel.id == group_id
        ).first()

        if not db_group:
            raise HTTPException(status_code=404, detail="Table group not found")

        update_data = table_group_data.dict(exclude_unset=True)

        for field, value in update_data.items():
            # Special handling for explicit_table_list (list to comma-separated string)
            if field == "explicit_table_list":
                setattr(db_group, field, ",".join(value) if value is not None else None)
            # Special handling for table_group_schema (maps to db_schema in DB model)
            elif field == "table_group_schema":
                db_group.db_schema = value
            # Special handling for profiling_include_mask (maps to tables_to_include_mask)
            elif field == "profiling_include_mask":
                db_group.tables_to_include_mask = value
            # Handle boolean fields (profile_use_sampling, profile_do_pair_rules) to 'Y'/'N' string
            elif field in ["profile_use_sampling", "profile_do_pair_rules"]:
                if value is True:
                    setattr(db_group, field, 'Y')
                elif value is False:
                    setattr(db_group, field, 'N')
                elif value is None: # Allow setting to None if Optional
                    setattr(db_group, field, None)
            # profile_flag_cdes is assumed to be a native boolean in DB, assign directly
            elif field == "profile_flag_cdes":
                setattr(db_group, field, value)

            # Handle numeric fields (profile_sample_percent, profile_pair_rule_pct, profile_sample_min_count, min_profiling_age_days)
            # Pay close attention to whether the DB expects int or float, or string representation
            elif field == "profile_sample_percent":
                # Assuming DB column for profile_sample_percent is a STRING ('30')
                setattr(db_group, field, str(value) if value is not None else None)
            elif field == "profile_pair_rule_pct":
                # PROBLEM IS HERE: DB wants INTEGER, Pydantic gives FLOAT, you stringify FLOAT ("95.0")
                # So, if DB wants INTEGER, convert to int.
                setattr(db_group, field, int(value) if value is not None else None) # Cast to int for DB
            elif field in ["profile_sample_min_count", "min_profiling_age_days"]:
                # These are already int in Pydantic and should be int in DB
                setattr(db_group, field, value)
            # Fields that are expected as int/float/UUID in Pydantic and directly map to DB
            elif field in ["dq_score_profiling", "dq_score_testing", "last_complete_profile_run_id"]:
                 setattr(db_group, field, value)
            # Default handling for all other string fields
            else:
                setattr(db_group, field, value)


        db.commit()
        db.refresh(db_group)

        # Prepare the response object (TableGroupOut) with correct data types
        # This section should remain consistent with what TableGroupOut expects.
        deserialized_explicit_table_list = []
        if db_group.explicit_table_list:
            deserialized_explicit_table_list = [item.strip() for item in db_group.explicit_table_list.split(',')]

        return TableGroupOut(
            id=db_group.id,
            project_code=db_group.project_code,
            connection_id=db_group.connection_id,
            table_groups_name=db_group.table_groups_name,
            table_group_schema=db_group.db_schema,
            explicit_table_list=deserialized_explicit_table_list,
            profiling_include_mask=db_group.tables_to_include_mask,
            profiling_exclude_mask=db_group.profiling_exclude_mask,
            profile_id_column_mask=db_group.profiling_id_column_mask,
            profile_sk_column_mask=db_group.profiling_surrogate_key_column_mask,
            profile_use_sampling=(db_group.profile_use_sampling == 'Y'), # DB 'Y'/'N' to Python bool
            profile_sample_percent=float(db_group.profile_sample_percent) if db_group.profile_sample_percent else 0.0, # DB string to Python float
            profile_sample_min_count=db_group.profile_sample_min_count,
            min_profiling_age_days=db_group.min_profiling_age_days,
            profile_flag_cdes=db_group.profile_flag_cdes, # Already bool from DB
            profile_do_pair_rules=(db_group.profile_do_pair_rules == 'Y'), # DB 'Y'/'N' to Python bool
            profile_pair_rule_pct=float(db_group.profile_pair_rule_pct) if db_group.profile_pair_rule_pct is not None else None, # DB int to Python float (assuming DB is int, Pydantic float)
            description=db_group.description,
            data_source=db_group.data_source,
            source_system=db_group.source_system,
            source_process=db_group.source_process,
            data_location=db_group.data_location,
            business_domain=db_group.business_domain,
            stakeholder_group=db_group.stakeholder_group,
            transform_level=db_group.transform_level,
            data_product=db_group.data_product,
            last_complete_profile_run_id=db_group.last_complete_profile_run_id,
            dq_score_profiling=db_group.dq_score_profiling,
            dq_score_testing=db_group.dq_score_testing,
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        LOG.error(f"Error updating table group {group_id} for connection {conn_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error updating table group: {str(e)}")
#-----------------------delete table group--------------------------------------

def delete_table_group_service(conn_id: int, group_id: str, db: Session = next(get_db())):
    try:
        group = db.query(TableGroupModel).filter(TableGroupModel.connection_id == conn_id, TableGroupModel.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Table group not found")
        db.delete(group)
        db.commit()
        return {"message": "Table group deleted successfully"}
    except Exception as e:
        db.rollback()
        LOG.error(f"Error deleting table group {group_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting table group: {str(e)}")
 
 
#--------------------do background profiling job---------------------------------
# Triggers a background profiling job using the TableGroup UUID (str)
def trigger_profiling_service(conn_id: int, group_id: str):
    try:
        rpb.run_profiling_in_background(group_id)
        return {"status": "started", "message": "Profiling job launched in background"}
    except Exception as e:
        LOG.error(f"Error triggering profiling for group {group_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
 
#---------------------profiling results--------------------------------------------------------------------

def get_profiling_runs_by_table_group(conn_id: int, group_id: int, db: Session):
    """
    Retrieves all profiling runs for a specific table group within a connection.
    """
    try:
        
        table_group = db.query(TableGroupModel).filter(
            TableGroupModel.id == group_id,
            TableGroupModel.connection_id == conn_id
        ).first()

        if not table_group:
            raise HTTPException(status_code=404, detail=f"Table group ID: {group_id} not found for connection ID: {conn_id}.")

        
        results = db.query(ProfilingRunModel).filter(
            ProfilingRunModel.table_groups_id == group_id,
            ProfilingRunModel.connection_id == conn_id 
        ).order_by(ProfilingRunModel.profiling_endtime.desc()).all()

        if not results:
            raise HTTPException(status_code=404, detail=f"No profiling runs found for table group ID: {group_id}.")
        return results
    except HTTPException:
        raise
    except Exception as e:
        LOG.error(f"Error fetching profiling runs for connection {conn_id}, group {group_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching profiling runs.")

def get_profile_results_for_run_detail(conn_id: int, group_id: int, run_id: UUID, db: Session):
    """
    Retrieves all profile results for a specific profiling run, ensuring it belongs
    to the specified table group and connection.
    """
    try:
        
        profiling_run = db.query(ProfilingRunModel).filter(
            ProfilingRunModel.id == run_id,
            ProfilingRunModel.table_groups_id == group_id,
            ProfilingRunModel.connection_id == conn_id
        ).first()

        if not profiling_run:
            raise HTTPException(status_code=404, detail=f"Profiling run ID: {run_id} not found for table group {group_id} and connection {conn_id}.")

        
        results = db.query(ProfileResultModel).filter(
            ProfileResultModel.profile_run_id == run_id
        ).all()

        if not results:
            raise HTTPException(status_code=404, detail=f"No profile results found for profiling run ID: {run_id}.")

        
        return [ProfileResultOut.from_orm(r) for r in results]

    except HTTPException:
        raise
    except Exception as e:
        LOG.error(f"Error fetching profile results for run {run_id} under connection {conn_id}, group {group_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching profile results.")

def get_all_profiling_runs_service(db: Session):
    try:
        connections_count = db.query(Connection).count()
        table_groups_count = db.query(TableGroupModel).count()
        profiling_runs = db.query(ProfilingRunModel).all()
 
        formatted_runs = [
            {
                "connection_id": run.connection_id,
                "profiling_id": run.id,
                "status": run.status,
                "table_groups_id": run.table_groups_id,
                "created_at": run.profiling_starttime,
            }
            for run in profiling_runs
        ]
 
        return {
            "connections": connections_count,
            "table_groups": table_groups_count,
            "profiling_runs": len(profiling_runs),
            "runs": formatted_runs,
        }
 
    except Exception as e:
        print(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard stats")
   
def get_latest_profiling_run_dashboard_data_service(db: Session) -> LatestProfilingRunDashboardData:
    latest_run = (
        db.query(ProfilingRunModel)
        .order_by(desc(ProfilingRunModel.profiling_starttime))
        .first()
    )
 
    if not latest_run:
        raise HTTPException(status_code=404, detail="No profiling run found")
 
    
    results = (
        db.query(ProfileResultModel)
        .filter(ProfileResultModel.profile_run_id == latest_run.id)
        .all()
    )
 
    return LatestProfilingRunDashboardData(
        latest_run=latest_run,
        profile_results=results
    )
   
   
   
#------------------------------------Scheduling profiling jobs---------------------------------------------------------------------
 
scheduler = BackgroundScheduler()
 

def load_existing_scheduled_jobs(db: Session):
    jobs = db.query(ScheduledProfilingJob).filter_by(is_active=True).all()
    for job in jobs:
        scheduler.add_job(
            func=trigger_profiling_service,
            trigger=CronTrigger.from_crontab(job.schedule_cron_expression),
            args=[job.conn_id, job.group_id],
            id=job.scheduled_job_id,
            replace_existing=True,
        )
 
 

def add_job_to_scheduler(job: ScheduledProfilingJob):
    scheduler.add_job(
        func=trigger_profiling_service,
        trigger=CronTrigger.from_crontab(job.schedule_cron_expression),
        args=[job.conn_id, str(job.group_id)],
        id=job.scheduled_job_id,
        replace_existing=True,
    )

def remove_job_from_scheduler(scheduled_job_id: str):
    try:
        scheduler.remove_job(scheduled_job_id)
    except Exception:
        pass  



def get_all_schedules_service(db: Session) -> List[ScheduledProfilingJobResponse]:
    """
    Service function to fetch all active scheduled profiling jobs,
    including the associated table group name and connection name.
    """
    try:
        # Perform a join to get data from all three tables
        results = (
            db.query(ScheduledProfilingJob, TableGroupModel, Connection)
            .join(
                TableGroupModel,
                ScheduledProfilingJob.group_id == TableGroupModel.id
            )
            .join(
                Connection,
                TableGroupModel.connection_id == Connection.connection_id
            )
            .filter(ScheduledProfilingJob.is_active == True)
            .all()
        )

        scheduled_jobs_with_details = []
        for job, table_group, connection in results:
            scheduled_jobs_with_details.append(
                ScheduledProfilingJobResponse(
                    id=job.id,
                    conn_id=job.conn_id,
                    connection_name=connection.connection_name, 
                    group_id=job.group_id,
                    table_group_name=table_group.table_groups_name,
                    schedule_cron_expression=job.schedule_cron_expression,
                    scheduled_job_id=job.scheduled_job_id,
                    is_active=job.is_active,
                )
            )
        return scheduled_jobs_with_details

    except SQLAlchemyError as e:
        print(f"Database error in get_all_schedules_service: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred in get_all_schedules_service: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


def get_schedule_by_id_service(scheduled_job_id: str, db: Session):
    job = db.query(ScheduledProfilingJob).filter_by(scheduled_job_id=scheduled_job_id, is_active=True).first()
    if not job:
        raise HTTPException(status_code=404, detail="Scheduled job not found.")
    return job

def create_schedule_service(request: ScheduleProfilingRequest, db: Session):
    scheduled_job_id = f"profile-{request.conn_id}-{request.group_id}-{hash(request.cron_expression)}"

    if db.query(ScheduledProfilingJob).filter_by(scheduled_job_id=scheduled_job_id).first():
        raise HTTPException(status_code=409, detail="Scheduled job already exists.")

    new_job = ScheduledProfilingJob(
        conn_id=request.conn_id,
        group_id=request.group_id,
        schedule_cron_expression=request.cron_expression,
        scheduled_job_id=scheduled_job_id,
        is_active=True,
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    try:
        add_job_to_scheduler(new_job)
    except Exception as e:
        db.delete(new_job)
        db.commit()
        raise HTTPException(status_code=400, detail=f"Scheduler error: {str(e)}")

    return new_job

def update_schedule_service(scheduled_job_id: str, update: ScheduleProfilingUpdate, db: Session):
    job = db.query(ScheduledProfilingJob).filter_by(scheduled_job_id=scheduled_job_id).first()
    if not job or not job.is_active:
        raise HTTPException(status_code=404, detail="Scheduled job not found or inactive.")

    if update.conn_id is not None:
        job.conn_id = update.conn_id
    if update.group_id is not None:
        job.group_id = update.group_id
    if update.cron_expression is not None:
        job.schedule_cron_expression = update.cron_expression
    if update.is_active is not None:
        job.is_active = update.is_active

    db.commit()
    db.refresh(job)

    remove_job_from_scheduler(scheduled_job_id)

    if job.is_active:
        try:
            add_job_to_scheduler(job)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Scheduler error: {str(e)}")

    return job

def delete_schedule_service(scheduled_job_id: str, db: Session, mode: str = "deactivate"):
    job = db.query(ScheduledProfilingJob).filter_by(scheduled_job_id=scheduled_job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Scheduled job not found.")

    remove_job_from_scheduler(scheduled_job_id)

    if mode == "deactivate":
        job.is_active = False
        db.commit()
        return {"status": "deactivated", "scheduled_job_id": scheduled_job_id}
    elif mode == "delete_permanent":
        db.delete(job)
        db.commit()
        return {"status": "deleted", "scheduled_job_id": scheduled_job_id}
    else:
        raise HTTPException(status_code=400, detail="Invalid delete mode. Use 'deactivate' or 'delete_permanent'.")
    
    
    
def reactivate_schedule_service(scheduled_job_id: str, db: Session) -> Dict[str, str]:
    """
    Reactivates a scheduled profiling job by setting its status to active
    and re-adding it to the in-memory scheduler.
    """
    try:
        job = db.query(ScheduledProfilingJob).filter_by(scheduled_job_id=scheduled_job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail=f"Scheduled job '{scheduled_job_id}' not found.")

        status = "already_active" if job.is_active else "reactivated"

        if not job.is_active:
            job.is_active = True
            db.commit()
            print(f"INFO: Job '{scheduled_job_id}' activated in database.")

        try:
            add_job_to_scheduler(job)
            print(f"INFO: Job '{scheduled_job_id}' added/re-added to scheduler.")
        except Exception as scheduler_error:
            if status == "reactivated":
                db.rollback()
            print(f"ERROR: Scheduler error for job '{scheduled_job_id}': {scheduler_error}")
            raise HTTPException(
                status_code=500,
                detail=f"Job reactivated in DB but failed to re-add to scheduler: {scheduler_error}"
            )

        return {"status": status, "scheduled_job_id": scheduled_job_id}

    except HTTPException:
        raise
    except SQLAlchemyError as db_error:
        db.rollback()
        print(f"ERROR: Database error for job '{scheduled_job_id}': {db_error}")
        raise HTTPException(status_code=500, detail=f"Database error: {db_error}")
    except Exception as e:
        print(f"ERROR: Unexpected error during job reactivation '{scheduled_job_id}': {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

# --- Service for Dashboard Overview and Recent Runs ---
def get_dashboard_overview_data_service(db: Session) -> DashboardData:
    try:
        total_tables_query = db.query(distinct(ProfileResultModel.table_name)).count()
        total_columns_query = db.query(distinct(ProfileResultModel.column_name)).count()

        max_record_ct_per_table = (
            db.query(func.max(ProfileResultModel.record_ct).label('max_rows'))
            .group_by(ProfileResultModel.table_name)
            .subquery()
        )
        total_row_count_agg = db.query(func.sum(max_record_ct_per_table.c.max_rows)).scalar() or 0
        total_missing_values_agg = db.query(func.sum(ProfileResultModel.null_value_ct)).scalar() or 0
        avg_dq_score_profiling = db.query(func.avg(ProfilingRunModel.dq_score_profiling)).filter(
            ProfilingRunModel.dq_score_profiling.isnot(None)
        ).scalar() or 0.0

        total_distinct_values_agg = db.query(func.sum(ProfileResultModel.distinct_value_ct)).scalar() or 0
        total_records_sum = db.query(func.sum(ProfileResultModel.record_ct)).scalar() or 0

        distinct_values_percentage = (
            (total_distinct_values_agg / total_records_sum) * 100 if total_records_sum > 0 else 0
        )
        completeness_percentage = (
            ((total_records_sum - total_missing_values_agg) / total_records_sum) * 100 if total_records_sum > 0 else 0
        )

        summary_data = LatestRunSummary(
            tables=total_tables_query,
            columns=total_columns_query,
            rowCount=total_row_count_agg,
            missingValues=total_missing_values_agg,
            dqScore=avg_dq_score_profiling,
            profilingScore=avg_dq_score_profiling,
            cdeScore=0.0,
            distinctValues=total_distinct_values_agg,
            distinctValuesPercentage=distinct_values_percentage,
            completenessPercentage=completeness_percentage
        )

        recent_runs_orm = (
            db.query(ProfilingRunModel)
            .order_by(desc(ProfilingRunModel.profiling_starttime))
            .limit(5)
            .all()
        )

        recent_runs_formatted = [
            RecentRunEntry(
                profiling_id=run.id,
                profilingTime=run.profiling_starttime,
                status=run.status,
                tables=run.table_ct or 0
            ) for run in recent_runs_orm
        ]

        return DashboardData(
            summary=summary_data,
            recentRuns=recent_runs_formatted
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        LOG.error(f"Error fetching dashboard overview data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error fetching dashboard data.")


def get_table_profiling_details_service(run_id: UUID, table_name: str, db: Session) -> TableDetailsData:
    try:
        profiling_run = db.query(ProfilingRunModel).filter(ProfilingRunModel.id == run_id).first()
        if not profiling_run:
            raise HTTPException(status_code=404, detail=f"Profiling run with ID {run_id} not found.")

        profile_results_for_table = (
            db.query(ProfileResultModel)
            .filter(
                ProfileResultModel.profile_run_id == run_id,
                ProfileResultModel.table_name == table_name
            )
            .order_by(ProfileResultModel.position)
            .all()
        )

        if not profile_results_for_table:
            raise HTTPException(status_code=404, detail=f"No profile results found for table '{table_name}' in run ID {run_id}.")

        column_data_types = []
        data_distribution = []

        total_record_ct = 0
        total_distinct_ct = 0
        total_null_ct = 0

        for res in profile_results_for_table:
            column_data_types.append(ColumnDataType(
                columnName=res.column_name,
                columnType=res.column_type,
                generalType=res.general_type
            ))

            empty_val_ct = res.null_value_ct or 0
            if res.column_type and ('VARCHAR' in res.column_type.upper() or 'TEXT' in res.column_type.upper()):
                empty_val_ct += res.zero_length_ct or 0
            elif res.column_type and ('NUMERIC' in res.column_type.upper() or 'INTEGER' in res.column_type.upper()):
                empty_val_ct += res.zero_value_ct or 0

            data_distribution.append(DataDistributionEntry(
                column=res.column_name,
                dataType=res.column_type,
                distinctValues=res.distinct_value_ct or 0,
                missingValues=res.null_value_ct or 0,
                emptyValues=empty_val_ct
            ))

            total_record_ct += res.record_ct or 0
            total_distinct_ct += res.distinct_value_ct or 0
            total_null_ct += res.null_value_ct or 0

        distinct_percentage = (
            (total_distinct_ct / total_record_ct) * 100 if total_record_ct > 0 else 0
        )
        completeness_percentage = (
            ((total_record_ct - total_null_ct) / total_record_ct) * 100 if total_record_ct > 0 else 0
        )
        profiling_score = profiling_run.dq_score_profiling or 0.0

        table_dq_history_raw = (
            db.query(
                ProfilingRunModel.id,
                ProfilingRunModel.profiling_starttime,
                ProfilingRunModel.dq_score_profiling
            )
            .join(ProfileResultModel, ProfilingRunModel.id == ProfileResultModel.profile_run_id)
            .filter(ProfileResultModel.table_name == table_name)
            .group_by(
                ProfilingRunModel.id,
                ProfilingRunModel.profiling_starttime,
                ProfilingRunModel.dq_score_profiling
            )
            .order_by(ProfilingRunModel.profiling_starttime)
            .all()
        )

        table_dq_score_history = [
            TableDQScoreHistory(
                profiling_id=run_id,
                profilingTime=profiling_time,
                dqScore=dq_score
            ) for run_id, profiling_time, dq_score in table_dq_history_raw
        ]

        return TableDetailsData(
            profilingTime=profiling_run.profiling_starttime,
            status=profiling_run.status,
            tableName=table_name,
            columnDataTypes=column_data_types,
            dataDistribution=data_distribution,
            tableDQScoreHistory=table_dq_score_history,
            profilingScore=profiling_score,
            distinctValuePercentage=distinct_percentage,
            completenessPercentage=completeness_percentage
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        LOG.error(f"Error fetching details for run {run_id}, table {table_name}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error fetching table details.")


def get_table_names_for_run_service(run_id: UUID, db: Session) -> List[TableNameItem]:
    try:
        distinct_table_names = (
            db.query(distinct(ProfileResultModel.table_name).label("table_name"))
            .filter(ProfileResultModel.profile_run_id == run_id)
            .order_by(ProfileResultModel.table_name)
            .all()
        )

        if not distinct_table_names:
            raise HTTPException(status_code=404, detail=f"No tables found for profiling run ID {run_id}.")

        return [TableNameItem(tableName=name.table_name) for name in distinct_table_names]

    except HTTPException as e:
        raise e
    except Exception as e:
        LOG.error(f"Error fetching table names for run {run_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error fetching table names.")


    
# ---------- Test suites -------------

def list_table_group_service(db: Session) -> List[Dict[str, Any]]:
    """
    Service function to display only the table groups (name,id) that have
    successfully run the profile.
    A profile run is considered successful if its status is 'Completed'.
    """
    try:
        # Define a subquery to find table_groups_ids that have successful profiling runs
        successful_profiling_runs_subquery = (
            db.query(ProfilingRunModel.table_groups_id)
            .filter(ProfilingRunModel.status == 'Complete') 
            .distinct() 
        ).subquery() 

        # Query TableGroupModel and filter based on the existence in the subquery
        tables = (
            db.query(TableGroupModel.id, TableGroupModel.table_groups_name)
            .filter(
                # Check if TableGroupModel.id exists in the list of successful_profiling_runs_subquery
                TableGroupModel.id.in_(
                    db.query(successful_profiling_runs_subquery.c.table_groups_id)
                )
            )
            .all()
        )

        return [{"id": t.id, "table_groups_name": t.table_groups_name} for t in tables]

    except SQLAlchemyError as e:
        LOG.error(f"Database error listing successful table groups: {e}")
        raise HTTPException(status_code=500, detail=f"Database error listing table groups: {str(e)}")
    except Exception as e:
        LOG.error(f"Unexpected error listing successful table groups: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    
 
def create_test_suites(data: Test_Generation, db: Session = Depends(get_db)):
    try:
        rgt.run_test_gen_queries(data.strTableGroupsID, data.strTestSuite, data.strGenerationSet)
        suite = db.query(TestSuiteModel).filter_by(test_suite=data.strTestSuite).first()
        suite.test_suite_description = data.description
        suite.severity = data.severity
        db.commit()
        return {"status": "started", "message": "Generating test queries background"}
       
    except Exception as e:
        LOG.error(f"Error generating test for group {data.strTableGroupsID}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
 
    
    
def read_test_suite(test_suite_id: str, db: Session = Depends(get_db)):
    test_suite = db.query(TestSuiteModel).filter(TestSuiteModel.id == test_suite_id).first()
    if not test_suite:
        raise HTTPException(status_code=404, detail="Test suite not found")
    return TestSuiteResponse.from_orm(test_suite)


def list_test_suites(db: Session = Depends(get_db)):
    test_suites = db.query(TestSuiteModel).all()
    response_list = []
    for suite in test_suites:
        # has_results = db.query(
        #     exists().where(
        #         and_(
        #             TestResultModel.test_run_id == TestRunModel.id,
        #             TestRunModel.test_suite_id == suite.id
        #         )
        #     )
        # ).scalar()

        # Alternative (simpler if test_suite_id in TestResultModel is always directly populated):
        has_results = db.query(
            exists().where(TestResultModel.test_suite_id == suite.id)
        ).scalar()


        response_list.append(
            TestSuiteResponse(
                id=suite.id,
                test_suite=suite.test_suite,
                table_groups_id=suite.table_groups_id,
                test_suite_description=suite.test_suite_description,
                severity=suite.severity,
                export_to_observability=suite.export_to_observability,
                test_suite_schema=suite.test_suite_schema,
                component_key=suite.component_key,
                component_type=suite.component_type,
                component_name=suite.component_name,
                has_test_results=has_results 
            )
        )
    return response_list


def update_test_suite(test_suite_id: UUID, update_data: TestSuiteMetadata, db: Session = Depends(get_db)):
    test_suite = db.query(TestSuiteModel).filter(TestSuiteModel.id == test_suite_id).first()
    if not test_suite:
        raise HTTPException(status_code=404, detail="Test suite not found")

    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(test_suite, field, value)

    db.commit()
    db.refresh(test_suite)
    return {"status": "success", "message": "Test suite metadata updated"}



def delete_test_suite(test_suite_id: str, db: Session = Depends(get_db)):
    test_suite = db.query(TestSuiteModel).filter(TestSuiteModel.id == test_suite_id).first()
    if not test_suite:
        raise HTTPException(status_code=404, detail="Test suite not found")

    db.delete(test_suite)
    db.commit()
    return {"status": "deleted", "message": f"Test suite {test_suite_id} deleted"}


def run_test_suites(project_code: str, test_suite: str, minutes_offset: int=0):
    try:
        ret.run_execution_steps(project_code, test_suite, minutes_offset=0, spinner=None)
        return {"status": "started", "message": "Execution test in background"}
    except Exception as e:
        LOG.error(f"Error executing tests for group {project_code}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

def display_test_results(test_suite_id: str, db: Session) -> List[TestResultWithDetails]:
    """
    Service function to fetch detailed test results for a given test suite ID,
    including enriched information from the test_types table.
    """
    try:
        results = (
            db.query(TestResultModel, TestTypeModel)
            .join(TestTypeModel, TestResultModel.test_type == TestTypeModel.test_type)
            .filter(TestResultModel.test_suite_id == test_suite_id)
            .all()
        )

        detailed_results = []
        for test_result, test_type_details in results:
            detailed_results.append(
                TestResultWithDetails(
                    id=test_result.id,
                    result_id=test_result.result_id,
                    test_type=test_result.test_type,
                    test_suite_id=test_result.test_suite_id,
                    test_definition_id=test_result.test_definition_id,
                    auto_gen=test_result.auto_gen,
                    test_time=test_result.test_time,
                    starttime=test_result.starttime,
                    endtime=test_result.endtime,
                    schema_name=test_result.schema_name,
                    table_name=test_result.table_name,
                    column_names=test_result.column_names,
                    skip_errors=test_result.skip_errors,
                    input_parameters=test_result.input_parameters,
                    result_code=test_result.result_code,
                    severity=test_result.severity,
                    result_status=test_result.result_status,
                    result_message=test_result.result_message,
                    result_measure=test_result.result_measure,
                    threshold_value=test_result.threshold_value,
                    result_error_data=test_result.result_error_data,
                    test_action=test_result.test_action,
                    disposition=test_result.disposition,
                    subset_condition=test_result.subset_condition,
                    result_query=test_result.result_query,
                    test_description=test_result.test_description, # From test_results table
                    test_run_id=test_result.test_run_id,
                    table_groups_id=test_result.table_groups_id,
                    dq_prevalence=test_result.dq_prevalence,
                    dq_record_ct=test_result.dq_record_ct,
                    observability_status=test_result.observability_status,
                    # Fields from TestTypeModel
                    test_name_short=test_type_details.test_name_short,
                    test_name_long=test_type_details.test_name_long,
                    test_type_description=test_type_details.test_description, # From test_types table
                )
            )
        return detailed_results
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    
    
#------------------- Anomaly results -------------------

def get_anomaly_results(
    table_group_id: UUID,
    group_by_table: bool,
    group_by_run: bool,
    db: Session
) -> Union[AnomalyGroupedByRun, AnomalyGroupedByTable, AnomalyUngrouped]:
    """
    Retrieves anomaly results for a specific table group, allowing grouping by
    table or by profile run time. Anomaly details are enriched using anomaly types.
    The profiling run time is included directly in the AnomalyResultOut Pydantic model.
    """
    try:
        # 1. Fetch the Table Group details
        table_group = db.query(TableGroupModel).filter(
            TableGroupModel.id == table_group_id
        ).first()
        if not table_group:
            raise HTTPException(status_code=404, detail="Table Group not found")

        # 2. Fetch Anomaly Results joined with Profiling Runs
        # We query both AnomalyResultModel and ProfilingRunModel to get the profiling_starttime.
        # Filtering for 'Completed' status as requested.
        anomaly_results_query = db.query(AnomalyResultModel, ProfilingRunModel).join(
            ProfilingRunModel,
            AnomalyResultModel.profile_run_id == ProfilingRunModel.id
        ).filter(
            AnomalyResultModel.table_groups_id == table_group_id,
            ProfilingRunModel.status == 'Complete' # Filter for successfully completed runs
        )
        anomaly_results_with_runs = anomaly_results_query.all()

        if not anomaly_results_with_runs:
            raise HTTPException(status_code=404, detail="No completed anomaly results found for this table group.")

        # 3. Fetch all anomaly types into a dictionary for quick lookup
        # Ensure type matching for anomaly_id (AnomalyResultModel.anomaly_id is Integer, ProfileAnomalyTypeModel.id is String)
        anomaly_types_map: Dict[str, ProfileAnomalyTypeModel] = {
            str(at.id): at for at in db.query(ProfileAnomalyTypeModel).all()
        }

        table_group_out = TableGroupOut.from_orm(table_group)

        # 4. Process raw anomaly results into AnomalyResultOut objects
        processed_anomaly_results: List[AnomalyResultOut] = []
        for anomaly_result_model, profiling_run_model in anomaly_results_with_runs:
            # Create AnomalyResultOut, manually populating profiling_starttime
            anomaly_out_data = anomaly_result_model.__dict__.copy() # Get dict from SQLAlchemy model
            anomaly_out_data['profiling_starttime'] = profiling_run_model.profiling_starttime
            anomaly_out = AnomalyResultOut(**anomaly_out_data) # Create Pydantic model from dict

            # Enrich with anomaly type details
            # Ensure type matching for anomaly_id (AnomalyResultModel.anomaly_id is Integer, ProfileAnomalyTypeModel.id is String)
            anomaly_type_detail = anomaly_types_map.get(str(anomaly_result_model.anomaly_id))

            if anomaly_type_detail:
                anomaly_out.anomaly_name = anomaly_type_detail.anomaly_name
                anomaly_out.anomaly_description = anomaly_type_detail.anomaly_description
                anomaly_out.issue_likelihood = anomaly_type_detail.issue_likelihood
                anomaly_out.suggested_action = anomaly_type_detail.suggested_action
                anomaly_out.dq_dimension = anomaly_type_detail.dq_dimension
            
            processed_anomaly_results.append(anomaly_out)

        # 5. Apply Grouping Logic
        if group_by_run:
            grouped = collections.defaultdict(lambda: collections.defaultdict(list))
            for result_out in processed_anomaly_results:
                # Use profiling_starttime directly from the AnomalyResultOut object
                run_time_key = result_out.profiling_starttime.isoformat()
                grouped[run_time_key][result_out.table_name].append(
                    result_out
                )
            return AnomalyGroupedByRun(
                table_group=table_group_out,
                anomaly_results_by_run={run_id: dict(tables) for run_id, tables in grouped.items()}
            )
        
        if group_by_table:
            grouped = collections.defaultdict(list)
            for result_out in processed_anomaly_results:
                grouped[result_out.table_name].append(result_out)
            return AnomalyGroupedByTable(
                table_group=table_group_out,
                anomaly_results_by_table=dict(grouped)
            )
        
        # Default ungrouped path
        return AnomalyUngrouped(
            table_group=table_group_out,
            all_anomaly_results=processed_anomaly_results
        )

    except SQLAlchemyError as e:
        LOG.error(f"Database error fetching anomaly results for table group {table_group_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        LOG.error(f"An unexpected error occurred while fetching anomaly results for table group {table_group_id}: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# ---------------  Test Dashboard Overview service -----------------------

def get_overall_data_quality_overview_service(duration: str, db: Session) -> OverallDataQualityOverviewResponse:
    try:
        time_filter = get_time_filter(duration)

        # 1. Data Quality Score
        avg_dq_score = db.query(func.avg(TestRunModel.dq_score_test_run)).filter(
            TestRunModel.test_starttime >= time_filter
        ).scalar()

        # 2. Test Failures
        current_failures = db.query(func.sum(TestRunModel.failed_ct)).filter(
            TestRunModel.test_starttime >= time_filter
        ).scalar()
        if current_failures is None:
            current_failures = 0

        # Calculate percentage change for test failures
        if duration.lower() == "last 30 days":
            previous_period_start = time_filter - timedelta(days=30)
        elif duration.lower() == "last 7 days":
            previous_period_start = time_filter - timedelta(days=7)
        elif duration.lower() == "today":
            previous_period_start = time_filter - timedelta(days=1)
        else:
            previous_period_start = time_filter - timedelta(days=30)

        previous_failures = db.query(func.sum(TestRunModel.failed_ct)).filter(
            TestRunModel.test_starttime >= previous_period_start,
            TestRunModel.test_starttime < time_filter
        ).scalar()
        if previous_failures is None:
            previous_failures = 0

        percentage_change_display: Union[float, str, None] = None
        if previous_failures == 0:
            if current_failures > 0:
                percentage_change_display = f"+{current_failures} (New Failures)"
            else:
                percentage_change_display = "No change"
        else:
            percentage_change_value = ((current_failures - previous_failures) / previous_failures) * 100
            percentage_change_display = round(percentage_change_value, 1)

        # 3. Records Tested - Return raw count
        total_columns_tested = db.query(func.sum(TestRunModel.test_ct)).filter(
            TestRunModel.test_starttime >= time_filter
        ).scalar()
        total_columns_tested = int(total_columns_tested) if total_columns_tested is not None else 0
        
        #This is wrt rows
        total_records_tested = db.query(func.sum(TestResultModel.dq_record_ct)).filter(
            TestResultModel.test_time >= time_filter
        ).scalar()
        raw_total_records_tested = int(total_records_tested) if total_records_tested is not None else 0
        total_records_tested = format_large_number(raw_total_records_tested)

        # 4. Test Status
        total_passed = db.query(func.sum(TestRunModel.passed_ct)).filter(
            TestRunModel.test_starttime >= time_filter
        ).scalar() or 0
        total_failed = db.query(func.sum(TestRunModel.failed_ct)).filter(
            TestRunModel.test_starttime >= time_filter
        ).scalar() or 0
        total_warning = db.query(func.sum(TestRunModel.warning_ct)).filter(
            TestRunModel.test_starttime >= time_filter
        ).scalar() or 0
        
        
        
       

        total_actions = total_passed + total_failed + total_warning

        passed_percentage = (total_passed  ) if total_actions > 0 else 0
        failed_percentage = (total_failed ) if total_actions > 0 else 0
        skipped_percentage = (total_warning  ) if total_actions > 0 else 0

        test_success_count = total_passed
        test_failure_count = total_failed

        return OverallDataQualityOverviewResponse(
            data_quality_score=round(avg_dq_score * 100) if avg_dq_score is not None else None,
            test_failures={
                "count": int(current_failures),
                "percentage_change": percentage_change_display
            },
            records_tested=total_records_tested,
            columns_tested=total_columns_tested,
            test_status={
                "passed_percentage": round(passed_percentage),
                "failed_percentage": round(failed_percentage),
                "skipped_percentage": round(skipped_percentage),
                "success_count": int(test_success_count),
                "failure_count": int(test_failure_count)
            }
        )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

def get_data_quality_trend_service(duration: str, metric: str, db: Session) -> DataQualityTrendResponse:
    try:
        time_filter = get_time_filter(duration)

        query_expression = None
        metric_label = ""

        if metric == "dq_score":
            query_expression = func.avg(TestRunModel.dq_score_test_run)
            metric_label = "DQ Score"
        elif metric == "test_failures_count":
            query_expression = func.sum(TestRunModel.failed_ct)
            metric_label = "Test Failures Count"
        else:
            raise HTTPException(status_code=400, detail="Invalid metric specified. Choose 'dq_score' or 'test_failures_count'.")

        results = db.query(
            cast(TestRunModel.test_starttime, Date),
            query_expression
        ).filter(
            TestRunModel.test_starttime >= time_filter
        ).group_by(
            cast(TestRunModel.test_starttime, Date)
        ).order_by(
            cast(TestRunModel.test_starttime, Date)
        ).all()

        trend_data = []
        if results:
            for i, (date, value) in enumerate(results):
                if metric == "dq_score":
                    processed_value = round(float(value) * 100, 1) if value is not None else 0.0
                elif metric == "test_failures_count":
                    processed_value = int(value) if value is not None else 0
                else:
                    processed_value = value

                day_diff = (date - time_filter.date()).days + 1

                trend_data.append({"day": day_diff, "value": processed_value})

        return DataQualityTrendResponse(
            trend_data=trend_data,
            metric_label=metric_label
        )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


def get_recent_test_runs_service(limit: int, db: Session) -> RecentTestRunsTableResponse:
    try:
        recent_runs_query = db.query(
            TestRunModel,
            Connection.connection_name,
            Connection.connection_id,
            TestSuiteModel.test_suite,
            TestSuiteModel.id.label("test_suite_id_alias"),
            TableGroupModel.table_groups_name,
            TableGroupModel.id.label("table_group_id_alias")
        ).join(
            TestSuiteModel, TestRunModel.test_suite_id == TestSuiteModel.id
        ).join(
            TableGroupModel, TestSuiteModel.table_groups_id == TableGroupModel.id
        ).join(
            Connection, TestRunModel.connection_id == Connection.id
        ).order_by(
            TestRunModel.test_starttime.desc()
        ).limit(limit)

        recent_runs = recent_runs_query.all()

        formatted_test_runs = []
        for run, test_suite_name, test_suite_id, table_group_name, table_group_id , connection_id, connection_name, sql_flavor, explicit_table_list in recent_runs:
            formatted_test_runs.append(RecentTestRunDetail(
                connection_id=connection_id,
                connection_name=connection_name,
                db_type = sql_flavor,
                test_run_id=run.id,
                test_suite_name=test_suite_name,
                test_suite_id=test_suite_id,
                status=run.status,
                records_tested=str(run.test_ct) if run.test_ct is not None else "N/A",
                duration_display=format_duration_display(run.duration),
                table_group_name=table_group_name,
                tables = explicit_table_list,
                table_group_id=table_group_id
            ))

        total_count = db.query(TestRunModel).count()

        return RecentTestRunsTableResponse(
            total_count=total_count,
            test_runs=formatted_test_runs
        )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


def get_data_sources_service(db: Session) -> List[DataSource]:
    try:
        data_sources_query = db.query(
            Connection.connection_name,
            Connection.connection_id,
            func.avg(TestRunModel.dq_score_test_run).label("avg_dq_score")
        ).join(
            TableGroupModel, Connection.connection_id == TableGroupModel.connection_id
        ).join(
            TestSuiteModel, TableGroupModel.id == TestSuiteModel.table_groups_id
        ).join(
            TestRunModel, TestSuiteModel.id == TestRunModel.test_suite_id
        ).group_by(
            Connection.connection_id, Connection.connection_name
        ).order_by(
            Connection.connection_name
        ).all()

        data_sources = []
        for name, conn_id, avg_dq_score in data_sources_query:
            status = "Active" # Placeholder
            data_sources.append(DataSource(
                connection_name=name,
                connection_id=conn_id,
                data_quality_score=round(avg_dq_score * 100) if avg_dq_score is not None else None,
                status=status
            ))
        return data_sources
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    
    
# ----------------------------------------------- New Profile Dashboard --------------------------------------

def calculate_success_rate_change(current_rate: float, previous_rate: float) -> Optional[float]:
    """Calculates the percentage change in success rate."""
    if previous_rate == 0:
        return None  # Cannot calculate percentage change from zero
    return round(((current_rate - previous_rate) / previous_rate) * 100, 2)

def get_overview_metrics_service(
    db: Session,
    database_connection_id: Optional[int],
    schema_table_group_uuid: Optional[uuid.UUID]
) -> OverviewMetricsResponse:
    try:
        # Base query for profiling runs
        base_query = db.query(ProfilingRunModel)

        # Apply filters
        if database_connection_id:
            base_query = base_query.filter(ProfilingRunModel.connection_id == database_connection_id)
        if schema_table_group_uuid:
            base_query = base_query.filter(ProfilingRunModel.table_groups_id == schema_table_group_uuid)

        all_runs = base_query.all()

        total_profiles = 0
        columns_profiled = 0
        raw_rows_profiled = 0
        #rows_profiled = 0
        failed_profiles_count = 0

        # Get unique table groups based on the filtered runs
        unique_table_group_ids = {run.table_groups_id for run in all_runs}
        total_profiles = len(unique_table_group_ids)

        # Calculate columns profiled and failed profiles based on the LATEST run for each unique table group
        for tg_id in unique_table_group_ids:
            # Find the latest run for this specific table group (within the overall filtered scope if applicable)
            latest_run_for_tg_query = db.query(ProfilingRunModel)\
                .filter(ProfilingRunModel.table_groups_id == tg_id)

            if database_connection_id:
                latest_run_for_tg_query = latest_run_for_tg_query.filter(ProfilingRunModel.connection_id == database_connection_id)

            latest_run_for_tg = latest_run_for_tg_query.order_by(ProfilingRunModel.profiling_endtime.desc()).first()

            if latest_run_for_tg:
                # Columns profiled: from the latest successful run for this table group
                latest_successful_run_for_tg_query = db.query(ProfilingRunModel)\
                    .filter(ProfilingRunModel.table_groups_id == tg_id)\
                    .filter(ProfilingRunModel.status == 'Complete')

                if database_connection_id:
                    latest_successful_run_for_tg_query = latest_successful_run_for_tg_query.filter(
                        ProfilingRunModel.connection_id == database_connection_id
                    )

                latest_successful_run_for_tg = latest_successful_run_for_tg_query.order_by(
                    ProfilingRunModel.profiling_endtime.desc()
                ).first()

                if latest_successful_run_for_tg:
                    record_count_sum = db.query(func.avg(ProfileResultModel.record_ct))\
                                            .filter(ProfileResultModel.profile_run_id == latest_successful_run_for_tg.id)\
                                            .scalar()
                    raw_rows_profiled += int(record_count_sum) if record_count_sum is not None else 0

                    # columns_profiled handling remains the same as it's separate
                    columns_profiled += (latest_successful_run_for_tg.column_ct or 0)
                    
                    
                # Failed profiles: based on the status of the absolute latest run
                if latest_run_for_tg.status != 'Complete':
                    failed_profiles_count += 1
        formatted_rows_profiled = format_large_number(raw_rows_profiled)
        #Rows count conversion
        rows_profiled = format_large_number(raw_rows_profiled)
        # Success rate calculation based on all filtered runs
        total_runs_count = len(all_runs)
        successful_runs_count = sum(1 for run in all_runs if run.status == 'Complete')

        success_rate = 0.0
        if total_runs_count > 0:
            success_rate = (successful_runs_count / total_runs_count) * 100

        success_rate_change = None

        # Calculate success rate change only if there's sufficient history
        if total_runs_count > 1:
            # Get the timestamp of the second latest run (if it exists) to define a "previous" period
            second_latest_run_query = base_query.order_by(ProfilingRunModel.profiling_endtime.desc()).offset(1).first()

            if second_latest_run_query:
                previous_period_runs = base_query.filter(
                    ProfilingRunModel.profiling_endtime < second_latest_run_query.profiling_endtime
                ).all()

                prev_total_runs = len(previous_period_runs)
                prev_successful_count = sum(1 for run in previous_period_runs if run.status == 'Complete')

                if prev_total_runs > 0:
                    previous_period_success_rate = (prev_successful_count / prev_total_runs) * 100
                    success_rate_change = calculate_success_rate_change(success_rate, previous_period_success_rate)

        # Special handling for single run / no history for a specific table group
        if schema_table_group_uuid:
            runs_for_specific_tg = db.query(ProfilingRunModel)\
                .filter(ProfilingRunModel.table_groups_id == schema_table_group_uuid)\
                .filter(ProfilingRunModel.connection_id == database_connection_id if database_connection_id else True)\
                .all()
            if len(runs_for_specific_tg) <= 1:
                success_rate = 100.00
                success_rate_change = None

        #formatted_rows_profiled = format_large_number(raw_rows_profiled)

        return OverviewMetricsResponse(
            total_profiles=total_profiles,
            rows_profiled = rows_profiled,
            columns_profiled=columns_profiled,
            success_rate=round(success_rate, 2),
            success_rate_change=success_rate_change,
            failed_profiles=failed_profiles_count
        )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


def get_profile_run_trend_service(
    db: Session,
    database_connection_id: Optional[int],
    schema_table_group_uuid: Optional[uuid.UUID],
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    interval: str,
    metric: str
) -> ProfileRunTrendResponse:
    try:
        query = db.query(ProfilingRunModel)
        if database_connection_id:
            query = query.filter(ProfilingRunModel.connection_id == database_connection_id)
        if schema_table_group_uuid:
            query = query.filter(ProfilingRunModel.table_groups_id == schema_table_group_uuid)
        if start_date:
            query = query.filter(ProfilingRunModel.profiling_starttime >= start_date)
        if end_date:
            query = query.filter(ProfilingRunModel.profiling_starttime <= end_date)

        # Grouping by interval
        if interval == "day":
            date_trunc_func = func.date_trunc('day', ProfilingRunModel.profiling_starttime)
        elif interval == "week":
            date_trunc_func = func.date_trunc('week', ProfilingRunModel.profiling_starttime)
        elif interval == "month":
            date_trunc_func = func.date_trunc('month', ProfilingRunModel.profiling_starttime)
        else:
            raise HTTPException(status_code=400, detail="Invalid interval. Choose 'day', 'week', or 'month'.")

        trend_query = db.query(
            date_trunc_func.label('date'),
            func.count(ProfilingRunModel.id).label('total_runs'),
            func.sum(case((ProfilingRunModel.status == 'Complete', 1), else_=0)).label('successful_runs'),
            func.avg(ProfilingRunModel.dq_score_profiling).label('avg_dq_score')
        )

        # Apply filters to the aggregation query
        if database_connection_id:
            trend_query = trend_query.filter(ProfilingRunModel.connection_id == database_connection_id)
        if schema_table_group_uuid:
            trend_query = trend_query.filter(ProfilingRunModel.table_groups_id == schema_table_group_uuid)
        if start_date:
            trend_query = trend_query.filter(ProfilingRunModel.profiling_starttime >= start_date)
        if end_date:
            trend_query = trend_query.filter(ProfilingRunModel.profiling_starttime <= end_date)

        trend_results = trend_query.group_by(date_trunc_func).order_by(date_trunc_func).all()

        trend_data = []
        for row in trend_results:
            trend_data.append(ProfileRunTrendDataPoint(
                date=row.date.strftime("%Y-%m-%d"),
                total_runs=row.total_runs,
                successful_runs=row.successful_runs,
                avg_dq_score=round(row.avg_dq_score, 2) if row.avg_dq_score is not None else None
            ))

        return ProfileRunTrendResponse(trend_data=trend_data)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


def get_recent_profile_runs_service(
    db: Session,
    database_connection_id: Optional[int],
    schema_table_group_uuid: Optional[uuid.UUID],
    limit: int,
    offset: int,
    sort_by: str,
    sort_order: str
) -> RecentProfileRunsResponse:
    try:
        query = db.query(
            ProfilingRunModel,
            Connection.connection_name,
            Connection.connection_id,
            TableGroupModel.table_groups_name,
            TableGroupModel.db_schema,
            TableGroupModel.id.label('table_group_model_id_uuid')
        )\
        .join(Connection, ProfilingRunModel.connection_id == Connection.connection_id)\
        .join(TableGroupModel, ProfilingRunModel.table_groups_id == TableGroupModel.id)

        if database_connection_id:
            query = query.filter(ProfilingRunModel.connection_id == database_connection_id)
        if schema_table_group_uuid:
            query = query.filter(ProfilingRunModel.table_groups_id == schema_table_group_uuid)

        # Apply sorting
        if sort_by == "profiling_starttime":
            order_column = ProfilingRunModel.profiling_starttime
        elif sort_by == "status":
            order_column = ProfilingRunModel.status
        elif sort_by == "columns_profiled":
            order_column = ProfilingRunModel.column_ct
        else:
            raise HTTPException(status_code=400, detail="Invalid sort_by parameter.")

        if sort_order == "desc":
            query = query.order_by(order_column.desc())
        elif sort_order == "asc":
            query = query.order_by(order_column.asc())
        else:
            raise HTTPException(status_code=400, detail="Invalid sort_order parameter. Use 'asc' or 'desc'.")

        total_runs = query.count()
        runs_data = query.offset(offset).limit(limit).all()

        recent_runs_list = []
        for run, conn_name, conn_id, tg_name, tg_schema, tg_uuid in runs_data:
            recent_runs_list.append(RecentProfileRun(
                run_display_id=f"Run on {run.profiling_starttime.strftime('%Y-%m-%d %H:%M')} ({run.status})",
                run_uuid=run.id,
                database_name=conn_name,
                database_connection_id=conn_id,
                schema_name=tg_schema,
                schema_table_group_uuid=tg_uuid,
                table_group_name=tg_name,
                status=run.status,
                columns_profiled=run.column_ct or 0,
                start_time=run.profiling_starttime
            ))

        return RecentProfileRunsResponse(total_runs=total_runs, runs=recent_runs_list)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


def get_column_stats_distribution_service(
    db: Session,
    metric_type: ColumnMetricType,
    database_connection_id: Optional[int],
    schema_table_group_uuid: Optional[uuid.UUID],
    bucket_size: float
) -> ColumnStatsDistributionResponse:
    try:
        # Step 1: Find the latest successful profile_run_id for the given scope
        latest_run_id = None

        latest_run_query_base = db.query(ProfilingRunModel)\
            .filter(ProfilingRunModel.status == 'Complete')\
            .order_by(ProfilingRunModel.profiling_endtime.desc())

        if database_connection_id:
            latest_run_query_base = latest_run_query_base.filter(ProfilingRunModel.connection_id == database_connection_id)
        if schema_table_group_uuid:
            latest_run_query_base = latest_run_query_base.filter(ProfilingRunModel.table_groups_id == schema_table_group_uuid)

        latest_run = latest_run_query_base.first()
        latest_run_id = latest_run.id if latest_run else None

        if not latest_run_id:
            raise HTTPException(status_code=404, detail="No complete profiling runs found for the specified scope.")

        # Step 2: Query ProfileResultModel for the latest successful run
        profile_results_query = db.query(ProfileResultModel)\
            .filter(ProfileResultModel.profile_run_id == latest_run_id)

        if database_connection_id:
            profile_results_query = profile_results_query.filter(ProfileResultModel.connection_id == database_connection_id)
        if schema_table_group_uuid:
            profile_results_query = profile_results_query.filter(ProfileResultModel.table_groups_id == schema_table_group_uuid)

        profile_results = profile_results_query.all()

        if not profile_results:
            raise HTTPException(status_code=404, detail="No profile results found for the latest complete run in the specified scope.")

        distribution_counts = {}
        chart_title = ""
        x_axis_label = ""

        max_val = 100
        if metric_type == ColumnMetricType.AVG_LENGTH:
            actual_max_length = max([res.max_length for res in profile_results if res.max_length is not None], default=0)
            max_val = max(actual_max_length + 10, 100)

        num_buckets = int(max_val / bucket_size)
        for i in range(num_buckets + 1):
            lower_bound = i * bucket_size
            upper_bound = (i + 1) * bucket_size

            if upper_bound > max_val:
                upper_bound = max_val

            if lower_bound == upper_bound:
                continue

            range_str = f"{int(lower_bound)}-{int(upper_bound)}"
            if metric_type != ColumnMetricType.AVG_LENGTH:
                range_str += "%"

            if range_str not in distribution_counts:
                distribution_counts[range_str] = 0

        for res in profile_results:
            value_to_bucket = None
            if metric_type == ColumnMetricType.NULL_PERCENTAGE:
                chart_title = "Distribution of Null Values"
                x_axis_label = "Null Value Percentage"
                if res.record_ct is not None and res.record_ct > 0:
                    value_to_bucket = (res.null_value_ct / res.record_ct) * 100
                else:
                    value_to_bucket = 0
            elif metric_type == ColumnMetricType.DISTINCT_PERCENTAGE:
                chart_title = "Distribution of Distinct Values"
                x_axis_label = "Distinct Value Percentage"
                if res.record_ct is not None and res.record_ct > 0:
                    value_to_bucket = (res.distinct_value_ct / res.record_ct) * 100
                else:
                    value_to_bucket = 0
            elif metric_type == ColumnMetricType.AVG_LENGTH:
                chart_title = "Distribution of Average Lengths"
                x_axis_label = "Average Length"
                value_to_bucket = res.avg_length

            if value_to_bucket is not None:
                bucket_index = int(value_to_bucket // bucket_size)

                if value_to_bucket == max_val and metric_type != ColumnMetricType.AVG_LENGTH:
                    bucket_index = num_buckets - 1
                elif value_to_bucket == max_val and metric_type == ColumnMetricType.AVG_LENGTH:
                    bucket_index = num_buckets - 1

                lower_bound = bucket_index * bucket_size
                upper_bound = (bucket_index + 1) * bucket_size

                if upper_bound > max_val:
                    upper_bound = max_val

                range_str = f"{int(lower_bound)}-{int(upper_bound)}"
                if metric_type != ColumnMetricType.AVG_LENGTH:
                    range_str += "%"

                if range_str in distribution_counts:
                    distribution_counts[range_str] += 1
                else:
                    distribution_counts[range_str] = 1

        sorted_distribution_data = []
        def sort_key_for_range(range_str_val):
            try:
                return float(range_str_val.split('-')[0].replace('%', ''))
            except ValueError:
                return float('inf')

        for key in sorted(distribution_counts.keys(), key=sort_key_for_range):
            sorted_distribution_data.append(DistributionDataPoint(range=key, column_count=distribution_counts[key]))

        return ColumnStatsDistributionResponse(
            chart_title=chart_title,
            x_axis_label=x_axis_label,
            y_axis_label="Number of Columns",
            distribution_data=sorted_distribution_data
        )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


def get_dropdown_options_service(
    db: Session,
    type: str,
    database_connection_id: Optional[int]
) -> List[DropdownOption]:
    try:
        options_list = []
        if type == "database":
            connections = db.query(Connection.connection_name, Connection.connection_id).distinct().all()
            for name, conn_id in connections:
                options_list.append(DropdownOption(display_name=name, value=str(conn_id)))
        elif type == "table_group":
            query = db.query(TableGroupModel.table_groups_name, TableGroupModel.id).distinct()
            if database_connection_id:
                query = query.filter(TableGroupModel.connection_id == database_connection_id)
            table_groups = query.all()
            for schema_name, tg_id in table_groups:
                options_list.append(DropdownOption(display_name=schema_name, value=str(tg_id)))
        else:
            raise HTTPException(status_code=400, detail="Invalid type. Choose 'database' or 'table_group'.")

        return options_list
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


def get_column_distinct_counts_service(
    db: Session,
    database_connection_id: Optional[int],
    schema_table_group_uuid: Optional[uuid.UUID],
    table_name: Optional[str],
    column_name: Optional[str]
) -> ColumnDistinctCountsResponse:
    try:
        column_distinct_counts_list = []

        # Step 1: Find the latest successful profile_run_id for the given scope
        latest_run_id = None

        latest_run_query_base = db.query(ProfilingRunModel)\
            .filter(ProfilingRunModel.status == 'Complete')\
            .order_by(ProfilingRunModel.profiling_endtime.desc())

        if database_connection_id:
            latest_run_query_base = latest_run_query_base.filter(ProfilingRunModel.connection_id == database_connection_id)
        if schema_table_group_uuid:
            latest_run_query_base = latest_run_query_base.filter(ProfilingRunModel.table_groups_id == schema_table_group_uuid)

        latest_run = latest_run_query_base.first()
        latest_run_id = latest_run.id if latest_run else None

        if not latest_run_id:
            return ColumnDistinctCountsResponse(column_distinct_counts=[])

        # Step 2: Query ProfileResultModel for the latest successful run and filters
        profile_results_query = db.query(ProfileResultModel)\
            .filter(ProfileResultModel.profile_run_id == latest_run_id)

        if database_connection_id:
            profile_results_query = profile_results_query.filter(ProfileResultModel.connection_id == database_connection_id)
        if schema_table_group_uuid:
            profile_results_query = profile_results_query.filter(ProfileResultModel.table_groups_id == schema_table_group_uuid)
        if table_name:
            profile_results_query = profile_results_query.filter(ProfileResultModel.table_name == table_name)
        if column_name:
            profile_results_query = profile_results_query.filter(ProfileResultModel.column_name == column_name)

        profile_results_query = profile_results_query.filter(ProfileResultModel.distinct_value_ct.isnot(None))

        profile_results = profile_results_query.all()

        for res in profile_results:
            column_distinct_counts_list.append(ColumnDistinctCountDetail(
                table_name=res.table_name,
                column_name=res.column_name,
                distinct_value_count=res.distinct_value_ct or 0
            ))

        return ColumnDistinctCountsResponse(column_distinct_counts=column_distinct_counts_list)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


#-----------------------------------------------------Test Summary -----------------------------------------------------

def get_test_run_status_summary_service(db: Session) -> Dict[str, int]:
    """
    Service function to get the aggregated result_status and their counts
    from the test_results table.
    """
    try:
        status_counts = db.query(
            TestResultModel.result_status,
            func.count(TestResultModel.id)
        ).group_by(TestResultModel.result_status).all()

        summary = {status: count for status, count in status_counts}
        return summary
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

def get_test_type_summary_by_status_service(result_status: str, db: Session) -> Dict[str, int]:
    """
    Service function to get the aggregated test_type and their counts
    from the test_results table, filtered by a specific result_status.
    """
    try:
        test_type_counts = db.query(
            TestResultModel.test_type,
            func.count(TestResultModel.id)
        ).filter(TestResultModel.result_status == result_status).group_by(TestResultModel.test_type).all()

        summary = {test_type: count for test_type, count in test_type_counts}
        return summary
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

def get_detailed_test_results_service(result_status: str, test_type: str, db: Session) -> List[TestResultDetail]:
    """
    Service function to get detailed test_results data, filtered by
    result_status and test_type.
    """
    try:
        detailed_results_objects = db.query(TestResultModel).filter(
            TestResultModel.result_status == result_status,
            TestResultModel.test_type == test_type
        ).all()

        detailed_results = [TestResultDetail.from_orm(result) for result in detailed_results_objects]
        return detailed_results
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

def get_test_runs_summary_by_suite_service(db: Session) -> TestSuiteSummary:
    """
    Service function to get aggregated counts of passed, failed, warning, and error tests
    for each distinct test suite, along with their percentages.
    """
    try:
        results = db.query(
            TestRunModel.test_suite_id,
            func.sum(TestRunModel.passed_ct).label('passed_ct'),
            func.sum(TestRunModel.failed_ct).label('failed_ct'),
            func.sum(TestRunModel.warning_ct).label('warning_ct'),
            func.sum(TestRunModel.error_ct).label('error_ct'),
            func.sum(TestRunModel.test_ct).label('total_tests_executed')
        ).group_by(TestRunModel.test_suite_id).all()

        suite_summaries = []
        for row in results:
            passed_ct = row.passed_ct if row.passed_ct is not None else 0
            failed_ct = row.failed_ct if row.failed_ct is not None else 0
            warning_ct = row.warning_ct if row.warning_ct is not None else 0
            error_ct = row.error_ct if row.error_ct is not None else 0
            total_tests_executed = row.total_tests_executed if row.total_tests_executed is not None else 0

            percentages = {}
            if total_tests_executed > 0:
                percentages = {
                    "passed_pct": (passed_ct / total_tests_executed) * 100,
                    "failed_pct": (failed_ct / total_tests_executed) * 100,
                    "warning_pct": (warning_ct / total_tests_executed) * 100,
                    "error_pct": (error_ct / total_tests_executed) * 100,
                }
            else:
                percentages = {
                    "passed_pct": 0.0,
                    "failed_pct": 0.0,
                    "warning_pct": 0.0,
                    "error_pct": 0.0,
                }

            suite_summaries.append(
                TestSuiteCounts(
                    test_suite_id=row.test_suite_id,
                    passed_ct=passed_ct,
                    failed_ct=failed_ct,
                    warning_ct=warning_ct,
                    error_ct=error_ct,
                    total_tests_executed=total_tests_executed,
                    percentages=percentages
                )
            )

        return TestSuiteSummary(test_suite_summaries=suite_summaries)

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    
    
#--------------------------------------------Test Case CRUD----------------------------------------------------
