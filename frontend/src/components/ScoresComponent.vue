<template>
  <div class="scores-container">
    <!-- Special Quiz Results Navbar -->
    <div class="quiz-navbar">
      <h2 class="quiz-nav-title">
        <span class="material-icons">assessment</span>
        Quiz Results
      </h2>
      <div class="quiz-info">
        <span class="material-icons">schedule</span>
        Time: {{ minutes }}m {{ seconds }}s
      </div>
    </div>
    
    <div class="main-content">
      <!-- Results Summary Card -->
      <div class="results-panel">
        <div class="panel-header">
          <span class="material-icons">leaderboard</span>
          Performance Summary
        </div>
        
        <div class="score-display">
          <div class="score-circle">
            <span class="score-value">{{ score }}</span>
            <span class="score-divider">/</span>
            <span class="score-total">{{ total }}</span>
          </div>
          <p class="score-percentage">{{ Math.round((score / total) * 100) }}% Score</p>
        </div>
        
        <div class="chart-container">
          <canvas ref="quizChart" width="250" height="250"></canvas>
        </div>
        
        <div class="legend">
          <div class="legend-item">
            <div class="legend-marker correct"></div>
            <span>Correct Answers ({{ score }})</span>
          </div>
          <div class="legend-item">
            <div class="legend-marker incorrect"></div>
            <span>Incorrect Answers ({{ total - score }})</span>
          </div>
        </div>
      </div>

      <!-- Questions Review -->
      <div class="quiz-content">
        <div class="quiz-card">
          <div class="quiz-card-header">
            <h2 class="card-title">
              <span class="material-icons">fact_check</span>
              Review Questions
            </h2>
          </div>
          
          <div class="questions-review" v-if="questions.length">
            <div class="question-item" v-for="(question, qIndex) in questions" :key="question.qid">
              <div class="question-header">
                <h3 class="question-number">Question {{ qIndex + 1 }}</h3>
                <div class="question-status" :class="{
                  'status-correct': getUserResponse(question.qid) == question.answer,
                  'status-incorrect': getUserResponse(question.qid) != question.answer && getUserResponse(question.qid) != null,
                  'status-unanswered': getUserResponse(question.qid) == null
                }">
                  <span class="material-icons">{{ 
                    getUserResponse(question.qid) == question.answer ? 'check_circle' : 
                    getUserResponse(question.qid) == null ? 'help' : 'cancel'
                  }}</span>
                  {{ 
                    getUserResponse(question.qid) == question.answer ? 'Correct' : 
                    getUserResponse(question.qid) == null ? 'Unanswered' : 'Incorrect'
                  }}
                </div>
              </div>
              
              <h3 class="question-text">{{ question.question }}</h3>
              
              <div class="options-container">
                <label 
                  v-for="option in getOptionsForQuestion(question.qid)" 
                  :key="option.option_id"
                  class="option-label"
                  :class="{ 
                    'option-correct': question.answer == option.option_id,
                    'option-selected': getUserResponse(question.qid) == option.option_id,
                    'option-incorrect': getUserResponse(question.qid) == option.option_id && question.answer != option.option_id
                  }"
                >
                  <input 
                    type="radio" 
                    :name="'question_' + question.qid" 
                    :value="option.option_id" 
                    disabled
                    :checked="getUserResponse(question.qid) == option.option_id"
                  >
                  <span class="option-text">{{ option.option }}</span>
                  <span class="option-status" v-if="question.answer == option.option_id">
                    <span class="material-icons">check_circle</span>
                  </span>
                  <span class="option-status" v-else-if="getUserResponse(question.qid) == option.option_id">
                    <span class="material-icons">cancel</span>
                  </span>
                </label>
              </div>
            </div>
          </div>
          <div class="no-questions" v-else>
            <span class="material-icons">sentiment_dissatisfied</span>
            <p>No questions found.</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Navigation Footer -->
    <div class="navigation-footer">
      <div class="nav-buttons">
        <router-link to="/dashboard" class="nav-button home-button">
          <span class="material-icons">home</span>
          Back to Home
        </router-link>
        
        <router-link to="/livequiz" class="nav-button live-button">
          <span class="material-icons">live_tv</span>
          Live Quizzes
        </router-link>
        
        <button class="nav-button share-button" @click="shareResults">
          <span class="material-icons">share</span>
          Share Results
        </button>
      </div>
    </div>
    
  </div>
