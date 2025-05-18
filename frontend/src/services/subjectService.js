// src/services/subjectService.js
import axios from 'axios';

// Get auth token from localStorage
const getAuthToken = () => {
  return localStorage.getItem('adminToken');
};

// Create headers with auth token
const getAuthHeaders = () => {
  return {
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`
    }
  };
};

/* eslint-disable no-useless-catch */
// This disables the no-useless-catch rule for the entire file
// We're keeping the try/catch structure for potential future error handling improvements

const subjectService = {
  // Get all subjects
  getAllSubjects: async () => {
    try {
      const response = await axios.get('/api/subjects', getAuthHeaders());
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  // Get subject details for editing
  getSubjectDetails: async (subjectId) => {
    try {
      const response = await axios.get(`/api/edit/${subjectId}`, getAuthHeaders());
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  // Add new subject
  addSubject: async (formData) => {
    try {
      const form = new FormData();
      form.append('subject', formData.subject_name);
      form.append('description', formData.description);
      
      const response = await axios.post('/api/addcomplete/', form, getAuthHeaders());
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  // Update existing subject
  updateSubject: async (subjectId, formData) => {
    try {
      const form = new FormData();
      form.append('subject', formData.subject_name);
      form.append('description', formData.description);
      
      const response = await axios.post(`/api/editsubjectcomplete/${subjectId}`, form, getAuthHeaders());
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  // Delete subject
  deleteSubject: async (subjectId) => {
    if (!subjectId) {
      throw new Error('Subject ID is required');
    }
    
    try {
      const response = await axios.post(
        `/api/deletesubject/${subjectId}`, 
        {}, 
        getAuthHeaders()
      );
      
      // Return the data or a standardized success response
      return response.data || { success: true, message: 'Subject deleted successfully' };
    } catch (error) {
      // Log the error for debugging
      console.error('Subject service delete error:', error);
      
      // Create a standardized error object
      const errorObj = {
        message: 'Failed to delete subject',
        details: null
      };
      
      // Extract error details if available
      if (error.response) {
        errorObj.status = error.response.status;
        errorObj.details = error.response.data;
      } else if (error.request) {
        errorObj.message = 'No response received from server';
        errorObj.details = error.request;
      } else {
        errorObj.message = error.message || 'Unknown error occurred';
      }
      
      // Throw the standardized error
      throw errorObj;
    }
  },
};

export default subjectService;