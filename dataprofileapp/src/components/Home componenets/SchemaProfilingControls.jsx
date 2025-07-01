import React, { useState } from 'react';
import {
    Box,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Typography,
    Button,
    // Removed icons from @mui/material import
} from '@mui/material';

// Import icons from @mui/icons-material
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ChevronRightIcon from '@mui/icons-material/ChevronRight'; // Corrected import path


const SchemaProfilingControls = ({ onCancel, onTestConnection, onTableItemClick, theme, connections = [], schemas = [], tables = [] }) => {
    const [selectedConnection, setSelectedConnection] = useState('');
    const [selectedSchema, setSelectedSchema] = useState('');

    // Handle connection dropdown change
    const handleConnectionChange = (event) => {
        setSelectedConnection(event.target.value);
        setSelectedSchema(''); // Reset schema when connection changes
        // In a real app, you would fetch schemas based on the selected connection here
        // e.g., fetchSchemas(event.target.value);
    };

    // Handle schema dropdown change
    const handleSchemaChange = (event) => {
        setSelectedSchema(event.target.value);
        // In a real app, you would fetch tables based on the selected schema here
        // e.g., fetchTables(selectedConnection, event.target.value);
    };

    return (
        <Box>
             {/* Note: The CloseIcon is handled in the parent (HomepageLayout) */}
            <Typography variant="h6" mb={2}>Schema Profiling</Typography> {/* Added title here */}

            <FormControl fullWidth margin="normal" size="small">
                <InputLabel id="database-connection-label">Database Connection</InputLabel>
                <Select
                    labelId="database-connection-label"
                    id="database-connection"
                    value={selectedConnection}
                    label="Database Connection"
                    onChange={handleConnectionChange}
                >
                    {/* Map over connections prop to generate MenuItems */}
                    {connections.map(conn => (
                         <MenuItem key={conn.connection_id} value={conn.connection_id}>
                             {conn.connection_name}
                         </MenuItem>
                    ))}
                     {/* Example static MenuItem if connections prop is empty */}
                     {connections.length === 0 && <MenuItem value=""><em>No connections available</em></MenuItem>}
                </Select>
            </FormControl>
            <FormControl fullWidth margin="normal" size="small">
                <InputLabel id="schema-label">Tables</InputLabel>
                <Select
                    labelId="schema-label"
                    id="schema"
                    value={selectedSchema}
                    label="Schema"
                    onChange={handleSchemaChange}
                     disabled={!selectedConnection || schemas.length === 0} // Disable if no connection selected or no schemas
                >
                     {/* Map over schemas prop to generate MenuItems */}
                     {schemas.map(schema => (
                         <MenuItem key={schema} value={schema}>
                             {schema}
                         </MenuItem>
                     ))}
                     {/* Example static MenuItem if schemas prop is empty */}
                     {schemas.length === 0 && <MenuItem value=""><em>Select connection first</em></MenuItem>}
                </Select>
            </FormControl>
            <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', borderBottom: `1px solid ${theme.palette.divider}`, pb: 0.5, mb: 0.5, color: theme.palette.text.secondary, fontSize: '0.8rem' }}>
                    <Box sx={{ width: '50%', pl: 3 }}>Table Name</Box>
                    <Box sx={{ width: '50%' }}>Columns</Box>
                </Box>
                {/* Table Rows - You would map over the 'tables' prop here */}
                 {tables.length === 0 ? (
                     <Box sx={{ textAlign: 'center', py: 2, color: theme.palette.text.secondary }}>
                         {selectedSchema ? 'No tables found for this schema.' : 'Select a schema to view tables.'}
                     </Box>
                 ) : (
                     tables.map((table) => (
                         <Box
                             key={table.name} // Assuming table object has a 'name' property
                             sx={{
                                 display: 'flex',
                                 alignItems: 'center',
                                 py: 0.5,
                                 borderBottom: `1px solid ${theme.palette.divider}`,
                                 cursor: 'pointer',
                                 '&:hover': {
                                     bgcolor: theme.palette.action.hover,
                                 },
                             }}
                             onClick={() => onTableItemClick(table)} // Pass the table object to the handler
                         >
                             <Box sx={{ width: '50%', display: 'flex', alignItems: 'center' }}>
                                 {/* You might use icons to indicate expandable rows if you implement nested views */}
                                 {/* <ExpandMoreIcon fontSize="small"/> */}
                                 <ChevronRightIcon fontSize="small"/> {/* Using ChevronRight for now */}
                                 <Typography variant="body2">{table.name}</Typography> {/* Display table name */}
                             </Box>
                             {/* Display columns - assuming table object has a 'columns' property (e.g., array of strings) */}
                             <Box sx={{ width: '50%' }}>
                                 <Typography variant="body2">{table.columns ? table.columns.join(', ') : 'N/A'}</Typography>
                             </Box>
                         </Box>
                     ))
                 )}
                {/* Example static rows (remove when mapping over 'tables' prop) */}
                {/* <Box sx={{ display: 'flex', alignItems: 'center', py: 0.5, borderBottom: `1px solid ${theme.palette.divider}`, cursor: 'pointer' }} onClick={() => onTableItemClick({ table: 'customers' })}>
                    <Box sx={{ width: '50%', display: 'flex', alignItems: 'center' }}>
                        <ExpandMoreIcon fontSize="small"/>
                        <Typography variant="body2">customers</Typography>
                    </Box>
                    <Box sx={{ width: '50%' }}><Typography variant="body2">id, name, email</Typography></Box>
                </Box> */}
                {/* ... other static rows ... */}
            </Box>
            
        </Box>
    );
};

export default SchemaProfilingControls;