</template>

<script>
import Chart from 'chart.js/auto';
import api from '../services/api';

export default {
  name: 'ScoresComponent',
  data() {
    return {
      score: 0,
      total: 0,
      minutes: 0,
      seconds: 0,
      questions: [],
      options: [],
      quizresponses: [],
      chart: null
    };
  },
  mounted() {
    this.fetchScores();
  },
  methods: {
    async fetchScores() {
      try {
        const quizId = this.$route.params.quiz_id;
        const uid = localStorage.getItem('uid');
        const timeTaken = this.$route.params.time_taken;
        
        const response = await api.getQuizScores(quizId, uid, timeTaken);
        const data = response.data;
        
        this.score = data.score;
        this.total = data.total;
        this.minutes = data.minutes;
        this.seconds = data.seconds;
        this.questions = data.questions;
        this.options = data.options;
        this.quizresponses = data.quizresponses;
        
        this.$nextTick(() => {
          this.renderChart();
        });
      } catch (error) {
        console.error('Error fetching scores:', error);
      }
    },
    renderChart() {
      const ctx = this.$refs.quizChart.getContext('2d');
      const correct = this.score;
      const incorrect = this.total - this.score;
      
      if (this.chart) {
        this.chart.destroy();
      }
      
      this.chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Correct', 'Incorrect'],
          datasets: [{
            label: 'Quiz Performance',
            data: [correct, incorrect],
            backgroundColor: ['#5bc0be', '#ff7675'],
            borderColor: ['#3da3a1', '#e06666'],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          cutout: '70%',
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const label = context.label || '';
                  const value = context.raw || 0;
                  const percentage = Math.round((value / (correct + incorrect)) * 100);
                  return `${label}: ${value} (${percentage}%)`;
                }
              }
            }
          }
        }
      });
    },
    getOptionsForQuestion(questionId) {
      return this.options.filter(option => option.question_id === questionId);
    },
    getUserResponse(questionId) {
      const response = this.quizresponses.find(r => r.questionid === questionId);
      return response ? response.optionid : null;
    },
    shareResults() {
      // This would be implemented based on your sharing requirements
      alert('Sharing functionality would be implemented here');
    }
  }
};
</script>

<style scoped>
/* Import Google Material Icons */
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

.scores-container {
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

.quiz-nav-title .material-icons {
  margin-right: 0.5rem;
}

.quiz-info {
  display: flex;
  align-items: center;
  font-size: 1rem;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.1);
  padding: 0.5rem 1rem;
  border-radius: 8px;
}

.quiz-info .material-icons {
  margin-right: 0.5rem;
}

/* Main Content Layout */
.main-content {
  display: flex;
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
  gap: 1.5rem;
}

/* Results Panel */
.results-panel {
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

.score-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem 1rem;
}

.score-circle {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ec 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  position: relative;
  margin-bottom: 1rem;
}

.score-value {
  font-size: 3rem;
  font-weight: 700;
  color: #5bc0be;
  line-height: 1;
}

.score-divider {
  font-size: 1.8rem;
  font-weight: 700;
  color: #3a506b;
  line-height: 1;
  margin: 0 0.2rem;
}

.score-total {
  font-size: 1.8rem;
  font-weight: 600;
  color: #3a506b;
  line-height: 1;
}

.score-percentage {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1c2541;
}

.chart-container {
  padding: 1rem;
  max-width: 250px;
  margin: 0 auto;
}

.legend {
  padding: 0.5rem 1rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-top: 1px solid #e2e8f0;
}

