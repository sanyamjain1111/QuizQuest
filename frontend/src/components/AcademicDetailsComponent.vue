<template>
  <div class="academic-details-container">
    <NavbarComponent @search="handleSearch" />
    
    <div class="dashboard-header">
      <h1 class="dashboard-title">{{ message }}</h1>
    </div>
    
    <div class="main-content">
      <!-- Content when quiz data is available -->
      <div v-if="quizdetails.length > 0" class="academic-content">
        <div class="stats-header">
          <h2 class="stats-title">Quiz Performance History 
</h2>
          <UserExportComponent />
        </div>
       
        <div class="charts-container">
          <div class="chart-card">
            <div class="chart-header">
              <h3 class="chart-title">Quizzes Attempted by Subject</h3>
            </div>
            <div class="chart-body">
              <canvas id="myBarChart" width="200" height="250"></canvas>
            </div>
          </div>
          
          <div class="chart-card">
            <div class="chart-header">
              <h3 class="chart-title">Average Score by Subject</h3>
            </div>
            <div class="chart-body">
              <canvas id="myBarChart2" width="200" height="250"></canvas>
            </div>
          </div>
        </div>
        
        <div class="table-container">
          <div class="table-header">
            <h3 class="table-title">Quiz History Details</h3>
          </div>
          
          <div class="table-responsive">
            <table class="quiz-table">
              <thead>
                <tr>
                  <th>Subject</th>
                  <th>Quiz ID</th>
                  <th>Score</th>
                  <th>Date Attempted</th>
                  <th>Time Taken</th>
                  <th v-if="quizdetails[0] && quizdetails[0].chaoter_id">Chapter</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(quiz, index) in quizdetails" :key="index">
                  <td>{{ quiz.subject_name }}</td>
                  <td>{{ quiz.quizname || quiz.quiz_name || quiz.quiz_id }}</td>
                  <td>
                    <div class="score-badge" :class="getScoreClass(quiz.score)">
                      {{ quiz.score }} / {{ quiz.max_score || quiz.total }}
                    </div>
                  </td>
                  <td>{{ formatDate(quiz.quiz_date || quiz.timestamp) }}</td>
                  <td>{{ formatTime(quizdetails.time_taken || quiz.time_spent || quiz.time_stamp) }}</td>
                  <td v-if="quizdetails[0] && quizdetails[0].chaoter_id">{{ quiz.chapter_name || 'N/A' }}</td>
                  <td>
                    <div class="action-buttons">
                      <router-link 
                        :to="`/scores/${quiz.quiz_id || quiz.quizid}/${uid}/${quiz.time_spent || quiz.time_stamp}`" 
                        class="action-link view-link"
                        title="View Score Details"
                      >
                        <span class="material-icons">assessment</span>
                      </router-link>
                      
                      
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      <!-- Empty state when no quizzes attempted -->
      <div v-else class="empty-state">
        <span class="material-icons empty-icon">quiz</span>
        <h3>No Quizzes Attempted</h3>
        <p>You haven't attempted any quizzes yet. Start taking quizzes to track your academic progress!</p>
        <button class="action-button" @click="goToSubjects">Browse Subjects</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import NavbarComponent from './NavbarComponent.vue';
import UserExportComponent from './UserExportComponent.vue';
import Chart from 'chart.js/auto';

