import React, { useState, useEffect, useMemo, useCallback } from 'react'; // Added useCallback
import { useNavigate } from 'react-router-dom';

// Import your API functions from your dbapi file
import { getAllConnections, getDashboardOverview, connectionAction } from '../api/dbapi'; // Added getDashboardOverview

// Import your SVG icon files
import postgresIcon from '../assets/postgres.svg';
import mysqlIcon from '../assets/mssql.svg';
import sqliteIcon from '../assets/mssql.svg'; // Note: using mssql.svg for sqlite
import oracleIcon from '../assets/oracle.svg';
import sqlserverIcon from '../assets/mssql.svg'; // Note: using mssql.svg for sqlserver
import mongodbIcon from '../assets/postgres.svg'; // Note: using postgres.svg for mongodb
import snowflakeIcon from '../assets/snowflake.svg';
import redshiftIcon from '../assets/redshift .svg'; // Corrected potential typo in filename
import defaultDatabaseIcon from '../assets/postgres.svg';

import {
    CssBaseline,
    Paper,
    Typography,
    Button,
    IconButton,
    Grid,
    Box,
    Switch,
    createTheme,
    ThemeProvider,
    CircularProgress
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import AddIcon from '@mui/icons-material/Add';

// Import the new components
import AddConnectionForm from './Home componenets/AddConnectionForm';
import SchemaProfilingControls from './Home componenets/SchemaProfilingControls';
import DataSourcesTable from './Home componenets/DataSourcesTable';
import TestCasesList from './Home componenets/TestCasesList';
// import ProfileRunDisplay from './Home componenets/ProfileRunDisplay'; // <--- REMOVED THIS IMPORT
import ProfileRunResults from './Home componenets/ProfileRunResults'; // <--- NEW IMPORT
import ProfileRunDetails from './Home componenets/ProfileRunDetails'; // <--- NEW IMPORT


const getDesignTokens = (mode) => ({
    palette: {
        mode,
        ...(mode === 'light'
            ? {
                primary: { main: '#1976d2' },
                secondary: { main: '#dc004e' },
                background: { default: '#f0f2f5', paper: '#fff' },
                text: { primary: 'rgba(0, 0, 0, 0.87)', secondary: 'rgba(0, 0, 0, 0.6)' },
                status: { connected: '#4caf50', notConnected: '#f44336', saliented: '#ff9800' },
            }
            : {
                primary: { main: '#90caf9' },
                secondary: { main: '#f48fb1' },
                background: { default: '#121212', paper: '#1e1e1e' },
                text: { primary: '#fff', secondary: 'rgba(255, 255, 255, 0.7)' },
                status: { connected: '#81c784', notConnected: '#e57373', saliented: '#ffb74d' },
            }),
    },
});

const useMemoizedTheme = (mode) => useMemo(() => createTheme(getDesignTokens(mode)), [mode]);

const DatabaseTypeImages = {
    "PostgreSQL": postgresIcon,
    "MySQL": mysqlIcon,
    "SQLite": sqliteIcon,
    "Oracle": oracleIcon,
    "SQL Server": sqlserverIcon,
    "MongoDB": mongodbIcon,
    "Snowflake": snowflakeIcon,
    "Redshift": redshiftIcon,
    "default": defaultDatabaseIcon,
};

const getDatabaseImageSrc = (sqlFlavor) => {
    return DatabaseTypeImages.hasOwnProperty(sqlFlavor) && DatabaseTypeImages[sqlFlavor] ? DatabaseTypeImages[sqlFlavor] : DatabaseTypeImages.default;
};


const HomepageLayout = () => {
    const navigate = useNavigate();
    const [mode, setMode] = useState(() => localStorage.getItem('themeMode') === 'light' ? 'light' : 'dark');
    const [connections, setConnections] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const [showAddConnectionForm, setShowAddConnectionForm] = useState(false);
    const [schemaProfilingData, setSchemaProfilingData] = useState({ connections: [], schemas: [], tables: [] });
    const [testCasesData, setTestCasesData] = useState([]);

    // State for Profile Run Display components
    const [selectedRunId, setSelectedRunId] = useState(null);
    const [selectedTableName, setSelectedTableName] = useState('');


    useEffect(() => {
        localStorage.setItem('themeMode', mode);
    }, [mode]);

    useEffect(() => {
        const fetchConnections = async () => {
            try {
                setLoading(true);
                const data = await getAllConnections();
                setConnections(data);
                setSchemaProfilingData(prevData => ({ ...prevData, connections: data }));
                setError(null);
            } catch (err) {
                setError(err);
                console.error("Failed to fetch connections:", err);
            } finally {
                setLoading(false);
            }
        };

        const fetchInitialRun = async () => {
            try {
                const data = await getDashboardOverview();
                if (data.recentRuns && data.recentRuns.length > 0) {
                    setSelectedRunId(data.recentRuns[0].profiling_id);
                }
            } catch (error) {
                console.error('Error fetching initial dashboard overview for HomeLayout:', error);
            }
        };

        fetchConnections();
        fetchInitialRun(); // Fetch initial run to set a default
    }, []);

    const theme = useMemoizedTheme(mode);

    const handleThemeToggle = () => {
        setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
    };

    const handleAddConnectionClick = () => {
        setShowAddConnectionForm(true);
    };

    const handleCloseAddConnectionForm = () => {
        setShowAddConnectionForm(false);
    };

    const handleCreateConnection = async (formData) => {
        console.log('Attempting to create connection with data:', formData);
        try {
            const newConnection = await connectionAction(formData);
            console.log('Connection created successfully:', newConnection);
            const updatedConnections = await getAllConnections();
            setConnections(updatedConnections);
            setSchemaProfilingData(prevData => ({ ...prevData, connections: updatedConnections }));
            setShowAddConnectionForm(false);
        } catch (err) {
            console.error('Error creating connection:', err);
            alert(`Error creating connection: ${err.message}`);
        }
    };

    const handleTestConnection = async (formData) => {
        console.log('Attempting to test connection with data:', formData);
        try {
            const testResult = await connectionAction(formData);
            console.log('Test connection result:', testResult);
            alert(`Connection Test Result: ${testResult.status === 'success' ? 'Successful' : 'Failed'}\nMessage: ${testResult.message}`);
        } catch (err) {
            console.error('Error testing connection:', err);
            alert(`Connection Test Failed: ${err.message}`);
        }
    };

    const handleConnectionRowClick = (connectionId) => {
        console.log('Connection row clicked, navigating to details:', connectionId);
        navigate(`/connection/${connectionId}`);
    };

    const handleSchemaProfilingCancel = () => {
        console.log('Schema Profiling Cancel clicked');
    };

    const handleSchemaProfilingTest = () => {
        console.log('Schema Profiling Test Connection clicked');
    };

    const handleSchemaTableClick = (itemDetails) => {
        console.log('Schema Table item clicked:', itemDetails);
    };

    const handleAddTestCase = () => {
        console.log('Add Test Case clicked');
    };

    const handleTestCaseClick = (itemDetails) => {
        console.log('Test Case item clicked:', itemDetails);
    };

    // Callbacks for ProfileRunResults and ProfileRunDetails
    const handleSelectRun = useCallback((runId) => {
        setSelectedRunId(runId);
        // Reset selected table when a new run is selected
        setSelectedTableName('');
    }, []);

    const handleSelectTableName = useCallback((tableName) => {
        setSelectedTableName(tableName);
    }, []);


    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <Box sx={{ p: 3, minHeight: '100vh', bgcolor: theme.palette.background.default }}>
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
                    <Typography variant="body2" color="text.primary" sx={{ mr: 1 }}>
                        {mode === 'dark' ? 'Dark Mode' : 'Light Mode'}
                    </Typography>
                    <Switch
                        checked={mode === 'dark'}
                        onChange={handleThemeToggle}
                        color="primary"
                        inputProps={{ 'aria-label': 'theme toggle switch' }}
                    />
                </Box>

                <Box
                    sx={{
                        display: 'flex',
                        flexWrap: 'wrap',
                        gap: 3,
                        justifyContent: 'center',
                        maxWidth: 'lg',
                        mx: 'auto',
                    }}
                >



                    {/* Profile Run Results Component (Left Panel) */}
                    <Grid item xs={12} md={6} sx={{ flexGrow: 1, flexBasis: 'min(400px, 100%)' }}>
                        <ProfileRunResults
                            onSelectRun={handleSelectRun}
                            selectedRunId={selectedRunId}
                        />
                    </Grid>

                    {/* Profile Run Details Component (Right Panel) */}
                    <Grid item xs={12} md={6} sx={{ flexGrow: 1, flexBasis: 'min(400px, 100%)' }}>
                        <ProfileRunDetails
                            selectedRunId={selectedRunId}
                            selectedTableName={selectedTableName}
                            onSelectTableName={handleSelectTableName}
                        />
                    </Grid>
                    
                    {/* Data Sources Card */}
                    <Grid item xs={12} sm={6} md={5} lg={4.5} sx={{ flexGrow: 1, flexBasis: 'min(400px, 100%)' }}>
                        <Paper sx={{ p: 2, height: '100%' }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                                <Typography variant="h6">Data Sources</Typography>
                                <Button variant="contained" startIcon={<AddIcon />} size="small" onClick={handleAddConnectionClick}>
                                    Add Connection
                                </Button>
                            </Box>
                            <DataSourcesTable
                                connections={connections}
                                loading={loading}
                                error={error}
                                getDatabaseImageSrc={getDatabaseImageSrc}
                                onConnectionClick={handleConnectionRowClick}
                                theme={theme}
                            />
                        </Paper>
                    </Grid>

                    {/* Add Connection Card */}
                    {showAddConnectionForm && (
                        <Grid item xs={12} sm={6} md={7} lg={6.5} sx={{ flexGrow: 1, flexBasis: 'min(500px, 100%)' }}>
                            <Paper sx={{ p: 2, position: 'relative', height: '100%' }}>
                                <IconButton aria-label="close" sx={{ position: 'absolute', top: 8, right: 8 }} onClick={handleCloseAddConnectionForm}>
                                    <CloseIcon />
                                </IconButton>
                                <AddConnectionForm
                                    onCancel={handleCloseAddConnectionForm}
                                    onTestConnection={handleTestConnection}
                                    onCreateConnection={handleCreateConnection}
                                />
                            </Paper>
                        </Grid>
                    )}

                    {/* Schema Profiling Card */}
                    <Grid item xs={12} sm={6} md={7} lg={6.5} sx={{ flexGrow: 1, flexBasis: 'min(500px, 100%)' }}>
                        <Paper sx={{ p: 2, position: 'relative', height: '100%' }}>
                            <SchemaProfilingControls
                                onTestConnection={handleSchemaProfilingTest}
                                onTableItemClick={handleSchemaTableClick}
                                theme={theme}
                                connections={schemaProfilingData.connections}
                                schemas={schemaProfilingData.schemas}
                                tables={schemaProfilingData.tables}
                            />
                        </Paper>
                    </Grid>

                    

                    {/* Test Cases Card */}
                    <Grid item xs={12} sm={6} md={5} lg={4.5} sx={{ flexGrow: 1, flexBasis: 'min(400px, 100%)' }}>
                        <Paper sx={{ p: 2, height: '100%' }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                                <Typography variant="h6">Test Cases</Typography>
                                <Button variant="contained" startIcon={<AddIcon />} size="small" onClick={handleAddTestCase}>
                                    Add Test Case
                                </Button>
                            </Box>
                            <TestCasesList
                                testCases={testCasesData}
                                onItemClick={handleTestCaseClick}
                                theme={theme}
                            />
                        </Paper>
                    </Grid>
                </Box>
            </Box>
        </ThemeProvider>
    );
};

export default HomepageLayout;