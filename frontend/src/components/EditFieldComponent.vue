<template>
  <div class="edit-field-container">
    
    <div class="edit-header">
      <h1 class="edit-title">Edit {{ fieldDisplayName }}</h1>
    </div>
    
    <div class="edit-content">
      <div class="edit-card">
        <!-- Error/Success Message -->
        <div v-if="errorMsg" class="error-alert">
          <span class="material-icons error-icon">error_outline</span>
          <span>{{ errorMsg }}</span>
        </div>
        
        <div v-if="successMsg" class="success-alert">
          <span class="material-icons success-icon">check_circle</span>
          <span>{{ successMsg }}</span>
        </div>
        
        <form @submit.prevent="saveField" class="edit-form">
          <!-- Field Input Based on Type -->
          <div class="form-group">
            <label :for="field">{{ fieldDisplayName }}:</label>
            
            <!-- Date Input -->
            <input 
              v-if="field === 'dob'" 
              type="date" 
              :id="field" 
              v-model="fieldValue"
              class="form-control"
              required
            />
            
            <!-- Text Input for most fields -->
            <input 
              v-else-if="field !== 'img_url'" 
              type="text" 
              :id="field" 
              v-model="fieldValue"
              class="form-control"
              required
            />
            
            <!-- Image Upload -->
            <div v-else class="image-upload-container">
              <img 
                :src="fieldValue || '/api/placeholder/150/150'" 
                alt="Profile Image"
                class="preview-image"
              />
              <input 
                type="file" 
                ref="fileInput" 
                @change="handleImageUpload" 
                accept="image/*" 
                class="file-input"
              />
              <button 
                type="button"
                @click="triggerFileInput"
                class="upload-button"
              >
                <span class="material-icons">upload</span>
                Choose Image
              </button>
            </div>
          </div>
          
          <!-- Password Verification Field -->
          <div class="form-group">
            <label for="password">Current Password (for verification):</label>
            <input 
              type="password" 
              id="password" 
              v-model="password"
              class="form-control"
              placeholder="Enter your current password"
              required
            />
          </div>
          
          <div class="form-actions">
            <button type="button" @click="goBack" class="cancel-btn">
              <span class="material-icons">arrow_back</span>
              Cancel
            </button>
            
            <button type="submit" class="save-btn" :disabled="isSubmitting">
              <span class="material-icons">save</span>
              {{ isSubmitting ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  name: 'EditFieldComponent',
  
  props: {
    field: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      fieldValue: '',
      originalValue: '',
      password: '', // Added for password verification
      errorMsg: '',
      successMsg: '',
      isSubmitting: false,
      searchQuery: '',
      fieldDisplayNames: {
        fullname: 'Full Name',
        dob: 'Date of Birth',
        qualification: 'Qualification',
        imgUrl: 'Profile Picture'
      }
    };
  },
  computed: {
    fieldDisplayName() {
      return this.fieldDisplayNames[this.field] || this.capitalizeFirstLetter(this.field);
    }
  },
  async created() {
    if (!localStorage.getItem('token')) {
      this.$router.push('/');
      return;
    }
    
    await this.fetchFieldData();
  },
  methods: {
    capitalizeFirstLetter(string) {
      return string.charAt(0).toUpperCase() + string.slice(1);
    },
    
    async fetchFieldData() {
      try {
        // Fetch the specific field data using the API
        const response = await api.getEditForm(this.field);
        console.log('Field data response:', response);
        
        // Extract field value from response
        if (response && response.data) {
          this.fieldValue = response.data[this.field] || '';
          this.originalValue = this.fieldValue;
        }
      } catch (error) {
        console.error(`Error fetching ${this.field} data:`, error);
        this.errorMsg = `Failed to load ${this.fieldDisplayName.toLowerCase()}. Please try again.`;
        
        // If unauthorized, redirect to login
        if (error.response && error.response.status === 401) {
          this.logout();
        }
      }
    },
    
    triggerFileInput() {
      if (this.$refs.fileInput) {
        this.$refs.fileInput.click();
      }
    },
    
    async handleImageUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      const formData = new FormData();
      formData.append('image', file);
      
      try {
        this.errorMsg = '';
        this.isSubmitting = true;
        
        const response = await api.uploadImage(formData);
        
        if (response && response.data && response.data.img_url) {
          this.fieldValue = response.data.img_url;
        }
      } catch (error) {
        console.error('Image upload failed:', error);
        this.errorMsg = 'Image upload failed. Please try again.';
      } finally {
        this.isSubmitting = false;
      }
    },
    
    goBack() {
      this.$router.push('/personal_details');
    },
    
    async saveField() {
      // Don't submit if there are no changes
      if (this.fieldValue === this.originalValue) {
        this.goBack();
        return;
      }
      
      // Validate password is not empty
      if (!this.password.trim()) {
        this.errorMsg = 'Please enter your current password for verification';
        return;
      }
      
      this.isSubmitting = true;
      this.errorMsg = '';
      this.successMsg = '';
      
      try {
        // Prepare data with the changed field, password and user id
        const data = {
          id: localStorage.getItem('uid') || '',
          password: this.password // Include password for verification
        };
        
        // Map the field name to backend field name if needed
        if (this.field === 'imgUrl') {
          data.img_url = this.fieldValue;
        } else {
          data[this.field] = this.fieldValue;
        }
        
        // Save changes to the backend
        await api.updatePersonalDetails(data);
        
        this.successMsg = `${this.fieldDisplayName} updated successfully!`;
        
        // Redirect after showing success message
        setTimeout(() => {
          this.$router.push('/personal_details');
        }, 1500);
      } catch (error) {
        console.error(`Error saving ${this.field}:`, error);
        
        // Handle specific error for incorrect password
        if (error.response && error.response.status === 401) {
          this.errorMsg = 'Incorrect password. Please try again.';
        } else if (error.response && error.response.status === 403) {
          this.errorMsg = 'You are not authorized to make this change.';
          this.logout();
        } else {
          this.errorMsg = `Failed to update ${this.fieldDisplayName.toLowerCase()}. Please try again.`;
        }
      } finally {
        this.isSubmitting = false;
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
.edit-field-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.edit-header {
  margin-bottom: 30px;
  text-align: center;
}

.edit-title {
  font-size: 24px;
  font-weight: 600;
}

.edit-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  color: #333;
}

.form-control {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  width: 100%;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.cancel-btn, .save-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.cancel-btn {
  background-color: #f2f2f2;
  border: 1px solid #ddd;
  color: #333;
}

.save-btn {
  background-color: #4285f4;
  border: none;
  color: white;
}

.save-btn:disabled {
  background-color: #a0c1f4;
  cursor: not-allowed;
}

.error-alert {
  background-color: #f8d7da;
  color: #721c24;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.error-icon {
  margin-right: 8px;
  color: #dc3545;
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

.image-upload-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.preview-image {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #ddd;
}

.file-input {
  display: none;
}

.upload-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background-color: #f2f2f2;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.upload-button:hover {
  background-color: #e5e5e5;
}
</style>