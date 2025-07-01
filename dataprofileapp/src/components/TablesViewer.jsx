import React from 'react';
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Box,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

const TablesViewer = ({ data }) => {
  if (!data || !data.tables || data.tables.length === 0) {
    return <Typography>No tables found.</Typography>;
  }

  return (
    <Box p={2}>
      <Typography variant="h5" gutterBottom>
        Database Type: {data.db_type}
      </Typography>

      {data.tables.map((table, idx) => (
        <Accordion key={idx}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">{table.name}</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell><strong>Column Name</strong></TableCell>
                  <TableCell><strong>Data Type</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {table.columns.map((col, colIdx) => (
                  <TableRow key={colIdx}>
                    <TableCell>{col.name}</TableCell>
                    <TableCell>{col.type}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  );
};

export default TablesViewer;
