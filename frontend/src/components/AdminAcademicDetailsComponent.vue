<template>
  <div class="admin-dashboard-container">
    <AdminNavbarComponent @search="handleSearch" />
    
    <div class="dashboard-header">
      <h1 class="dashboard-title">Student Academic Details</h1>
    </div>
    
    <div class="main-content">
    
      <!-- Filter options -->
      <div class="filter-container">
        <div class="filter-dropdown">
          <label for="userFilter">Filter by User ID:</label>
          <select id="userFilter" v-model="selectedUserId" class="form-select">
            <option value="">All Users</option>
            <option v-for="userId in uniqueUserIds" :key="userId" :value="userId">User ID: {{ userId }}</option>
          </select>
        </div>
          <AdminExportComponent />

      </div>

      <!-- Alert messages -->
      <div class="alert alert-danger" v-if="error">{{ error }}</div>
      <div class="alert alert-success" v-if="success">{{ success }}</div>
      
      <!-- Loading state -->
      <div v-if="loading" class="empty-state">
        <span class="material-icons empty-icon">hourglass_top</span>
        <h3>Loading academic data...</h3>
      </div>
      
      <!-- Charts and Stats -->
      <div v-if="!loading && quizDetails.length > 0" class="charts-container">
        <div class="chart-card">
          <div class="chart-header">
            <h3 class="chart-title">Quizzes Attempted by Subject</h3>
          </div>
          <div class="chart-body">
            <canvas ref="subjectCountChart"></canvas>
          </div>
        </div>
        
        <div class="chart-card">
          <div class="chart-header">
            <h3 class="chart-title">Average Scores by Subject</h3>
          </div>
          <div class="chart-body">
            <canvas ref="subjectMarksChart"></canvas>
          </div>
        </div>
      </div>
      
      <!-- Quiz Details Table -->
      <div v-if="!loading" class="table-container">
        <div class="table-header">
          <h3 class="table-title">
            <span class="material-icons">assignment</span>
            Quiz Transcripts
          </h3>
          <p class="records-count">{{ filteredQuizDetails.length }} {{ filteredQuizDetails.length === 1 ? 'Record' : 'Records' }} Found</p>
        </div>
        
        <div v-if="filteredQuizDetails.length > 0" class="responsive-table">
          <table class="table">
            <thead>
              <tr>
                <th>Quiz ID</th>
                <th>User ID</th>
                <th>Chapter Name</th>
                <th>Quiz Date</th>
                <th>Duration</th>
                <th>Score</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="quiz in filteredQuizDetails" :key="`${quiz.uid}-${quiz.quiz_id}`">
                <td>{{ quiz.quizid || quiz.quiz_id }}</td>
                <td>{{ quiz.uid }}</td>
                <td>{{ quiz.chapter_name }}</td>
                <td>{{ formatDate(quiz.quiz_date) }}</td>
                <td>{{ quiz.duration }} minutes</td>
                <td>
                  <div class="score-container">
                    <div class="score-text">{{ quiz.score }}/{{ quiz.total }}</div>
                    <div class="score-bar">
                      <div class="score-progress" :style="{ width: `${(quiz.score / quiz.total) * 100}%` }"></div>
                    </div>
                  </div>
                </td>
                <td>
                  <button class="action-btn view-btn" @click="viewTranscript(quiz.quizid || quiz.quiz_id, quiz.uid)">
                    <span class="material-icons">visibility</span>
                    View Transcript
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Empty state when no quizzes found -->
        <div v-if="quizDetails.length === 0" class="empty-state">
          <span class="material-icons empty-icon">book</span>
          <h3>No Quiz Records Found</h3>
          <p>There are currently no quiz attempts recorded in the system</p>
        </div>
        
        <!-- Empty state when no quizzes match filters -->
        <div v-if="quizDetails.length > 0 && filteredQuizDetails.length === 0" class="empty-state">
          <span class="material-icons empty-icon">search_off</span>
          <h3>No matching quiz records found</h3>
          <p>Try adjusting your search or filter criteria</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AdminNavbarComponent from './AdminNavbarComponent.vue';
import AdminExportComponent from './AdminExportComponent.vue';
import api from '@/services/api';
import Chart from 'chart.js/auto';