export default {
  name: 'AcademicDetailsComponent',
  components: {
    NavbarComponent,
    UserExportComponent
  },
  data() {
    return {
      message: 'Academic Performance Dashboard',
      quizdetails: [],
      subjectcount: [],
      subjectmarks: [],
      uid: localStorage.getItem('uid') || '',
      searchQuery: '',
      charts: []
    }
  },
  async mounted() {
    if (!localStorage.getItem('token')) {
      this.$router.push('/');
      return;
    }
    
    await this.fetchData();
    if (this.quizdetails.length > 0) {
      this.$nextTick(() => {
        this.renderCharts();
      });
    }
  },
  methods: {
    async fetchData() {
      try {
        const response = await axios.get('/api/academic_details', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        this.subjectcount = response.data.subjectcount;
        this.quizdetails = response.data.quizdetails;
        this.subjectmarks = response.data.subjectmarks;
        this.uid = response.data.uid;
      } catch (error) {
        console.error('Error fetching academic details:', error);
        if (error.response && error.response.status === 401) {
          this.logout();
        }
      }
    },
    renderCharts() {
      // Destroy existing charts if they exist
      this.charts.forEach(chart => chart.destroy());
      this.charts = [];
      
      // Chart for quiz attempts by subject
      if (this.subjectcount.length > 0) {
        const ctx = document.getElementById('myBarChart').getContext('2d');
        const chart1 = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: this.subjectcount.map(item => item.subject_name),
            datasets: [{
              label: 'Number of Quizzes Attempted',
              data: this.subjectcount.map(item => item.count),
              backgroundColor: 'rgba(91, 192, 190, 0.7)',
              borderColor: 'rgba(91, 192, 190, 1)',
              borderWidth: 1,
              borderRadius: 5
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: false
              },
              tooltip: {
                backgroundColor: 'rgba(11, 19, 43, 0.8)',
                titleFont: {
                  family: 'Poppins'
                },
                bodyFont: {
                  family: 'Poppins'
                }
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  stepSize: 1,
                  font: {
                    family: 'Poppins'
                  }
                },
                grid: {
                  color: 'rgba(91, 192, 190, 0.1)'
                }
              },
              x: {
                ticks: {
                  font: {
                    family: 'Poppins'
                  }
                },
                grid: {
                  display: false
                }
              }
            }
          }
        });
        this.charts.push(chart1);
      }

      // Chart for average scores by subject
      if (this.subjectmarks.length > 0) {
        const ctx2 = document.getElementById('myBarChart2').getContext('2d');
        const chart2 = new Chart(ctx2, {
          type: 'bar',
          data: {
            labels: this.subjectmarks.map(item => item.subject_name),
            datasets: [{
              label: 'Average Score',
              data: this.subjectmarks.map(item => item.avg),
              backgroundColor: 'rgba(58, 80, 107, 0.7)',
              borderColor: 'rgba(58, 80, 107, 1)',
              borderWidth: 1,
              borderRadius: 5
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: false
              },
              tooltip: {
                backgroundColor: 'rgba(11, 19, 43, 0.8)',
                titleFont: {
                  family: 'Poppins'
                },
                bodyFont: {
                  family: 'Poppins'
                }
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                max: 10,
                ticks: {
                  callback: function(value) {
                    return value ;
                  },
                  font: {
                    family: 'Poppins'
                  }
                },
                grid: {
                  color: 'rgba(58, 80, 107, 0.1)'
                }
              },
              x: {
                ticks: {
                  font: {
                    family: 'Poppins'
                  }
                },
                grid: {
                  display: false
                }
              }
            }
          }
        });
        this.charts.push(chart2);
      }
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) {
          // Try parsing SQL date format (YYYY-MM-DD HH:MM:SS)
          const parts = dateString.split(/[- :]/);
          const parsedDate = new Date(parts[0], parts[1]-1, parts[2], parts[3] || 0, parts[4] || 0, parts[5] || 0);
          if (!isNaN(parsedDate.getTime())) {
            return parsedDate.toLocaleDateString('en-US', { 
              year: 'numeric', 
              month: 'short', 
              day: 'numeric' 
            });
          }
          return dateString; // Return as is if can't parse
        }
        return date.toLocaleDateString('en-US', { 
          year: 'numeric', 
          month: 'short', 
          day: 'numeric' 
        });
      } catch (error) {
        console.error('Error formatting date:', error);
        return dateString;
      }
    },
    formatTime(seconds) {
      if (!seconds && seconds !== 0) return 'N/A';
      
      // Handle if seconds is a string
      if (typeof seconds === 'string') {
        seconds = parseInt(seconds, 10);
        if (isNaN(seconds)) return 'N/A';
      }
      
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = Math.floor(seconds % 60);
      return `${minutes}m ${remainingSeconds}s`;
    },
    getScoreClass(score) {
      if (score >= 9) return 'excellent';
      if (score >= 7.5) return 'good';
      if (score >= 6) return 'average';
      return 'needs-improvement';
    },
    goToSubjects() {
      this.$router.push('/dashboard');
    },
    handleSearch(query) {
      this.searchQuery = query;
      // Implement search functionality if needed
    },
    logout() {
      localStorage.removeItem('token');
      localStorage.removeItem('fullname');
      localStorage.removeItem('uid');
      this.$router.push('/');
    }
  },
  beforeUnmount() {
    // Clean up charts
    this.charts.forEach(chart => chart.destroy());
  }
}
</script>

<style scoped>
/* Import Google Material Icons */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

