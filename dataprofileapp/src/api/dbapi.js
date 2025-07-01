// import axiosInstance from 'axiosInstance';
import { baseURL } from '../utilities/constants';
import axiosInstance from '../utilities/axiosInstance';

const BASE_URL = baseURL;

export const connectionAction = async (data, actionType) => {
  try {
    const payload = {
      action: actionType,
      ...data,
    };
    const response = await axiosInstance.post(`${BASE_URL}/api/connections`, payload);
    return response.data;
  } catch (error) {
    console.error(`Error performing connection ${actionType}:`, error);
    throw error;
  }
};


export const getAllConnections = async () => {
  try {
    const response = await axiosInstance.get(`${BASE_URL}/api/connections`);
    return response.data;
  } catch (error) {
    console.error("Error getting all connections:", error);
    throw error;
  }
};

export const getConnectionById = async (id) => {
  try {
    const response = await axiosInstance.get(`${BASE_URL}/api/connections/${id}`);
    return response.data;
  } catch (error) {
    console.error("Error getting connection by ID:", error);
    throw error;
  }
};

export const updateConnection = async (id, data) => {
  try {
    const response = await axiosInstance.put(`${BASE_URL}/api/connections/${id}`, {
      project_code: data.project_code,
      connection_name: data.connection_name,
      connection_description: data.connection_description || null,
      sql_flavor: data.sql_flavor,
      project_host: data.project_host,
      project_port: data.project_port,
      project_user: data.project_user,
      password: data.password || undefined,
      project_db: data.project_db || null,
    });
    return response.data;
  } catch (error) {
    console.error("Error updating connection:", error);
    throw error;
  }
};

export const deleteConnection = async (id) => {
  try {
    const response = await axiosInstance.delete(`${BASE_URL}/api/connections/${id}`);
    return response.data;
  } catch (error) {
    console.error("Error deleting connection:", error);
    throw error;
  }
};

export const getConnectionProfiling = async (connection_id, connectionData) => {
  try {
    const response = await axiosInstance.post(`${BASE_URL}/api/connection/${connection_id}/profiling`, connectionData);
    return response.data;
  } catch (error) {
    console.error("Error fetching profiling data:", error);
    throw error;
  }
};

export const createTableGroup = async (connection_id, data) => {
  try {
    const response = await axiosInstance.post(`${baseURL}/api/connections/${connection_id}/table-groups`, {
      table_groups_name: data.table_groups_name,
      table_group_schema: data.table_group_schema || null,
      explicit_table_list: data.explicit_table_list,
      profiling_include_mask: data.profiling_include_mask || null,
      profiling_exclude_mask: data.profiling_exclude_mask || null,
      profile_id_column_mask: data.profile_id_column_mask || '%id',
      profile_sk_column_mask: data.profile_sk_column_mask || '%_sk',
      profile_use_sampling: data.profile_use_sampling || 'N',
      profile_sample_percent: data.profile_sample_percent || '30',
      profile_sample_min_count: data.profile_sample_min_count || 100000,
      profiling_delay_days: data.min_profiling_age_days ? String(data.min_profiling_age_days) : '0',
      profile_flag_cdes: data.profile_flag_cdes || true,
      profile_do_pair_rules: data.profile_do_pair_rules || 'N',
      profile_pair_rule_pct: data.profile_pair_rule_pct || 95,
      description: data.description || null,
      data_source: data.data_source || null,
      source_system: data.source_system || null,
      source_process: data.source_process || null,
      data_location: data.data_location || null,
      business_domain: data.business_domain || null,
      stakeholder_group: data.stakeholder_group || null,
      transform_level: data.transform_level || null,
      data_product: data.data_product || null,
      last_complete_profile_run_id: data.last_complete_profile_run_id || null,
      dq_score_profiling: data.dq_score_profiling || null,
      dq_score_testing: data.dq_score_testing || null,
    });
    return response.data;
  } catch (error) {
    console.error("Error creating table group:", error);
    throw error;
  }
};


