<template>
  <div class="admin-dashboard-container">
    <!-- Reuse the AdminNavbarComponent we have -->
    <AdminNavbarComponent @search="handleSearch" />
    
    <div class="dashboard-header">
      <h1 class="dashboard-title">Admin Dashboard</h1>
    </div>
    
    <div class="main-content">
      <!-- Add Quiz Button -->
      <div class="action-buttons">
        <button class="add-quiz-btn" @click="navigateToAddQuiz">
          <span class="material-icons">add</span>
          Add New Quiz
        </button>
      </div>

      <!-- Quiz List Container -->
      <div class="quiz-container">
        <div class="quiz-count" v-if="quizzes.length > 0">
          <span class="material-icons">assessment</span>
          <span>{{ filteredQuizzes.length }} {{ filteredQuizzes.length === 1 ? 'Quiz' : 'Quizzes' }} Available</span>
        </div>
        <div v-if="quizzes.length > 0" class="quiz-list">
          <div v-for="(quiz, index) in filteredQuizzes" :key="quiz.quizid" class="quiz-item">
            <div class="quiz-badge">{{ index + 1 }}</div>
            <div class="quiz-item-header">
              <div class="quiz-item-title">
                <span class="quiz-id">Quiz #{{ quiz.quizid }}</span>
                <span class="chapter-name">{{ getChapterName(quiz.chapter_id) }}</span>
              </div>
              <div class="quiz-item-meta">
                <div class="meta-item">
                  <span class="material-icons">calendar_today</span>
                  <span>{{ formatDate(quiz.quiz_date) }}</span>
                </div>
                <div class="meta-item">
                  <span class="material-icons">quiz</span>
                  <span>{{ getQuestionCount(quiz.chapter_id) }} Questions</span>
                </div>
                <div class="meta-item">
                  <span class="material-icons">timer</span>
                  <span>{{ quiz.duration }} minutes</span>
                </div>
              </div>
            </div>
            <div class="quiz-item-actions">
              <button class="action-btn edit-btn" @click="editQuiz(quiz.quizid)">
                <span class="material-icons">edit</span>
                Edit
              </button>
              <button class="action-btn delete-btn" @click="confirmDelete(quiz.quizid)">
                <span class="material-icons">delete</span>
                Delete
              </button>
            </div>
          </div>
        </div>
        
        <!-- Empty state when no quizzes exist -->
        <div v-if="quizzes.length === 0" class="empty-state">
          <span class="material-icons empty-icon">quiz</span>
          <h3>No Quizzes Created</h3>
          <p>Create your first quiz by clicking the "Add New Quiz" button above</p>
        </div>
        
        <!-- Empty state when no quizzes match search -->
        <div v-if="quizzes.length > 0 && filteredQuizzes.length === 0" class="empty-state">
          <span class="material-icons empty-icon">search_off</span>
          <h3>No matching quizzes found</h3>
          <p>Try adjusting your search query</p>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteModal" tabindex="-1" aria-labelledby="deleteModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="deleteModalLabel">Confirm Delete</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            Are you sure you want to delete this quiz? This action cannot be undone.
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-danger" @click="deleteQuiz">Delete</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AdminNavbarComponent from './AdminNavbarComponent.vue';
import quizService from '../services/quizService';
import { Modal } from 'bootstrap';

