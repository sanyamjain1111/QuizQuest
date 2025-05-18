<template>
  <div class="dashboard-container">
    <NavbarComponent @search="handleSearch" />
    
    <div class="dashboard-header">
      <h1 class="dashboard-title">Personal Profile</h1>
    </div>
    
    <div class="main-content">
      <div class="profile-card subject-card">
        <div class="subject-header">
          <div class="profile-header-content">
            <img 
              :src="displayImgUrl" 
              alt="User Profile" 
              class="profile-img" 
            />
            <h2 class="profile-name">{{ fullname }}</h2>
            <button 
              @click="triggerImageUpload" 
              class="profile-img-btn"
              title="Change profile picture"
            >
              <span class="material-icons">edit</span>
              Change Photo
            </button>
          </div>
        </div>
        
        <!-- Alert Messages -->
        <div v-if="warningMsg" class="warning-alert">
          <span class="material-icons warning-icon">error_outline</span>
          <span>{{ warningMsg }}</span>
        </div>
        
        <div v-if="successMsg" class="success-alert">
          <span class="material-icons success-icon">check_circle</span>
          <span>{{ successMsg }}</span>
        </div>
        
        <div class="profile-details-grid">
          <!-- Name Card -->
          <div class="detail-card">
            <div class="detail-header">
              <span class="material-icons detail-icon">person</span>
              <h3 class="detail-title">Name</h3>
            </div>
            <div class="detail-content">
              <p class="detail-value">{{ fullname }}</p>
              <button 
                @click="editField('fullname')" 
                class="detail-edit-btn"
              >
                <span class="material-icons">edit</span>
              </button>
            </div>
          </div>

          <!-- Date of Birth Card -->
          <div class="detail-card">
            <div class="detail-header">
              <span class="material-icons detail-icon">cake</span>
              <h3 class="detail-title">Date of Birth</h3>
            </div>
            <div class="detail-content">
              <p class="detail-value">{{ dob }}</p>
              <button 
                @click="editField('dob')" 
                class="detail-edit-btn"
              >
                <span class="material-icons">edit</span>
              </button>
            </div>
          </div>

          <!-- Username Card -->
          <div class="detail-card">
            <div class="detail-header">
              <span class="material-icons detail-icon">account_circle</span>
              <h3 class="detail-title">Username</h3>
            </div>
            <div class="detail-content">
              <p class="detail-value">{{ username }}</p>
              <!-- Username typically can't be changed -->
            </div>
          </div>

          <!-- Qualification Card -->
          <div class="detail-card">
            <div class="detail-header">
              <span class="material-icons detail-icon">school</span>
              <h3 class="detail-title">Qualification</h3>
            </div>
            <div class="detail-content">
              <p class="detail-value">{{ qualification }}</p>
              <button 
                @click="editField('qualification')" 
                class="detail-edit-btn"
              >
                <span class="material-icons">edit</span>
              </button>
            </div>
          </div>
        </div>
        
        <!-- Save Changes Button -->
        <div class="profile-footer">
          <button 
            @click="saveChanges" 
            class="save-changes-btn"
            :disabled="!hasChanges"
            :class="{'btn-disabled': !hasChanges}"
          >
            <span class="material-icons">save</span>
            Save Changes
          </button>
        </div>
      </div>
    </div>

    <!-- Hidden file input for image upload -->
    <input 
      type="file" 
      ref="fileInput" 
      @change="handleImageUpload" 
      accept="image/*" 
      class="d-none"
    />
  </div>
</template>

<script>
import api from '@/services/api';
import axios from 'axios';

import NavbarComponent from './NavbarComponent.vue';

