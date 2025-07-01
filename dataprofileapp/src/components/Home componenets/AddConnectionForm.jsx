import React, { useState } from 'react';
import {
    TextField,
    Grid,
    Box,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Button,
    Typography, // Added Typography for the title within the form
    CircularProgress // Import CircularProgress
} from '@mui/material';

// Import API functions from your dbapi file
import { connectionAction } from '../../api/dbapi';

// Assuming you have a list of supported database types
const supportedDatabaseTypes = [
    'PostgreSQL',
    'MySQL',
    'SQLite',
    'Oracle',
    'SQL Server',
    'MongoDB',
    'Snowflake',
    'Redshift',
    'Other Database',
];

/**
 * A form component for adding a new database connection.
 * Manages form state and calls provided handlers for actions.
 * @param {object} props - Component props.
 * @param {function} props.onCancel - Handler for the Cancel button.
 * @param {function} [props.onConnectionCreated] - Optional handler to call after a connection is successfully created (e.g., to refresh the list).
 */
const AddConnectionForm = ({ onCancel, onConnectionCreated }) => {
    // State to manage form input values
    const [formData, setFormData] = useState({
        connection_name: '',
        sql_flavor: '', // Corresponds to Database Type
        project_port: '', // Corresponds to Port
        project_host: '', // Corresponds to Host
        project_db: '', // Corresponds to Database
        project_user: '', // Corresponds to Username
        password: '', // Corresponds to Password
        connection_description: '', // Corresponds to Description
        project_code: '', // Assuming project_code is needed for creation
    });

    // State to manage loading and error states for API calls
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [testResult, setTestResult] = useState(null); // State to store test connection result

    // Handle input changes
    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prevData => ({
            ...prevData,
            [name]: value
        }));
    };

    // Handle form submission for Create
    const handleSubmitCreate = async (e) => {
        e.preventDefault(); // Prevent default form submission
        setLoading(true);
        setError(null);
        setTestResult(null); // Clear previous test results

        setSaveStatus(null);
        try {
            const savePayload = {
                action: "create",
                sql_flavor: values.sql_flavor,
                db_hostname: values.project_host,
                db_port: parseInt(values.project_port, 10),
                user_id: values.project_user,
                password: values.password,
                project_db: values.project_db || null,

                // Additional optional fields from ConnectionActionRequest
                project_code: values.project_code || null,
                connection_name: values.connection_name || null,
                connection_description: values.connection_description || null,
                max_query_chars: values.max_query_chars || null,
                url: values.url || null,
                connect_by_url: values.connect_by_url || false,
                connect_by_key: values.connect_by_key || false,
                private_key: values.private_key || null,
                private_key_passphrase: values.private_key_passphrase || null,
                http_path: values.http_path || null,
            };

            const saved = await connectionAction(savePayload, "create");
            setSaveStatus({ type: 'success', message: 'Connection saved successfully!', savedConnectionId: saved.connection_id });
            setSavedConnectionData(saved);
            if (onConnectionSaved) onConnectionSaved(saved);
            resetForm();
            setTestStatus(null);
            setOverviewData(null);
        } catch (error) {
            const errorDetail = error.response?.data?.detail;
            const formattedError =
                Array.isArray(errorDetail)
                    ? errorDetail.map(err => `${err.loc.join('.')}: ${err.msg}`).join(', ')
                    : errorDetail || error.message || 'Failed to save connection.';

            setSaveStatus({ type: 'error', message: formattedError });

        }
    };

    // Handle form submission for Test Connection
    const handleSubmitTest = async (e) => {
        e.preventDefault(); // Prevent default form submission
        setLoading(true);
        setError(null);
        setTestResult(null); // Clear previous test results
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
                setTestStatus({ type: 'success', message: result.message });
            } else {
                setTestStatus({ type: 'error', message: result.message || 'Connection test failed.' });
            }
        } catch (error) {
            setTestStatus({ type: 'error', message: `Failed to connect to the database: ${error.message || 'Unknown error'}` });
        }
    };


    return (
        <Box component="form" onSubmit={handleSubmitCreate} noValidate autoComplete="off">
            {/* Note: The CloseIcon is handled in the parent (HomepageLayout) */}
            <Typography variant="h6" mb={2}>Add Connection</Typography> {/* Added title here */}

            <TextField
                fullWidth
                label="Connection Name"
                variant="outlined"
                margin="normal"
                size="small"
                name="connection_name"
                value={formData.connection_name}
                onChange={handleInputChange}
                disabled={loading}
            />
            <FormControl fullWidth margin="normal" size="small" disabled={loading}>
                <InputLabel id="database-type-label">Database Type</InputLabel>
                <Select
                    labelId="database-type-label"
                    id="database-type"
                    value={formData.sql_flavor}
                    label="Database Type"
                    onChange={handleInputChange}
                    name="sql_flavor"
                >
                    {supportedDatabaseTypes.map(type => (
                        <MenuItem key={type} value={type}>{type}</MenuItem>
                    ))}
                </Select>
            </FormControl >
            <Grid container spacing={4} mb={2}>
                {/* Assuming 'Sort' label is actually 'Port' based on typical connection details */}
                <Grid item xs={6}>
                    <TextField
                        fullWidth
                        label="Port" // Changed label to Port
                        variant="outlined"
                        size="small"
                        name="project_port"
                        value={formData.project_port}
                        onChange={handleInputChange}
                        type="number" // Assuming port is a number
                        disabled={loading}
                    />
                </Grid>
                <Grid item xs={6}>
                    {/* This field seems redundant based on the screenshot, keeping it for now but might need clarification */}
                    {/* <TextField fullWidth label="5432" variant="outlined" size="small" disabled/> */}
                </Grid>
            </Grid>
            <Grid container spacing={2} mb={2}>
                <Grid item xs={6}>
                    <TextField
                        fullWidth
                        label="Host"
                        variant="outlined"
                        size="small"
                        name="project_host"
                        value={formData.project_host}
                        onChange={handleInputChange}
                        disabled={loading}
                    />
                </Grid>
                <Grid item xs={6}>
                    <TextField
                        fullWidth
                        label="Database"
                        variant="outlined"
                        size="small"
                        name="project_db"
                        value={formData.project_db}
                        onChange={handleInputChange}
                        disabled={loading}
                    />
                </Grid>
            </Grid>
            {/* Assuming Project Code is needed for creation based on your dbapi */}
            <TextField
                fullWidth
                label="Project Code"
                variant="outlined"
                margin="normal"
                size="small"
                name="project_code"
                value={formData.project_code}
                onChange={handleInputChange}
                disabled={loading}
            />
            <TextField
                fullWidth
                label="Username"
                variant="outlined"
                margin="normal"
                size="small"
                name="project_user"
                value={formData.project_user}
                onChange={handleInputChange}
                disabled={loading}
            />
            <TextField
                fullWidth
                label="Password"
                type="password"
                variant="outlined"
                margin="normal"
                size="small"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                disabled={loading}
            />
            <TextField
                fullWidth
                label="Description"
                multiline
                rows={2}
                variant="outlined"
                margin="normal"
                size="small"
                name="connection_description"
                value={formData.connection_description}
                onChange={handleInputChange}
                disabled={loading}
            />

            {/* Display loading, error, or test result messages */}
            {loading && (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                    <CircularProgress size={20} />
                    <Typography variant="body2" color="textSecondary" sx={{ ml: 1 }}>
                        {testResult ? 'Testing...' : 'Creating...'}
                    </Typography>
                </Box>
            )}
            {error && (
                <Typography variant="body2" color="error" sx={{ mt: 2 }}>
                    Error: {error.message || 'An unexpected error occurred.'}
                </Typography>
            )}
            {testResult && !loading && (
                <Typography variant="body2" color={testResult.status === true ? 'success.main' : 'error.main'} sx={{ mt: 2 }}>
                    Test Result: {testResult.status === true ? 'Successful' : 'Failed'} - {testResult.message}
                </Typography>
            )}


            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
                <Button variant="outlined" size="small" onClick={onCancel} disabled={loading}>Cancel</Button>
                {/* Use type="button" to prevent this button from submitting the form */}
                <Button variant="contained" size="small" onClick={handleSubmitTest} type="button" disabled={loading}>Test Connection</Button>
                {/* This button will trigger the form's onSubmit */}
                <Button variant="contained" size="small" type="submit" disabled={loading}>Create</Button>
            </Box>
        </Box>
    );
};

export default AddConnectionForm;
