import React, { useState, useEffect } from 'react';
import {
    Dialog, DialogTitle, DialogContent, DialogActions,
    TextField, Button, FormControlLabel, Checkbox, Grid, Box,
    Typography, CircularProgress // Added CircularProgress
} from '@mui/material';
import { updateTableGroup } from '../api/dbapi'; // Import the update function
import { styled } from '@mui/material/styles'; // Import styled

// Define a default structure/empty state for the form, useful as a fallback
const defaultFormValues = {
    table_group_name: '',
    table_group_schema: '',
    explicit_table_list: '', // Assuming TextField uses comma-separated string
    profiling_include_mask: '%',
    profiling_exclude_mask: 'tmp%',
    profile_id_column_mask: '%id',
    profile_sk_column_mask: '%_sk',
    profile_use_sampling: false, // Checkbox state is boolean
    profile_sample_percent: '30', // Backend expects string
    profile_sample_min_count: 100000,
    min_profiling_age_days: 0, // Backend expects int
    profile_flag_cdes: true, // Checkbox state is boolean
    profile_do_pair_rules: false, // Checkbox state is boolean
    profile_pair_rule_pct: 95, // Backend expects int
    description: '',
    data_source: '',
    source_system: '',
    source_process: '',
    data_location: '',
    business_domain: '',
    stakeholder_group: '',
    transform_level: '',
    data_product: '',
    // Note: last_complete_profile_run_id, dq_score_profiling, dq_score_testing
    // are likely not editable in this form, will be passed through.
};