export default {
  name: 'PersonalDetailsComponent',
  components: {
    NavbarComponent
  },
  data() {
    return {
      id: '',
      fullname: '',
      dob: '',
      imgUrl: '',
      username: '',
      qualification: '',
      warningMsg: '',
      successMsg: '',
      hasChanges: false,
      searchQuery: '',
      originalValues: {}
    };
  },
  computed: {
    displayImgUrl() {
      if (!this.imgUrl) return '/api/placeholder/150/150';
      
      // If the URL is already absolute, return as is
      if (this.imgUrl.startsWith('http')) return this.imgUrl;
      
      // If it's a relative URL from Flask app, prepend the API base URL
      const baseUrl = process.env.VUE_APP_API_URL || 'http://localhost:5000';
      
      // Remove /api from the path if needed to match your Flask static file setup
      const apiBase = baseUrl.endsWith('/api') ? baseUrl.slice(0, -4) : baseUrl;
      
      return `${apiBase}${this.imgUrl}`;
    }
  },
  async mounted() {
    if (!localStorage.getItem('token')) {
    console.warn('No token found. Redirecting to login.');
      this.$router.push('/');
      return;
    }
    
    await this.fetchPersonalDetails();
  },
  methods: {
    async fetchPersonalDetails() {
      try {
        const response = await axios.get('/api/personal_details', {
        headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        const data = response.data;
        console.log('Fetched personal details:', data);
        this.id = data.id;
        this.fullname = data.fullname;
        this.dob = data.dob;
        this.imgUrl = data.img_url;
        this.username = data.username;
        this.qualification = data.qualification;
        
        // Store original values to track changes
        this.originalValues = {
          fullname: this.fullname,
          dob: this.dob,
          imgUrl: this.imgUrl,
          qualification: this.qualification
        };
        
        // Don't store the password client-side for security
        if (data.password) {
          console.warn('Password data was sent to client. This should be avoided.');
        }
      }  catch (error) {
        console.error('Error fetching personal details:', error);
        if (error.response && error.response.status === 401) {
          this.logout();
        } else {
          this.warningMsg = 'Failed to load your details. Please try again later.';
        }
      }
    },
    
    editField(field) {
    console.log(`Editing field: ${field}`);
      this.$router.push(`/edit/${field}`);
    },
    
    triggerImageUpload() {
      this.$refs.fileInput.click();
    },
    
    async handleImageUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      const formData = new FormData();
      formData.append('image', file);
      
      try {
        this.warningMsg = '';
        const response = await api.uploadImage(formData);
        this.imgUrl = response.data.file_url;
        this.hasChanges = true;
        this.successMsg = 'Profile picture updated! Click "Save Changes" to apply.';
        setTimeout(() => {
          this.successMsg = '';
        }, 3000);
      } catch (error) {
        console.error('Image upload failed:', error);
        this.warningMsg = 'Image upload failed. Please try again.';
      }
    },
    
    async saveChanges() {
      if (!this.hasChanges) return;
      
      try {
        this.warningMsg = '';
        
        // Collect changed fields only
        const changedData = {
          id: this.id
        };
        
        if (this.name !== this.originalValues.name) {
          changedData.name = this.name;
        }
        
        if (this.dob !== this.originalValues.dob) {
          changedData.dob = this.dob;
        }
        
        if (this.qualification !== this.originalValues.qualification) {
          changedData.qualification = this.qualification;
        }
        
        if (this.imgUrl !== this.originalValues.imgUrl) {
          changedData.img_url = this.imgUrl;
        }
        
        // Send to backend endpoint
        await api.updatePersonalDetails(changedData);
        
        // Update original values after successful save
        this.originalValues = {
          name: this.name,
          dob: this.dob,
          imgUrl: this.imgUrl,
          qualification: this.qualification
        };
        
        this.hasChanges = false;
        this.successMsg = 'Your changes have been saved successfully!';
        setTimeout(() => {
          this.successMsg = '';
        }, 3000);
      } catch (error) {
        console.error('Failed to save changes:', error);
        this.warningMsg = 'Failed to save your changes. Please try again.';
      }
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
  }
};
</script>


<style scoped>
/* Import Google Material Icons */
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');

.dashboard-container {
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

.profile-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid rgba(91, 192, 190, 0.2);
}

.profile-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08);
}

.subject-header {
  background: linear-gradient(135deg, #0b132b 0%, #1c2541 100%);
  padding: 2rem 1.5rem;
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

.profile-header-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  z-index: 2;
}

.profile-img {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  border: 5px solid white;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  object-fit: cover;
  margin-bottom: 1rem;
}

.profile-name {
  color: white;
  margin: 0.5rem 0;
  font-size: 1.8rem;
  font-weight: 600;
}

.profile-img-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.4);
  color: white;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 0.5rem;
}

.profile-img-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.warning-alert {
  margin: 1.5rem;
  padding: 1rem;
  background-color: #fdeded;
  border-left: 4px solid #f44336;
  color: #d32f2f;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.warning-icon {
  color: #f44336;
}

.profile-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  padding: 1.5rem;
}

.detail-card {
  background: #f8f9fa;
  border-radius: 10px;
  border: 1px solid rgba(91, 192, 190, 0.15);
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.detail-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
}

.detail-header {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
  border-bottom: 1px solid rgba(91, 192, 190, 0.2);
  padding-bottom: 0.5rem;
}

.detail-icon {
  color: #5bc0be;
  margin-right: 0.5rem;
  font-size: 1.3rem;
}

.detail-title {
  color: #0b132b;
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
}

.detail-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-value {
  font-size: 1.1rem;
  color: #3a506b;
  margin: 0;
}

.detail-edit-btn {
  background: transparent;
  border: none;
  color: #5bc0be;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
}

.detail-edit-btn:hover {
  background: rgba(91, 192, 190, 0.1);
  transform: scale(1.1);
}

.profile-footer {
  background: #f8f9fa;
  padding: 1.5rem;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid rgba(91, 192, 190, 0.15);
}

.save-changes-btn {
  background: linear-gradient(135deg, #5bc0be 0%, #3a506b 100%);
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.save-changes-btn:hover:not(.btn-disabled) {
  background: linear-gradient(135deg, #4ca8a7 0%, #2d405a 100%);
  box-shadow: 0 4px 12px rgba(91, 192, 190, 0.3);
  transform: translateY(-2px);
}

.btn-disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.material-icons {
  font-size: 1.2rem;
}
.edit-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.edit-modal-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 500px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.cancel-btn, .confirm-btn {
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.cancel-btn {
  background-color: #f2f2f2;
  border: 1px solid #ddd;
}

.confirm-btn {
  background-color: #4285f4;
  color: white;
  border: none;
}

.success-alert {
  background-color: #d4edda;
  color: #155724;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.success-icon {
  margin-right: 8px;
  color: #28a745;
}

.d-none {
  display: none;
}

/* Responsive adjustments */
@media (max-width: 992px) {
  .profile-details-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-title {
    font-size: 1.8rem;
  }
  
  .profile-name {
    font-size: 1.6rem;
  }
  
  .profile-img {
    width: 120px;
    height: 120px;
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
  
  .subject-header {
    padding: 1.5rem 1rem;
  }
  
  .profile-details-grid {
    padding: 1rem;
    gap: 1rem;
  }
  
  .detail-card {
    padding: 1rem;
  }
  
  .profile-footer {
    padding: 1rem;
  }
}
</style>