from typing import Optional, List
from datetime import datetime
from uuid import UUID
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    BigInteger,
    LargeBinary,
    Boolean,
    Float,
    ForeignKey,
    Identity,
    Text,
    func, # func.gen_random_uuid() is good!
)
from sqlalchemy.orm import sessionmaker, relationship, foreign, remote
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID as PGUUID # <--- CONSISTENTLY USE PGUUID
import logging
# Redundant import of Column, String, etc. removed. They are already imported above.
from sqlalchemy import TIMESTAMP, Numeric # These were missing but used.
import uuid # For default=uuid.uuid4 where needed

# Logging config
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:bhuvan@localhost:5432/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Define Connection first as it's referenced by TableGroupModel
class Connection(Base):
    __tablename__ = "connections"
    __table_args__ = {'schema': 'tgapp'}

    id = Column(PGUUID(as_uuid=True), default=func.gen_random_uuid()) # Use PGUUID here too if it's an actual UUID
    project_code = Column(String(30), nullable=True)
    connection_id = Column(BigInteger, Identity(always=True), primary_key=True) # This is the "friendly" ID
    sql_flavor = Column('sql_flavor', String(30))
    project_host = Column(String(250))
    project_port = Column(String(5))
    project_user = Column(String(50))
    project_db = Column(String(100))
    connection_name = Column(String(40))
    connection_description = Column(String(1000), nullable=True)
    project_pw_encrypted = Column(LargeBinary, nullable=True)
    max_threads = Column(Integer, default=4)
    max_query_chars = Column(Integer, nullable=True)
    url = Column(String(200), default='')
    connect_by_url = Column(Boolean, default=False)
    connect_by_key = Column(Boolean, default=False)
    private_key = Column(LargeBinary, nullable=True)
    private_key_passphrase = Column(LargeBinary, nullable=True)
    http_path = Column(String(200), nullable=True)


# Define TableGroupModel next as it references Connection
class TableGroupModel(Base):
    __tablename__ = "table_groups"
    __table_args__ = {'schema': 'tgapp'}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid())
    project_code = Column(String(30), nullable=True)
    connection_id = Column(BigInteger, ForeignKey('tgapp.connections.connection_id'), nullable=True)
    table_groups_name = Column('table_groups_name', String(100))
    db_schema = Column('table_group_schema', String(100))
    explicit_table_list = Column('profiling_table_set', String(2000), nullable=True)
    tables_to_include_mask = Column('profiling_include_mask', String(2000), nullable=True)
    profiling_exclude_mask = Column('profiling_exclude_mask', String(2000), nullable=True)
    profiling_id_column_mask = Column('profile_id_column_mask', String(2000), default='%id', nullable=True)
    profiling_surrogate_key_column_mask = Column('profile_sk_column_mask', String(150), default='%_sk', nullable=True)
    profile_use_sampling = Column(String(3), default='N', nullable=True)
    profile_sample_percent = Column(String(3), default='30', nullable=True)
    profile_sample_min_count = Column(BigInteger, default=100000, nullable=True)
    min_profiling_age_days = Column('profiling_delay_days', String(3), default='0', nullable=True)
    profile_flag_cdes = Column(Boolean, default=True, nullable=True)
    profile_do_pair_rules = Column(String(3), default='N', nullable=True)
    profile_pair_rule_pct = Column(Integer, default=95, nullable=True)
    description = Column(String(1000), nullable=True)
    data_source = Column(String(40), nullable=True)
    source_system = Column(String(40), nullable=True)
    source_process = Column(String(40), nullable=True)
    data_location = Column(String(40), nullable=True)
    business_domain = Column(String(40), nullable=True)
    stakeholder_group = Column(String(40), nullable=True)
    transform_level = Column(String(40), nullable=True)
    data_product = Column(String(40), nullable=True)
    last_complete_profile_run_id = Column(PGUUID(as_uuid=True), nullable=True) # Use PGUUID
    dq_score_profiling = Column(Float, nullable=True)
    dq_score_testing = Column(Float, nullable=True)

    connection = relationship("Connection", primaryjoin="TableGroupModel.connection_id == Connection.connection_id", foreign_keys=[connection_id], backref="table_groups")


class ProfilingRunModel(Base):
    __tablename__ = "profiling_runs"
    __table_args__ = {'schema': 'tgapp'}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_code = Column(String(30), nullable=False)
    connection_id = Column(BigInteger, nullable=False)
    table_groups_id = Column(PGUUID(as_uuid=True), nullable=False)
    profiling_starttime = Column(TIMESTAMP)
    profiling_endtime = Column(TIMESTAMP)
    status = Column(String(100), default='Running')
    log_message = Column(String)
    table_ct = Column(BigInteger)
    column_ct = Column(BigInteger)
    anomaly_ct = Column(BigInteger)
    anomaly_table_ct = Column(BigInteger)
    anomaly_column_ct = Column(BigInteger)
    dq_affected_data_points = Column(BigInteger)
    dq_total_data_points = Column(BigInteger)
    dq_score_profiling = Column(Float)
    process_id = Column(Integer)