export default {
  name: 'AdminAcademicDetailsComponent',
  components: {
    AdminNavbarComponent,
    AdminExportComponent
  },
  data() {
    return {
      quizDetails: [],
      subjectCount: [],
      subjectMarks: [],
      loading: true,
      error: '',
      success: '',
      selectedUserId: '',
      searchTerm: '',
      charts: {
        subjectCountChart: null,
        subjectMarksChart: null
      }
    };
  },
  computed: {
    uniqueUserIds() {
      return [...new Set(this.quizDetails.map(quiz => quiz.uid))].sort((a, b) => a - b);
    },
    filteredQuizDetails() {
      let result = this.quizDetails;
      
      if (this.selectedUserId) {
        result = result.filter(quiz => quiz.uid == this.selectedUserId);
      }
      
      if (this.searchTerm) {
        const searchLower = this.searchTerm.toLowerCase();
        result = result.filter(quiz => 
          quiz.chapter_name?.toLowerCase().includes(searchLower) ||
          String(quiz.uid).includes(searchLower) ||
          String(quiz.quizid || quiz.quiz_id).includes(searchLower)
        );
      }
      
      return result;
    }
  },
  async created() {
    if (!localStorage.getItem('adminToken')) {
      this.$router.push('/');
      return;
    }
    
    await this.fetchData();
  },
  methods: {
    async fetchData() {
      this.loading = true;
      this.error = '';
      
      try {
        const response = await api.getStudentAcademicDetails();
        this.quizDetails = response.data.quizdetails || [];
        this.subjectCount = response.data.subjectcount || [];
        this.subjectMarks = response.data.subjectmarks || [];
        
        console.log('Quiz Details:', this.quizDetails);
        console.log('Subject Count:', this.subjectCount);
        console.log('Subject Marks:', this.subjectMarks);
        
      } catch (error) {
        console.error('Error fetching academic data:', error);
        
        if (error.response) {
          console.error('Response data:', error.response.data);
          console.error('Response status:', error.response.status);
          this.error = `Failed to load academic data (${error.response.status}): ${error.response.data.message || 'Unknown error'}`;
        } else if (error.request) {
          console.error('No response received:', error.request);
          this.error = 'Server not responding. Please check your API server is running.';
        } else {
          console.error('Request error:', error.message);
          this.error = `Request error: ${error.message}`;
        }
        
        if (error.response?.status === 401) {
          this.logout();
        }
      } finally {
        this.loading = false;
        this.$nextTick(() => {
          this.initCharts();
        });
      }
    },
    
    handleSearch(query) {
      this.searchTerm = query;
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      
      try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        });
      } catch (e) {
        return dateString;
      }
    },
    
    viewTranscript(quizId, userId) {
      // Navigate to transcript view
      this.$router.push(`/admin/transcript/${quizId}/${userId}`);
    },
    
    initCharts() {
      if (this.quizDetails.length === 0) return;
      
      this.$nextTick(() => {
        // Destroy existing charts if they exist
        if (this.charts.subjectCountChart) {
          this.charts.subjectCountChart.destroy();
        }
        if (this.charts.subjectMarksChart) {
          this.charts.subjectMarksChart.destroy();
        }
        
        // Initialize subject count chart
        const subjectCountCtx = this.$refs.subjectCountChart?.getContext('2d');
        if (subjectCountCtx) {
          const labels = this.subjectCount.map(item => item.subject_name);
          const dataValues = this.subjectCount.map(item => item.count);
          
          this.charts.subjectCountChart = new Chart(subjectCountCtx, {
            type: 'bar',
            data: {
              labels: labels,
              datasets: [{
                label: 'Quizzes Attempted',
                data: dataValues,
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
                    family: 'Poppins',
                    size: 16
                  },
                  bodyFont: {
                    family: 'Poppins',
                    size: 14
                  },
                  padding: 12
                }
              },
              scales: {
                y: {
                  beginAtZero: true,
                  ticks: {
                    stepSize: 1,
                    font: {
                      family: 'Poppins',
                      size: 14
                    }
                  },
                  grid: {
                    color: 'rgba(91, 192, 190, 0.1)'
                  }
                },
                x: {
                  ticks: {
                    font: {
                      family: 'Poppins',
                      size: 14
                    }
                  },
                  grid: {
                    display: false
                  }
                }
              }
            }
          });
        }
        
        // Initialize subject marks chart
        const subjectMarksCtx = this.$refs.subjectMarksChart?.getContext('2d');
        if (subjectMarksCtx) {
          const labels = this.subjectMarks.map(item => item.subject_name);
          const dataValues = this.subjectMarks.map(item => item.avg);
          
          this.charts.subjectMarksChart = new Chart(subjectMarksCtx, {
            type: 'bar',
            data: {
              labels: labels,
              datasets: [{
                label: 'Average Score',
                data: dataValues,
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
                    family: 'Poppins',
                    size: 16
                  },
                  bodyFont: {
                    family: 'Poppins',
                    size: 14
                  },
                  padding: 12
                }
              },
              scales: {
                y: {
                  beginAtZero: true,
                  ticks: {
                    font: {
                      family: 'Poppins',
                      size: 14
                    }
                  },
                  grid: {
                    color: 'rgba(58, 80, 107, 0.1)'
                  }
                },
                x: {
                  ticks: {
                    font: {
                      family: 'Poppins',
                      size: 14
                    }
                  },
                  grid: {
                    display: false
                  }
                }
              }
            }
          });
        }
      });
    },
    
    logout() {
      localStorage.removeItem('adminToken');
      localStorage.removeItem('adminName');
      localStorage.removeItem('adminId');
      this.$router.push('/');
    }
  },
  watch: {
    selectedUserId() {
      // Reinitialize charts when user ID filter changes
      this.initCharts();
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

/* Filter styles */
/* Filter styles - Updated */
.filter-container {
  margin-bottom: 1.5rem;
  background: white;
  padding: 1rem;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(91, 192, 190, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.filter-dropdown {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.filter-dropdown label {
  font-weight: 500;
  color: #3a506b;
  min-width: 120px;
}

.form-select {
  flex: 1;
  padding: 0.5rem;
  border-radius: 6px;
  border: 1px solid #ddd;
  font-family: 'Poppins', sans-serif;
}

/* Charts container */
.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.chart-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(91, 192, 190, 0.2);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
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

/* Table styles */
.table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(91, 192, 190, 0.2);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  margin-bottom: 2rem;
}
.main-content > .export-section {
  margin-bottom: 1.5rem;
}
.table-container:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08);
}

.table-header {
  background: linear-gradient(135deg, #0b132b 0%, #1c2541 100%);
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  position: relative;
  z-index: 2;
}

.table-title .material-icons {
  color: #5bc0be;
}

.records-count {
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  font-size: 0.9rem;
  position: relative;
  z-index: 2;
}

.responsive-table {
  overflow-x: auto;
  padding: 0.5rem;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th, .table td {
  padding: 1rem 1.5rem;
  text-align: left;
  vertical-align: middle;
}

.table th {
  background-color: rgba(91, 192, 190, 0.1);
  color: #3a506b;
  font-weight: 600;
  border-bottom: 1px solid #eee;
}

.table tbody tr {
  border-bottom: 1px solid rgba(91, 192, 190, 0.2);
  transition: background-color 0.2s ease;
}

.table tbody tr:hover {
  background-color: rgba(91, 192, 190, 0.05);
}

.table tbody tr:last-child {
  border-bottom: none;
}

/* Score display */
.score-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.score-text {
  font-weight: 600;
  color: #1c2541;
}

.score-bar {
  height: 6px;
  background-color: #e9ecef;
  border-radius: 3px;
  overflow: hidden;
  width: 100%;
}

.score-progress {
  height: 100%;
  background: linear-gradient(90deg, #5bc0be, #3a506b);
  border-radius: 3px;
}

/* Button styles */
.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  border: none;
}

.view-btn {
  background: linear-gradient(135deg, #5bc0be 0%, #3a506b 100%);
  color: white;
}

.view-btn:hover {
  background: linear-gradient(135deg, #4ca8a7 0%, #2d405a 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(91, 192, 190, 0.3);
}

/* Empty state */
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
  color: #3a506b;
  opacity: 0.6;
  margin-bottom: 1rem;
}

.empty-state h3 {
  color: #1c2541;
  margin: 1rem 0 0.5rem;
  font-weight: 600;
}

.empty-state p {
  color: #6c757d;
  text-align: center;
  max-width: 500px;
  margin: 0;
}

/* Alert styles */
.alert {
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  font-weight: 500;
}

.alert-danger {
  background-color: rgba(231, 76, 60, 0.1);
  color: #e74c3c;
  border: 1px solid rgba(231, 76, 60, 0.3);
}

.alert-success {
  background-color: rgba(46, 204, 113, 0.1);
  color: #2ecc71;
  border: 1px solid rgba(46, 204, 113, 0.3);
}

/* Responsive adjustments */
@media (max-width: 992px) {
  .charts-container {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: 0 1rem;
  }
  
  .dashboard-title {
    font-size: 1.8rem;
  }
  
  .chart-body {
    height: 250px;
  }
  
  .table th, .table td {
    padding: 0.75rem;
  }
  
  .action-btn {
    padding: 0.4rem 0.8rem;
    font-size: 0.8rem;
  }
}

@media (max-width: 576px) {
  .dashboard-title {
    font-size: 1.5rem;
  }
  
  .filter-dropdown {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filter-dropdown label {
    margin-bottom: 0.5rem;
  }
  
  .chart-header, .table-header {
    padding: 1rem;
  }
  
  .table-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .records-count {
    margin-top: 0.5rem;
  }
}
</style>