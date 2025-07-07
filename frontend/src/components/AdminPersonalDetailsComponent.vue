<template>
  <div class="admin-dashboard-container">
    <AdminNavbarComponent @search="handleSearch" />
    
    <div class="dashboard-header">
      <h1 class="dashboard-title">Student Personal Details</h1>
    </div>
    
    <div class="main-content">
      <!-- Filter options -->
      <div class="filter-container">
        <div class="filter-dropdown">
          <label for="userFilter">Filter by Status:</label>
          <select id="userFilter" v-model="selectedStatus" class="form-select">
            <option value="">All Users</option>
            <option value="active">Blocked Users</option>
            <option value="inactive">Unblocked Users</option>
          </select>
        </div>
      </div>

      <!-- Alert messages -->
      <div class="alert alert-danger" v-if="error">{{ error }}</div>
      <div class="alert alert-success" v-if="success">{{ success }}</div>
      
      <!-- Loading state -->
      <div v-if="loading" class="empty-state">
        <span class="material-icons empty-icon">hourglass_top</span>
        <h3>Loading user data...</h3>
      </div>
      
      <!-- Users List Container -->
      <div v-else class="users-container">
        <div class="users-count" v-if="filteredUsers.length > 0">
          <span class="material-icons">people</span>
          <span>{{ filteredUsers.length }} {{ filteredUsers.length === 1 ? 'User' : 'Users' }} Found</span>
        </div>
        
        <div v-if="filteredUsers.length > 0" class="users-list">
          <div v-for="(user, index) in filteredUsers" :key="user.uid" class="user-item">
            <div class="user-badge">{{ index + 1 }}</div>
            <div class="user-item-header">
              <div class="user-profile">
                <img :src="getUserImageUrl(user.file_url)" alt="User Profile" class="user-img" />
                <div class="user-info">
                  <h3 class="user-name">{{ user.fullname }}</h3>
                  <span class="user-username">@{{ user.username }}</span>
                </div>
              </div>
              
              <div class="user-stats-grid">
                <!-- Personal Details -->
                <div class="user-detail-card">
                  <div class="detail-header">
                    <span class="material-icons detail-icon">person</span>
                    <h3 class="detail-title">Personal Details</h3>
                  </div>
                  <div class="detail-content">
                    <div class="detail-row">
                      <span class="detail-label">User ID:</span>
                      <span class="detail-value">{{ user.uid }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="detail-label">Date of Birth:</span>
                      <span class="detail-value">{{ user.dob || 'Not specified' }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="detail-label">Qualification:</span>
                      <span class="detail-value">{{ user.qualification || 'Not specified' }}</span>
                    </div>
                  </div>
                </div>
                
                <!-- Security Information -->
                <div class="user-detail-card">
                  <div class="detail-header">
                    <span class="material-icons detail-icon">security</span>
                    <h3 class="detail-title">Account Information</h3>
                  </div>
                  <div class="detail-content">
                    <div class="detail-row">
                      <span class="detail-label">Password:</span>
                      <span class="detail-value">******</span>
                    </div>
                    <div class="detail-row">
                      <span class="detail-label">Status:</span>
                      <span class="detail-value">{{ user.is_active ? 'Active' : 'Unblocked' }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="detail-label">Registration:</span>
                      <span class="detail-value">{{ user.created_at || 'Unknown' }}</span>
                    </div>
                  </div>
                </div>
                
                <!-- Files Information -->
                <div class="user-detail-card">
                  <div class="detail-header">
                    <span class="material-icons detail-icon">folder</span>
                    <h3 class="detail-title">Uploaded Files</h3>
                  </div>
                  <div class="detail-content">
                    <div v-if="getUserFiles(user.uid).length > 0" class="file-list">
                      <div v-for="(file, idx) in getUserFiles(user.uid)" :key="idx" class="file-item">
                        <span class="material-icons file-icon">description</span>
                        <div class="file-info">
                          <div class="file-name">{{ file.filename }}</div>
                          <div class="file-date">Uploaded: {{ formatDate(file.upload_date) }}</div>
                        </div>
                      </div>
                    </div>
                    <div v-else class="no-data">
                      No files uploaded
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="user-actions">
              <button class="action-btn view-btn" @click="openDetailsModal(user)">
                <span class="material-icons">visibility</span>
                View Details
              </button>
              <button class="action-btn delete-btn" @click="confirmDelete(user)">
                <span class="material-icons">delete</span>
                Delete User
              </button>
            </div>
          </div>
        </div>
        
        <!-- Empty state when no users exist -->
        <div v-if="users.length === 0" class="empty-state">
          <span class="material-icons empty-icon">people_outline</span>
          <h3>No Users Found</h3>
          <p>There are currently no registered users in the system</p>
        </div>
        
        <!-- Empty state when no users match filters -->
        <div v-if="users.length > 0 && filteredUsers.length === 0" class="empty-state">
          <span class="material-icons empty-icon">search_off</span>
          <h3>No matching users found</h3>
          <p>Try adjusting your search or filter criteria</p>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Confirm User Deletion</h3>
        <p>Are you sure you want to delete this user account? This will remove all associated data including:</p>
        <ul class="delete-warning-list">
          <li>Profile information</li>
          <li>Quiz responses</li>
          <li>Score history</li>
          <li>Uploaded files</li>
        </ul>
        <div class="user-preview">
          <img :src="getUserImageUrl(userToDelete?.file_url)" alt="User Profile" class="user-preview-img" />
          <div>
            <h4>{{ userToDelete?.fullname }}</h4>
            <p>User ID: {{ userToDelete?.uid }}</p>
          </div>
        </div>
        <p class="modal-warning">This action cannot be undone!</p>
        <div class="modal-buttons">
          <button @click="deleteUser" class="confirm-button">Yes, Delete User</button>
          <button @click="cancelDelete" class="cancel-button">Cancel</button>
        </div>
      </div>
    </div>

    <!-- User Details Modal -->
    <div v-if="showDetailsModal" class="modal-overlay" @click="closeDetailsModal"></div>
    <div v-if="showDetailsModal" class="modal-container" role="dialog" aria-labelledby="userDetailsModalLabel">
      <div class="modal-content user-details-modal">
        <div class="modal-header">
          <h3 class="modal-title" id="userDetailsModalLabel">User Details</h3>
          <button type="button" class="close-button" @click="closeDetailsModal" aria-label="Close">
            <span class="material-icons">close</span>
          </button>
        </div>
        <div class="modal-body">
          <!-- User Profile Section -->
          <div class="modal-profile-section">
            <img :src="getUserImageUrl(selectedUser?.file_url)" alt="User Profile" class="modal-user-img" />
            <div class="modal-user-heading">
              <h2 class="modal-user-name">{{ selectedUser?.fullname }}</h2>
              <span class="modal-user-username">@{{ selectedUser?.username }}</span>
            </div>
          </div>

          <!-- User Details Sections -->
          <div class="modal-details-grid">
            <!-- Personal Information -->
            <div class="modal-detail-section">
              <div class="modal-section-header">
                <span class="material-icons">person</span>
                <h4>Personal Information</h4>
              </div>
              <div class="modal-detail-list">
                <div class="modal-detail-item">
                  <div class="modal-detail-label">User ID</div>
                  <div class="modal-detail-value">{{ selectedUser?.uid }}</div>
                </div>
                <div class="modal-detail-item">
                  <div class="modal-detail-label">Full Name</div>
                  <div class="modal-detail-value">{{ selectedUser?.fullname }}</div>
                </div>
                <div class="modal-detail-item">
                  <div class="modal-detail-label">Username</div>
                  <div class="modal-detail-value">{{ selectedUser?.username }}</div>
                </div>
                <div class="modal-detail-item">
                  <div class="modal-detail-label">Date of Birth</div>
                  <div class="modal-detail-value">{{ selectedUser?.dob || 'Not specified' }}</div>
                </div>
                <div class="modal-detail-item">
                  <div class="modal-detail-label">Qualification</div>
                  <div class="modal-detail-value">{{ selectedUser?.qualification || 'Not specified' }}</div>
                </div>
              </div>
            </div>

            <!-- Contact Information -->
            <div class="modal-detail-section">
              <div class="modal-section-header">
                <span class="material-icons">contact_mail</span>
                <h4>Contact Information</h4>
              </div>
              <div class="modal-detail-list">
                <div class="modal-detail-item">
                  <div class="modal-detail-label">Email</div>
                  <div class="modal-detail-value">{{ selectedUser?.username }}</div>
                </div>
                <div class="modal-detail-item">
                  <div class="modal-detail-label">Phone</div>
                  <div class="modal-detail-value">{{ selectedUser?.phone || 'Not available' }}</div>
                </div>
              </div>
            </div>

            <!-- Account Details -->
            <div class="modal-detail-section">
              <div class="modal-section-header">
                <span class="material-icons">security</span>
                <h4>Account Details</h4>
              </div>
              <div class="modal-detail-list">
                
                <div class="modal-detail-item">
                  <div class="modal-detail-label">Account Status</div>
                  <div class="modal-detail-value">{{ selectedUser?.is_active ? 'Active' : 'Unblocked' }}</div>
                </div>
                <div class="modal-detail-item">
                  <div class="modal-detail-label">Last Login</div>
                  <div class="modal-detail-value">{{ selectedUser?.last_login || 'Not available' }}</div>
                </div>
              </div>
            </div>

            <!-- Uploaded Files -->
            <div class="modal-detail-section">
              <div class="modal-section-header">
                <span class="material-icons">folder</span>
                <h4>Uploaded Files</h4>
              </div>
              <div class="modal-detail-content">
                <div v-if="selectedUserFiles.length > 0" class="modal-files-list">
                  <div v-for="(file, idx) in selectedUserFiles" :key="idx" class="modal-file-item">
                    <span class="material-icons">description</span>
                    <div class="modal-file-details">
                      <div class="modal-file-name">{{ file.filename }}</div>
                      <div class="modal-file-info">Uploaded: {{ formatDate(file.upload_date) }}</div>
                    </div>
                  </div>
                </div>
                <div v-else class="modal-no-data">
                  <span class="material-icons">info</span>
                  No files uploaded by this user
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="modal-close-btn" @click="closeDetailsModal">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AdminNavbarComponent from './AdminNavbarComponent.vue';
import api from '@/services/api';

export default {
  name: 'AdminPersonalDetailsComponent',
  components: {
    AdminNavbarComponent
  },
  data() {
    return {
      users: [],
      files: [],
      loading: true,
      error: '',
      success: '',
      selectedStatus: '',
      searchTerm: '',
      showDeleteModal: false,
      userToDelete: null,
      showDetailsModal: false,
      selectedUser: null
    };
  },
  async created() {
    if (!localStorage.getItem('adminToken')) {
      this.$router.push('/');
      return;
    }
    
    await this.fetchData();
    
    // Add event listener for escape key to close modals
    document.addEventListener('keydown', this.handleKeyDown);
  },
  beforeUnmount() {
    // Remove event listener
    document.removeEventListener('keydown', this.handleKeyDown);
  },
  computed: {
    filteredUsers() {
      let result = this.users;
      
      if (this.selectedStatus === 'active') {
        result = result.filter(user => user.is_active);
      } else if (this.selectedStatus === 'inactive') {
        result = result.filter(user => !user.is_active);
      }
      
      if (this.searchTerm) {
        const searchLower = this.searchTerm.toLowerCase();
        result = result.filter(user => 
          user.fullname?.toLowerCase().includes(searchLower) ||
          user.username?.toLowerCase().includes(searchLower) ||
          (user.qualification && user.qualification.toLowerCase().includes(searchLower))
        );
      }
      
      return result;
    },
    selectedUserFiles() {
      if (!this.selectedUser) return [];
      return this.getUserFiles(this.selectedUser.uid);
    }
  },
  methods: {
    async fetchData() {
      this.loading = true;
      this.error = '';
      
      try {
        // Use the dedicated method from the API service instead of direct path
        const response = await api.getStudentPersonalDetails();
        this.users = response.data.users || [];
        this.files = response.data.files || [];
        console.log('Users:', this.users);
        console.log('Files:', this.files);
      } catch (error) {
        console.error('Error fetching data:', error);
        
        // More detailed error message for debugging
        if (error.response) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          console.error('Response data:', error.response.data);
          console.error('Response status:', error.response.status);
          this.error = `Failed to load user data (${error.response.status}): ${error.response.data.message || 'Unknown error'}`;
        } else if (error.request) {
          // The request was made but no response was received
          console.error('No response received:', error.request);
          this.error = 'Server not responding. Please check your API server is running.';
        } else {
          // Something happened in setting up the request that triggered an Error
          console.error('Request error:', error.message);
          this.error = `Request error: ${error.message}`;
        }
        
        if (error.response?.status === 401) {
          this.logout();
        }
      } finally {
        this.loading = false;
      }
    },
    
    getUserImageUrl(imgUrl) {
      if (!imgUrl) return '/api/placeholder/64/64';
      
      // If the URL is already absolute, return as is
      if (imgUrl?.startsWith('http')) return imgUrl;
      
      // If it's a relative URL from Flask app, prepend the API base URL
      const baseUrl = process.env.VUE_APP_API_URL || 'http://127.0.0.1:5000';
      
      return `${baseUrl}${imgUrl}`;
    },
    
    getUserFiles(userId) {
      return this.files.filter(file => file.uid === userId);
    },
    
    formatDate(dateString) {
      if (!dateString) return 'Unknown';
      
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
    
    handleSearch(query) {
      this.searchTerm = query;
    },
    
    confirmDelete(user) {
      this.userToDelete = user;
      this.showDeleteModal = true;
    },
    
    openDetailsModal(user) {
      this.selectedUser = user;
      this.showDetailsModal = true;
      // Prevent body scrolling when modal is open
      document.body.style.overflow = 'hidden';
    },
    
    closeDetailsModal() {
      this.showDetailsModal = false;
      this.selectedUser = null;
      // Re-enable body scrolling
      document.body.style.overflow = '';
    },
    
    handleKeyDown(e) {
      if (e.key === 'Escape') {
        if (this.showDetailsModal) {
          this.closeDetailsModal();
        } else if (this.showDeleteModal) {
          this.cancelDelete();
        }
      }
    },
    
    async deleteUser() {
      if (!this.userToDelete) return;
      
      this.error = '';
      this.success = '';
      
      try {
        // Call the API to delete the user
        await api.deleteuser(this.userToDelete.uid);
        this.success = `User "${this.userToDelete.fullname}" deleted successfully.`;
        
        // Remove from local array
        this.users = this.users.filter(user => user.uid !== this.userToDelete.uid);
        
        this.showDeleteModal = false;
        this.userToDelete = null;
        
        // Show success notification if toast is available
        if (this.$toast) {
          this.$toast.success('User deleted successfully', {
            position: 'top-right',
            duration: 3000
          });
        }
      } catch (error) {
        console.error('Error deleting user:', error);
        this.error = error.response?.data?.error || 'Failed to delete user. Please try again.';
        
        if (error.response?.status === 401) {
          this.logout();
        }
      }
    },
    
    cancelDelete() {
      this.showDeleteModal = false;
      this.userToDelete = null;
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
  border-bottom: 1px solid rgba(58, 80, 107, 0.2);
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
  background: linear-gradient(90deg, #3a506b, #5bc0be);
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

/* Users Container */
.users-container {
  position: relative;
}

.users-count {
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

.users-count .material-icons {
  color: #3a506b;
  font-size: 1.4rem;
}

.users-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.user-item {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid rgba(58, 80, 107, 0.15);
  position: relative;
}

.user-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
}

.user-badge {
  position: absolute;
  top: -10px;
  left: -10px;
  background: linear-gradient(135deg, #3a506b 0%, #1c2541 100%); 
  color: white;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
  box-shadow: 0 4px 10px rgba(58, 80, 107, 0.3);
  z-index: 3;
}

.user-item-header {
  padding: 1.5rem;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(58, 80, 107, 0.1);
}

.user-img {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #fff;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 1.3rem;
  font-weight: 600;
  color: #1c2541;
  margin: 0;
}

.user-username {
  font-size: 0.9rem;
  color: #5bc0be;
}

.user-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.user-detail-card {
  background: #f8f9fa;
  border-radius: 10px;
  border: 1px solid rgba(58, 80, 107, 0.08);
  padding: 1rem;
}

.detail-header {
  display: flex;
  align-items: center;
  margin-bottom: 0.8rem;
  border-bottom: 1px solid rgba(58, 80, 107, 0.1);
  padding-bottom: 0.5rem;
}

.detail-icon {
  color: #3a506b;
  margin-right: 0.5rem;
  font-size: 1.2rem;
}

.detail-title {
  color: #1c2541;
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
}

.detail-label {
  color: #3a506b;
  font-weight: 500;
}

.detail-value {
  color: #1c2541;
  font-weight: 500;
}

/* File list styles */
.file-list {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.5rem;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.5);
  transition: background 0.2s ease;
}

.file-item:hover {
  background: rgba(91, 192, 190, 0.1);
}

.file-icon {
  color: #3a506b;
  font-size: 1.2rem;
}

.file-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.file-name {
  font-size: 0.85rem;
  font-weight: 500;
  color: #1c2541;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-date {
  font-size: 0.75rem;
  color: #6c757d;
}

.user-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1rem 1.5rem;
  background: #f8f9fa;
  border-top: 1px solid rgba(58, 80, 107, 0.1);
}

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
}

.view-btn {
  background: linear-gradient(135deg, #5bc0be 0%, #3a506b 100%);
  color: white;
  border: none;
}

.view-btn:hover {
  background: linear-gradient(135deg, #4ca8a7 0%, #2d405a 100%);
  transform: translateY(-2px);
}

.delete-btn {
  background: transparent;
  border: 1px solid #e74c3c;
  color: #e74c3c;
}

.delete-btn:hover {
  background: rgba(231, 76, 60, 0.1);
  transform: translateY(-2px);
}

.no-data {
  color: #6c757d;
  font-style: italic;
  text-align: center;
  padding: 0.5rem;
}

/* Empty state */
/* Empty state */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
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

/* Delete Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(28, 37, 65, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  padding: 2rem;
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
  position: relative;
  animation: modalFadeIn 0.3s ease-out;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.delete-warning-list {
  margin: 1rem 0;
  padding-left: 1.5rem;
  color: #6c757d;
}

.delete-warning-list li {
  margin-bottom: 0.3rem;
}

.user-preview {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  margin: 1rem 0;
  border: 1px solid #dee2e6;
}

.user-preview-img {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
}

.user-preview h4 {
  margin: 0 0 0.3rem;
  color: #1c2541;
  font-weight: 600;
}

.user-preview p {
  margin: 0;
  font-size: 0.9rem;
  color: #6c757d;
}

.modal-warning {
  color: #e74c3c;
  font-weight: 600;
  text-align: center;
  margin: 1.5rem 0;
}

.modal-buttons {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 1.5rem;
}

.confirm-button, .cancel-button {
  flex: 1;
  padding: 0.8rem;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.confirm-button {
  background: #e74c3c;
  color: white;
}

.confirm-button:hover {
  background: #c0392b;
}

.cancel-button {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  color: #6c757d;
}

.cancel-button:hover {
  background: #e9ecef;
}

/* User Details Modal */
.modal-container {
  position: fixed;
  top: 50%;
  left: 60%;
  transform: translate(-50%, -50%);
  z-index: 1005;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.user-details-modal {
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  padding: 0;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #dee2e6;
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1c2541;
  margin: 0;
}

.close-button {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6c757d;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.3rem;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.close-button:hover {
  background: #f8f9fa;
  color: #1c2541;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

.modal-profile-section {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #dee2e6;
}

.modal-user-img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid white;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.modal-user-heading {
  display: flex;
  flex-direction: column;
}

.modal-user-name {
  font-size: 1.8rem;
  font-weight: 600;
  color: #1c2541;
  margin: 0 0 0.3rem;
}

.modal-user-username {
  font-size: 1.1rem;
  color: #5bc0be;
}

.modal-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.modal-detail-section {
  background: #f8f9fa;
  border-radius: 10px;
  border: 1px solid #dee2e6;
  overflow: hidden;
}

.modal-section-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background: white;
  border-bottom: 1px solid #dee2e6;
}

.modal-section-header span {
  color: #3a506b;
}

.modal-section-header h4 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #1c2541;
}

.modal-detail-list {
  padding: 1rem;
}

.modal-detail-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px dashed #dee2e6;
}

.modal-detail-item:last-child {
  border-bottom: none;
}

.modal-detail-label {
  font-weight: 500;
  color: #6c757d;
  flex: 1;
}

.modal-detail-value {
  font-weight: 500;
  color: #1c2541;
  flex: 2;
  text-align: right;
}

.modal-detail-content {
  padding: 1rem;
}

.modal-files-list {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.modal-file-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.8rem;
  background: white;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.modal-file-item:hover {
  background: rgba(91, 192, 190, 0.1);
}

.modal-file-details {
  flex: 1;
}

.modal-file-name {
  font-weight: 500;
  color: #1c2541;
  margin-bottom: 0.2rem;
}

.modal-file-info {
  font-size: 0.85rem;
  color: #6c757d;
}

.modal-no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.8rem;
  padding: 2rem;
  color: #6c757d;
  text-align: center;
}

.modal-footer {
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #dee2e6;
}

.modal-close-btn {
  padding: 0.6rem 1.5rem;
  background: linear-gradient(135deg, #5bc0be 0%, #3a506b 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.modal-close-btn:hover {
  background: linear-gradient(135deg, #4ca8a7 0%, #2d405a 100%);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .main-content {
    padding: 0 1rem;
  }
  
  .dashboard-title {
    font-size: 1.8rem;
  }
  
  .user-stats-grid {
    grid-template-columns: 1fr;
  }
  
  .user-actions {
    flex-direction: column;
    gap: 0.8rem;
  }
  
  .action-btn {
    width: 100%;
  }
  
  .modal-details-grid {
    grid-template-columns: 1fr;
  } 
  
  .modal-profile-section {
    flex-direction: column;
    text-align: center;
  }
}
</style>