class ProfileResultModel(Base):
    __tablename__ = "profile_results"
    __table_args__ = {'schema': 'tgapp'}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dk_id = Column(BigInteger)
    column_id = Column(PGUUID(as_uuid=True))
    project_code = Column(String(30))
    connection_id = Column(BigInteger)
    table_groups_id = Column(PGUUID(as_uuid=True))
    profile_run_id = Column(PGUUID(as_uuid=True))
    schema_name = Column(String(50))
    run_date = Column(TIMESTAMP)
    table_name = Column(String(120))
    position = Column(Integer)
    column_name = Column(String(120))
    column_type = Column(String(50))
    general_type = Column(String(1))
    record_ct = Column(BigInteger)
    value_ct = Column(BigInteger)
    distinct_value_ct = Column(BigInteger)
    distinct_std_value_ct = Column(BigInteger)
    null_value_ct = Column(BigInteger)
    min_length = Column(Integer)
    max_length = Column(Integer)
    avg_length = Column(Float)
    zero_value_ct = Column(BigInteger)
    zero_length_ct = Column(BigInteger)
    lead_space_ct = Column(BigInteger)
    quoted_value_ct = Column(BigInteger)
    includes_digit_ct = Column(BigInteger)
    filled_value_ct = Column(BigInteger)
    min_text = Column(String(1000))
    max_text = Column(String(1000))
    upper_case_ct = Column(BigInteger)
    lower_case_ct = Column(BigInteger)
    non_alpha_ct = Column(BigInteger)
    mixed_case_ct = Column(BigInteger)
    numeric_ct = Column(BigInteger)
    date_ct = Column(BigInteger)
    top_patterns = Column(String(1000))
    top_freq_values = Column(String(1500))
    distinct_value_hash = Column(String(40))
    min_value = Column(Float)
    min_value_over_0 = Column(Float)
    max_value = Column(Float)
    avg_value = Column(Float)
    stdev_value = Column(Float)
    percentile_25 = Column(Float)
    percentile_50 = Column(Float)
    percentile_75 = Column(Float)
    fractional_sum = Column(Numeric(38, 6))
    min_date = Column(TIMESTAMP)
    max_date = Column(TIMESTAMP)
    before_1yr_date_ct = Column(BigInteger)
    before_5yr_date_ct = Column(BigInteger)
    before_20yr_date_ct = Column(BigInteger)
    before_100yr_date_ct = Column(BigInteger)
    within_1yr_date_ct = Column(BigInteger)
    within_1mo_date_ct = Column(BigInteger)
    future_date_ct = Column(BigInteger)
    distant_future_date_ct = Column(BigInteger)
    date_days_present = Column(BigInteger)
    date_weeks_present = Column(BigInteger)
    date_months_present = Column(BigInteger)
    boolean_true_ct = Column(BigInteger)
    datatype_suggestion = Column(String(50))
    distinct_pattern_ct = Column(BigInteger)
    embedded_space_ct = Column(BigInteger)
    avg_embedded_spaces = Column(Float)
    std_pattern_match = Column(String(30))
    pii_flag = Column(String(50))
    functional_data_type = Column(String(50))
    functional_table_type = Column(String(50))
    sample_ratio = Column(Float)

class ScheduledProfilingJob(Base):
    __tablename__ = "scheduled_profiling_jobs"
    __table_args__ = {'schema': 'tgapp'}

    id = Column(Integer, primary_key=True, index=True)
    conn_id = Column(Integer, nullable=False)
    group_id = Column(String, nullable=False)
    schedule_cron_expression = Column(String, nullable=False)
    scheduled_job_id = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    
    #relationship
    table_group_details = relationship(
        "TableGroupModel",
        # Use primaryjoin to link group_id to TableGroupModel.id
        primaryjoin="foreign(ScheduledProfilingJob.group_id) == remote(TableGroupModel.id)",
        #back_populates="scheduled_jobs", 
        uselist=False # A single job likely corresponds to one table group
    )

