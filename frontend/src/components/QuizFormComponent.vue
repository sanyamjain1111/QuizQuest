<template>
  <div class="quiz-form-container">
    <!-- Reuse the AdminNavbarComponent we have -->
    
    <div class="dashboard-header">
      <h1 class="dashboard-title">{{ isEditMode ? 'Edit Quiz' : 'Add New Quiz' }}</h1>
    </div>
    
    <div class="main-content">
      <div class="user_reg">
        <div class="ahead">{{ isEditMode ? 'Edit' : 'Add New' }} Quiz</div>
        
        <div class="alert alert-danger" v-if="error">{{ error }}</div>
        <div class="alert alert-success" v-if="success">{{ success }}</div>
        
        <form @submit.prevent="submitForm" class="form">
          <div class="input">
            Enter the date for which you want to {{ isEditMode ? 'edit' : 'add' }} a quiz: <br>
            <input type="date" id="datePicker" v-model="formData.date" class="input2" required>
          </div>
          <br>
          <div class="input">
            Choose the chapter for which you want to {{ isEditMode ? 'edit' : 'add' }} a quiz: <br>
            <select v-model="formData.chapter_id" class="input2" required>
              <option value="">Choose the chapter here</option>
              <option v-for="chapter in chapters" :key="chapter.chaoter_id" :value="chapter.chaoter_id">
                {{ chapter.chapter_name }} ({{ chapter.chaoter_id }})
              </option>
            </select>
          </div>
          <br>
          <div class="input">
            Enter the duration of quiz (minutes):
            <input type="number" class="input3" v-model="formData.duration" min="1" required>
          </div>
          
          <div class="buttons2">
            <button type="submit" class="button3">Submit</button>
            <button type="button" class="button3" @click="goBack">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import quizService from '../services/quizService';

export default {
  name: 'QuizFormComponent',
  components: {
    // Include any other components you might need here
  },
  data() {
    return {
      isEditMode: false,
      quiz_id: null,
      chapters: [],
      formData: {
        date: '',
        chapter_id: '',
        duration: ''
      },
      error: '',
      success: ''
    };
  },
  async created() {
    if (!localStorage.getItem('adminToken')) {
      this.$router.push('/');
      return;
    }
    
    // Check if we're in edit mode
    this.quiz_id = this.$route.params.id;
    this.isEditMode = !!this.quiz_id;
    
    // Set minimum date for datepicker
    this.$nextTick(() => {
      const today = new Date().toISOString().split('T')[0];
      document.getElementById('datePicker').setAttribute('min', today);
    });
    
    await this.fetchChapters();
    
    if (this.isEditMode) {
      await this.fetchQuizDetails();
    }
  },
  methods: {
    async fetchChapters() {
      try {
        this.chapters = await quizService.getChapters();
      } catch (error) {
        console.error('Error fetching chapters:', error);
        this.error = 'Failed to load chapters. Please try again.';
        
        if (error.response?.status === 401) {
          this.logout();
        }
      }
    },
    async fetchQuizDetails() {
      try {
        const quizData = await quizService.getQuizDetails(this.quiz_id);
        
        this.formData = {
          date: quizData.quiz_date,
          chapter_id: quizData.current_chapter_id,
          duration: quizData.duration
        };
      } catch (error) {
        console.error('Error fetching quiz details:', error);
        this.error = 'Failed to load quiz details. Please try again.';
        
        if (error.response?.status === 401) {
          this.logout();
        }
      }
    },
    async submitForm() {
      this.error = '';
      this.success = '';
      
      if (!this.formData.date || !this.formData.chapter_id || !this.formData.duration) {
        this.error = 'Please fill in all required fields';
        return;
      }
      
      try {
        if (this.isEditMode) {
          // Edit existing quiz
          await quizService.updateQuiz(this.quiz_id, this.formData);
          this.success = 'Quiz updated successfully';
        } else {
          // Add new quiz
          await quizService.addQuiz(this.formData);
          this.success = 'Quiz added successfully';
        }
        
        // Redirect after a short delay
        setTimeout(() => {
          this.$router.push('/admindashboard');
        }, 1500);
      } catch (error) {
        console.error('Error submitting form:', error);
        this.error = error.response?.data?.error || 'Failed to save quiz. Please try again.';
        
        if (error.response?.status === 401) {
          this.logout();
        }
      }
    },
    goBack() {
      this.$router.push('/admindashboard');
    },
    logout() {
      localStorage.removeItem('adminToken');
      localStorage.removeItem('adminName');
      localStorage.removeItem('adminId');
      this.$router.push('/');
    }
  }
};
</script>

<style scoped>
.quiz-form-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.dashboard-header {
  margin-bottom: 30px;
}

.dashboard-title {
  font-size: 1.8rem;
  color: #333;
}

.user_reg {
  display: flex;
  flex-direction: column;
  border: 1px solid #ddd;
  border-radius: 15px;
  margin: 20px auto;
  max-width: 600px;
  padding: 20px;
  background-color: rgb(252, 250, 239);
}

.ahead {
  margin-bottom: 20px;
  text-align: center;
  font-size: 1.5rem;
  font-weight: bold;
}

.form {
  width: 100%;
}

.input {
  margin-bottom: 15px;
}

.input2, select {
  margin-top: 5px;
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.input3 {
  width: 100px;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 5px;
  margin-left: 10px;
}

.buttons2 {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 20px;
}

.button3 {
  padding: 8px 15px;
  border: none;
  border-radius: 15px;
  background-color: #4CAF50;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s;
}

.button3:hover {
  background-color: #45a049;
}

.button3:nth-child(2) {
  background-color: #f44336;
}

.button3:nth-child(2):hover {
  background-color: #d32f2f;
}

.alert {
  padding: 10px;
  margin-bottom: 15px;
  border-radius: 5px;
}

.alert-danger {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.alert-success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}
</style>