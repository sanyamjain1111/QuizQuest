<template>
  <div class="chapter-form-container">
    <!-- Reuse the AdminNavbarComponent we have -->
    <AdminNavbarComponent />
    
    <div class="dashboard-header">
      <h1 class="dashboard-title">{{ isEditMode ? 'Edit Chapter' : 'Add New Chapter' }}</h1>
    </div>
    
    <div class="main-content">
      <div class="user_reg">
        <div class="ahead">{{ isEditMode ? 'Edit' : 'Add New' }} Chapter</div>
        
        <div class="alert alert-danger" v-if="error">{{ error }}</div>
        <div class="alert alert-success" v-if="success">{{ success }}</div>
        
        <form @submit.prevent="submitForm" class="form">
          <div class="input">
            Enter the chapter name: <br>
            <input type="text" v-model="formData.chapter_name" class="input2" required>
          </div>
          <br>
          <div class="input">
            Select subject: <br>
            <select v-model="formData.subject_id" class="input2" required>
              <option value="">-- Select Subject --</option>
              <option v-for="subject in subjects" :key="subject.subject_id" :value="subject.subject_id">
                {{ subject.subject_name }}
              </option>
            </select>
          </div>
          <br>
          <div class="input">
            Enter the description: <br>
            <textarea v-model="formData.description" class="input2 description-area" required></textarea>
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
import chapterService from '../services/chapterService';

export default {
  name: 'ChapterFormComponent',
  components: {
    AdminNavbarComponent
  },
  data() {
    return {
      isEditMode: false,
      chapter_id: null,
      subjects: [],
      formData: {
        chapter_name: '',
        subject_id: '',
        description: ''
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
    
    // Fetch available subjects
    await this.fetchSubjects();
    
    // Check if we're in edit mode
    this.chapter_id = this.$route.params.id;
    this.isEditMode = !!this.chapter_id;
    
    if (this.isEditMode) {
      await this.fetchChapterDetails();
    }
  },
  methods: {
    async fetchSubjects() {
      try {
        const response = await chapterService.getSubjects();
        this.subjects = response.subjects;
      } catch (error) {
        console.error('Error fetching subjects:', error);
        this.error = 'Failed to load subjects. Please try again.';
        
        if (error.response?.status === 401) {
          this.logout();
        }
      }
    },
    async fetchChapterDetails() {
      try {
        const chapterData = await chapterService.getChapterDetails(this.chapter_id);
        
        this.formData = {
          chapter_name: chapterData.chapter_name,
          subject_id: chapterData.current_subject_id,
          description: chapterData.description
        };
      } catch (error) {
        console.error('Error fetching chapter details:', error);
        this.error = 'Failed to load chapter details. Please try again.';
        
        if (error.response?.status === 401) {
          this.logout();
        }
      }
    },
    async submitForm() {
      this.error = '';
      this.success = '';
      
      if (!this.formData.chapter_name || !this.formData.subject_id || !this.formData.description) {
        this.error = 'Please fill in all required fields';
        return;
      }
      
      try {
        if (this.isEditMode) {
          // Edit existing chapter
          await chapterService.updateChapter(this.chapter_id, this.formData);
          this.success = 'Chapter updated successfully';
        } else {
          // Add new chapter
          await chapterService.addChapter(this.formData);
          this.success = 'Chapter added successfully';
        }
        
        // Redirect after a short delay
        setTimeout(() => {
          this.$router.push('/adminchapters');
        }, 1500);
      } catch (error) {
        console.error('Error submitting form:', error);
        this.error = error.response?.data?.error || 'Failed to save chapter. Please try again.';
        
        if (error.response?.status === 401) {
          this.logout();
        }
      }
    },
    goBack() {
      this.$router.push('/adminchapters');
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

.chapter-form-container {
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

.description-area {
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