const EditTableGroupModal = ({ open, onClose, connectionId, initialData, onSave }) => {
    const [formValues, setFormValues] = useState(defaultFormValues);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState(null);

    // Effect to populate the form when the modal opens or initialData changes
    useEffect(() => {
        if (open && initialData) {
            console.log("Edit Modal: Initial data received:", initialData);
            // Map the initialData (from backend TableGroupOut) to form state
            setFormValues({
                // Use initialData fields, provide fallbacks or map types
                table_group_name: initialData.table_group_name || '',
                table_group_schema: initialData.table_group_schema || '',

                // Map array from backend to comma-separated string for TextField
                explicit_table_list:initialData.explicit_table_list,

                profiling_include_mask: initialData.profiling_include_mask || '%',
                profiling_exclude_mask: initialData.profiling_exclude_mask || 'tmp%',
                profile_id_column_mask: initialData.profile_id_column_mask || '%id',
                profile_sk_column_mask: initialData.profile_sk_column_mask || '%_sk',

                // Map 'Y'/'N' or boolean from backend to boolean for Checkbox state
                profile_use_sampling: initialData.profile_use_sampling === 'Y' || initialData.profile_use_sampling === true,
                profile_do_pair_rules: initialData.profile_do_pair_rules === 'Y' || initialData.profile_do_pair_rules === true,
                profile_flag_cdes: initialData.profile_flag_cdes === null || initialData.profile_flag_cdes === undefined ? true : initialData.profile_flag_cdes, // Handle potential null/undefined from backend

                profile_sample_percent: String(initialData.profile_sample_percent || '30'), // Ensure it's string for backend
                profile_sample_min_count: initialData.profile_sample_min_count || 100000, // Ensure number
                min_profiling_age_days: initialData.min_profiling_age_days || 0, // Ensure number
                profile_pair_rule_pct: initialData.profile_pair_rule_pct || 95, // Ensure number

                description: initialData.description || '',
                data_source: initialData.data_source || '',
                source_system: initialData.source_system || '',
                source_process: initialData.source_process || '',
                data_location: initialData.data_location || '',
                business_domain: initialData.business_domain || '',
                stakeholder_group: initialData.stakeholder_group || '',
                transform_level: initialData.transform_level || '',
                data_product: initialData.data_product || '',

                // Non-editable fields from initialData (pass-through) - these won't have form inputs
                // but include them here if you need to pass them back in the payload.
                // Based on the `updateTableGroup` payload structure we decided on, we will pass
                // them through in the handleSave function using the original initialData.
            });
            setError(null); // Clear errors on opening
        } else if (!open) {
            // Reset form when modal is closed
             setFormValues(defaultFormValues); // Reset to default values
             setError(null); // Clear errors
        }
    }, [open, initialData]); // Re-run effect when modal opens/closes or initialData changes

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;

        // Handle numeric inputs carefully to allow empty string initially
        if (type === 'number') {
             setFormValues((prev) => ({
                ...prev,
                [name]: value === '' ? '' : Number(value), // Store as number or empty string
             }));
        } else {
            setFormValues((prev) => ({
                ...prev,
                [name]: type === 'checkbox' ? checked : value,
            }));
        }
    };

    const handleSave = async () => {
        setIsSubmitting(true);
        setError(null);

        // Ensure we have the data to update
        if (!initialData || !initialData.group_id || !connectionId) {
            console.error("Error: Missing data for update.");
            setError("Cannot save: Missing table group or connection information.");
            setIsSubmitting(false);
            return;
        }

        try {
            // Construct the payload matching the backend's TableGroupUpdate model (based on TableGroupBase)
            const updatePayload = {
                 table_group_name: formValues.table_group_name,
                 table_group_schema: formValues.table_group_schema || null,

                 // Map comma-separated string from TextField back to array for backend
                 explicit_table_list: formValues.explicit_table_list,

                 profiling_include_mask: formValues.profiling_include_mask || null,
                 profiling_exclude_mask: formValues.profiling_exclude_mask || null,
                 profile_id_column_mask: formValues.profile_id_column_mask || '%id',
                 profile_sk_column_mask: formValues.profile_sk_column_mask || '%_sk',

                 // Map boolean form state back to 'Y'/'N' strings for backend
                 profile_use_sampling: formValues.profile_use_sampling ? 'Y' : 'N',
                 profile_do_pair_rules: formValues.profile_do_pair_rules ? 'Y' : 'N',

                 profile_sample_percent: formValues.profile_sample_percent || '30', // Backend expects string

                 // Convert numeric form state (can be empty string or number) to integer or null for backend
                 profile_sample_min_count: formValues.profile_sample_min_count === '' || formValues.profile_sample_min_count === null ? null : parseInt(formValues.profile_sample_min_count, 10),
                 min_profiling_age_days: formValues.min_profiling_age_days === '' || formValues.min_profiling_age_days === null ? null : parseInt(formValues.min_profiling_age_days, 10),
                 profile_pair_rule_pct: formValues.profile_pair_rule_pct === '' || formValues.profile_pair_rule_pct === null ? null : parseInt(formValues.profile_pair_rule_pct, 10),

                 // profile_flag_cdes is boolean in backend and form state - ok
                 profile_flag_cdes: formValues.profile_flag_cdes,


                 description: formValues.description || null,
                 data_source: formValues.data_source || null,
                 source_system: formValues.source_system || null,
                 source_process: formValues.source_process || null,
                 data_location: formValues.data_location || null,
                 business_domain: formValues.business_domain || null,
                 stakeholder_group: formValues.stakeholder_group || null,
                 transform_level: formValues.transform_level || null,
                 data_product: formValues.data_product || null,

                 // Pass through non-editable fields from the original data
                 last_complete_profile_run_id: initialData.last_complete_profile_run_id || null,
                 dq_score_profiling: initialData.dq_score_profiling || null,
                 dq_score_testing: initialData.dq_score_testing || null,
            };

            console.log("Attempting to update table group", initialData.group_id, "payload:", updatePayload);

            // Call the update API function with connectionId, group_id, and the payload
            await updateTableGroup(connectionId, initialData.group_id, updatePayload);

            console.log("Table group updated successfully!");

            // Call the onSave callback provided by the parent component
            // You might pass the group ID or the updated group data back
            if (onSave) {
                // Pass the updated group ID back so the parent can refresh the details
                onSave(initialData.group_id);
            }

            // Close the modal
            onClose();

        } catch (error) {
            console.error('Error updating table group:', error);
            const errorMessage = error.response?.data?.detail || error.message || 'Failed to update table group.';
            setError(errorMessage);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle sx={{ fontWeight: 600, fontSize: '1.25rem' }}>
                Edit Table Group: {initialData?.table_group_name || ''}
            </DialogTitle>

            <DialogContent dividers sx={(theme) => ({
                pt: 3,
                backgroundColor: theme.palette.background.paper,
                color: theme.palette.text.primary,
            })}>
                {/* Show loading or error if initialData wasn't loaded properly */}
                {!initialData ? (
                     <Box display="flex" justifyContent="center" alignItems="center" minHeight="100px">
                        <CircularProgress size={24} />
                        <Typography sx={{ ml: 2 }}>Loading data...</Typography>
                     </Box>
                ) : (
                     <Grid container spacing={3}>
                         <Grid item xs={12} md={6}>
                             <TextField
                                 label="Table Group Name"
                                 name="table_group_name"
                                 value={formValues.table_group_name}
                                 onChange={handleChange}
                                 fullWidth
                                 size="small"
                                 required
                             />
                         </Grid>
                         <Grid item xs={12} md={6}>
                             <TextField
                                 label="DB Schema"
                                 name="table_group_schema"
                                 value={formValues.table_group_schema}
                                 onChange={handleChange}
                                 fullWidth
                                 size="small"
                             />
                         </Grid>
                         <Grid item xs={12}> {/* Full width for list */}
                             <TextField
                                 label="Explicit Table List (comma-separated)"
                                 name="explicit_table_list"
                                 value={formValues.explicit_table_list}
                                 onChange={handleChange}
                                 fullWidth
                                 size="small"
                                 helperText="Enter table names separated by commas (e.g., table1, schema.table2)"
                             />
                         </Grid>
                         <Grid item xs={12} md={6}>
                             <TextField
                                 label="Profiling Include Mask"
                                 name="profiling_include_mask"
                                 value={formValues.profiling_include_mask}
                                 onChange={handleChange}
                                 fullWidth
                                 size="small"
                             />
                         </Grid>
                         <Grid item xs={12} md={6}>
                             <TextField
                                 label="Profiling Exclude Mask"
                                 name="profiling_exclude_mask"
                                 value={formValues.profiling_exclude_mask}
                                 onChange={handleChange}
                                 fullWidth
                                 size="small"
                             />
                         </Grid>
                         <Grid item xs={12} md={6}>
                             <TextField
                                 label="Profile ID Column Mask"
                                 name="profile_id_column_mask"
                                 value={formValues.profile_id_column_mask}
                                 onChange={handleChange}
                                 fullWidth
                                 size="small"
                             />
                         </Grid>
                         <Grid item xs={12} md={6}>
                             <TextField
                                 label="Profile SK Column Mask"
                                 name="profile_sk_column_mask"
                                 value={formValues.profile_sk_column_mask}
                                 onChange={handleChange}
                                 fullWidth
                                 size="small"
                             />
                         </Grid>
                         <Grid item xs={12} md={4}>
                             <TextField
                                 label="Min Profiling Age (Days)"
                                 type="number"
                                 name="min_profiling_age_days"
                                 value={formValues.min_profiling_age_days} // State is number or empty string
                                 onChange={handleChange}
                                 fullWidth
                                 size="small"
                                 inputProps={{ min: 0 }}
                             />
                         </Grid>
                         <Grid item xs={12} md={4}>
                              <TextField
                                  label="Profile Sample Percent (%)"
                                  type="number"
                                  name="profile_sample_percent"
                                  value={formValues.profile_sample_percent} // State is number or empty string
                                  onChange={handleChange}
                                  fullWidth
                                  size="small"
                                  inputProps={{ min: 0, max: 100 }}
                              />
                          </Grid>
                          <Grid item xs={12} md={4}>
                               <TextField
                                   label="Profile Sample Min Count"
                                   type="number"
                                   name="profile_sample_min_count"
                                   value={formValues.profile_sample_min_count} // State is number or empty string
                                   onChange={handleChange}
                                   fullWidth
                                   size="small"
                                   inputProps={{ min: 0 }}
                               />
                           </Grid>

                          {/* Descriptive Fields */}
                           <Grid item xs={12} md={6}>
                                <TextField
                                    label="Description"
                                    name="description"
                                    value={formValues.description}
                                    onChange={handleChange}
                                    fullWidth
                                    size="small"
                                    multiline
                                    rows={2}
                                />
                            </Grid>
                           <Grid item xs={12} md={6}>
                                <TextField
                                     label="Data Source"
                                     name="data_source"
                                     value={formValues.data_source}
                                     onChange={handleChange}
                                     fullWidth
                                     size="small"
                                />
                            </Grid>
                            <Grid item xs={12} md={6}>
                                 <TextField
                                     label="Source System"
                                     name="source_system"
                                     value={formValues.source_system}
                                     onChange={handleChange}
                                     fullWidth
                                     size="small"
                                 />
                             </Grid>
                            <Grid item xs={12} md={6}>
                                 <TextField
                                     label="Source Process"
                                     name="source_process"
                                     value={formValues.source_process}
                                     onChange={handleChange}
                                     fullWidth
                                     size="small"
                                 />
                             </Grid>
                             <Grid item xs={12} md={6}>
                                  <TextField
                                      label="Data Location"
                                      name="data_location"
                                      value={formValues.data_location}
                                      onChange={handleChange}
                                      fullWidth
                                      size="small"
                                  />
                              </Grid>
                              <Grid item xs={12} md={6}>
                                   <TextField
                                        label="Business Domain"
                                        name="business_domain"
                                        value={formValues.business_domain}
                                        onChange={handleChange}
                                        fullWidth
                                        size="small"
                                   />
                               </Grid>
                               <Grid item xs={12} md={6}>
                                    <TextField
                                         label="Stakeholder Group"
                                         name="stakeholder_group"
                                         value={formValues.stakeholder_group}
                                         onChange={handleChange}
                                         fullWidth
                                         size="small"
                                    />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                     <TextField
                                          label="Transform Level"
                                          name="transform_level"
                                          value={formValues.transform_level}
                                          onChange={handleChange}
                                          fullWidth
                                          size="small"
                                     />
                                 </Grid>
                                 <Grid item xs={12} md={6}>
                                      <TextField
                                           label="Data Product"
                                           name="data_product"
                                           value={formValues.data_product}
                                           onChange={handleChange}
                                           fullWidth
                                           size="small"
                                      />
                                  </Grid>


                         {/* Checkboxes */}
                         <Grid item xs={12}>
                             <Box display="flex" flexDirection="row" flexWrap="wrap" gap={3}> {/* Increased gap */}
                                 <FormControlLabel
                                     control={
                                         <Checkbox
                                             checked={formValues.profile_flag_cdes}
                                             onChange={handleChange}
                                             name="profile_flag_cdes"
                                         />
                                     }
                                     label="Profile Flag CDEs"
                                 />
                                 <FormControlLabel
                                     control={
                                         <Checkbox
                                             checked={formValues.profile_use_sampling} // Checkbox uses boolean state
                                             onChange={handleChange}
                                             name="profile_use_sampling"
                                         />
                                     }
                                     label="Use Profile Sampling"
                                 />
                                  <FormControlLabel
                                      control={
                                          <Checkbox
                                               checked={formValues.profile_do_pair_rules} // Checkbox uses boolean state
                                               onChange={handleChange}
                                               name="profile_do_pair_rules"
                                           />
                                       }
                                      label="Profile Do Pair Rules"
                                  />
                                  {/* Removed the "Add Scorecard" checkbox as it's not in TableGroupBase */}
                             </Box>
                         </Grid>
                     </Grid>
                )}


                {error && (
                    <Box mt={2} p={2} bgcolor="error.dark" color="white" borderRadius={1}>
                        <Typography>{error}</Typography>
                    </Box>
                )}

            </DialogContent>

            <DialogActions sx={{ px: 3, py: 2 }}>
                <Button onClick={onClose} color="secondary" variant="outlined" disabled={isSubmitting}>
                    Cancel
                </Button>
                <Button
                    onClick={handleSave} // Use the handleSave function
                    variant="contained"
                    color="primary"
                    disabled={isSubmitting || !initialData} // Disable if submitting or no data loaded
                    startIcon={isSubmitting ? <CircularProgress size={20} color="inherit" /> : null}
                >
                    {isSubmitting ? 'Saving...' : 'Save Changes'} {/* Change button text */}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default EditTableGroupModal;