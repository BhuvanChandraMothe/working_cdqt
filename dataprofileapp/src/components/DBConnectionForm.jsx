import React, { useState } from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import {
    Container,
    Box,
    TextField,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    Button,
    IconButton,
    InputAdornment,
    FormHelperText,
    Paper,
    Typography,
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { styled, createTheme, ThemeProvider } from '@mui/material/styles';

// Assuming dark theme is provided elsewhere or imported
// import { createTheme, ThemeProvider } from '@mui/material/styles';
// const darkTheme = createTheme({ ... });

const darkTheme = createTheme({
    palette: {
        mode: 'dark',
        primary: {
            main: '#90caf9',
        },
        secondary: {
            main: '#f48fb1',
        },
        background: {
            default: '#121212',
            paper: '#1e1e1e',
        },
        text: {
            primary: '#fff',
            secondary: '#e0e0e0',
        },
        success: {
            main: '#4caf50',
            dark: '#388e3c',
        },
        error: {
            main: '#f44336',
            dark: '#d32f2f',
        },
    },
});


const StyledContainer = styled(Container)(({ theme }) => ({
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100vh', // This might make the form too large if used directly in a smaller container
    padding: theme.spacing(3),
    backgroundColor: theme.palette.background.default,
}));

const StyledPaper = styled(Paper)(({ theme }) => ({
    padding: theme.spacing(4),
    borderRadius: theme.shape.borderRadius,
    boxShadow: theme.shadows[8],
    width: '100%',
    maxWidth: 600, // Max width for the form container
}));

const StyledFormControl = styled(FormControl)({
    width: '100%',
    marginBottom: '1.5rem',
});

const StyledTextField = styled(TextField)(({ theme }) => ({
    '& label': {
        color: theme.palette.text.secondary,
    },
    '& label.Mui-focused': {
        color: theme.palette.primary.main,
    },
    '& .MuiOutlinedInput-root': {
        '& fieldset': {
            borderColor: theme.palette.divider,
        },
        '&:hover fieldset': {
            borderColor: theme.palette.primary.light,
        },
        '&.Mui-focused fieldset': {
            borderColor: theme.palette.primary.main,
        },
        '& input': {
            color: theme.palette.text.primary,
        },
    },
}));

const StyledSelect = styled(Select)(({ theme }) => ({
    '& .MuiOutlinedInput-notchedOutline': {
        borderColor: theme.palette.divider, // Default border color
    },
    '&:hover .MuiOutlinedInput-notchedOutline': {
        borderColor: theme.palette.primary.light, // Hover border color
    },
    '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
        borderColor: theme.palette.primary.main, // Focused border color
    },
    '& .MuiSelect-select': {
        color: theme.palette.text.primary, // Selected value color
    },
    '& .MuiSvgIcon-root': {
        color: theme.palette.text.secondary, // Dropdown arrow color
    },
    '&.Mui-disabled .MuiOutlinedInput-notchedOutline': {
        borderColor: theme.palette.action.disabledBackground, // Disabled border color
    },
    '&.Mui-disabled .MuiSelect-select': {
        color: theme.palette.action.disabled, // Disabled text color
    },
    '&.Mui-disabled .MuiSvgIcon-root': {
        color: theme.palette.action.disabled, // Disabled arrow color
    },
}));


const StyledMenuItem = styled(MenuItem)(({ theme }) => ({
    color: theme.palette.text.primary,
}));


const StyledButton = styled(Button)(({ theme }) => ({
    marginTop: theme.spacing(3),
    padding: theme.spacing(1.5, 3),
    borderRadius: theme.shape.borderRadius,
    fontWeight: 'bold',
}));

const StyledMessage = styled(Box)(({ theme, type }) => ({
    marginTop: theme.spacing(2),
    padding: theme.spacing(2),
    borderRadius: theme.shape.borderRadius,
    fontSize: '0.9rem',
    color: theme.palette.text.primary,
    backgroundColor: type === 'success'
        ? theme.palette.success.dark
        : theme.palette.error.dark,
}));

// Define supported database types for the Select dropdown
const SUPPORTED_DB_TYPES_FOR_SELECT = [
    "PostgreSQL",
    "MSSQL",
    "Oracle",
    "SQL Server",
    "Snowflake",
    "Redshift"
];


