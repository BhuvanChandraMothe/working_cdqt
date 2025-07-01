import React from 'react';
import {
    Box,
    Typography,
    CircularProgress,
    // Removed ArrowRightIcon from @mui/material import
} from '@mui/material';

// Import ArrowRightIcon from @mui/icons-material
import ArrowRightIcon from '@mui/icons-material/ArrowRight'; // Corrected import path


/**
 * Displays a table of data source connections.
 * @param {object} props - Component props.
 * @param {Array<object>} props.connections - Array of connection objects to display.
 * @param {boolean} props.loading - Loading state.
 * @param {object | null} props.error - Error object if fetching failed.
 * @param {function} props.getDatabaseImageSrc - Function to get the image source for a given SQL flavor.
 * @param {function} props.onConnectionClick - Handler for clicking a connection row. Receives connection ID.
 * @param {object} props.theme - The Material UI theme object for consistent styling.
 */
const DataSourcesTable = ({ connections, loading, error, getDatabaseImageSrc, onConnectionClick, theme }) => {
    return (
        <Box>
            {/* Table Header */}
            <Box sx={{ display: 'flex', borderBottom: `1px solid ${theme.palette.divider}`, pb: 0.5, mb: 0.5, color: theme.palette.text.secondary, fontSize: '0.8rem' }}>
                {/* Adjusted padding to align content under the image */}
                <Box sx={{ width: '30%', pl: '30px' }}>Name</Box>
                <Box sx={{ width: '20%' }}>Type</Box>
                <Box sx={{ width: '20%' }}>Project</Box>
                <Box sx={{ width: '20%' }}>Connection Details</Box>
                <Box sx={{ width: '10%', textAlign: 'right' }}></Box> {/* For arrow */}
            </Box>

            {/* Data Rows */}
            {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                    <CircularProgress size={20} />
                </Box>
            ) : error ? (
                <Box sx={{ color: theme.palette.error.main, textAlign: 'center', py: 2 }}>
                    Error loading connections.
                </Box>
            ) : connections.length === 0 ? (
                 <Box sx={{ textAlign: 'center', py: 2, color: theme.palette.text.secondary }}>
                    No connections found.
                </Box>
            ) : (
                connections.map((connection) => (
                    <Box
                        key={connection.id} // Use the unique 'id' from the API for the key
                        sx={{
                            display: 'flex',
                            alignItems: 'center',
                            py: 0.5,
                            borderBottom: `1px solid ${theme.palette.divider}`,
                            cursor: 'pointer',
                            '&:hover': {
                                bgcolor: theme.palette.action.hover, // Add hover effect
                            },
                        }}
                        // Attach click handler to navigate
                        onClick={() => onConnectionClick(connection.connection_id)} // Use connection_id for routing
                    >
                        {/* Name Column with Image Icon */}
                        <Box sx={{ width: '30%', display: 'flex', alignItems: 'center' }}>
                            <img
                                src={getDatabaseImageSrc(connection.sql_flavor)}
                                alt={`${connection.sql_flavor} Icon`}
                                style={{
                                    width: 20,
                                    height: 20,
                                    marginRight: 10,
                                    verticalAlign: 'middle', // Align image with text vertically
                                }}
                            />
                            {/* Display connection_name */}
                            <Typography variant="body2">{connection.connection_name}</Typography>
                        </Box>
                        {/* Type Column - Display sql_flavor */}
                        <Box sx={{ width: '20%' }}>
                            <Typography variant="body2">{connection.sql_flavor}</Typography>
                        </Box>
                        {/* Project Column - Display project_code */}
                        <Box sx={{ width: '20%' }}>
                            <Typography variant="body2">{connection.project_code}</Typography>
                        </Box>
                        {/* Connection Details Column - Display project_db */}
                        <Box sx={{ width: '20%' }}>
                            <Typography variant="body2">{connection.project_db}</Typography>
                        </Box>
                        {/* Arrow Icon for Navigation Hint */}
                        <Box sx={{ width: '10%', textAlign: 'right', color: theme.palette.text.secondary }}>
                            <ArrowRightIcon fontSize="small"/>
                        </Box>
                    </Box>
                ))
            )}
        </Box>
    );
};

export default DataSourcesTable;
