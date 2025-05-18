// src/services/quizService.js
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

const quizService = {
  // Get all quizzes for admin dashboard
  getAllQuizzes: async () => {
    try {
      const response = await axios.get('/api/adminhome', getAuthHeaders());
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  // Get chapters for quiz form
  getChapters: async () => {
    try {
      const response = await axios.get('/api/addquiz', getAuthHeaders());
      return response.data.chapters;
    } catch (error) {
      throw error;
    }
  },
  
  // Get quiz details for editing
  getQuizDetails: async (quizId) => {
    try {
      const response = await axios.get(`/api/edit_quiz/${quizId}`, getAuthHeaders());
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  // Add new quiz
  addQuiz: async (formData) => {
    try {
      const form = new FormData();
      form.append('date', formData.date);
      form.append('chapter_id', formData.chapter_id);
      form.append('duration', formData.duration);
      
      const response = await axios.post('/api/addcompletequiz', form, getAuthHeaders());
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  // Update existing quiz
  updateQuiz: async (quizId, quizData) => {
    try {
      const response = await axios.post(`/api/editcompletequiz/${quizId}`, quizData, getAuthHeaders());
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  // Delete quiz
  deleteQuiz: async (quizId) => {
    if (!quizId) {
      throw new Error('Quiz ID is required');
    }
    
    try {
      const response = await axios.delete(
        `/api/admin/quizzes/${quizId}`, 
        getAuthHeaders()
      );
      
      // Return the data or a standardized success response
      return response.data || { success: true, message: 'Quiz deleted successfully' };
    } catch (error) {
      // Log the error for debugging
      console.error('Quiz service delete error:', error);
      
      // Create a standardized error object
      const errorObj = {
        message: 'Failed to delete quiz',
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

export default quizService;