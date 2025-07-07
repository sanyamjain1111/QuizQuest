<!-- User Export Component for Personal Quiz Data -->
<template>
  <div class="export-inline">
    <button 
      class="export-btn-inline" 
      @click="triggerUserExport"
      :disabled="isExporting"
    >
      <span v-if="isExporting">
        <span class="material-icons spinning">sync</span>
        Exporting...
      </span>
      <span v-else>
        <span class="material-icons">file_download</span>
        Export Data
      </span>
    </button>
    
    <div v-if="exportStatus" class="status-popup">
      <div 
        :class="['alert-mini', 
                 exportStatus.type === 'success' ? 'alert-success' : 
                 exportStatus.type === 'error' ? 'alert-danger' : 'alert-info']"
      >
        {{ exportStatus.message }}
      </div>
    </div>
  </div>
</template>
<script>
export default {
  name: 'UserExportComponent',
  data() {
    return {
      isExporting: false,
      exportStatus: null,
      taskId: null,
      statusCheckInterval: null,
      debugInfo: null,
      userStats: null,
      // Add base URL for your Flask API
      apiBaseUrl: 'http://127.0.0.1:5000',
      isDevelopment: process.env.NODE_ENV === 'development'
    }
  },
  methods: {
    async triggerUserExport() {
      this.isExporting = true;
      this.exportStatus = null;
      this.debugInfo = null;
      
      try {
        // Use absolute URL to your Flask server
        const apiUrl = `${this.apiBaseUrl}/api/export/user-quizzes`;
        console.log('Making request to:', apiUrl);
        
        const token = localStorage.getItem('token') || sessionStorage.getItem('token');
        
        const headers = {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        };
        
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }
        
        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: headers,
          credentials: 'include'
          // No body needed since backend gets user from JWT token
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', [...response.headers.entries()]);
        
        // Check content type
        const contentType = response.headers.get('content-type');
        console.log('Content-Type:', contentType);
        
        if (!contentType || !contentType.includes('application/json')) {
          // Log the actual response to see what we got
          const responseText = await response.text();
          console.log('Non-JSON response:', responseText.substring(0, 500));
          throw new Error(`Expected JSON response, got ${contentType}. Response: ${responseText.substring(0, 100)}`);
        }
        
        const data = await response.json();
        console.log('Response data:', data);
        
        this.debugInfo = {
          status: response.status,
          response: JSON.stringify(data),
          error: null,
          url: apiUrl
        };
        
        if (response.ok && data.status === 'success') {
          this.taskId = data.task_id;
          this.exportStatus = {
            type: 'info',
            message: data.message || 'Export initiated. Processing your quiz data...'
          };
          this.checkTaskStatus();
        } else {
          this.exportStatus = {
            type: 'error',
            message: data.message || `HTTP ${response.status}: ${response.statusText}`
          };
          this.isExporting = false;
        }
      } catch (error) {
        console.error('Export request failed:', error);
        
        this.debugInfo = {
          status: 'network_error',
          response: null,
          error: error.message,
          url: `${this.apiBaseUrl}/api/export/user-quizzes`
        };
        
        this.exportStatus = {
          type: 'error',
          message: `Network error: ${error.message}`
        };
        this.isExporting = false;
      }
    },
    
    async checkTaskStatus() {
      this.statusCheckInterval = setInterval(async () => {
        try {
          const token = localStorage.getItem('token') || sessionStorage.getItem('token');
          
          const headers = {
            'X-Requested-With': 'XMLHttpRequest'
          };
          
          if (token) {
            headers['Authorization'] = `Bearer ${token}`;
          }
          
          // Use absolute URL here too
          const apiUrl = `${this.apiBaseUrl}/api/task-status/${this.taskId}`;
          const response = await fetch(apiUrl, {
            headers: headers,
            credentials: 'include'
          });
          
          const data = await response.json();
          
          if (data.status === 'completed') {
            this.exportStatus = {
              type: 'success',
              message: 'Export completed successfully! Check your email for the CSV file with your quiz data.'
            };
            this.isExporting = false;
            clearInterval(this.statusCheckInterval);
          } else if (data.status === 'failed') {
            this.exportStatus = {
              type: 'error',
              message: 'Export failed. Please try again or contact support.'
            };
            this.isExporting = false;
            clearInterval(this.statusCheckInterval);
          }
        } catch (error) {
          console.error('Error checking task status:', error);
        }
      }, 3000);
    }
  },
  
  beforeUnmount() {
    if (this.statusCheckInterval) {
      clearInterval(this.statusCheckInterval);
    }
  }
}
</script>

<style scoped>
.export-inline {
  position: relative;
}

.export-btn-inline {
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
  font-family: 'Poppins', sans-serif;
}

.export-btn-inline:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.export-btn-inline:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.status-popup {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  z-index: 1000;
  min-width: 250px;
}

.alert-mini {
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
}

.alert-success {
  background-color: rgba(46, 204, 113, 0.9);
  color: white;
}

.alert-danger {
  background-color: rgba(231, 76, 60, 0.9);
  color: white;
}

.alert-info {
  background-color: rgba(52, 152, 219, 0.9);
  color: white;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>