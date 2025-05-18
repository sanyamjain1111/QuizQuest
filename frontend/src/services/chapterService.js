// src/services/chapterService.js
import axios from 'axios';

const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:5000';

class ChapterService {
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
  
  // Get all subjects for dropdown
  async getSubjects() {
    const response = await this.api.get('/api/addchapter');
    return response.data;
  }
  
  // Get all chapters
  async getChapters() {
    const response = await this.api.get('/api/chapters');
    return response.data;
  }
  
  // Get single chapter details
  async getChapterDetails(chapterId) {
    const response = await this.api.get(`/api/editch/${chapterId}`);
    return response.data;
  }
  
  // Add new chapter
  async addChapter(chapterData) {
    // Create FormData instead of JSON
    const formData = new FormData();
    formData.append('chapter', chapterData.chapter_name);
    formData.append('sub_id', chapterData.subject_id);
    formData.append('description', chapterData.description);
    
    console.log('Adding chapter with data:', Object.fromEntries(formData));
    
    const response = await this.api.post('/api/addcompletech/', formData);
    return response.data;
  }
  
  // Update existing chapter
  async updateChapter(chapterId, chapterData) {
    // Using JSON format as required by the edit endpoint
    const data = {
      chapter: chapterData.chapter_name,
      sub_id: chapterData.subject_id,
      description: chapterData.description
    };
    
    const response = await this.api.post(`/api/editcompletech/${chapterId}`, data, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    return response.data;
  }
  
  // Delete chapter
  async deleteChapter(chapterId) {
    const response = await this.api.post(`/api/deletechapter/${chapterId}`);
    return response.data;
  }
}

export default new ChapterService();