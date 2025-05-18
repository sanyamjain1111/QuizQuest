import axios from 'axios';

const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:5000';

class QuestionService {
  constructor() {
    this.api = axios.create({
      baseURL: API_URL
    });
    
    // Add request interceptor to include token
    this.api.interceptors.request.use(config => {
      const token = localStorage.getItem('adminToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }
  
  // Get all chapters for dropdown
  async getChapters() {
    const response = await this.api.get('/api/addquestion');
    return response.data;
  }
  
  // Get all questions
  async getQuestions() {
    const response = await this.api.get('/api/questions');
    return response.data;
  }
  
  // Get single question details
  async getQuestionDetails(questionId) {
    const response = await this.api.get(`/api/edit_question/${questionId}`);
    return response.data;
  }
  
  // Add new question
  async addQuestion(formData) {
    console.log('Adding question with data:', Object.fromEntries(formData));
    
    const response = await this.api.post('/api/addcompleteque', formData);
    return response.data;
  }
  
  // Update existing question
  async updateQuestion(questionId, formData) {
    console.log('Updating question with data:', Object.fromEntries(formData));
    
    const response = await this.api.post(`/api/editcompleteque/${questionId}`, formData);
    return response.data;
  }
  
  // Delete question
  async deleteQuestion(questionId) {
    const response = await this.api.post(`/api/delete_question/${questionId}`);
    return response.data;
  }
}

export default new QuestionService();