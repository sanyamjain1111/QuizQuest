<template>
  <div class="dashboard-container">
    <NavbarComponent @search="handleSearch" />
    
    <div class="dashboard-header">
      <h1 class="dashboard-title">{{ message }}</h1>
    </div>
    
    <div class="main-content">
      <!-- Add Reminder Settings Component -->
      <div class="reminder-container">
        <ReminderSettingsComponent />
      </div>
      
      <div v-for="subject in filteredSubjects" :key="subject.subject_id" class="subject-card">
        <div class="subject-header">
          <h2 class="subject-title">{{ subject.subject_name }}</h2>
        </div>
        
        <div class="subject-description">
          <p>{{ subject.description }}</p>
        </div>
        
        <div v-if="filteredChapters(subject.subject_id).length > 0" class="chapters-section">
          <h3 class="chapters-title">Chapters</h3>
          
          <div class="chapters-grid">
            <div 
              v-for="chapter in filteredChapters(subject.subject_id)" 
              :key="chapter.chapter_id" 
              class="chapter-item"
            >
              <div class="dropdown chapter-dropdown">
                <button 
                  class="chapter-button" 
                  type="button" 
                  :id="'dropdown' + chapter.chapter_id" 
                  data-bs-toggle="dropdown" 
                  aria-expanded="false"
                >
                  <span class="chapter-name">{{ chapter.chapter_name }}</span>
                  <span class="material-icons chapter-icon">expand_more</span>
                </button>
                <ul class="dropdown-menu chapter-dropdown-menu" :aria-labelledby="'dropdown' + chapter.chapter_id">
                  <li class="chapter-dropdown-item">
                    <div class="chapter-description">{{ chapter.description }}</div>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Empty state when no subjects match search -->
      <div v-if="filteredSubjects.length === 0" class="empty-state">
        <span class="material-icons empty-icon">search_off</span>
        <h3>No subjects found</h3>
        <p>Try adjusting your search query</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import NavbarComponent from './NavbarComponent.vue';
import ReminderSettingsComponent from './ReminderSettingsComponent.vue';
import { Dropdown } from 'bootstrap';

export default {
  name: 'DashboardComponent',
  components: {
    NavbarComponent,
    ReminderSettingsComponent
  },
  data() {
    return {
      subjects: [],
      chapters: [],
      message: 'Academics Dashboard',
      searchQuery: '',
      dropdowns: []
    };
  },
  computed: {
    filteredSubjects() {
      if (!this.searchQuery) return this.subjects;
      return this.subjects.filter(subject => 
        subject.subject_name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        subject.description.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    }
  },
  async mounted() {
    if (!localStorage.getItem('token')) {
      this.$router.push('/');
      return;
    }
    
    await this.fetchData();
    this.initDropdowns();
  },
  methods: {
    async fetchData() {
      try {
        const response = await axios.get(`/api/user/${localStorage.getItem('fullname')}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        this.subjects = response.data.subjects;
        this.chapters = response.data.chapters;
      } catch (error) {
        console.error('Error fetching data:', error);
        if (error.response?.status === 401) {
          this.logout();
        }
      }
    },
    initDropdowns() {
      this.$nextTick(() => {
        const dropdownElements = document.querySelectorAll('.dropdown-toggle, .chapter-button');
        this.dropdowns = Array.from(dropdownElements).map(
          el => new Dropdown(el)
        );
      });
    },
    filteredChapters(subjectId) {
      return this.chapters.filter(chapter => chapter.subject_id === subjectId);
    },
    handleSearch(query) {
      this.searchQuery = query;
    },
    logout() {
      localStorage.removeItem('token');
      localStorage.removeItem('fullname');
      localStorage.removeItem('uid');
      this.$router.push('/');
    }
  },
  beforeUnmount() {
    // Clean up Bootstrap dropdowns
    this.dropdowns.forEach(dropdown => dropdown.dispose());
  }
};
</script>

<style scoped>
/* Import Google Material Icons */

.dashboard-container {
  font-family: 'Poppins', sans-serif;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ec 100%);
  color: #1c2541;
  max-width: 1200px; /* Same width as Dashboard */
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
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(540px, 1fr));
  gap: 2rem;
}

/* Reminder container styling */
.reminder-container {
  grid-column: 1 / -1; /* Make it span all columns */
  width: 100%;
}

.subject-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid rgba(91, 192, 190, 0.2);
}

.subject-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08);
}

.subject-header {
  background: linear-gradient(135deg, #0b132b 0%, #1c2541 100%);
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
}

.subject-header:before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(91, 192, 190, 0.2) 0%, rgba(91, 192, 190, 0) 70%);
  z-index: 1;
}

.subject-title {
  color: white;
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  position: relative;
  z-index: 2;
}

.subject-description {
  padding: 1.5rem;
  font-size: 1rem;
  line-height: 1.7;
  color: #3a506b;
  border-bottom: 1px solid rgba(91, 192, 190, 0.15);
  min-height: 120px;
}

.chapters-section {
  padding: 1.5rem;
}

.chapters-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 1.2rem;
  color: #0b132b;
  display: flex;
  align-items: center;
}

.chapters-title:before {
  content: '';
  display: inline-block;
  width: 4px;
  height: 18px;
  background: linear-gradient(to bottom, #5bc0be, #3a506b);
  margin-right: 10px;
  border-radius: 2px;
}

.chapters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.chapter-item {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.chapter-dropdown {
  width: 100%;
}

.chapter-button {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #5bc0be 0%, #3a506b 100%);
  color: white;
  border: none;
  padding: 0.8rem 1.2rem;
  font-family: 'Poppins', sans-serif;
  font-size: 0.95rem;
  font-weight: 500;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
}

.chapter-button:hover, .chapter-button:focus {
  background: linear-gradient(135deg, #4ca8a7 0%, #2d405a 100%);
  box-shadow: 0 4px 12px rgba(91, 192, 190, 0.3);
  transform: translateY(-2px);
}

.chapter-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 85%;
}

.chapter-icon {
  font-size: 1.2rem;
  transition: transform 0.3s ease;
}

.chapter-button[aria-expanded="true"] .chapter-icon {
  transform: rotate(180deg);
}

.chapter-dropdown-menu {
  width: 100%;
  padding: 1rem;
  margin-top: 0.5rem;
  background-color: white;
  border: 1px solid rgba(91, 192, 190, 0.2);
  border-radius: 8px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}

.chapter-dropdown-item {
  padding: 0;
}

.chapter-description {
  font-size: 0.9rem;
  line-height: 1.6;
  color: #3a506b;
  white-space: normal;
  max-width: 100%;
}

.empty-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  color: #a0aec0;
}

/* Responsive adjustments */
@media (max-width: 992px) {
  .main-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-title {
    font-size: 1.8rem;
  }
  
  .subject-title {
    font-size: 1.3rem;
  }
  
  .subject-description {
    font-size: 0.95rem;
  }
  
  .chapters-grid {
    grid-template-columns: 1fr;
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
  
  .subject-header, .subject-description, .chapters-section {
    padding: 1rem;
  }
}
</style>