# Define TestSuiteModel before TestRunModel as TestRunModel references it
class TestSuiteModel(Base):
    __tablename__ = "test_suites"
    __table_args__ = {'schema': 'tgapp'}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid()) # Use PGUUID and func.gen_random_uuid() for primary key
    test_suite = Column(String)
    table_groups_id = Column(PGUUID(as_uuid=True)) # Use PGUUID
    test_suite_description = Column(String)
    severity = Column(String)
    export_to_observability = Column(String)
    test_suite_schema = Column(String)
    component_key = Column(String)
    component_type = Column(String)
    component_name = Column(String)

    # Relationships
    table_group = relationship("TableGroupModel", primaryjoin="TestSuiteModel.table_groups_id == TableGroupModel.id", foreign_keys=[table_groups_id], backref="test_suites")
    test_runs = relationship("TestRunModel", back_populates="test_suite")


# Define TestRunModel now that TestSuiteModel is fully defined
class TestRunModel(Base):
    __tablename__ = "test_runs"
    __table_args__ = {'schema': 'tgapp'}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_suite_id = Column(PGUUID(as_uuid=True), ForeignKey("tgapp.test_suites.id"), nullable=False) # Use PGUUID and specify schema
    test_starttime = Column(TIMESTAMP)
    test_endtime = Column(TIMESTAMP)
    status = Column(String(100), default="Running")
    log_message = Column(String)
    duration = Column(String(50))
    test_ct = Column(Integer)
    passed_ct = Column(Integer)
    failed_ct = Column(Integer)
    warning_ct = Column(Integer)
    error_ct = Column(Integer)
    table_ct = Column(Integer)
    column_ct = Column(Integer)
    column_failed_ct = Column(Integer)
    column_warning_ct = Column(Integer)
    dq_affected_data_points = Column(BigInteger)
    dq_total_data_points = Column(BigInteger)
    dq_score_test_run = Column(Float)
    process_id = Column(Integer)

    # Relationships
    test_suite = relationship("TestSuiteModel", primaryjoin="TestRunModel.test_suite_id == TestSuiteModel.id", foreign_keys=[test_suite_id], back_populates="test_runs")

class TestTypeModel(Base):
    __tablename__ = "test_types"
    __table_args__ = {"schema": "tgapp"}

    
    # 'test_type' is the primary key based on your DDL
    id = Column(String) # This is just a regular column
    test_type = Column(String(200), primary_key=True, index=True) # This is the PK and used for linking
    test_name_short = Column(String(30))
    test_name_long = Column(String(100))
    test_description = Column(String(1000))
    except_message = Column(String(1000))
    measure_uom = Column(String(100))
    measure_uom_description = Column(String(200))
    selection_criteria = Column(String)
    dq_score_prevalence_formula = Column(String)
    dq_score_risk_factor = Column(String)
    column_name_prompt = Column(String)
    column_name_help = Column(String)
    default_parm_columns = Column(String)
    default_parm_values = Column(String)
    default_parm_prompts = Column(String)
    default_parm_help = Column(String)
    default_severity = Column(String(10))
    run_type = Column(String(10))
    test_scope = Column(String)
    dq_dimension = Column(String(50))
    health_dimension = Column(String(50))
    threshold_description = Column(String(200))
    usage_notes = Column(String)
    active = Column(String)

    # Define the relationship from TestType to TestResult
    # back_populates antey two sided osthade
    # Use primaryjoin to explicitly define the join condition
    test_results = relationship(
        "TestResultModel",
        primaryjoin="TestTypeModel.test_type == foreign(TestResultModel.test_type)",
        back_populates="test_type_details"
    )


class TestResultModel(Base):
    __tablename__ = 'test_results'
    __table_args__ = {'schema': 'tgapp'}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4) # Use PGUUID and default
    result_id = Column(Integer)
    test_type = Column(String)
    test_suite_id = Column(PGUUID(as_uuid=True)) # Use PGUUID. No ForeignKey here if not strictly enforced in DB
    test_definition_id = Column(PGUUID(as_uuid=True)) # Use PGUUID
    auto_gen = Column(Boolean)
    test_time = Column(TIMESTAMP)
    starttime = Column(TIMESTAMP)
    endtime = Column(TIMESTAMP)
    schema_name = Column(String)
    table_name = Column(String)
    column_names = Column(String)
    skip_errors = Column(Integer)
    input_parameters = Column(String)
    result_code = Column(Integer)
    severity = Column(String)
    result_status = Column(String)
    result_message = Column(String)
    result_measure = Column(String)
    threshold_value = Column(String)
    result_error_data = Column(String)
    test_action = Column(String)
    disposition = Column(String)
    subset_condition = Column(String)
    result_query = Column(String)
    test_description = Column(String)
    test_run_id = Column(PGUUID(as_uuid=True), ForeignKey('tgapp.test_runs.id')) # Use PGUUID and specify schema
    table_groups_id = Column(PGUUID(as_uuid=True), ForeignKey('tgapp.table_groups.id')) # Use PGUUID and specify schema
    dq_prevalence = Column(Float)
    dq_record_ct = Column(Integer)
    observability_status = Column(String)
    
    
    #relationships
    test_type_details = relationship(
        "TestTypeModel",
        primaryjoin="foreign(TestResultModel.test_type) == remote(TestTypeModel.test_type)",
        back_populates="test_results",
        uselist=False # Assuming one test result maps to one test type
    )



