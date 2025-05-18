<template>
  <div class="admin-dashboard-container">
    <!-- Reuse the AdminNavbarComponent we have -->
    <AdminNavbarComponent @search="handleSearch" />
    
    <div class="dashboard-header">
      <h1 class="dashboard-title">Chapters Management</h1>
    </div>
    
    <div class="main-content">
      <!-- Add Chapter Button -->
      <div class="action-buttons">
        <router-link to="/admin/chapters/add" class="add-quiz-btn">
          <span class="material-icons">add</span>
          Add New Chapter
        </router-link>
      </div>

      <!-- Filter by Subject dropdown -->
      <div class="filter-container" v-if="subjects.length > 0">
        <div class="filter-dropdown">
          <label for="subjectFilter">Filter by Subject:</label>
          <select id="subjectFilter" v-model="selectedSubject" class="form-select">
            <option value="">All Subjects</option>
            <option v-for="subject in subjects" :key="subject.subject_id" :value="subject.subject_id">
              {{ subject.subject_name }}
            </option>
          </select>
        </div>
      </div>

      <!-- Alert messages -->
      <div class="alert alert-danger" v-if="error">{{ error }}</div>
      <div class="alert alert-success" v-if="success">{{ success }}</div>
      
      <!-- Loading state -->
      <div v-if="loading" class="empty-state">
        <span class="material-icons empty-icon">hourglass_top</span>
        <h3>Loading chapters...</h3>
      </div>
      
      <!-- Chapters List Container -->
      <div v-else class="quiz-container">
        <div class="quiz-count" v-if="filteredChapters.length > 0">
          <span class="material-icons">menu_book</span>
          <span>{{ filteredChapters.length }} {{ filteredChapters.length === 1 ? 'Chapter' : 'Chapters' }} Available</span>
        </div>
        
        <div v-if="filteredChapters.length > 0" class="quiz-list">
          <div v-for="(chapter, index) in filteredChapters" :key="chapter.chaoter_id" class="quiz-item">
            <div class="quiz-badge">{{ index + 1 }}</div>
            <div class="quiz-item-header">
              <div class="quiz-item-title">
                <span class="quiz-id">Chapter #{{ chapter.chaoter_id }}</span>
                <span class="chapter-name">{{ chapter.chapter_name }}</span>
              </div>
              <div class="quiz-item-meta">
                <div class="meta-item description-meta">
                  <span class="material-icons">description</span>
                  <span>{{ truncateText(chapter.description, 150) }}</span>
                </div>
                <div class="meta-item">
                  <span class="material-icons">category</span>
                  <span>Subject: {{ getSubjectName(chapter.subject_id) }}</span>
                </div>
              </div>
            </div>
            <div class="quiz-item-actions">
              <router-link :to="`/admin/chapters/edit/${chapter.chaoter_id}`" class="action-btn edit-btn">
                <span class="material-icons">edit</span>
                Edit
              </router-link>
              <button class="action-btn delete-btn" @click="confirmDelete(chapter)">
                <span class="material-icons">delete</span>
                Delete
              </button>
            </div>
          </div>
        </div>
        
        <!-- Empty state when no chapters exist -->
        <div v-if="chapters.length === 0" class="empty-state">
          <span class="material-icons empty-icon">book</span>
          <h3>No Chapters Created</h3>
          <p>Create your first chapter by clicking the "Add New Chapter" button above</p>
        </div>
        
        <!-- Empty state when no chapters match filters -->
        <div v-if="chapters.length > 0 && filteredChapters.length === 0" class="empty-state">
          <span class="material-icons empty-icon">search_off</span>
          <h3>No matching chapters found</h3>
          <p>Try adjusting your search or filter criteria</p>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Confirm Delete</h3>
        <p>Are you sure you want to delete chapter "{{ chapterToDelete?.chapter_name }}"?</p>
        <p class="modal-warning">This action cannot be undone!</p>
        <div class="modal-buttons">
          <button @click="deleteChapter" class="confirm-button">Yes, Delete</button>
          <button @click="cancelDelete" class="cancel-button">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AdminNavbarComponent from './AdminNavbarComponent.vue';
import chapterService from '../services/chapterService';

