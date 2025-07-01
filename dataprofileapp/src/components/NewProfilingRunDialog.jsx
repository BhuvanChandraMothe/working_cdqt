import React, { useEffect, useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  CircularProgress,
  Typography,
  Box,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { getAllConnections, getTableGroups, triggerProfiling } from '../api/dbapi';

const NewProfilingRunDialog = ({ open, onClose, onRunSuccess }) => {
  const [connections, setConnections] = useState([]);
  const [tableGroups, setTableGroups] = useState([]);
  const [selectedConnection, setSelectedConnection] = useState('');
  const [selectedTableGroup, setSelectedTableGroup] = useState('');
  const [loadingConnections, setLoadingConnections] = useState(false);
  const [loadingTableGroups, setLoadingTableGroups] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (open) {
      loadConnections();
    }
  }, [open]);

  useEffect(() => {
    if (!open) {
      setSelectedConnection('');
      setSelectedTableGroup('');
      setTableGroups([]);
    }
  }, [open]);
  

  const loadConnections = async () => {
    setLoadingConnections(true);
    try {
      const data = await getAllConnections();
      setConnections(data);
    } catch (error) {
      console.error('Failed to load connections:', error);
    } finally {
      setLoadingConnections(false);
    }
  };

  const loadTableGroups = async (connectionId) => {
    setLoadingTableGroups(true);
    try {
      const data = await getTableGroups(connectionId);
      setTableGroups(data);
    } catch (error) {
      console.error('Failed to load table groups:', error);
    } finally {
      setLoadingTableGroups(false);
    }
  };

  const handleConnectionChange = (event) => {
    const connId = event.target.value;
    setSelectedConnection(connId);
    setSelectedTableGroup('');
    loadTableGroups(connId);
  };

  const handleTableGroupChange = (event) => {
    setSelectedTableGroup(event.target.value);
  };

  const handleRunProfiling = async () => {
    if (!selectedConnection || !selectedTableGroup) return;
    setSubmitting(true);
    try {
      await triggerProfiling({
        connection_id: selectedConnection,
        table_group_id: selectedTableGroup,
      });
      
      if (onRunSuccess) {
        onRunSuccess();
      }
      onClose();
    } catch (error) {
      console.error('Failed to trigger profiling:', error);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle sx={{ m: 0, p: 2 }}>
        New Profiling Run
        <IconButton
          aria-label="close"
          onClick={onClose}
          sx={{
            position: 'absolute',
            right: 8,
            top: 8,
            color: (theme) => theme.palette.grey[500],
          }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogContent dividers>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <FormControl fullWidth>
            <InputLabel id="connection-label">Connection</InputLabel>
            <Select
              labelId="connection-label"
              value={selectedConnection}
              onChange={handleConnectionChange}
              label="Connection"
              disabled={loadingConnections}
            >
              {connections.map((conn) => (
                <MenuItem key={conn.connection_id} value={conn.connection_id}>
                  {conn.name || `Connection ${conn.connection_id}`}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth disabled={!selectedConnection || loadingTableGroups}>
            <InputLabel id="table-group-label">Table Group</InputLabel>
            <Select
              labelId="table-group-label"
              value={selectedTableGroup}
              onChange={handleTableGroupChange}
              label="Table Group"
            >
              {tableGroups.map((group) => (
                <MenuItem key={group.id} value={group.id}>
                  {group.table_group_name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={submitting}>
          Cancel
        </Button>
        <Button
          onClick={handleRunProfiling}
          variant="contained"
          disabled={!selectedConnection || !selectedTableGroup || submitting}
        >
          {submitting ? <CircularProgress size={24} /> : 'Run Profiling'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default NewProfilingRunDialog;