export const getTableGroups = async (connection_id) => {
  try {
    const response = await axiosInstance.get(`${baseURL}/api/connections/${connection_id}/table-groups/`);
    return response.data;
  } catch (error) {
    console.error("Error fetching table groups:", error);
    throw error;
  }
};


export const getTableGroupById = async (connection_id, group_id) => {
  try {
    const response = await axiosInstance.get(`${baseURL}/api/connections/${connection_id}/table-groups/${group_id}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching specific table group:", error);
    throw error;
  }
};

export const getSpecificTableGroup = async (connection_id, group_id) => {
  try {
    const response = await axiosInstance.get(`${baseURL}/api/connections/${connection_id}/table-groups/${group_id}`);
    return response.data;
  } catch (error) {
    console.error(`Error getting table group ${group_id}:`, error);
    throw error;
  }
};


export const deleteTableGroup = async (connection_id, group_id) => {
  try {
    await axiosInstance.delete(`${baseURL}/api/connections/${connection_id}/table-groups/${group_id}`);
  } catch (error) {
    console.error("Error deleting table group:", error);
    throw error;
  }
};


export const triggerProfiling = async (requestPayload) => {
  try {
    console.log(
      `Attempting to trigger profiling for Connection ID: ${requestPayload.connection_id}, Table Group ID: ${requestPayload.table_group_id}`
    );

    const response = await axiosInstance.post(`${BASE_URL}/api/run-profiling`, {
      connection_id: requestPayload.connection_id,
      table_group_id: requestPayload.table_group_id,
    });

    console.log('Profiling trigger response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error triggering profiling job:', error);
    throw error;
  }
};



export const fetchDashboardSummary = async () => {
  const response = await axiosInstance.get(`${BASE_URL}/api/home`);
  return response.data;
};


export const fetchProfileResult = async (conn_id, group_id, profileresult_id) => {
  const response = await axiosInstance.get(
    `${BASE_URL}/api/connections/${conn_id}/table-groups/${group_id}/profiling-runs/${profileresult_id}/profile-results`
  );
  return response.data;
};


export const fetchLatestProfilingRun = async () => {
  const response = await axiosInstance.get(`${BASE_URL}/api/latest-profiling-run`);
  return response.data;
};


export const getDashboardOverview = async () => {
  try {
    const response = await axiosInstance.get(`${BASE_URL}/api/dashboard-overview`);
    // Axios already parses JSON into response.data
    return response.data;
  } catch (error) {
    console.error('Error fetching dashboard overview:', error);
    // If the error is an AxiosError, you can access response data from error.response.data
    if (error.response && error.response.data && error.response.data.detail) {
      throw new Error(error.response.data.detail || 'Failed to fetch dashboard overview');
    }
    throw error;
  }
};

export const getTableNamesForProfilingRun = async (runId) => {
  try {
    const response = await axiosInstance.get(`${BASE_URL}/api/profiling-runs/${runId}/table-names`);
    // Axios already parses JSON into response.data
    return response.data;
  } catch (error) {
    console.error(`Error fetching table names for run ${runId}:`, error);
    if (error.response && error.response.data && error.response.data.detail) {
      throw new Error(error.response.data.detail || `Failed to fetch table names for run ${runId}`);
    }
    throw error;
  }
};

export const getProfilingTableDetails = async (runId, tableName) => {
  try {
    const response = await axiosInstance.get(`${BASE_URL}/api/profiling-runs/${runId}/tables/${tableName}/details`);
    // Axios already parses JSON into response.data
    return response.data;
  } catch (error) {
    console.error(`Error fetching profiling details for table ${tableName} in run ${runId}:`, error);
    if (error.response && error.response.data && error.response.data.detail) {
      throw new Error(error.response.data.detail || `Failed to fetch profiling details for table ${tableName} in run ${runId}`);
    }
    throw error;
  }
};