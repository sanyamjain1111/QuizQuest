<template>
  <div class="question-form-container">
    <!-- Reuse the AdminNavbarComponent we have -->
    <AdminNavbarComponent />
    
    <div class="dashboard-header">
      <h1 class="dashboard-title">{{ isEditMode ? 'Edit Question' : 'Add New Question' }}</h1>
    </div>
    
    <div class="main-content">
      <div class="user_reg">
        <div class="ahead">{{ isEditMode ? 'Edit' : 'Add New' }} Question</div>
        
        <div class="alert alert-danger" v-if="error">{{ error }}</div>
        <div class="alert alert-success" v-if="success">{{ success }}</div>
        
        <form @submit.prevent="submitForm" class="form">
          <div class="input">
            Enter the Question: <br>
            <textarea v-model="formData.question_text" class="input2 question-area" required></textarea>
          </div>
          
          <div class="input">
            Select Chapter: <br>
            <select v-model="formData.chapter_id" class="input2" required>
              <option value="">-- Choose the Chapter --</option>
              <option v-for="chapter in chapters" :key="chapter.chaoter_id" :value="chapter.chaoter_id">
                {{ chapter.chapter_name }} (ID: {{ chapter.chaoter_id }})
              </option>
            </select>
          </div>
          
          <div class="input" v-for="(option, index) in formData.options" :key="index">
            Option {{ index + 1 }}: <br>
            <input type="text" v-model="formData.options[index]" class="input2" required>
          </div>
          
          <div class="input">
            Select the Correct Option (1-4): <br>
            <input type="number" v-model="formData.correct_option" min="1" max="4" class="input2" required>
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
import AdminNavbarComponent from './AdminNavbarComponent.vue';
import questionService from '../services/questionService';

export default {
  name: 'QuestionFormComponent',
  components: {
    AdminNavbarComponent
  },
  data() {
    return {
      isEditMode: false,
      question_id: null,
      chapters: [],
      formData: {
        question_text: '',
        chapter_id: '',
        options: ['', '', '', ''],
        correct_option: null
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
    this.question_id = this.$route.params.id;
    this.isEditMode = !!this.question_id;
    
    try {
      // Fetch available chapters
      await this.fetchChapters();
      
      if (this.isEditMode) {
        await this.fetchQuestionDetails();
      }
    } catch (error) {
      console.error('Error during initialization:', error);
      this.error = 'Failed to initialize form. Please try again.';
      
      if (error.response?.status === 401) {
        this.logout();
      }
    }
  },
  methods: {
    async fetchChapters() {
      try {
        const response = await questionService.getChapters();
        this.chapters = response.chapters;
      } catch (error) {
        console.error('Error fetching chapters:', error);
        this.error = 'Failed to load chapters. Please try again.';
        
        if (error.response?.status === 401) {
          this.logout();
        }
      }
    },
    async fetchQuestionDetails() {
      try {
        const data = await questionService.getQuestionDetails(this.question_id);
        
        // Set question text and chapter ID
        this.formData.question_text = data.question_text;
        this.formData.chapter_id = data.current_chapter_id;
        
        // Process options
        if (data.options && data.options.length > 0) {
          // Map options based on their IDs to maintain order
          const optionsArray = [];
          data.options.forEach(opt => {
            optionsArray.push(opt.option);
          });
          this.formData.options = optionsArray;
        }
        
        // Find index of correct option based on option_id
        if (data.current_answer_id) {
          // Find the index of the option that matches the answer ID
          const correctOptionIndex = data.options.findIndex(opt => opt.option_id === data.current_answer_id);
          if (correctOptionIndex !== -1) {
            this.formData.correct_option = correctOptionIndex + 1; // +1 because form uses 1-4
          }
        }
      } catch (error) {
        console.error('Error fetching question details:', error);
        this.error = 'Failed to load question details. Please try again.';
        
        if (error.response?.status === 401) {
          this.logout();
        }
      }
    },
    async submitForm() {
      this.error = '';
      this.success = '';
      
      if (!this.formData.question_text || !this.formData.chapter_id || 
          !this.formData.options.every(option => option.trim()) || 
          !this.formData.correct_option) {
        this.error = 'Please fill in all required fields';
        return;
      }
      
      try {
        // Create FormData object for API submission
        const formData = new FormData();
        formData.append('question_text', this.formData.question_text);
        formData.append('chapter_id', this.formData.chapter_id);
        
        // Add options to form data
        this.formData.options.forEach((option, index) => {
          formData.append(`option${index + 1}`, option);
        });
        
        formData.append('correct_option', this.formData.correct_option);
        
        if (this.isEditMode) {
          // Edit existing question
          await questionService.updateQuestion(this.question_id, formData);
          this.success = 'Question updated successfully';
        } else {
          // Add new question
          await questionService.addQuestion(formData);
          this.success = 'Question added successfully';
        }
        
        // Redirect after a short delay
        setTimeout(() => {
          this.$router.push('/adminquestions');
        }, 1500);
      } catch (error) {
        console.error('Error submitting form:', error);
        this.error = error.response?.data?.error || 'Failed to save question. Please try again.';
        
        if (error.response?.status === 401) {
          this.logout();
        }
      }
    },
    goBack() {
      this.$router.push('/adminquestions');
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
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

.question-form-container {
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

.user_reg {
  display: flex;
  flex-direction: column;
  border: 1px solid #ddd;
  border-radius: 15px;
  margin: 20px auto;
  max-width: 600px;
  padding: 20px;
  background: linear-gradient(135deg, white 0%, rgb(252, 250, 239) 100%);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
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

.question-area {
  min-height: 120px;
  resize: vertical;
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