class AnomalyResultModel(Base):
    __tablename__ = 'profile_anomaly_results'
    __table_args__ = {'schema': 'tgapp'}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4) # Use PGUUID and default
    project_code = Column(String, nullable=False)
    table_groups_id = Column(PGUUID(as_uuid=True), ForeignKey('tgapp.table_groups.id'), nullable=False)
    profile_run_id = Column(PGUUID(as_uuid=True))
    column_id = Column(PGUUID(as_uuid=True), nullable=True)
    schema_name = Column(String, nullable=False)
    table_name = Column(String, nullable=False)
    column_name = Column(String, nullable=False)
    column_type = Column(String, nullable=False)
    anomaly_id = Column(Integer, nullable=False)
    detail = Column(String, nullable=True)
    disposition = Column(String, nullable=True)
    dq_prevalence = Column(Float, nullable=True)

class ProfileAnomalyTypeModel(Base):
    __tablename__ = "profile_anomaly_types"
    __table_args__ = {'schema': 'tgapp'}

    id = Column(String(10), primary_key=True, index=True)
    anomaly_type = Column(String(200), nullable=False)
    data_object = Column(String(10), nullable=True)
    anomaly_name = Column(String(100), nullable=True)
    anomaly_description = Column(String(500), nullable=True)
    anomaly_criteria = Column(String(2000), nullable=True)
    detail_expression = Column(String(2000), nullable=True)
    issue_likelihood = Column(String(50), nullable=True)
    suggested_action = Column(String(1000), nullable=True)
    dq_score_prevalence_formula = Column(String(1000), nullable=True)
    dq_score_risk_factor = Column(String, nullable=True)
    dq_dimension = Column(String(50), nullable=True)

    def __repr__(self):
        return (
            f"<ProfileAnomalyType(id='{self.id}', anomaly_name='{self.anomaly_name}', "
            f"dq_dimension='{self.dq_dimension}')>"
        )
        

class TestDefinitionModel(Base):
    __tablename__ = "test_definitions"
    __table_args__= {'schema': 'tgapp'}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cat_test_id = Column(BigInteger, primary_key=True, autoincrement=True)
    table_groups_id = Column(PGUUID(as_uuid=True))
    profile_run_id = Column(PGUUID(as_uuid=True))
    test_type = Column(String(200), nullable=False)
    test_suite_id = Column(PGUUID(as_uuid=True), ForeignKey("tgapp.test_suites.id"), nullable=False)
    test_description = Column(String(1000))
    test_action = Column(String(100))
    schema_name = Column(String(100))
    table_name = Column(String(100))
    column_name = Column(String(500))
    skip_errors = Column(Integer)
    baseline_ct = Column(String(1000))
    baseline_unique_ct = Column(String(1000))
    baseline_value = Column(String(1000))
    baseline_value_ct = Column(String(1000))
    threshold_value = Column(String(1000))
    baseline_sum = Column(String(1000))
    baseline_avg = Column(String(1000))
    baseline_sd = Column(String(1000))
    subset_condition = Column(String(500))
    groupby_names = Column(String(200))
    having_condition = Column(String(500))
    window_date_column = Column(String(100))
    window_days = Column(Integer)
    match_schema_name = Column(String(100))
    match_table_name = Column(String(100))
    match_column_names = Column(String(200))
    match_subset_condition = Column(String(500))
    match_groupby_names = Column(String(200))
    match_having_condition = Column(String(500))
    test_mode = Column(String(20))
    custom_query = Column(Text)
    test_active = Column(String(10), default='Y', nullable=False)
    test_definition_status = Column(String(200))
    severity = Column(String(10))
    watch_level = Column(String(10), default='WARN', nullable=False)
    check_result = Column(String(500))
    lock_refresh = Column(String(10), default='N', nullable=False)
    last_auto_gen_date = Column(TIMESTAMP)
    profiling_as_of_date = Column(TIMESTAMP)
    last_manual_update = Column(TIMESTAMP, default=None, onupdate=datetime.now)
    export_to_observability = Column(String(5))



def create_tables():
    # This function is for initial database setup.
    # If your schema 'tgapp' and tables already exist with data,
    # you should not run Base.metadata.create_all().
    print("Skipping table creation as schema 'tgapp' and tables are assumed to exist.")
    # Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