export default {
  name: 'AdminDashboardComponent',
  components: {
    AdminNavbarComponent
  },
  data() {
    return {
      quizzes: [],
      chapters: [],
      questionCounts: [],
      searchQuery: '',
      deleteModal: null,
      quizToDelete: null
    };
  },
  computed: {
    filteredQuizzes() {
      if (!this.searchQuery) return this.quizzes;
      
      return this.quizzes.filter(quiz => {
        const chapterName = this.getChapterName(quiz.chapter_id).toLowerCase();
        return (
          quiz.quizid.toString().includes(this.searchQuery.toLowerCase()) ||
          chapterName.includes(this.searchQuery.toLowerCase()) ||
          quiz.quiz_date.toLowerCase().includes(this.searchQuery.toLowerCase())
        );
      });
    }
  },
  async mounted() {
    if (!localStorage.getItem('adminToken')) {
      this.$router.push('/');
      return;
    }
    
    await this.fetchData();
    this.initModal();
  },
  methods: {
    async fetchData() {
      try {
        const data = await quizService.getAllQuizzes();
        this.quizzes = data.quiz_details;
        this.chapters = data.chapters;
        this.questionCounts = data.counter;
      } catch (error) {
        console.error('Error fetching data:', error);
        if (error.response?.status === 401) {
          this.logout();
        }
      }
    },
    initModal() {
      this.$nextTick(() => {
        const modalEl = document.getElementById('deleteModal');
        if (modalEl) {
          this.deleteModal = new Modal(modalEl);
        }
      });
    },
    getChapterName(chapterId) {
      const chapter = this.chapters.find(c => c.chaoter_id === chapterId);
      return chapter ? chapter.chapter_name : 'Unknown Chapter';
    },
    getQuestionCount(chapterId) {
      const counter = this.questionCounts.find(c => c.chapter_id === chapterId);
      return counter ? counter.question_count : 0;
    },
    formatDate(dateString) {
      try {
        const date = new Date(dateString);
        return date.toLocaleDateString();
      } catch (e) {
        return dateString;
      }
    },
    handleSearch(query) {
      this.searchQuery = query;
    },
    navigateToAddQuiz() {
      this.$router.push('/admin/quizzes/add');
    },
    editQuiz(quizId) {
      this.$router.push(`/admin/quizzes/edit/${quizId}`);
    },
    confirmDelete(quizId) {
      this.quizToDelete = quizId;
      this.deleteModal.show();
    },
    async deleteQuiz() {
  if (!this.quizToDelete) return;
  
  try {
    // Call the service method and wait for the response
    await quizService.deleteQuiz(this.quizToDelete);
    
    // Remove the quiz from the list
    this.quizzes = this.quizzes.filter(quiz => quiz.quizid !== this.quizToDelete);
    
    // Close the modal and reset quizToDelete
    if (this.deleteModal) {
      this.deleteModal.hide();
    }
    this.quizToDelete = null;
    
    // Show success notification
    if (this.$toast) {
      this.$toast.success('Quiz deleted successfully', {
        position: 'top-right',
        duration: 3000
      });
    } else {
      console.log('Quiz deleted successfully');
    }
  } catch (error) {
    // Log the full error for debugging
    console.error('Error deleting quiz:', error);
    
    // Determine an appropriate error message
    let errorMessage = 'Failed to delete quiz. Please try again.';
    
    // Only try to access error properties if they exist
    if (error && typeof error === 'object') {
      if (error.response && error.response.data) {
        if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        } else if (error.response.data.error) {
          errorMessage = error.response.data.error;
        } else if (error.response.data.message) {
          errorMessage = error.response.data.message;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
    }
    
    // Display the error message
    if (this.$toast) {
      this.$toast.error(errorMessage, {
        position: 'top-right',
        duration: 3000
      });
    } else {
      console.error(errorMessage);
    }
  } finally {
    // Make sure modal is closed and state is reset even if there was an error
    if (this.deleteModal && this.quizToDelete) {
      this.deleteModal.hide();
      this.quizToDelete = null;
    }
  }
},
    logout() {
      localStorage.removeItem('adminToken');
      localStorage.removeItem('adminName');
      localStorage.removeItem('adminId');
      this.$router.push('/admin/login');
    }
  }
};
</script>

<style scoped>
/* Import Google Material Icons */
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

.admin-dashboard-container {
  font-family: 'Poppins', sans-serif;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ec 100%);
  color: #1c2541;
}

.dashboard-header {
  text-align: center;
  padding: 2rem 0 1rem;
  background: linear-gradient(135deg, rgba(11, 19, 43, 0.05) 0%, rgba(28, 37, 65, 0.1) 100%);
  border-bottom: 1px solid rgba(255, 126, 103, 0.2);
}

.dashboard-title {
  font-weight: 600;
  color: #0b132b;
  margin: 0;
  font-size: 2.2rem;
  position: relative;
  display: inline-block;
}

.dashboard-title:after {
  content: '';
  position: absolute;
  width: 60px;
  height: 4px;
  background: linear-gradient(90deg, #ff7e67, #3a506b);
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  border-radius: 2px;
}

.main-content {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 1.5rem;
}

.action-buttons {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 1.5rem;
}

.add-quiz-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #ff7e67 0%, #d45d50 100%);
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 10px rgba(255, 126, 103, 0.2);
}

.add-quiz-btn:hover {
  background: linear-gradient(135deg, #f27059 0%, #c54c40 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(255, 126, 103, 0.3);
}

/* New List Style for Quizzes */
.quiz-list {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  padding: 0.5rem;
}

.quiz-container {
  position: relative;
}

.quiz-container:before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 70%;
  height: 100%;
  background: radial-gradient(ellipse at top, rgba(255, 126, 103, 0.2) 0%, rgba(255, 126, 103, 0) 70%);
  z-index: 0;
  pointer-events: none;
}

.quiz-item {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid rgba(255, 126, 103, 0.2);
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}

