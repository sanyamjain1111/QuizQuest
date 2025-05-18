import axios from 'axios';

const api = axios.create({
  baseURL: process.env.VUE_APP_API_URL || 'http://127.0.0.1:5000',
  timeout: 15000,
});

// Setup request interceptor for authentication
api.interceptors.request.use(config => {
  // Check for admin token first, then regular user token
  const adminToken = localStorage.getItem('adminToken');
  const userToken = localStorage.getItem('token');
  
  if (adminToken) {
    config.headers.Authorization = `Bearer ${adminToken}`;
  } else if (userToken) {
    config.headers.Authorization = `Bearer ${userToken}`;
  }
  
  return config;
});

// Define API service methods
export default {
  // Authentication
  login(credentials) {
    return api.post('/api/login', credentials);
  },
  
  admin(credentials) {
    return api.post('/api/admin', credentials);
  },

  // Student User APIs
  getAcademicDetails() {
    return api.get('/api/academic_details');
  },

  getPersonalDetails() {
    return api.get('/api/personal_details');
  },
  getStudentAcademicDetails() {
    return api.get('/api/student_academic_details');
  },

  getLiveQuizzes() {
    return api.get('/api/livequiz');
  },

  getQuizInstructions(quizId) {
    return api.get(`/api/quizinstructions/${quizId}`);
  },

  startQuiz(quizId) {
    return api.get(`/api/startquiz/${quizId}`);
  },

  submitQuiz(quizId, formData) {
    console.log(`Calling submitQuiz API with quizId: ${quizId}`);

    // Log formData for debugging
    for (let pair of formData.entries()) {
      console.log(pair[0] + ': ' + pair[1]);
    }

    return api.post(`/api/submitquiz/${quizId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },

  updatePersonalDetails(data) {
    return api.post('/api/editcomplete', data);
  },

  getEditForm(field) {
    return api.get(`/api/edit/${field}`);
  },

  submitComplaint(data) {
    return api.post('/api/complaint', data);
  },

  getQuizScores(quizId, uid, timeTaken) {
    return api.get(`/api/scores/${quizId}/${uid}/${timeTaken}`);
  },
  
  getQuizTranscript(quizId, uid) {
    return api.get(`/api/transcript/${quizId}/${uid}`);
  },

  uploadImage(formData) {
    const uid = localStorage.getItem('uid');
    return api.post(`/api/upload/${uid}`, formData);
  },

  // Admin APIs
  getStudentPersonalDetails() {
    return api.get('/api/student_personal_details');
  },
  
  deleteUser(userId) {
    return api.get(`/api/delete_user/${userId}`);
  },
  
  // Admin dashboard stats
  getAdminDashboardStats() {
    return api.get('/api/admin/dashboard/stats');
  },
  
  // Quiz management
  getQuizzesList() {
    return api.get('/api/admin/quizzes');
  },
  
  createQuiz(quizData) {
    return api.post('/api/admin/quizzes/create', quizData);
  },
  
  updateQuiz(quizId, quizData) {
    return api.put(`/api/admin/quizzes/${quizId}`, quizData);
  },
  
  deleteQuiz(quizId) {
    return api.delete(`/api/admin/quizzes/${quizId}`);
  },
  deleteuser(userId) {
    return api.delete(`/api/delete_user/${userId}`);
  },
  // User management
  
  deleteFile(fileId) {
    return api.delete(`/api/admin/files/${fileId}`);
  }
};