.legend-item {
  display: flex;
  align-items: center;
  font-size: 0.9rem;
  color: #3a506b;
}

.legend-marker {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  margin-right: 8px;
}

.legend-marker.correct {
  background: #5bc0be;
}

.legend-marker.incorrect {
  background: #ff7675;
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

.card-title .material-icons {
  margin-right: 0.5rem;
}

.questions-review {
  padding: 1rem;
}

.question-item {
  background: #f8fafc;
  border-radius: 10px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border: 1px solid #e2e8f0;
}

.question-item:last-child {
  margin-bottom: 0;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.question-number {
  font-size: 1.1rem;
  color: #3a506b;
  font-weight: 600;
  margin: 0;
}

.question-status {
  display: flex;
  align-items: center;
  font-size: 0.9rem;
  font-weight: 500;
  padding: 0.25rem 0.75rem;
  border-radius: 50px;
}

.question-status .material-icons {
  font-size: 1rem;
  margin-right: 0.25rem;
}

.status-correct {
  background: rgba(91, 192, 190, 0.1);
  color: #5bc0be;
}

.status-incorrect {
  background: rgba(255, 118, 117, 0.1);
  color: #ff7675;
}

.status-unanswered {
  background: rgba(220, 221, 225, 0.3);
  color: #636e72;
}

.question-text {
  font-size: 1.2rem;
  color: #1c2541;
  margin-bottom: 1.2rem;
  line-height: 1.5;
}

.options-container {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.option-label {
  display: flex;
  position: relative;
  padding: 0.8rem 1.2rem;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  align-items: center;
}

.option-correct {
  background: rgba(91, 192, 190, 0.1);
  border-color: #5bc0be;
}

.option-incorrect {
  background: rgba(255, 118, 117, 0.1);
  border-color: #ff7675;
}

.option-selected:not(.option-correct) {
  background: rgba(255, 118, 117, 0.1);
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
  font-size: 1rem;
  color: #3a506b;
}

.option-status {
  display: flex;
  align-items: center;
  justify-content: center;
}

.option-status .material-icons {
  font-size: 1.2rem;
}

.option-correct .material-icons {
  color: #5bc0be;
}

.option-incorrect .material-icons {
  color: #ff7675;
}

.no-questions {
  padding: 3rem;
  text-align: center;
  color: #3a506b;
}

.no-questions .material-icons {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #cbd5e0;
}

/* Navigation Footer */
.navigation-footer {
  background: white;
  border-top: 1px solid #e2e8f0;
  padding: 1rem;
  position: sticky;
  bottom: 0;
  z-index: 900;
  box-shadow: 0 -4px 10px rgba(0, 0, 0, 0.05);
}

.nav-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
  max-width: 1400px;
  margin: 0 auto;
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
  text-decoration: none;
  border: none;
  gap: 0.5rem;
}

.home-button {
  background: linear-gradient(135deg, #3a506b 0%, #1c2541 100%);
  color: white;
}

.home-button:hover {
  background: linear-gradient(135deg, #324559 0%, #151d30 100%);
  box-shadow: 0 4px 12px rgba(58, 80, 107, 0.3);
  transform: translateY(-2px);
}

.live-button {
  background: linear-gradient(135deg, #5bc0be 0%, #3a506b 100%);
  color: white;
}

.live-button:hover {
  background: linear-gradient(135deg, #4ca8a7 0%, #2d405a 100%);
  box-shadow: 0 4px 12px rgba(91, 192, 190, 0.3);
  transform: translateY(-2px);
}

.share-button {
  background: linear-gradient(135deg, #6d28d9 0%, #4c1d95 100%);
  color: white;
}

.share-button:hover {
  background: linear-gradient(135deg, #5b21b6 0%, #3b1583 100%);
  box-shadow: 0 4px 12px rgba(109, 40, 217, 0.3);
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
  }
  
  .results-panel {
    width: 100%;
    position: static;
  }
}
</style>