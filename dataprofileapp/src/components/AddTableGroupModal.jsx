import React, { useState, useEffect } from 'react';
import {
    Dialog, DialogTitle, DialogContent, DialogActions,
    TextField, Button, FormControlLabel, Checkbox, Grid, Box,
    Typography
} from '@mui/material';
import { createTableGroup } from '../api/dbapi';

// Changed explicit_table_list to an empty string for TextField compatibility
const initialFormValues = {
    table_groups_name: '',
    table_group_schema: '',
    explicit_table_list: '', // <--- Changed to a string
    profiling_include_mask: '%',
    profiling_exclude_mask: 'tmp%',
    profile_id_column_mask: '%id',
    profile_sk_column_mask: '%_sk',
    profile_use_sampling: 'N',
    profile_sample_percent: '30',
    profile_sample_min_count: 100000,
    min_profiling_age_days: 0,
    profile_flag_cdes: true,
    profile_do_pair_rules: 'N',
    profile_pair_rule_pct: 95,
    description: '',
    data_source: '',
    source_system: '',
    source_process: '',
    data_location: '',
    business_domain: '',
    stakeholder_group: '',
    transform_level: '',
    data_product: '',
    scorecard: false,
};

const AddTableGroupModal = ({ open, onClose, connectionId }) => {
    const [formValues, setFormValues] = useState(initialFormValues);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (open) {
            setFormValues(initialFormValues);
            setError(null);
        }
    }, [open]);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormValues((prev) => ({
            ...prev,
            // For checkboxes, handle 'checked'. For text fields, handle 'value'.
            // No special handling needed for explicit_table_list here, as it's just a string in state.
            [name]: type === 'checkbox' ? checked : value,
        }));
    };

    const handleAdd = async () => {
        setIsSubmitting(true);
        setError(null);

        try {
            // Create the payload for the API call
            const payload = {
                ...formValues,
                // Convert explicit_table_list string to an array here
                explicit_table_list: formValues.explicit_table_list
                    ? formValues.explicit_table_list.split(',').map(item => item.trim())
                    : [], // If empty string, send an empty array
                profile_use_sampling: formValues.profile_use_sampling === 'Y',
                profile_do_pair_rules: formValues.profile_do_pair_rules === 'Y',
                profile_sample_min_count: parseInt(formValues.profile_sample_min_count, 10) || 100000,
                min_profiling_age_days: parseInt(formValues.min_profiling_age_days, 10) || 0,
                profile_pair_rule_pct: parseInt(formValues.profile_pair_rule_pct, 10) || 95,
            };

            // Remove scorecard as it's not part of the backend model
            delete payload.scorecard;

            console.log('Payload to send:', payload);
            await createTableGroup(connectionId, payload);
            onClose(); // Close modal on successful creation
        } catch (err) {
            console.error('Error creating table group:', err);
            const errorMessage = err.response?.data?.detail || err.message || 'Failed to create table group.';
            setError(errorMessage);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle sx={{ fontWeight: 600, fontSize: '1.25rem' }}>
                Add Table Group
            </DialogTitle>
            <DialogContent dividers sx={(theme) => ({
                pt: 3,
                backgroundColor: theme.palette.background.paper,
                color: theme.palette.text.primary,
            })}>
                <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                        <TextField
                            label="Table Group Name"
                            name="table_groups_name" // <--- Should be 'table_groups_name'
                            value={formValues.table_groups_name} // <--- Should be 'table_groups_name'
                            onChange={handleChange}
                            fullWidth
                            size="small"
                            required
                        />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <TextField label="DB Schema" name="table_group_schema" value={formValues.table_group_schema} onChange={handleChange} fullWidth size="small" />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        {/* The explicit_table_list TextField will now correctly handle string values */}
                        <TextField
                            label="Explicit Table List (comma-separated)" // <--- Updated label for clarity
                            name="explicit_table_list"
                            value={formValues.explicit_table_list}
                            onChange={handleChange}
                            fullWidth
                            size="small"
                            placeholder="e.g., table_name_1, schema.table_name_2" // <--- Added placeholder
                        />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <TextField label="Profiling Include Mask" name="profiling_include_mask" value={formValues.profiling_include_mask} onChange={handleChange} fullWidth size="small" />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <TextField label="Profiling Exclude Mask" name="profiling_exclude_mask" value={formValues.profiling_exclude_mask} onChange={handleChange} fullWidth size="small" />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <TextField label="Profile ID Column Mask" name="profile_id_column_mask" value={formValues.profile_id_column_mask} onChange={handleChange} fullWidth size="small" />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <TextField label="Profile SK Column Mask" name="profile_sk_column_mask" value={formValues.profile_sk_column_mask} onChange={handleChange} fullWidth size="small" />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <TextField label="Min Profiling Age (Days)" type="number" name="min_profiling_age_days" value={formValues.min_profiling_age_days} onChange={handleChange} fullWidth size="small" inputProps={{ min: 0 }} />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <TextField label="Profile Sample Percent (%)" type="number" name="profile_sample_percent" value={formValues.profile_sample_percent} onChange={handleChange} fullWidth size="small" inputProps={{ min: 0, max: 100 }} />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <TextField label="Profile Sample Min Count" type="number" name="profile_sample_min_count" value={formValues.profile_sample_min_count} onChange={handleChange} fullWidth size="small" inputProps={{ min: 0 }} />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <TextField label="Description" name="description" value={formValues.description} onChange={handleChange} fullWidth size="small" multiline rows={2} />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <TextField label="Data Source" name="data_source" value={formValues.data_source} onChange={handleChange} fullWidth size="small" />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <TextField label="Source System" name="source_system" value={formValues.source_system} onChange={handleChange} fullWidth size="small" />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <TextField label="Source Process" name="source_process" value={formValues.source_process} onChange={handleChange} fullWidth size="small" />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <TextField label="Data Location" name="data_location" value={formValues.data_location} onChange={handleChange} fullWidth size="small" />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <TextField label="Business Domain" name="business_domain" value={formValues.business_domain} onChange={handleChange} fullWidth size="small" />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <TextField label="Stakeholder Group" name="stakeholder_group" value={formValues.stakeholder_group} onChange={handleChange} fullWidth size="small" />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <TextField label="Transform Level" name="transform_level" value={formValues.transform_level} onChange={handleChange} fullWidth size="small" />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <TextField label="Data Product" name="data_product" value={formValues.data_product} onChange={handleChange} fullWidth size="small" />
                    </Grid>

                    <Grid item xs={12}>
                        <Box display="flex" flexDirection="row" flexWrap="wrap" gap={2}>
                            <FormControlLabel control={<Checkbox checked={formValues.profile_flag_cdes} onChange={handleChange} name="profile_flag_cdes" />} label="Profile Flag CDEs" />
                            {/* Checkbox for 'Y'/'N' string values */}
                            <FormControlLabel
                                control={<Checkbox checked={formValues.profile_use_sampling === 'Y'} onChange={(e) => handleChange({ target: { name: 'profile_use_sampling', value: e.target.checked ? 'Y' : 'N', type: 'text' } })} name="profile_use_sampling" />}
                                label="Use Profile Sampling"
                            />
                            <FormControlLabel
                                control={<Checkbox checked={formValues.profile_do_pair_rules === 'Y'} onChange={(e) => handleChange({ target: { name: 'profile_do_pair_rules', value: e.target.checked ? 'Y' : 'N', type: 'text' } })} name="profile_do_pair_rules" />}
                                label="Profile Do Pair Rules"
                            />
                            <FormControlLabel control={<Checkbox checked={formValues.scorecard} onChange={handleChange} name="scorecard" />} label="Add Scorecard for Table Group" />
                        </Box>
                    </Grid>
                </Grid>

                {error && (
                    <Box mt={2} p={2} bgcolor="error.dark" color="white" borderRadius={1}>
                        <Typography>{error}</Typography>
                    </Box>
                )}
            </DialogContent>

            <DialogActions sx={{ px: 3, py: 2 }}>
                <Button onClick={onClose} color="secondary" variant="outlined" disabled={isSubmitting}>Cancel</Button>
                <Button onClick={handleAdd} variant="contained" color="primary" disabled={isSubmitting}>
                    {isSubmitting ? 'Adding...' : 'Add Table Group'}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default AddTableGroupModal;