.quiz-item:before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 126, 103, 0.2) 0%, rgba(255, 126, 103, 0) 70%);
  z-index: 1;
  opacity: 0.6;
  transition: opacity 0.3s ease;
}

.quiz-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
}

.quiz-item:hover:before {
  opacity: 1;
}

.quiz-item-header {
  flex: 1;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  position: relative;
  z-index: 2;
}

.quiz-item-title {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.quiz-id {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1a1b2e;
  display: inline-block;
  background: linear-gradient(135deg, rgba(26, 27, 46, 0.1) 0%, rgba(58, 80, 107, 0.05) 100%);
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  margin-bottom: 0.3rem;
  border-left: 3px solid #ff7e67;
}

.chapter-name {
  font-size: 1rem;
  color: #3a506b;
  font-weight: 500;
  display: inline-block;
}

.quiz-count {
  text-align: center;
  font-size: 1.1rem;
  font-weight: 500;
  color: #3a506b;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.quiz-count .material-icons {
  color: #ff7e67;
  font-size: 1.4rem;
}

.quiz-badge {
  position: absolute;
  top: -10px;
  left: -10px;
  background: linear-gradient(135deg, #ff7e67 0%, #d45d50 100%);
  color: white;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
  box-shadow: 0 4px 10px rgba(255, 126, 103, 0.3);
  z-index: 3;
}

.quiz-item-meta {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.6) 0%, rgba(255, 255, 255, 0.9) 100%);
  padding: 0.8rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(255, 126, 103, 0.1);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.9rem;
  color: #1a1b2e;
  font-weight: 500;
}

.meta-item .material-icons {
  font-size: 1.1rem;
  color: #ff7e67;
  background: rgba(255, 126, 103, 0.1);
  padding: 0.3rem;
  border-radius: 50%;
}

.quiz-item-actions {
  display: flex;
  gap: 0.8rem;
  padding: 1.2rem 1.5rem;
  align-items: center;
  background: linear-gradient(135deg, rgba(26, 27, 46, 0.03) 0%, rgba(26, 27, 46, 0.07) 100%);
  border-left: 2px solid rgba(255, 126, 103, 0.2);
  position: relative;
  z-index: 2;
}

.quiz-item-actions:before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: 100%;
  background: radial-gradient(circle at right, rgba(255, 126, 103, 0.1) 0%, rgba(255, 126, 103, 0) 70%);
  z-index: -1;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.3rem;
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 30px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.edit-btn {
  background: linear-gradient(135deg, #5bc0be 0%, #3a506b 100%);
  color: white;
  position: relative;
  overflow: hidden;
}

.edit-btn:before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: 0.5s;
}

.edit-btn:hover:before {
  left: 100%;
}

.edit-btn:hover {
  background: linear-gradient(135deg, #4ca8a7 0%, #2d405a 100%);
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(91, 192, 190, 0.3);
}

.delete-btn {
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  color: white;
  position: relative;
  overflow: hidden;
}

.delete-btn:before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: 0.5s;
}

.delete-btn:hover:before {
  left: 100%;
}

.delete-btn:hover {
  background: linear-gradient(135deg, #d44637 0%, #a53125 100%);
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(231, 76, 60, 0.3);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
  margin: 2rem 0;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  color: #a0aec0;
}

/* Modal customization */
.modal-content {
  border-radius: 12px;
  border: none;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.modal-header {
  background: linear-gradient(135deg, #1a1b2e 0%, #2c3145 100%);
  color: white;
  border-bottom: none;
  border-top-left-radius: 12px;
  border-top-right-radius: 12px;
  padding: 1.5rem;
}

.modal-title {
  font-weight: 600;
}

.modal-body {
  padding: 2rem;
  font-size: 1.1rem;
}

.modal-footer {
  border-top: none;
  padding: 1.5rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .dashboard-title {
    font-size: 1.8rem;
  }
  
  .quiz-item {
    flex-direction: column;
    align-items: stretch;
  }
  
  .quiz-item-actions {
    border-left: none;
    border-top: 2px solid rgba(255, 126, 103, 0.2);
    padding: 1rem 1.5rem;
    justify-content: center;
  }
  
  .action-buttons {
    justify-content: center;
  }
  
  .quiz-badge {
    top: 10px;
    left: 10px;
  }
}

@media (max-width: 576px) {
  .main-content {
    padding: 0 1rem;
    margin: 1.5rem auto;
  }
  
  .dashboard-title {
    font-size: 1.5rem;
  }
  
  .quiz-item-header {
    padding: 1rem;
  }
  
  .quiz-item-meta {
    flex-direction: column;
    gap: 0.6rem;
  }
  
  .action-btn {
    padding: 0.4rem 0.8rem;
    font-size: 0.8rem;
  }
}
</style>