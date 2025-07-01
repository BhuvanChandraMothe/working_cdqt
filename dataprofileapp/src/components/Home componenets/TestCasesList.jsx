import React from 'react';
import {
    Box,
    Typography,
    List,
    ListItem,
    ListItemText,
    ListItemIcon, // Keep ListItemIcon if you plan to use icons like CheckCircleOutlineIcon
    // Assuming ArrowRightIcon is used here
    
} from '@mui/material';
import ArrowRightIcon from '@mui/icons-material/ArrowRight';

// Assuming you might use a status icon
// import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
// import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';


/**
 * Displays a list of test cases.
 * @param {object} props - Component props.
 * @param {Array<object>} [props.testCases] - Array of test case objects to display.
 * @param {function} props.onItemClick - Handler for clicking a test case item. Receives item details.
 * @param {object} props.theme - The Material UI theme object for consistent styling.
 */
const TestCasesList = ({ testCases = [], onItemClick, theme }) => {
    return (
        <Box>
             {/* Note: The title and Add Button are handled in the parent (HomepageLayout) */}
            <List dense>
                {/* Map over testCases prop to generate ListItems */}
                {testCases.length === 0 ? (
                     <Box sx={{ textAlign: 'center', py: 2, color: theme.palette.text.secondary }}>
                        No test cases found.
                     </Box>
                ) : (
                    testCases.map((testCase) => (
                        <ListItem
                            key={testCase.id} // Assuming testCase object has a unique 'id'
                            sx={{ cursor: 'pointer' }}
                            onClick={() => onItemClick(testCase)} // Pass the testCase object to the handler
                        >
                            {/* You might add status icons for test cases here if your API provides status */}
                            {/* Example: */}
                            {/* <ListItemIcon sx={{ minWidth: 30 }}>
                                {testCase.status === 'passed' ? (
                                    <CheckCircleOutlineIcon color="success" fontSize="small"/>
                                ) : testCase.status === 'failed' ? (
                                    <ErrorOutlineIcon color="error" fontSize="small"/>
                                ) : null}
                            </ListItemIcon> */}
                            <ListItemText
                                primary={<Typography variant="body2">{testCase.name}</Typography>} // Assuming testCase object has a 'name' property
                                secondary={<Typography variant="caption" color="textSecondary">Table: {testCase.table}</Typography>} // Assuming testCase object has a 'table' property
                            />
                            <ArrowRightIcon sx={{ ml: 'auto' }} fontSize="small" />
                        </ListItem>
                    ))
                )}
                {/* Example static ListItem (remove when mapping over 'testCases' prop) */}
                 {/* <ListItem sx={{ cursor: 'pointer' }} onClick={() => onItemClick({ testCase: 'order_items.id Not null' })}>
                     <ListItemText
                         primary={<Typography variant="body2">order_items.id Not null</Typography>}
                         secondary={<Typography variant="caption" color="textSecondary">Table: Sales DB</Typography>}
                     />
                     <ArrowRightIcon sx={{ ml: 'auto' }} fontSize="small" />
                 </ListItem> */}
                {/* More ListItems */}
            </List>
        </Box>
    );
};

export default TestCasesList;
