<template>
  <div class="livequiz-container">
    <NavbarComponent @search="handleSearch" />
    
    <div class="quiz-header">
      <h1 class="quiz-title">{{ message }}</h1>
    </div>
    
    <div class="main-content">
      <div class="quiz-card">
        <div class="quiz-card-header">
          <h2 class="card-title">
            <span class="material-icons quiz-icon">quiz</span>
            Upcoming Quizzes
          </h2>
        </div>
        
        <div class="quiz-table-container">
          <table class="quiz-table" v-if="quizDetails.length > 0">
            <thead>
              <tr>
                <th>Quiz ID</th>
                <th>Questions</th>
                <th>Date</th>
                <th>Duration</th>
                <th colspan="2">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(quiz, index) in quizDetails" :key="quiz.quizid" class="quiz-row">
                <td class="quiz-id">{{ quiz.quizid }}</td>
                <td class="question-count">{{ listForQuiz[index].questioncount }}</td>
                <td class="quiz-date">{{ quiz.quiz_date }}</td>
                <td class="quiz-duration">{{ quiz.duration }}</td>
                <td class="action-cell">
                  <button 
                    class="view-button"
                    @click="setModalData(quiz, index)"
                  >
                    <span class="material-icons">visibility</span>
                    View
                  </button>
                </td>
                <td class="action-cell">
                  <router-link 
                    v-if="isQuizAvailableToday(quiz.quiz_date)"
                    :to="{ name: 'QuizInstructions', params: { quiz_id: quiz.quizid } }"
                    class="attempt-link"
                    style="text-decoration: none; color: inherit;"
                  >
                    <button 
                      class="attempt-button"
                      :class="{ 'attempted': isQuizAttempted(quiz.quizid) }"
                      :disabled="isQuizAttempted(quiz.quizid)"
                    >
                      <span class="material-icons">
                        {{ isQuizAttempted(quiz.quizid) ? 'check_circle' : 'play_arrow' }}
                      </span>
                      {{ isQuizAttempted(quiz.quizid) ? 'Attempted' : 'Attempt' }}
                    </button>
                  </router-link>
                  <div v-else class="not-available">
                    <span class="material-icons">schedule</span>
                    Upcoming
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          
          <!-- Empty state when no quizzes are available -->
          <div v-else class="empty-state">
            <span class="material-icons empty-icon">event_busy</span>
            <h3>No Upcoming Quizzes</h3>
            <p>Check back later for scheduled quizzes</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Backdrop -->
    <div v-if="showModal" class="modal-backdrop" @click="closeModal"></div>

    <!-- Quiz Modal -->
    <div v-if="showModal" class="modal-container" role="dialog" aria-labelledby="quizModalLabel">
      <div class="modal-content">
        <div class="modal-header">
          <h3 class="modal-title" id="quizModalLabel">Quiz Details</h3>
          <button type="button" class="close-button" @click="closeModal" aria-label="Close">
            <span class="material-icons">close</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="detail-item">
            <div class="detail-label">Quiz ID</div>
            <div class="detail-value">{{ modalData.quizid }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">Chapter</div>
            <div class="detail-value">{{ modalData.chapter_name }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">Subject</div>
            <div class="detail-value">{{ modalData.subjectname }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">Number of Questions</div>
            <div class="detail-value">{{ modalData.questioncount }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">Date of Quiz</div>
            <div class="detail-value">{{ modalData.quiz_date }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">Duration</div>
            <div class="detail-value">{{ modalData.duration }}</div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="modal-close-btn" @click="closeModal">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import NavbarComponent from './NavbarComponent.vue';

export default {
  name: 'LiveQuizComponent',
  components: {
    NavbarComponent
  },
  data() {
    return {
      message: 'Live Quizzes',
      quizDetails: [],
      listForQuiz: [],
      quizResponses: [],
      currId: '',
      searchQuery: '',
      today: new Date().toISOString().split('T')[0], // Current date in YYYY-MM-DD format
      modalData: {
        quizid: '',
        chapter_name: '',
        subjectname: '',
        questioncount: '',
        quiz_date: '',
        duration: ''
      },
      showModal: false
    };
  },
  async mounted() {
    await this.fetchLiveQuizData();
    
    // Add event listener for escape key to close modal
    document.addEventListener('keydown', this.handleKeyDown);
  },
  beforeUnmount() {
    // Remove event listener
    document.removeEventListener('keydown', this.handleKeyDown);
  },
  methods: {
    async fetchLiveQuizData() {
      try {
        const response = await axios.get('/api/livequiz', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        this.quizDetails = response.data.quiz_details;
        this.listForQuiz = response.data.listforquiz;
        this.quizResponses = response.data.quizresponses;
        this.currId = response.data.curr_id;
        
        console.log('Quiz Responses:', this.quizResponses);
        console.log('Quiz Details:', this.quizDetails);
      } catch (error) {
        console.error('Error fetching live quiz data:', error);
        if (error.response?.status === 401) {
          this.$router.push('/');
        }
      }
    },
    async setModalData(quiz, index) {
      // Set modal data first
      this.modalData = {
        quizid: quiz.quizid,
        chapter_name: this.listForQuiz[index].chapter_name,
        subjectname: this.listForQuiz[index].subjectname,
        questioncount: this.listForQuiz[index].questioncount,
        quiz_date: quiz.quiz_date,
        duration: quiz.duration
      };
      
      // Show modal
      this.showModal = true;
      
      // Prevent body scrolling when modal is open
      document.body.style.overflow = 'hidden';
      
      // Send hidden API request to mark quiz as viewed
      await this.markQuizAsViewed(quiz.quizid);
    },
    async markQuizAsViewed(quizId) {
      try {
        const response = await axios.post(`/api/viewed/${quizId}`, {}, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        console.log('Quiz marked as viewed:', response.data.message);
      } catch (error) {
        // Handle the error silently in background, or show a subtle notification
        console.error('Error marking quiz as viewed:', error);
        
        // Optional: Handle specific error cases
        if (error.response?.status === 401) {
          // Token expired, redirect to login
          this.$router.push('/');
        } else if (error.response?.status === 404) {
          console.warn('User not found');
        } else if (error.response?.status === 200 && error.response?.data?.message === "Quiz already viewed") {
          console.log('Quiz was already viewed by this user');
        }
      }
    },
    closeModal() {
      this.showModal = false;
      // Re-enable body scrolling
      document.body.style.overflow = '';
    },
    isQuizAttempted(quizId) {
      // Convert quizId to string for comparison to ensure type matching
      const quizIdStr = String(quizId);
      return this.quizResponses.some(response => String(response.quizid) === quizIdStr);
    },
    isQuizAvailableToday(quizDate) {
      // Check if the quiz date is today
      return quizDate === this.today;
    },
    handleKeyDown(e) {
      if (e.key === 'Escape' && this.showModal) {
        this.closeModal();
      }
    },
    handleSearch(query) {
      this.searchQuery = query;
      // You could implement search functionality for quizzes here
    }
  }
};
</script>

<style scoped>
/* Import Google Material Icons */
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

.livequiz-container {
  font-family: 'Poppins', sans-serif;
  min-height: 100vh;
  max-width: 1200px; /* Same width as Dashboard */
  margin: 0 auto;   /* Center the container */
  padding: 0 1.5rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ec 100%);
  color: #1c2541;
}

.quiz-header {
  text-align: center;
  padding: 2rem 0 1rem;
  background: linear-gradient(135deg, rgba(11, 19, 43, 0.05) 0%, rgba(28, 37, 65, 0.1) 100%);
  border-bottom: 1px solid rgba(91, 192, 190, 0.2);
}

.quiz-title {
  font-weight: 600;
  color: #0b132b;
  margin: 0;
  font-size: 2.2rem;
  position: relative;
  display: inline-block;
}

.quiz-title:after {
  content: '';
  position: absolute;
  width: 60px;
  height: 4px;
  background: linear-gradient(90deg, #5bc0be, #3a506b);
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

.quiz-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  border: 1px solid rgba(91, 192, 190, 0.2);
}

.quiz-card-header {
  background: linear-gradient(135deg, #0b132b 0%, #1c2541 100%);
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
}

.quiz-card-header:before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(91, 192, 190, 0.2) 0%, rgba(91, 192, 190, 0) 70%);
  z-index: 1;
}

.card-title {
  color: white;
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
}

.quiz-icon {
  margin-right: 0.5rem;
}

.quiz-table-container {
  padding: 1.5rem;
  overflow-x: auto;
}

.quiz-table {
  width: 100%;
  border-collapse: collapse;
  border-spacing: 0;
  margin-bottom: 0;
}

.quiz-table thead th {
  background-color: #f1f5f9;
  color: #1c2541;
  font-weight: 600;
  text-align: left;
  padding: 1rem;
  border-bottom: 2px solid #e2e8f0;
  font-size: 0.95rem;
}

.quiz-table tbody td {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
  color: #3a506b;
  font-size: 0.95rem;
}

.quiz-row {
  transition: background-color 0.2s ease;
}

.quiz-row:hover {
  background-color: #f8fafc;
}

.action-cell {
  width: 120px;
  text-align: center;
}

.view-button, .attempt-button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-family: 'Poppins', sans-serif;
  font-weight: 500;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  gap: 0.5rem;
  width: 100%;
}

.view-button {
  background: linear-gradient(135deg, #5bc0be 0%, #3a506b 100%);
  color: white;
}

.view-button:hover {
  background: linear-gradient(135deg, #4ca8a7 0%, #2d405a 100%);
  box-shadow: 0 4px 12px rgba(91, 192, 190, 0.3);
  transform: translateY(-2px);
}

.attempt-button {
  background: linear-gradient(135deg, #6d28d9 0%, #4c1d95 100%);
  color: white;
}

.attempt-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #5b21b6 0%, #3b1583 100%);
  box-shadow: 0 4px 12px rgba(109, 40, 217, 0.3);
  transform: translateY(-2px);
}

.attempt-button.attempted {
  background: #a0aec0;
  cursor: not-allowed;
}

.not-available {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  font-size: 0.9rem;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 8px;
  background-color: #f1f5f9;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  color: #a0aec0;
}

/* Modal Styles */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1050;
  animation: fadeIn 0.2s ease-out;
}

.modal-container {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1055;
  width: 90%;
  max-width: 600px;
  animation: modalZoomIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes modalZoomIn {
  from { opacity: 0; transform: translate(-50%, -50%) scale(0.95); }
  to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
}

.modal-content {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.modal-header {
  background: linear-gradient(135deg, #0b132b 0%, #1c2541 100%);
  color: white;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}

.modal-header:before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(91, 192, 190, 0.2) 0%, rgba(91, 192, 190, 0) 70%);
  z-index: 1;
}

.modal-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  position: relative;
  z-index: 2;
}

.close-button {
  background: transparent;
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  border-radius: 50%;
  transition: background-color 0.2s ease;
  position: relative;
  z-index: 2;
}

.close-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.modal-body {
  padding: 1.5rem;
}

.detail-item {
  display: flex;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.detail-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.detail-label {
  font-weight: 600;
  width: 40%;
  color: #1c2541;
}

.detail-value {
  width: 60%;
  color: #3a506b;
}

.modal-footer {
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: flex-end;
  background-color: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

.modal-close-btn {
  background: linear-gradient(135deg, #5bc0be 0%, #3a506b 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-family: 'Poppins', sans-serif;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.modal-close-btn:hover {
  background: linear-gradient(135deg, #4ca8a7 0%, #2d405a 100%);
  box-shadow: 0 4px 12px rgba(91, 192, 190, 0.3);
  transform: translateY(-2px);
}

/* Responsiveness */
@media (max-width: 1024px) {
  .quiz-title {
    font-size: 1.8rem;
  }
  
  .main-content {
    padding: 0 1rem;
  }
}

@media (max-width: 768px) {
  .quiz-title {
    font-size: 1.5rem;
  }
  
  .quiz-table thead th,
  .quiz-table tbody td {
    padding: 0.75rem;
    font-size: 0.85rem;
  }
  
  .view-button, .attempt-button {
    padding: 0.4rem 0.75rem;
    font-size: 0.8rem;
  }
  
  .card-title {
    font-size: 1.3rem;
  }
  
  .detail-item {
    flex-direction: column;
  }
  
  .detail-label, .detail-value {
    width: 100%;
  }
  
  .detail-value {
    margin-top: 0.25rem;
  }
}

@media (max-width: 576px) {
  .quiz-header {
    padding: 1.5rem 0 0.75rem;
  }
  
  .quiz-title {
    font-size: 1.3rem;
  }
  
  .quiz-title:after {
    width: 40px;
    height: 3px;
  }
  
  .main-content {
    margin: 1rem auto;
  }
  
  .quiz-card-header {
    padding: 1rem;
  }
  
  .card-title {
    font-size: 1.1rem;
  }
  
  .quiz-table-container {
    padding: 1rem;
  }
  
  /* Stack quiz details on mobile */
  .quiz-table, .quiz-table thead, .quiz-table tbody, .quiz-table th, .quiz-table td, .quiz-table tr {
    display: block;
  }
  
  .quiz-table thead tr {
    position: absolute;
    top: -9999px;
    left: -9999px;
  }
  
  .quiz-row {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    margin-bottom: 1rem;
    padding: 0.5rem;
    position: relative;
  }
  
  .quiz-table td {
    border: none;
    border-bottom: 1px solid #edf2f7;
    position: relative;
    padding-left: 50%;
    text-align: right;
  }


/* Make sure the button doesn't inherit text decoration */
.attempt-button[data-v-593aaac8] {
  text-decoration: none !important;
}

  
  .quiz-table td:before {
    position: absolute;
    top: 1rem;
    left: 1rem;
    width: 45%;
    padding-right: 10px;
    white-space: nowrap;
    text-align: left;
    font-weight: 600;
  }
  
  /* Add labels for mobile view */
  .quiz-table td:nth-of-type(1):before { content: "Quiz ID"; }
  .quiz-table td:nth-of-type(2):before { content: "Questions"; }
  .quiz-table td:nth-of-type(3):before { content: "Date"; }
  .quiz-table td:nth-of-type(4):before { content: "Duration"; }
  .quiz-table td:nth-of-type(5):before { content: "View"; }
  .quiz-table td:nth-of-type(6):before { content: "Attempt"; }
  
  .quiz-table td:last-child {
    border-bottom: none;
  }
  
  .action-cell {
    width: 100%;
    text-align: right;
  }
  
  .view-button, .attempt-button {
    width: auto;
    display: inline-flex;
  }
  
  .modal-container {
    width: 95%;
  }
  
  .modal-header {
    padding: 1rem;
  }
  
  .modal-title {
    font-size: 1.2rem;
  }
  
  .modal-body {
    padding: 1rem;
  }
  
  .empty-state {
    padding: 2rem 1rem;
  }
  
  .empty-icon {
    font-size: 3rem;
  }
}

/* Accessibility improvements */
@media (prefers-reduced-motion: reduce) {
  .view-button:hover,
  .attempt-button:hover,
  .modal-close-btn:hover {
    transform: none;
  }
  
  .modal-backdrop,
  .modal-container {
    animation: none;
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .livequiz-container {
    background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
    color: #e2e8f0;
  }
  
  .quiz-title {
    color: #f7fafc;
  }
  
  .quiz-card {
    background: #2d3748;
    border-color: rgba(91, 192, 190, 0.3);
  }
  
  .quiz-table thead th {
    background-color: #1a202c;
    color: #e2e8f0;
    border-bottom-color: #4a5568;
  }
  
  .quiz-table tbody td {
    border-bottom-color: #4a5568;
    color: #cbd5e0;
  }
  
  .quiz-row:hover {
    background-color: #364156;
  }
  
  .empty-icon {
    color: #718096;
  }
  
  .modal-content {
    background-color: #2d3748;
  }
  
  .modal-footer {
    background-color: #1a202c;
    border-top-color: #4a5568;
  }
  
  .detail-item {
    border-bottom-color: #4a5568;
  }
  
  .detail-label {
    color: #e2e8f0;
  }
  
  .detail-value {
    color: #cbd5e0;
  }
  
  .not-available {
    background-color: #1a202c;
    color: #a0aec0;
  }
}
</style>