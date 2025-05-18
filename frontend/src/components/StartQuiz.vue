<template>
  <div class="quiz-container">
    <!-- Special Quiz Timer Navbar -->
    <div class="quiz-navbar">
      <h2 class="quiz-nav-title">MCQ Based Quiz</h2>
      <div class="timer" :class="{ 'timer-warning': timeLeft < 60 }">
        <span class="material-icons timer-icon">timer</span>
        Time Left: {{ formatTime(timeLeft) }}
      </div>
      <div class="controls">
        <button class="control-button" @click="toggleTimer">
          <span class="material-icons">{{ isPaused ? 'play_arrow' : 'pause' }}</span>
          {{ isPaused ? 'Resume' : 'Pause' }}
        </button>
      </div>
    </div>
    
    <div class="main-content">
      <!-- Question Progress Panel -->
      <div class="question-panel">
        <div class="panel-header">
          <span class="material-icons">visibility</span>
          Question Navigation
        </div>
        <div class="question-grid">
          <div 
            v-for="(question, index) in questions" 
            :key="question.qid"
            class="question-number" 
            :class="{ 
              'answered': answeredQuestions.includes(question.qid),
              'current': currentQuestionIndex === index
            }"
            @click="navigateToQuestion(index)"
          >
            {{ index + 1 }}
          </div>
        </div>
        <div class="legend">
          <div class="legend-item">
            <div class="legend-marker answered"></div>
            <span>Answered</span>
          </div>
          <div class="legend-item">
            <div class="legend-marker"></div>
            <span>Unanswered</span>
          </div>
          <div class="legend-item">
            <div class="legend-marker current"></div>
            <span>Current</span>
          </div>
        </div>
      </div>

      <!-- Quiz Content -->
      <div class="quiz-content">
        <div class="quiz-card">
          <div class="quiz-card-header">
            <h2 class="card-title">
              <span class="material-icons quiz-icon">quiz</span>
              Question {{ currentQuestionIndex + 1 }} of {{ questions.length }}
            </h2>
          </div>
          
          <div class="question-container" v-if="questions.length > 0 && currentQuestionIndex < questions.length">
            <h3 class="question-text">{{ questions[currentQuestionIndex].question }}</h3>
            
            <div class="options-container">
              <label 
                v-for="option in getOptionsForCurrentQuestion()" 
                :key="option.option_id" 
                class="option-label"
                :class="{ 'selected': selectedOptions[questions[currentQuestionIndex].qid] === option.option_id }"
              >
                <input 
                  type="radio" 
                  :name="'question_' + questions[currentQuestionIndex].qid" 
                  :value="option.option_id"
                  v-model="selectedOptions[questions[currentQuestionIndex].qid]"
                  @change="markAsAnswered(questions[currentQuestionIndex].qid)"
                >
                <span class="option-text">{{ option.option }}</span>
                <span class="checkmark"></span>
              </label>
            </div>
            
            <div class="navigation-buttons">
              <button 
                class="nav-button prev-button" 
                @click="previousQuestion" 
                :disabled="currentQuestionIndex === 0"
              >
                <span class="material-icons">arrow_back</span>
                Previous
              </button>
              <button 
                class="nav-button next-button" 
                @click="nextQuestion" 
                :disabled="currentQuestionIndex === questions.length - 1"
              >
                Next
                <span class="material-icons">arrow_forward</span>
              </button>
            </div>
          </div>
          
          <div class="quiz-submission">
            <button type="button" class="submit-button" @click="submitQuiz" :disabled="isSubmitting">
              <span class="material-icons">send</span>
              {{ isSubmitting ? 'Submitting...' : 'Submit Quiz' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Pause Modal -->
    <div class="modal-backdrop" v-if="isPaused" @click.self="resumeTimer"></div>
    <div class="modal" v-if="isPaused">
      <div class="modal-content">
        <span class="material-icons pause-icon">pause_circle_filled</span>
        <h3 class="modal-title">Quiz Paused</h3>
        <p class="modal-text">Your quiz timer has been paused. Click resume to continue.</p>
        <button class="resume-button" @click="resumeTimer">
          <span class="material-icons">play_arrow</span>
          Resume Quiz
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';


export default {
  name: 'StartQuiz',
  data() {
    return {
      quizId: this.$route.params.quiz_id,
      questions: [],
      options: [],
      duration: 0,
      currentQuestionIndex: 0,
      selectedOptions: {},
      answeredQuestions: [],
      timeLeft: 0,
      timerInterval: null,
      startTime: null,
      isPaused: false,
      isSubmitting: false
    };
  },
  async mounted() {
    // Prevent back button
    history.pushState(null, "", location.href);
    window.onpopstate = () => {
      history.pushState(null, "", location.href);
    };
    
    // Set up the quiz ID
    this.quizId = this.$route.params.quiz_id;
    if (!this.quizId || this.quizId === 'undefined') {
      this.quizId = localStorage.getItem('currentQuizId');
    }
    
    if (!this.quizId || this.quizId === 'undefined') {
      console.error('Quiz ID is undefined! Cannot proceed.');
      alert('Error: Quiz ID is missing. Please return to the quiz selection page.');
      this.$router.push('/quizzes');
      return;
    }
    
    await this.fetchQuizData();
    this.startQuiz();
    document.addEventListener('keydown', this.handleKeyDown);
    window.addEventListener('beforeunload', this.handleBeforeUnload);
  },
  beforeUnmount() {
    // Clean up event listeners when component is destroyed
    document.removeEventListener('keydown', this.handleKeyDown);
    window.removeEventListener('beforeunload', this.handleBeforeUnload);
    
    // Ensure any modal-related classes are removed from body
    document.body.classList.remove('modal-open');
    
    // Clear any active timers
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
    }
  },
  methods: {
    async fetchQuizData() {
      try {
        // Changed from /api/start_quiz/ to /api/startquiz/ to match the backend route
        const response = await axios.get(`/api/startquiz/${this.quizId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        this.questions = response.data.questions;
        this.options = response.data.options;
        this.duration = response.data.duration;
        this.timeLeft = this.duration * 60;
      } catch (error) {
        console.error('Error fetching quiz data:', error);
        if (error.response?.status === 401) {
          this.$router.push('/');
        } else if (error.response?.status === 404) {
          alert('Quiz endpoint not found. Please check with the administrator.');
          this.$router.push('/quizzes');
        }
      }
    },
    startQuiz() {
      this.startTime = new Date();
      this.startTimer();
    },
    startTimer() {
      if (!this.timerInterval) {
        this.timerInterval = setInterval(this.updateTimer, 1000);
      }
    },
    updateTimer() {
      if (this.timeLeft > 0) {
        this.timeLeft--;
      } else {
        this.submitQuiz(); // Auto-submit when time runs out
      }
    },
    formatTime(seconds) {
      const minutes = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    },
    pauseTimer() {
      if (this.timerInterval) {
        clearInterval(this.timerInterval);
        this.timerInterval = null;
      }
      this.isPaused = true;
    },
    resumeTimer() {
      this.isPaused = false;
      this.startTimer();
    },
    toggleTimer() {
      if (this.isPaused) {
        this.resumeTimer();
      } else {
        this.pauseTimer();
      }
    },
    getOptionsForCurrentQuestion() {
      if (this.questions.length === 0 || this.currentQuestionIndex >= this.questions.length) {
        return [];
      }
      const currentQuestionId = this.questions[this.currentQuestionIndex].qid;
      return this.options.filter(option => option.question_id === currentQuestionId);
    },
    markAsAnswered(questionId) {
      if (!this.answeredQuestions.includes(questionId)) {
        this.answeredQuestions.push(questionId);
      }
    },
    navigateToQuestion(index) {
      if (index >= 0 && index < this.questions.length) {
        this.currentQuestionIndex = index;
      }
    },
    nextQuestion() {
      if (this.currentQuestionIndex < this.questions.length - 1) {
        this.currentQuestionIndex++;
      }
    },
    previousQuestion() {
      if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex--;
      }
    },
    handleKeyDown(e) {
      if (this.isPaused) return;
      
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
        this.nextQuestion();
      } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
        this.previousQuestion();
      } else if (e.key >= '1' && e.key <= '9') {
        const index = parseInt(e.key) - 1;
        if (index < this.questions.length) {
          this.navigateToQuestion(index);
        }
      }
    },
      async submitQuiz() {
        console.log('Submit quiz called - proceeding with submission directly');
        
        // Prevent double submission
        if (this.isSubmitting) {
          return;
        }
        
        // Pause timer during submission
        if (this.timerInterval) {
          clearInterval(this.timerInterval);
          this.timerInterval = null;
        }
        
        this.isSubmitting = true;
        
        try {
          const endTime = new Date();
          const timeTaken = Math.floor((endTime - this.startTime) / 1000);
          
          const formData = new FormData();
          Object.entries(this.selectedOptions).forEach(([questionId, optionId]) => {
            formData.append(`question_${questionId}`, optionId);
          });
          
          formData.append('time_taken', timeTaken);
          
          const uid = localStorage.getItem('uid');
          
          // Debug logs to ensure API call parameters are correct
          console.log(`Submitting quiz ${this.quizId} with timeTaken ${timeTaken} and uid ${uid}`);
          
          // Use axios directly with authorization header
          const response = await axios.post(`/api/submitquiz/${this.quizId}`, formData, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
          });
          
          console.log('API Response:', response.data);
          
          // Use the quiz_id from the current component state rather than response
          // This ensures we have a valid ID for navigation
          this.$router.push(`/scores/${this.quizId}/${uid || 'guest'}/${timeTaken}`);
          
        } catch (error) {
          console.error('Error submitting quiz:', error);
          // More detailed error handling
          if (error.response) {
            console.error('Response error data:', error.response.data);
            console.error('Response error status:', error.response.status);
            alert(`Submission error (${error.response.status}): ${error.response.data.message || 'Unknown error'}`);
          } else if (error.request) {
            console.error('Request error:', error.request);
            alert('Network error: No response from server. Please check your connection.');
          } else {
            console.error('Error message:', error.message);
            alert('Error: ' + error.message);
          }
          
          // Reset submission state
          this.isSubmitting = false;
          
          // Resume the quiz in case of error
          this.isPaused = false;
          this.startTimer();
        }
      },
    handleBeforeUnload(e) {
      const message = 'Leaving this page will end your quiz session. Are you sure?';
      e.returnValue = message;
      return message;
    }
  }
};
</script>

<style scoped>
/* Import Google Material Icons */
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

.quiz-container {
  font-family: 'Poppins', sans-serif;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ec 100%);
  color: #1c2541;
  position: relative;
  padding-top: 60px; /* Space for fixed navbar */
}

/* Quiz Navbar */
.quiz-navbar {
  height: 60px;
  background: linear-gradient(135deg, #0b132b 0%, #1c2541 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.quiz-nav-title {
  font-weight: 600;
  font-size: 1.3rem;
  margin: 0;
  display: flex;
  align-items: center;
}

.timer {
  display: flex;
  align-items: center;
  font-size: 1.2rem;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.1);
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.timer-icon {
  margin-right: 0.5rem;
}

.timer-warning {
  background: rgba(255, 59, 48, 0.2);
  color: #ffcc00;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
}

.controls {
  display: flex;
}

.control-button {
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(91, 192, 190, 0.2);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.5rem 1rem;
  font-family: 'Poppins', sans-serif;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.control-button:hover {
  background: rgba(91, 192, 190, 0.4);
  transform: translateY(-2px);
}

.control-button .material-icons {
  margin-right: 0.3rem;
  font-size: 1.1rem;
}

/* Main Content Layout */
.main-content {
  display: flex;
  padding: 1.5rem;
  min-width: 1400px;
  max-width: 1400px;
  margin: 0 auto;
  gap: 1.5rem;
}

/* Question Panel */
.question-panel {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  border: 1px solid rgba(91, 192, 190, 0.2);
  width: 300px;
  height: fit-content;
  position: sticky;
  top: 80px;
}

.panel-header {
  background: linear-gradient(135deg, #0b132b 0%, #1c2541 100%);
  color: white;
  padding: 1rem;
  font-weight: 600;
  font-size: 1rem;
  display: flex;
  align-items: center;
}

.panel-header .material-icons {
  margin-right: 0.5rem;
}

.question-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 1rem;
  justify-content: center;
}

.question-number {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
  background: #e2e8f0;
  color: #1c2541;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.question-number:hover {
  transform: scale(1.1);
  box-shadow: 0 0 0 2px rgba(91, 192, 190, 0.3);
}

.question-number.answered {
  background: #5bc0be;
  color: white;
}

.question-number.current {
  border: 2px solid #6d28d9;
  box-shadow: 0 0 0 2px rgba(109, 40, 217, 0.3);
}

.legend {
  padding: 0.5rem 1rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-top: 1px solid #e2e8f0;
}

.legend-item {
  display: flex;
  align-items: center;
  font-size: 0.8rem;
  color: #3a506b;
}

.legend-marker {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 8px;
  background: #e2e8f0;
}

.legend-marker.answered {
  background: #5bc0be;
}

.legend-marker.current {
  background: #e2e8f0;
  border: 2px solid #6d28d9;
  width: 8px;
  height: 8px;
}

/* Quiz Content */
.quiz-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.quiz-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  border: 1px solid rgba(91, 192, 190, 0.2);
  margin-bottom: 1.5rem;
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

.question-container {
  padding: 1.5rem;
}

.question-text {
  font-size: 1.3rem;
  color: #1c2541;
  margin-top: 0;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.options-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
}

.option-label {
  display: flex;
  position: relative;
  padding: 1rem 1.5rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.option-label:hover {
  background: #f1f5f9;
  border-color: #cbd5e0;
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.option-label.selected {
  background: rgba(91, 192, 190, 0.1);
  border-color: #5bc0be;
}

.option-label input[type="radio"] {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.option-text {
  flex: 1;
  padding-right: 2rem;
  font-size: 1.1rem;
  color: #3a506b;
}

.checkmark {
  position: absolute;
  top: 50%;
  right: 1.5rem;
  transform: translateY(-50%);
  height: 20px;
  width: 20px;
  background-color: #fff;
  border: 2px solid #cbd5e0;
  border-radius: 50%;
}

.option-label:hover .checkmark {
  border-color: #5bc0be;
}

.option-label.selected .checkmark {
  background-color: #5bc0be;
  border-color: #5bc0be;
}

.option-label.selected .checkmark:after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: white;
}

.navigation-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 1rem;
}

.nav-button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-family: 'Poppins', sans-serif;
  font-weight: 500;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  gap: 0.5rem;
}

.prev-button {
  background: linear-gradient(135deg, #3a506b 0%, #1c2541 100%);
  color: white;
}

.prev-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #324559 0%, #151d30 100%);
  box-shadow: 0 4px 12px rgba(58, 80, 107, 0.3);
  transform: translateY(-2px);
}

.next-button {
  background: linear-gradient(135deg, #5bc0be 0%, #3a506b 100%);
  color: white;
}

.next-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #4ca8a7 0%, #2d405a 100%);
  box-shadow: 0 4px 12px rgba(91, 192, 190, 0.3);
  transform: translateY(-2px);
}

.nav-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quiz-submission {
  padding: 1.5rem;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: center;
}

.submit-button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 2rem;
  background: linear-gradient(135deg, #6d28d9 0%, #4c1d95 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-family: 'Poppins', sans-serif;
  font-weight: 500;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  gap: 0.5rem;
}

.submit-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #5b21b6 0%, #3b1583 100%);
  box-shadow: 0 4px 12px rgba(109, 40, 217, 0.3);
  transform: translateY(-2px);
}

.submit-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Modal Styles for Pause Only */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(27, 37, 65, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(4px);
}

.modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2001;
  width: 90%;
  max-width: 500px;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.modal-title {
  font-size: 1.5rem;
  margin: 0.5rem 0 1rem;
  color: #1c2541;
}

.modal-text {
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  color: #3a506b;
  line-height: 1.5;
}

.resume-button {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-family: 'Poppins', sans-serif;
  font-weight: 500;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
  background: linear-gradient(135deg, #6d28d9 0%, #4c1d95 100%);
  color: white;
}

.resume-button:hover {
  background: linear-gradient(135deg, #5b21b6 0%, #3b1583 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(109, 40, 217, 0.3);
}

.pause-icon {
  font-size: 3rem;
  color: #6d28d9;
  margin-bottom: 0.5rem;
}

/* Responsiveness */
@media (max-width: 1440px) {
  .main-content {
    min-width: 100%;
    flex-direction: column;
  }
  
  .question-panel {
    width: 100%;
    position: static;
    margin-bottom: 1.5rem;
  }
  
  .question-grid {
    justify-content: flex-start;
  }
}

@media (max-width: 768px) {
  .quiz-navbar {
    padding: 0 10px;
    height: auto;
    flex-wrap: wrap;
    padding: 10px;
  }
  
  .quiz-nav-title {
    font-size: 1rem;
    width: 100%;
    margin-bottom: 5px;
  }
  
  .timer, .controls {
    font-size: 0.9rem;
  }
  
  .main-content {
    padding: 1rem;
  }
  
  .question-text {
    font-size: 1.1rem;
  }
  
  .option-text {
    font-size: 1rem;
  }
  
  .nav-button {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }
  
  .modal-content {
    padding: 1.5rem;
  }
  
  .modal-title {
    font-size: 1.3rem;
  }
  
  .modal-text {
    font-size: 1rem;
  }
  
  .resume-button {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }
}
</style>