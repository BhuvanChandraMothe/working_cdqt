import React, { useState } from 'react';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  Typography, LinearProgress, Chip, Dialog, DialogTitle, DialogContent, IconButton, Divider, Box, List, ListItem, Popover
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';

const getPercentage = (value, total) => total ? ((value / total) * 100).toFixed(1) : 0;

const ProfilingResultsTable = ({ profilingData }) => {
  const [selectedColumn, setSelectedColumn] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  // State for Popover
  const [popoverAnchorEl, setPopoverAnchorEl] = useState(null);
  const [popoverContent, setPopoverContent] = useState(null);

  const handlePopoverOpen = (event, col) => {
    setPopoverAnchorEl(event.currentTarget);
    setPopoverContent(col); // Store the column data for the popover
  };

  const handlePopoverClose = () => {
    setPopoverAnchorEl(null);
    setPopoverContent(null); // Clear content on close
  };

  const openDialog = (col) => {
    setSelectedColumn(col);
    setDialogOpen(true);
    handlePopoverClose(); // Close popover if dialog is opened from hover
  };

  const closeDialog = () => {
    setSelectedColumn(null);
    setDialogOpen(false);
  };

  const popoverOpen = Boolean(popoverAnchorEl);
  const popoverId = popoverOpen ? 'row-overview-popover' : undefined;

  return (
    <>
      <TableContainer component={Paper} sx={{ bgcolor: '#424242', color: '#e0e0e0' }}> {/* Dark grey background */}
        <Table>
          <TableHead>
            <TableRow sx={{ bgcolor: '#505050' }}> {/* Slightly lighter grey for head */}
              <TableCell><Typography fontWeight="bold" sx={{ color: '#e0e0e0' }}>Column</Typography></TableCell>
              <TableCell sx={{ color: '#e0e0e0' }}>Type</TableCell>
              <TableCell sx={{ color: '#e0e0e0' }}>Gen. Type</TableCell>
              <TableCell sx={{ color: '#e0e0e0' }}>Nulls</TableCell>
              <TableCell sx={{ color: '#e0e0e0' }}>Distinct</TableCell>
              <TableCell sx={{ color: '#e0e0e0' }}>PII</TableCell>
              <TableCell sx={{ color: '#e0e0e0' }}>Suggestion</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {profilingData.map((col) => (
              <TableRow
                key={col.id}
                hover
                onClick={() => openDialog(col)}
                onMouseEnter={(event) => handlePopoverOpen(event, col)}
                onMouseLeave={handlePopoverClose}
                sx={{ cursor: 'pointer', '&:hover': { bgcolor: '#616161' } }} // Darker grey on hover
              >
                <TableCell sx={{ color: '#e0e0e0' }}>{col.column_name}</TableCell>
                <TableCell sx={{ color: '#e0e0e0' }}>{col.column_type}</TableCell>
                <TableCell sx={{ color: '#e0e0e0' }}>{col.general_type}</TableCell>
                <TableCell sx={{ color: '#e0e0e0' }}>
                  {col.null_value_ct} ({getPercentage(col.null_value_ct, col.record_ct)}%)
                  <LinearProgress
                    variant="determinate"
                    value={getPercentage(col.null_value_ct, col.record_ct)}
                    color="error"
                    sx={{ bgcolor: '#757575' }} // Adjust progress bar background
                  />
                </TableCell>
                <TableCell sx={{ color: '#e0e0e0' }}>
                  {col.distinct_value_ct} ({getPercentage(col.distinct_value_ct, col.value_ct)}%)
                  <LinearProgress
                    variant="determinate"
                    value={getPercentage(col.distinct_value_ct, col.value_ct)}
                    color="primary"
                     sx={{ bgcolor: '#757575' }} // Adjust progress bar background
                  />
                </TableCell>
                <TableCell sx={{ color: '#e0e0e0' }}>
                  {col.pii_flag ? (
                    <Chip label="PII" color="warning" size="small" />
                  ) : (
                    <Chip label="No" size="small" />
                  )}
                </TableCell>
                <TableCell sx={{ color: '#e0e0e0' }}>{col.datatype_suggestion}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Popover for Overview on Hover */}
      <Popover
        id={popoverId}
        open={popoverOpen}
        anchorEl={popoverAnchorEl}
        onClose={handlePopoverClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'left',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'left',
        }}
        disableRestoreFocus // Keep focus on the table
        sx={{
          pointerEvents: 'none', // Allows mouse events to pass through popover to trigger click on row
          '& .MuiPopover-paper': {
              bgcolor: '#616161', // Dark grey background for popover
              color: '#e0e0e0',
              p: 2, // Add some padding
              maxWidth: '300px' // Limit popover width
          }
        }}
      >
        {popoverContent && (
          <Box>
            <Typography variant="subtitle2" fontWeight="bold" gutterBottom>{popoverContent.column_name} Overview</Typography>
            <Typography variant="body2">Type: {popoverContent.column_type}</Typography>
            <Typography variant="body2">Gen. Type: {popoverContent.general_type}</Typography>
            <Typography variant="body2">Nulls: {popoverContent.null_value_ct} ({getPercentage(popoverContent.null_value_ct, popoverContent.record_ct)}%)</Typography>
            <Typography variant="body2">Distinct: {popoverContent.distinct_value_ct} ({getPercentage(popoverContent.distinct_value_ct, popoverContent.value_ct)}%)</Typography>
            <Typography variant="body2">PII: {popoverContent.pii_flag ? 'Yes' : 'No'}</Typography>
             {/* Add more key overview details here */}
          </Box>
        )}
      </Popover>


      {/* Detailed Dialog (Existing) */}
      <Dialog open={dialogOpen} onClose={closeDialog} fullWidth maxWidth="md">
        <DialogTitle sx={{ bgcolor: '#424242', color: '#e0e0e0' }}> {/* Dark grey background */}
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">{selectedColumn?.column_name} - Detailed Profile</Typography>
            <IconButton onClick={closeDialog} sx={{ color: '#e0e0e0' }}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent dividers sx={{ bgcolor: '#424242', color: '#e0e0e0' }}> {/* Dark grey background */}
          {selectedColumn && (
            <>
              {/* Overview */}
              <Typography variant="subtitle1" gutterBottom>Overview</Typography>
              <Divider sx={{ bgcolor: '#616161' }} /> {/* Grey divider */}
              <Box my={1}>
                <Typography><b>Table:</b> {selectedColumn.table_name}</Typography>
                <Typography><b>Schema:</b> {selectedColumn.schema_name}</Typography>
                <Typography><b>Run Date:</b> {new Date(selectedColumn.run_date).toLocaleString()}</Typography>
                <Typography><b>Column Type:</b> {selectedColumn.column_type}</Typography>
                <Typography><b>General Type:</b> {selectedColumn.general_type}</Typography>
                <Typography><b>Datatype Suggestion:</b> {selectedColumn.datatype_suggestion}</Typography>
                <Typography><b>PII Flag:</b> {selectedColumn.pii_flag ? 'Yes' : 'No'}</Typography>
                <Typography><b>Functional Type:</b> {selectedColumn.functional_data_type} / {selectedColumn.functional_table_type}</Typography>
              </Box>

              {/* Completeness */}
              <Typography variant="subtitle1" gutterBottom>Completeness</Typography>
              <Divider sx={{ bgcolor: '#616161' }} />
              <Box my={1}>
                <Typography>Record Count: {selectedColumn.record_ct}</Typography>
                <Typography>Value Count: {selectedColumn.value_ct}</Typography>
                <Typography>Null Count: {selectedColumn.null_value_ct}</Typography>
                <LinearProgress
                  variant="determinate"
                  value={getPercentage(selectedColumn.value_ct, selectedColumn.record_ct)}
                  sx={{ mb: 1, bgcolor: '#757575' }}
                />
              </Box>

              {/* Uniqueness */}
              <Typography variant="subtitle1" gutterBottom>Uniqueness</Typography>
              <Divider sx={{ bgcolor: '#616161' }} />
              <Box my={1}>
                <Typography>Distinct Values: {selectedColumn.distinct_value_ct}</Typography>
                <Typography>Standard Distinct: {selectedColumn.distinct_std_value_ct}</Typography>
                <Typography>Hash: {selectedColumn.distinct_value_hash}</Typography>
                <LinearProgress
                  variant="determinate"
                  value={getPercentage(selectedColumn.distinct_value_ct, selectedColumn.value_ct)}
                  color="secondary"
                  sx={{ bgcolor: '#757575' }}
                />
              </Box>

              {/* Conditional Sections */}
              {['T', 'O', 'A'].includes(selectedColumn.general_type) && (
                <>
                  <Typography variant="subtitle1" gutterBottom>Text Characteristics</Typography>
                  <Divider sx={{ bgcolor: '#616161' }} />
                  <Box my={1}>
                    
                    <Typography>Min Length: {selectedColumn.min_length}</Typography>
                    <Typography>Max Length: {selectedColumn.max_length}</Typography>
                    <Typography>Avg Length: {selectedColumn.avg_length}</Typography>
                    <Typography>Upper Case Count: {selectedColumn.upper_case_ct}</Typography>
                    <Typography>Lower Case Count: {selectedColumn.lower_case_ct}</Typography>
                    {selectedColumn.top_freq_values && (
                      <>
                        <Typography>Top Values:</Typography>
                        <List dense>
                          {selectedColumn.top_freq_values.map((val, i) => (
                            <ListItem key={i} sx={{ color: '#e0e0e0' }}>{val}</ListItem>
                          ))}
                        </List>
                      </>
                    )}
                  </Box>
                </>
              )}

              {selectedColumn.general_type === 'N' && (
                <>
                  <Typography variant="subtitle1" gutterBottom>Numeric Stats</Typography>
                  <Divider sx={{ bgcolor: '#616161' }} />
                  <Box my={1}>
                    <Typography>Min: {selectedColumn.min_value}</Typography>
                    <Typography>Max: {selectedColumn.max_value}</Typography>
                    <Typography>Avg: {selectedColumn.avg_value}</Typography>
                    <Typography>Stdev: {selectedColumn.stdev_value}</Typography>
                  </Box>
                </>
              )}

              {selectedColumn.general_type === 'D' && (
                <>
                  <Typography variant="subtitle1" gutterBottom>Date Stats</Typography>
                  <Divider sx={{ bgcolor: '#616161' }} />
                  <Box my={1}>
                    <Typography>Min Date: {selectedColumn.min_date}</Typography>
                    <Typography>Max Date: {selectedColumn.max_date}</Typography>
                    <Typography>Within 1yr: {selectedColumn.within_1yr_date_ct}</Typography>
                    <Typography>Before 5yr: {selectedColumn.before_5yr_date_ct}</Typography>
                  </Box>
                </>
              )}

              {selectedColumn.general_type === 'B' && (
                <>
                  <Typography variant="subtitle1" gutterBottom>Boolean Stats</Typography>
                  <Divider sx={{ bgcolor: '#616161' }} />
                  <Box my={1}>
                    <Typography>True Count: {selectedColumn.boolean_true_ct}</Typography>
                    <LinearProgress
                      variant="determinate"
                      value={getPercentage(selectedColumn.boolean_true_ct, selectedColumn.value_ct)}
                      color="info"
                      sx={{ bgcolor: '#757575' }}
                    />
                  </Box>
                </>
              )}
            </>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
};

export default ProfilingResultsTable;