.academic-details-container {
  font-family: 'Poppins', sans-serif;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ec 100%);
  color: #1c2541;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  text-align: center;
  padding: 2rem 0 1rem;
  background: linear-gradient(135deg, rgba(11, 19, 43, 0.05) 0%, rgba(28, 37, 65, 0.1) 100%);
  border-bottom: 1px solid rgba(91, 192, 190, 0.2);
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

.academic-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.stats-header {
  background: linear-gradient(135deg, #0b132b 0%, #1c2541 100%);
  padding: 1.5rem;
  border-radius: 12px;
  position: relative;
  margin-bottom: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;

}



.stats-title {
  color: white;
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  position: relative;
  z-index: 2;
}

.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 2rem;
}

.chart-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid rgba(91, 192, 190, 0.2);
}

.chart-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08);
}

.chart-header {
  background: linear-gradient(135deg, #5bc0be 0%, #3a506b 100%);
  padding: 1rem 1.5rem;
}

.chart-title {
  color: white;
  margin: 0;
  font-size: 1.2rem;
  font-weight: 500;
}

.chart-body {
  padding: 1.5rem;
  height: 300px;
}

.table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid rgba(91, 192, 190, 0.2);
}

.table-container:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08);
}

.table-header {
  background: linear-gradient(135deg, #0b132b 0%, #1c2541 100%);
  padding: 1rem 1.5rem;
  position: relative;
  overflow: hidden;
}

.table-header:before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(91, 192, 190, 0.2) 0%, rgba(91, 192, 190, 0) 70%);
  z-index: 1;
}

.table-title {
  color: white;
  margin: 0;
  font-size: 1.2rem;
  font-weight: 500;
  position: relative;
  z-index: 2;
}

.table-responsive {
  overflow-x: auto;
  padding: 1rem;
}

.quiz-table {
  width: 100%;
  border-collapse: collapse;
  border-spacing: 0;
}

.quiz-table th,
.quiz-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid rgba(91, 192, 190, 0.2);
}

.quiz-table th {
  font-weight: 600;
  color: #0b132b;
  background: rgba(91, 192, 190, 0.1);
}

.quiz-table tr:last-child td {
  border-bottom: none;
}

.quiz-table tr:hover {
  background-color: rgba(91, 192, 190, 0.05);
}

.score-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.35rem 0.75rem;
  border-radius: 50px;
  font-weight: 500;
  font-size: 0.85rem;
}

.score-badge.excellent {
  background-color: rgba(39, 174, 96, 0.15);
  color: #27ae60;
}

.score-badge.good {
  background-color: rgba(52, 152, 219, 0.15);
  color: #3498db;
}

.score-badge.average {
  background-color: rgba(241, 196, 15, 0.15);
  color: #f1c40f;
}

.score-badge.needs-improvement {
  background-color: rgba(231, 76, 60, 0.15);
  color: #e74c3c;
}

/* Action buttons in table */
.action-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.action-link {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  color: white;
  transition: all 0.2s ease;
}

.view-link {
  background: linear-gradient(135deg, #5bc0be 0%, #3a506b 100%);
}

.view-link:hover {
  background: linear-gradient(135deg, #4ca8a7 0%, #2d405a 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(91, 192, 190, 0.3);
}

.transcript-link {
  background: linear-gradient(135deg, #6d28d9 0%, #4c1d95 100%);
}

.transcript-link:hover {
  background: linear-gradient(135deg, #5b21b6 0%, #3b1583 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(109, 40, 217, 0.3);
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
  border: 1px solid rgba(91, 192, 190, 0.2);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  color: #a0aec0;
}

.action-button {
  margin-top: 1.5rem;
  background: linear-gradient(135deg, #5bc0be 0%, #3a506b 100%);
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-button:hover {
  background: linear-gradient(135deg, #4ca8a7 0%, #2d405a 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(91, 192, 190, 0.3);
}

/* Responsive adjustments */
@media (max-width: 992px) {
  .charts-container {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-title {
    font-size: 1.8rem;
  }
  
  .stats-title, .chart-title, .table-title {
    font-size: 1.3rem;
  }
  
  .chart-body {
    height: 250px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 5px;
  }
  
  .action-link {
    width: 32px;
    height: 32px;
  }
  
  .action-link .material-icons {
    font-size: 18px;
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
  
  .stats-header, .chart-header, .table-header {
    padding: 1rem;
  }
  
  .chart-body {
    padding: 1rem;
  }
  
  .quiz-table th, 
  .quiz-table td {
    padding: 0.75rem;
    font-size: 0.9rem;
  }
}
</style>