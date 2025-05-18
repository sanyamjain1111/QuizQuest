<template>
  <div class="quiz-instructions-container">
    <NavbarComponent @search="handleSearch" />
    
    <div class="quiz-header">
      <h1 class="quiz-title">Quiz Instructions</h1>
    </div>
    
    <div class="main-content">
      <div class="quiz-card">
        <div class="quiz-card-header">
          <h2 class="card-title">
            <span class="material-icons quiz-icon">info</span>
            Read Before You Begin
          </h2>
        </div>
        
        <div class="instructions-container">
          <div class="instructions-content">
            <p class="instructions-intro">Please read the following instructions carefully before starting the quiz:</p>
            
            <div class="instruction-items">
              <div class="instruction-item">
                <span class="material-icons instruction-icon">help</span>
                <div class="instruction-text">
                  The quiz consists of multiple-choice questions (MCQs).
                </div>
              </div>
              
              <div class="instruction-item">
                <span class="material-icons instruction-icon">timer</span>
                <div class="instruction-text">
                  You will have <span class="highlight">{{ duration }}</span> minutes to complete the quiz.
                </div>
              </div>
              
              <div class="instruction-item">
                <span class="material-icons instruction-icon">check_circle</span>
                <div class="instruction-text">
                  Each question has only one correct answer.
                </div>
              </div>
              
              <div class="instruction-item">
                <span class="material-icons instruction-icon">refresh</span>
                <div class="instruction-text">
                  Avoid refreshing or closing the browser during the quiz, as it may result in losing progress.
                </div>
              </div>
              
              <div class="instruction-item">
                <span class="material-icons instruction-icon">wifi</span>
                <div class="instruction-text">
                  Make sure you have a stable internet connection before starting the quiz.
                </div>
              </div>
              
              <div class="instruction-item">
                <span class="material-icons instruction-icon">grade</span>
                <div class="instruction-text">
                  Your score will be displayed at the end of the quiz.
                </div>
              </div>
            </div>
            
            <div class="quiz-action">
              <p class="quiz-message">Click the button below to start the quiz. Good luck!</p>
              <router-link :to="'/startquiz/' + quizId"
              style="text-decoration: none; color: inherit;">
                <button class="start-button">
                  <span class="material-icons">play_arrow</span>
                  Start Quiz
                </button>
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import NavbarComponent from './NavbarComponent.vue';

export default {
  name: 'QuizInstructions',
  components: {
    NavbarComponent
  },
  data() {
    return {
      quizId: this.$route.params.quiz_id,
      duration: null,
      searchQuery: ''
    };
  },
  async mounted() {
    await this.fetchQuizInstructions();
  },
  methods: {
    async fetchQuizInstructions() {
      try {
        const response = await axios.get(`/api/quizinstructions/${this.quizId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        this.duration = response.data.duration;
      } catch (error) {
        console.error('Error fetching quiz instructions:', error);
        if (error.response?.status === 401) {
          this.$router.push('/');
        }
      }
    },
    handleSearch(query) {
      this.searchQuery = query;
      // Search functionality can be implemented here if needed
    }
  }
};
</script>

<style scoped>
/* Import Google Material Icons */
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

.quiz-instructions-container {
  font-family: 'Poppins', sans-serif;
  min-height: 100vh;
  max-width: 1200px;
  margin: 0 auto;
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

.instructions-container {
  padding: 1.5rem;
}

.instructions-content {
  padding: 0.5rem;
}

.instructions-intro {
  font-size: 1.1rem;
  color: #1c2541;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.instruction-items {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  margin-bottom: 2rem;
}

.instruction-item {
  display: flex;
  align-items: flex-start;
  padding: 0.5rem 1rem;
  background-color: #f8fafc;
  border-radius: 8px;
  border-left: 4px solid #5bc0be;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.instruction-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.instruction-icon {
  color: #5bc0be;
  margin-right: 1rem;
  margin-top: 0.1rem;
}

.instruction-text {
  font-size: 1rem;
  line-height: 1.5;
  color: #3a506b;
}

.highlight {
  font-weight: 600;
  color: #0b132b;
}

.quiz-action {
  text-align: center;
  margin-top: 2rem;
  padding: 1.5rem;
  background-color: #f1f5f9;
  border-radius: 8px;
}

.quiz-message {
  font-size: 1.1rem;
  color: #1c2541;
  margin-bottom: 1.5rem;
}

.start-button {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
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

.start-button:hover {
  background: linear-gradient(135deg, #5b21b6 0%, #3b1583 100%);
  box-shadow: 0 4px 12px rgba(109, 40, 217, 0.3);
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
  
  .card-title {
    font-size: 1.3rem;
  }
  
  .instructions-intro,
  .quiz-message {
    font-size: 1rem;
  }
  
  .instruction-item {
    padding: 0.5rem;
  }
  
  .instruction-text {
    font-size: 0.95rem;
  }
  
  .start-button {
    font-size: 1rem;
    padding: 0.7rem 1.7rem;
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
  
  .instructions-container {
    padding: 1rem;
  }
  
  .instruction-items {
    gap: 0.8rem;
  }
  
  .instruction-item {
    flex-direction: column;
  }
  
  .instruction-icon {
    margin-bottom: 0.5rem;
    margin-right: 0;
  }
  
  .quiz-action {
    padding: 1rem;
  }
  
  .start-button {
    width: 100%;
  }
}

/* Accessibility improvements */
@media (prefers-reduced-motion: reduce) {
  .instruction-item:hover,
  .start-button:hover {
    transform: none;
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .quiz-instructions-container {
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
  
  .instructions-intro,
  .quiz-message {
    color: #e2e8f0;
  }
  
  .instruction-item {
    background-color: #364156;
    border-left-color: #5bc0be;
  }
  
  .instruction-text {
    color: #cbd5e0;
  }
  
  .highlight {
    color: #f7fafc;
  }
  
  .quiz-action {
    background-color: #1a202c;
  }
}
</style>