const DBConnectionForm = ({ initialValues, onSubmit, isEditing, onTestConnection, status }) => {
    const [showPassword, setShowPassword] = useState(false);

    // Toggle password visibility, but only if editing is enabled
    const togglePasswordVisibility = () => {
        if (!isEditing) return; // Only allow toggling if in edit mode
        setShowPassword((prev) => !prev);
    };

    // Define the validation schema using Yup
    // Updated field names and validation based on Pydantic models and SQL schema
    const validationSchema = Yup.object({
        // project_code is required for creation, but might be optional for update depending on backend logic
        // Assuming it's required for the form itself if present in initialValues
        project_code: Yup.string().required('Project Code is required'),
        connection_name: Yup.string().required('Connection Name is required'),
        connection_description: Yup.string(), // Description is optional in SQL schema
        sql_flavor: Yup.string().required('Database Type is required'),
        project_host: Yup.string().required('Hostname is required'),
        // project_port is VARCHAR(5) in SQL, Pydantic model is string. Validate as string.
        project_port: Yup.string().required('Port is required'),
        project_user: Yup.string().required('User ID is required'),
        // Password is required for creation. For update, it might be optional if not changed.
        // The form requires it here, but the parent component handles sending it only if updated.
        password: Yup.string().required('Password is required'),
        project_db: Yup.string().required('Please specify the database'), // Database Name is optional in SQL schema
        // Add validation for other fields if included in initialValues
        // max_threads: Yup.number().integer().min(1).nullable(),
        // ...
    });

    return (
        // ThemeProvider is likely provided by a parent component like DBConnectionView
        // or App. Keeping it here for self-containment if needed, but can be removed
        // if a parent provides it.
        <ThemeProvider theme={darkTheme}>
            {/* StyledContainer might not be needed if this component is placed inside another layout */}
            {/* <StyledContainer> */}
            <StyledPaper>
                {/* Heading for the form */}
                <Typography variant="h5" component="h5" align="center" sx={{ mb: 3 }}>
                    {isEditing ? 'Edit Connection' : 'Connection Details'}
                </Typography>
                {/* Formik wrapper for form state management and validation */}
                <Formik
                    initialValues={initialValues} // Initial values passed from parent (DBConnectionView)
                    enableReinitialize // Re-initialize form when initialValues change (important for edit mode)
                    validationSchema={validationSchema} // Apply validation schema
                    onSubmit={onSubmit} // Call the onSubmit function passed from parent (handleUpdate or handleSave)
                >
                    {({ values, isSubmitting }) => (
                        <Form>
                            {/* Project Code Field */}
                            <StyledFormControl>
                                <Field
                                    as={StyledTextField}
                                    name="project_code" // Matches Pydantic/SQL field name
                                    placeholder="Enter Project Code"
                                    variant="outlined"
                                    fullWidth
                                    disabled={!isEditing} // Disable if not in edit mode
                                />
                                <ErrorMessage name="project_code" component={FormHelperText} error />
                            </StyledFormControl>

                            {/* Connection Name Field */}
                            <StyledFormControl>
                                <Field
                                    as={StyledTextField}
                                    name="connection_name" // Matches Pydantic/SQL field name
                                    placeholder="Enter Connection Name"
                                    variant="outlined"
                                    fullWidth
                                    disabled={!isEditing}
                                />
                                <ErrorMessage name="connection_name" component={FormHelperText} error />
                            </StyledFormControl>

                            {/* Description Field */}
                            <StyledFormControl>
                                <Field
                                    as={StyledTextField}
                                    name="connection_description" // Matches Pydantic/SQL field name
                                    placeholder="Enter Description"
                                    variant="outlined"
                                    fullWidth
                                    multiline
                                    rows={2}
                                    disabled={!isEditing}
                                />
                                <ErrorMessage name="connection_description" component={FormHelperText} error />
                            </StyledFormControl>

                            {/* Database Type Select */}
                            <StyledFormControl>
                                <Field
                                    as={StyledSelect}
                                    name="sql_flavor" // Matches Pydantic/SQL field name
                                    fullWidth
                                    displayEmpty // Allows placeholder
                                    disabled={!isEditing}
                                    // InputLabel is often preferred over placeholder for Select
                                    // <InputLabel id="sql-flavor-label">Database Type</InputLabel>
                                    // labelId="sql-flavor-label" // Link label to select
                                >
                                    <MenuItem value="" disabled> {/* Placeholder item */}
                                        Select Database Type
                                    </MenuItem>
                                    {/* Map supported database types to MenuItem components */}
                                    {SUPPORTED_DB_TYPES_FOR_SELECT.map((type) => (
                                        <MenuItem key={type} value={type}>{type}</MenuItem>
                                    ))}
                                </Field>
                                <ErrorMessage name="sql_flavor" component={FormHelperText} error />
                            </StyledFormControl>

                            {/* Hostname Field */}
                            <StyledFormControl>
                                <Field
                                    as={StyledTextField}
                                    name="project_host" // Matches Pydantic/SQL field name
                                    placeholder="Enter Hostname"
                                    variant="outlined"
                                    fullWidth
                                    disabled={!isEditing}
                                />
                                <ErrorMessage name="project_host" component={FormHelperText} error />
                            </StyledFormControl>

                            {/* Port Field */}
                            <StyledFormControl>
                                <Field
                                    as={StyledTextField}
                                    name="project_port" // Matches Pydantic/SQL field name
                                    placeholder="Enter Port"
                                    variant="outlined"
                                    fullWidth
                                    disabled={!isEditing}
                                    // type="number" // Keep as text input because SQL column is VARCHAR(5)
                                />
                                <ErrorMessage name="project_port" component={FormHelperText} error />
                            </StyledFormControl>

                            {/* User ID Field */}
                            <StyledFormControl>
                                <Field
                                    as={StyledTextField}
                                    name="project_user" // Matches Pydantic/SQL field name
                                    placeholder="Enter User ID"
                                    variant="outlined"
                                    fullWidth
                                    disabled={!isEditing}
                                />
                                <ErrorMessage name="project_user" component={FormHelperText} error />
                            </StyledFormControl>

                            {/* Password Field */}
                            <StyledFormControl>
                                <Field
                                    as={StyledTextField}
                                    name="password" // Matches Pydantic/SQL field name (input field)
                                    placeholder="Enter Password"
                                    type={showPassword ? 'text' : 'password'}
                                    variant="outlined"
                                    fullWidth
                                    disabled={!isEditing}
                                    InputProps={{
                                        endAdornment: (
                                            <InputAdornment position="end">
                                                <IconButton
                                                    onClick={togglePasswordVisibility}
                                                    edge="end"
                                                    disabled={!isEditing} // Disable button if not in edit mode
                                                >
                                                    {showPassword ? <VisibilityOff /> : <Visibility />}
                                                </IconButton>
                                            </InputAdornment>
                                        ),
                                    }}
                                />
                                <ErrorMessage name="password" component={FormHelperText} error />
                            </StyledFormControl>

                            {/* Database Name Field */}
                            <StyledFormControl>
                                <Field
                                    as={StyledTextField}
                                    name="project_db" // Matches Pydantic/SQL field name
                                    placeholder="Enter Database Name"
                                    variant="outlined"
                                    fullWidth
                                    disabled={!isEditing}
                                />
                                <ErrorMessage name="project_db" component={FormHelperText} error />
                            </StyledFormControl>


                            {/* Action buttons shown only when editing */}
                            {isEditing && (
                                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}> {/* Added flexWrap */}
                                    {/* Test Connection Button */}
                                    {/* Calls onTestConnection prop with current form values */}
                                    <StyledButton
                                        variant="contained"
                                        color="primary"
                                        onClick={() => onTestConnection(values)}
                                        disabled={isSubmitting}
                                    >
                                        Test Connection
                                    </StyledButton>
                                    {/* Submit Button (Update/Save) */}
                                    {/* Triggers Formik's onSubmit (which calls the onSubmit prop) */}
                                    <StyledButton
                                        type="submit"
                                        variant="contained"
                                        color="secondary"
                                        disabled={isSubmitting}
                                    >
                                        {/* Button text changes based on isEditing */}
                                        {isEditing ? 'Update Connection' : 'Save Connection'}
                                    </StyledButton>
                                </Box>
                            )}

                            {/* Display status message if available */}
                            {status?.message && (
                                <StyledMessage type={status.type}>{status.message}</StyledMessage>
                            )}
                        </Form>
                    )}
                </Formik>
            </StyledPaper>
            {/* </StyledContainer> */}
        </ThemeProvider>
    );
};

export default DBConnectionForm;

