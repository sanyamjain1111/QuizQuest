<template>
  <div class="reminder-settings">
    <div class="reminder-header" @click="toggleExpand">
      <span class="material-icons reminder-icon">notifications</span>
      <span class="reminder-title">Reminder Settings</span>
      <span class="material-icons expand-icon" :class="{ 'expanded': isExpanded }">
        {{ isExpanded ? 'expand_less' : 'expand_more' }}
      </span>
    </div>
    
    <div class="reminder-content" v-if="isExpanded">
      <p class="reminder-description">
        Choose when you'd like to receive daily reminders for new quizzes
      </p>
      
      <div class="reminder-options">
        <div class="time-options">
          <div 
            v-for="option in timeOptions" 
            :key="option.value"
            class="time-option" 
            :class="{ 'active': selectedTime === option.value }"
            @click="selectTime(option.value)"
          >
            <span class="material-icons option-icon">{{ option.icon }}</span>
            <span class="option-label">{{ option.label }}</span>
          </div>
        </div>
      </div>
      
      <div class="reminder-actions">
        <button class="save-button" @click="savePreference" :disabled="isSaving">
          <span class="material-icons save-icon" v-if="!isSaving">save</span>
          <span class="material-icons save-icon rotating" v-else>sync</span>
          {{ isSaving ? 'Saving...' : 'Save Preference' }}
        </button>
      </div>
      
      <div class="reminder-status" v-if="showStatus">
        <div class="status-message" :class="statusType">
          {{ statusMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ReminderSettingsComponent',
  data() {
    return {
      isExpanded: false,
      selectedTime: null, // Start with null instead of default
      isSaving: false,
      showStatus: false,
      statusMessage: '',
      statusType: 'success',
      timeOptions: [
        { value: 'morning', label: 'Morning', icon: 'wb_sunny' },
        { value: 'afternoon', label: 'Afternoon', icon: 'wb_twilight' },
        { value: 'evening', label: 'Evening', icon: 'nights_stay' }
      ]
    };
  },
  async mounted() {
    await this.fetchCurrentPreference();
  },
  methods: {
    toggleExpand() {
      this.isExpanded = !this.isExpanded;
    },
    selectTime(time) {
      this.selectedTime = time;
    },
    async fetchCurrentPreference() {
      try {
        const response = await axios.get('/api/reminders/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (response.data && response.data.reminder_preference) {
          this.selectedTime = response.data.reminder_preference;
        } else {
          // Set default if no preference is found
          this.selectedTime = 'morning';
        }
      } catch (error) {
        console.error('Error fetching reminder preference:', error);
        this.selectedTime = 'morning'; // Default in case of error
      }
    },
    async savePreference() {
      this.isSaving = true;
      try {
        await axios.post('/api/reminders/', {
          reminder_preference: this.selectedTime
        }, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        this.showStatusMessage('Reminder preference saved successfully', 'success');
      } catch (error) {
        console.error('Error saving reminder preference:', error);
        this.showStatusMessage('Failed to save preference', 'error');
      } finally {
        this.isSaving = false;
      }
    },
    showStatusMessage(message, type) {
      this.statusMessage = message;
      this.statusType = type;
      this.showStatus = true;
      
      // Auto-hide after 3 seconds
      setTimeout(() => {
        this.showStatus = false;
      }, 3000);
    }
  }
};
</script>

<style scoped>
.reminder-settings {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  margin-bottom: 1.5rem;
  overflow: hidden;
  border: 1px solid rgba(91, 192, 190, 0.2);
  transition: all 0.3s ease;
}

.reminder-header {
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  cursor: pointer;
  background: linear-gradient(135deg, #0b132b 0%, #1c2541 100%);
  color: white;
}

.reminder-icon {
  margin-right: 0.75rem;
  color: #5bc0be;
}

.reminder-title {
  font-size: 1.1rem;
  font-weight: 500;
  flex: 1;
}

.expand-icon {
  transition: transform 0.3s ease;
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

.reminder-content {
  padding: 1.5rem;
  border-top: 1px solid rgba(91, 192, 190, 0.15);
}

.reminder-description {
  margin-top: 0;
  margin-bottom: 1.2rem;
  color: #3a506b;
  font-size: 0.95rem;
}

.time-options {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.time-option {
  flex: 1;
  margin: 0 0.5rem;
  padding: 1rem 0.5rem;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid #e4e7ec;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.time-option:first-child {
  margin-left: 0;
}

.time-option:last-child {
  margin-right: 0;
}

.time-option:hover {
  background-color: #f5f7fa;
  transform: translateY(-2px);
}

.time-option.active {
  border-color: #5bc0be;
  background-color: rgba(91, 192, 190, 0.1);
  transform: translateY(-2px);
}

.option-icon {
  font-size: 1.8rem;
  margin-bottom: 0.5rem;
  color: #3a506b;
}

.time-option.active .option-icon {
  color: #5bc0be;
}

.option-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #1c2541;
}

.reminder-actions {
  display: flex;
  justify-content: flex-end;
}

.save-button {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #5bc0be 0%, #3a506b 100%);
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  font-family: 'Poppins', sans-serif;
  font-size: 0.95rem;
  font-weight: 500;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.save-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #4ca8a7 0%, #2d405a 100%);
  box-shadow: 0 4px 12px rgba(91, 192, 190, 0.3);
}

.save-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.save-icon {
  margin-right: 0.5rem;
}

.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.reminder-status {
  margin-top: 1rem;
}

.status-message {
  padding: 0.75rem;
  border-radius: 6px;
  font-size: 0.9rem;
  text-align: center;
}

.status-message.success {
  background-color: rgba(72, 187, 120, 0.1);
  color: #2f855a;
  border: 1px solid rgba(72, 187, 120, 0.2);
}

.status-message.error {
  background-color: rgba(245, 101, 101, 0.1);
  color: #c53030;
  border: 1px solid rgba(245, 101, 101, 0.2);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .time-options {
    flex-direction: column;
  }
  
  .time-option {
    margin: 0.5rem 0;
    flex-direction: row;
    justify-content: flex-start;
    padding: 0.75rem 1rem;
  }
  
  .time-option:first-child {
    margin-top: 0;
  }
  
  .time-option:last-child {
    margin-bottom: 0;
  }
  
  .option-icon {
    margin-bottom: 0;
    margin-right: 1rem;
  }
}
</style>