export default {
  name: 'ChaptersPage',
  components: {
    AdminNavbarComponent
  },
  data() {
    return {
      chapters: [],
      subjects: [],
      loading: true,
      error: '',
      success: '',
      selectedSubject: '',
      searchTerm: '',
      showDeleteModal: false,
      chapterToDelete: null
    };
  },
  async created() {
    if (!localStorage.getItem('adminToken')) {
      this.$router.push('/');
      return;
    }
    
    await this.fetchData();
  },
  computed: {
    filteredChapters() {
      let result = this.chapters;
      
      if (this.selectedSubject) {
        result = result.filter(chapter => 
          chapter.subject_id === parseInt(this.selectedSubject)
        );
      }
      
      if (this.searchTerm) {
        const searchLower = this.searchTerm.toLowerCase();
        result = result.filter(chapter => 
          chapter.chapter_name.toLowerCase().includes(searchLower) ||
          (chapter.description && chapter.description.toLowerCase().includes(searchLower))
        );
      }
      
      return result;
    }
  },
  methods: {
    async fetchData() {
      this.loading = true;
      this.error = '';
      
      try {
        const response = await chapterService.getChapters();
        this.chapters = response.chapters;
        this.subjects = response.subjects;
      } catch (error) {
        console.error('Error fetching data:', error);
        this.error = 'Failed to load chapters. Please try again.';
        
        if (error.response?.status === 401) {
          this.logout();
        }
      } finally {
        this.loading = false;
      }
    },
    getSubjectName(subjectId) {
      const subject = this.subjects.find(s => s.subject_id === subjectId);
      return subject ? subject.subject_name : 'Unknown Subject';
    },
    truncateText(text, maxLength) {
      if (text && text.length > maxLength) {
        return text.substring(0, maxLength) + '...';
      }
      return text;
    },
    handleSearch(query) {
      this.searchTerm = query;
    },
    confirmDelete(chapter) {
      this.chapterToDelete = chapter;
      this.showDeleteModal = true;
    },
    async deleteChapter() {
      if (!this.chapterToDelete) return;
      
      this.error = '';
      this.success = '';
      
      try {
        await chapterService.deleteChapter(this.chapterToDelete.chaoter_id);
        this.success = `Chapter "${this.chapterToDelete.chapter_name}" deleted successfully.`;
        
        // Remove from local array
        this.chapters = this.chapters.filter(
          chapter => chapter.chaoter_id !== this.chapterToDelete.chaoter_id
        );
        
        this.showDeleteModal = false;
        this.chapterToDelete = null;
        
        // Show success notification if toast is available
        if (this.$toast) {
          this.$toast.success('Chapter deleted successfully', {
            position: 'top-right',
            duration: 3000
          });
        }
      } catch (error) {
        console.error('Error deleting chapter:', error);
        this.error = error.response?.data?.error || 'Failed to delete chapter. Please try again.';
        
        if (error.response?.status === 401) {
          this.logout();
        }
        
        // Show error notification if toast is available
        if (this.$toast) {
          this.$toast.error(this.error, {
            position: 'top-right',
            duration: 3000
          });
        }
      }
    },
    cancelDelete() {
      this.showDeleteModal = false;
      this.chapterToDelete = null;
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
  text-decoration: none;
}

.add-quiz-btn:hover {
  background: linear-gradient(135deg, #f27059 0%, #c54c40 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(255, 126, 103, 0.3);
}

/* Filter styles */
.filter-container {
  margin-bottom: 1.5rem;
  background: white;
  padding: 1rem;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

.filter-dropdown {
  display: flex;
  align-items: center;
  gap: 1rem;
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

/* List Style for Chapters */
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

.description-meta {
  flex-basis: 100%;
  margin-bottom: 0.5rem;
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
  text-decoration: none;
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

/* Alert styles */
.alert {
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-weight: 500;
}

.alert-danger {
  background-color: rgba(231, 76, 60, 0.1);
  color: #c0392b;
  border-left: 4px solid #e74c3c;
}

.alert-success {
  background-color: rgba(46, 204, 113, 0.1);
  color: #27ae60;
  border-left: 4px solid #2ecc71;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.modal-content h3 {
  color: #1a1b2e;
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-weight: 600;
}

.modal-warning {
  color: #e74c3c;
  font-weight: 500;
  margin-top: 1rem;
}

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.confirm-button, .cancel-button {
  padding: 0.8rem 1.5rem;
  border-radius: 30px;
  font-family: 'Poppins', sans-serif;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.3s ease;
}

.confirm-button {
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  color: white;
}

.confirm-button:hover {
  background: linear-gradient(135deg, #d44637 0%, #a53125 100%);
  transform: translateY(-2px);
}

.cancel-button {
  background: #f5f7fa;
  color: #1a1b2e;
  border: 1px solid #ddd;
}

.cancel-button:hover {
  background: #e4e7ec;
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
  
  .filter-dropdown {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filter-dropdown .form-select {
    width: 100%;
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