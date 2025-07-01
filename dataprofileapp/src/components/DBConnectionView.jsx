import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
    getConnectionById,
    updateConnection,
    connectionAction,
    getTableGroups,
    getConnectionProfiling,
} from '../api/dbapi';
import DBConnectionForm from './DBConnectionForm';
import {
    MenuItem, FormControl, InputLabel, Select, CircularProgress,
    IconButton, Box, Typography, Button, Paper
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import { styled } from '@mui/material/styles';
import AddTableGroupModal from './AddTableGroupModal';

const StyledPaper = styled(Paper)(({ theme }) => ({
    padding: theme.spacing(2),
    backgroundColor: theme.palette.background.paper,
    color: theme.palette.text.primary,
}));

const DBConnectionView = () => {
    const { connection_id } = useParams();

    const [connectionData, setConnectionData] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [status, setStatus] = useState({});
    const [isLoadingConnection, setIsLoadingConnection] = useState(true);
    const [tableGroups, setTableGroups] = useState([]);
    const [selectedGroupId, setSelectedGroupId] = useState('');
    const [overviewData, setOverviewData] = useState(null);
    const [isFetchingOverview, setIsFetchingOverview] = useState(false);
    const [showAddTableGroupModal, setShowAddTableGroupModal] = useState(false);

    const transformToFormValues = (data) => {
        if (!data) return null;
        return {
            project_code: data.project_code || '',
            connection_name: data.connection_name || '',
            connection_description: data.connection_description || '',
            sql_flavor: data.sql_flavor || '',
            project_host: data.project_host || '',
            project_port: data.project_port || '',
            project_user: data.project_user || '',
            password: data.project_pw_encrypted || '',
            project_db: data.project_db || '',
        };
    };

    useEffect(() => {
        const fetchConnection = async () => {
            setIsLoadingConnection(true);
            try {
                const data = await getConnectionById(connection_id);
                setConnectionData(transformToFormValues(data));
            } catch (err) {
                setStatus({ type: 'error', message: 'Failed to load connection details.' });
            } finally {
                setIsLoadingConnection(false);
            }
        };
        if (connection_id) fetchConnection();
    }, [connection_id]);

    const fetchTableGroupsList = async () => {
        if (!connection_id) return setTableGroups([]);
        try {
            const groups = await getTableGroups(connection_id);
            setTableGroups(Array.isArray(groups) ? groups : []);
        } catch (err) {
            setStatus({ type: 'error', message: 'Failed to load table groups.' });
            setTableGroups([]);
        }
    };

    useEffect(() => {
        if (connection_id) fetchTableGroupsList();
    }, [connection_id]);

    const handleUpdate = async (values) => {
        setStatus({});
        try {
            const updatePayload = { ...values };
            await updateConnection(connection_id, updatePayload);
            setStatus({ type: 'success', message: 'Connection updated successfully' });
            setIsEditing(false);
            setConnectionData(transformToFormValues({ ...connectionData, ...values }));
        } catch (err) {
            const errorMessage = err.response?.data?.detail || err.message || 'Failed to update connection.';
            setStatus({ type: 'error', message: errorMessage });
        }
    };

    const handleTest = async (currentFormValues) => {
        setStatus({});
        // setTestStatus(null);
            try {
              const testPayload = {
                action: 'test',
                sql_flavor: values.sql_flavor,
                db_hostname: values.project_host, 
                db_port: parseInt(values.project_port, 10),
                user_id: values.project_user,
                password: values.password,
                project_db: values.project_db, 
              };
        
        
              const result = await connectionAction(testPayload, "test");
              if (result.status) {
                setStatus({ type: 'success', message: result.message });
              } else {
                setStatus({ type: 'error', message: result.message || 'Connection test failed.' });
              }
            } catch (error) {
              setStatus({ type: 'error', message: `Failed to connect to the database: ${error.message || 'Unknown error'}` });
            }
    };

    const handleOpenAddTableGroupModal = () => setShowAddTableGroupModal(true);
    const handleCloseAddTableGroupModal = () => {
        setShowAddTableGroupModal(false);
        fetchTableGroupsList();
    };

    const handleRunProfiling = async () => {
        if (!selectedGroupId) return setStatus({ type: 'error', message: 'Please select a table group.' });
        setIsFetchingOverview(true);
        try {
            const overview = await getConnectionProfiling(connection_id, selectedGroupId);
            setOverviewData(overview);
        } catch (err) {
            setStatus({ type: 'error', message: 'Failed to fetch profiling overview.' });
        } finally {
            setIsFetchingOverview(false);
        }
    };

    if (isLoadingConnection) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
                <CircularProgress color="primary" />
                <Typography variant="h6" color="white" ml={2}>Loading Connection...</Typography>
            </Box>
        );
    }

    if (!connectionData) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
                <Typography color="error">Failed to load connection details.</Typography>
            </Box>
        );
    }

    return (
        <Box display="flex" sx={{ width: '100%', height: 'calc(100vh - 64px)', overflow: 'auto' }}>
            <Box flexGrow={1} sx={{ overflow: 'auto', p: 2, mr: 2, maxWidth: '50%' }}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="h6" color="white">
                        {isEditing ? 'Edit Connection' : 'Connection Details'}
                    </Typography>
                    <IconButton onClick={() => setIsEditing(prev => !prev)} color="primary">
                        <EditIcon sx={{ color: '#fff' }} />
                    </IconButton>
                </Box>
                <StyledPaper sx={{ mb: 2, backgroundColor: '#1e1e1e', color: '#fff' }}>
                    <DBConnectionForm
                        initialValues={connectionData}
                        onSubmit={handleUpdate}
                        onTestConnection={handleTest}
                        isEditing={isEditing}
                        status={status}
                    />
                    {!isEditing && (
                        <Box mt={2} display="flex" gap={2} flexWrap="wrap">
                            <Button variant="outlined" color="primary" onClick={() => handleTest(connectionData)}>
                                Test Connection
                            </Button>
                            <Button variant="outlined" color="success" onClick={handleOpenAddTableGroupModal}>
                                + Add Table Group
                            </Button>
                        </Box>
                    )}
                    {status.message && (
                        <Box mt={2} p={2} bgcolor={status.type === 'success' ? 'success.dark' : 'error.dark'} color="white" borderRadius={1}>
                            <Typography>{status.message}</Typography>
                        </Box>
                    )}
                </StyledPaper>
            </Box>
            <Box flexGrow={1} sx={{ overflow: 'auto', p: 2 }}>
                <Typography variant="h6" color="white" mb={2}>Run Profiling</Typography>
                <FormControl fullWidth variant="outlined" sx={{ mb: 2 }}>
                    <InputLabel id="select-group-label">Select Table Group</InputLabel>
                    <Select
                        labelId="select-group-label"
                        value={selectedGroupId}
                        onChange={(e) => setSelectedGroupId(e.target.value)}
                        label="Select Table Group"
                    >
                        {tableGroups.map(group => (
                            <MenuItem key={group.id} value={group.id}>{group.name}</MenuItem>
                        ))}
                    </Select>
                </FormControl>
                <Button variant="contained" color="primary" onClick={handleRunProfiling} disabled={isFetchingOverview}>
                    {isFetchingOverview ? 'Running...' : 'Run'}
                </Button>
                {overviewData && (
                    <Box mt={3} bgcolor="#1e1e1e" p={2} borderRadius={1}>
                        <Typography variant="h6" color="white" mb={1}>Database Overview:</Typography>
                        {overviewData.status === 'failed' ? (
                            <Typography color="error">{overviewData.message}</Typography>
                        ) : (
                            <pre style={{ color: 'white', whiteSpace: 'pre-wrap' }}>{JSON.stringify(overviewData, null, 2)}</pre>
                        )}
                    </Box>
                )}
            </Box>
            {showAddTableGroupModal && (
                <AddTableGroupModal open={showAddTableGroupModal} onClose={handleCloseAddTableGroupModal} connectionId={connection_id} />
            )}
        </Box>
    );
};

export default DBConnectionView;
