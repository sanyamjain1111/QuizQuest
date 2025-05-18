<template>
  <div class="contact-container">
    <NavbarComponent />
    
    <div class="contact-header">
      <h1 class="contact-title">Contact Us</h1>
    </div>
    
    <div class="main-content">
      <div class="contact-card">
        <div class="contact-card-header">
          <h2 class="card-title">
            <span class="material-icons contact-icon">support_agent</span>
            Get In Touch
          </h2>
        </div>
        
        <div class="contact-form-container">
          <form @submit.prevent="submitComplaint" class="contact-form">
            <div class="form-group">
              <label for="issue">How can we help you?</label>
              <select 
                id="issue"
                v-model="form.issue" 
                required
                class="form-control"
              >
                <option value="How can we help you?">How can we help you?</option>
                <option value="I need assistance with my profile">I need assistance with my profile</option>
                <option value="I need assistance with quiz related issue">I need assistance with quiz related issue</option>
                <option value="Found an incorrect question or wrong answer">Found an incorrect question or wrong answer</option>
                <option value="I need assistance with new subject/course registration">I need assistance with new subject/course registration</option>
                <option value="Something else">Something else</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="name">Full Name</label>
              <input 
                type="text" 
                id="name"
                v-model="form.name" 
                placeholder="Enter your name" 
                class="form-control" 
                required
              >
            </div>
            
            <div class="form-group">
              <label for="phone">Phone Number</label>
              <input 
                type="number" 
                id="phone"
                v-model="form.number" 
                placeholder="Enter your phone number" 
                class="form-control" 
                maxlength="10" 
                required
              >
            </div>
            
            <div class="form-group">
              <label for="details">Details</label>
              <textarea 
                id="details"
                v-model="form.details" 
                maxlength="410" 
                minlength="10" 
                placeholder="Please describe your issue in detail" 
                class="form-control"
                rows="5"
                required
              ></textarea>
              <small class="char-count">{{ form.details.length }}/410 characters</small>
            </div>
            
            <div class="form-action">
              <button type="submit" class="submit-button">
                <span class="material-icons">send</span>
                Submit
              </button>
            </div>
          </form>
        </div>
      </div>
      
      <div class="contact-info">
        <div class="info-card">
          <div class="info-icon">
            <span class="material-icons">schedule</span>
          </div>
          <h3>Response Time</h3>
          <p>We typically respond within 24-48 hours during business days.</p>
        </div>
        
        <div class="info-card">
          <div class="info-icon">
            <span class="material-icons">support</span>
          </div>
          <h3>Support Hours</h3>
          <p>Monday to Friday: 9:00 AM - 6:00 PM</p>
        </div>
        
        <div class="info-card">
          <div class="info-icon">
            <span class="material-icons">question_answer</span>
          </div>
          <h3>FAQ</h3>
          <p>Check our <a href="#">frequently asked questions</a> for quick answers.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import NavbarComponent from './NavbarComponent.vue';

export default {
  name: 'ContactComponent',
  components: {
    NavbarComponent
  },
  data() {
    return {
      form: {
        issue: 'How can we help you?',
        name: '',
        number: '',
        details: ''
      },
      isSubmitting: false
    };
  },
  methods: {
    async submitComplaint() {
      this.isSubmitting = true;
      
      try {
        const response = await axios.post('/api/complaint', this.form, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
          }
        });
        
        // Success message - safely using optional chaining
        const successMessage = response && response.data && response.data.message 
          ? response.data.message 
          : 'Your message has been sent successfully!';
        
        // Check if toast is available before using it
        if (typeof this.$toast === 'object' && this.$toast !== null && typeof this.$toast.success === 'function') {
          this.$toast.success(successMessage);
        } else {
          console.log('Success:', successMessage);
          // Uncomment if you want to use alert as fallback
          // alert(successMessage);
        }
        
        this.resetForm();
      } catch (err) {
        // Log the error for debugging
        console.error('Error submitting complaint:', err);
        
        // Default error message
        let errorMessage = 'Failed to submit your message. Please try again.';
        
        // Safely extract error message if available
        try {
          if (err && typeof err === 'object') {
            if (err.response && typeof err.response === 'object' && 
                err.response.data && typeof err.response.data === 'object' && 
                typeof err.response.data.error === 'string') {
              errorMessage = err.response.data.error;
            } else if (err.message && typeof err.message === 'string') {
              errorMessage = err.message;
            }
          }
        } catch (extractError) {
          console.error('Error while extracting error details:', extractError);
        }
        
        // Check if toast is available before using it
        if (typeof this.$toast === 'object' && this.$toast !== null && typeof this.$toast.error === 'function') {
          this.$toast.error(errorMessage);
        } else {
          console.error('Error:', errorMessage);
          // Uncomment if you want to use alert as fallback
          // alert(errorMessage);
        }
      } finally {
        this.isSubmitting = false;
      }
    },
    resetForm() {
      this.form = {
        issue: 'How can we help you?',
        name: '',
        number: '',
        details: ''
      };
    }
  }
};
</script>

<style scoped>
/* Import Google Material Icons */
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

.contact-container {
  font-family: 'Poppins', sans-serif;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ec 100%);
  color: #1c2541;
}

.contact-header {
  text-align: center;
  padding: 2rem 0 1rem;
  background: linear-gradient(135deg, rgba(11, 19, 43, 0.05) 0%, rgba(28, 37, 65, 0.1) 100%);
  border-bottom: 1px solid rgba(91, 192, 190, 0.2);
}

.contact-title {
  font-weight: 600;
  color: #0b132b;
  margin: 0;
  font-size: 2.2rem;
  position: relative;
  display: inline-block;
}

.contact-title:after {
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
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
}

.contact-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  border: 1px solid rgba(91, 192, 190, 0.2);
  flex: 1;
  min-width: 300px;
}

.contact-card-header {
  background: linear-gradient(135deg, #0b132b 0%, #1c2541 100%);
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
}

.contact-card-header:before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(91, 192, 190, 0.2) 0%, rgba(91, 192, 190, 0) 70%);
  z-index: 1;
}

.card-title {
  color: white;
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
}

.contact-icon {
  margin-right: 0.5rem;
}

.contact-form-container {
  padding: 1.5rem;
}

.contact-form {
  width: 100%;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #3a506b;
}

.form-control {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  background-color: #f8fafc;
  color: #1c2541;
  transition: all 0.3s ease;
}

.form-control:focus {
  outline: none;
  border-color: #5bc0be;
  box-shadow: 0 0 0 3px rgba(91, 192, 190, 0.2);
}

.form-control::placeholder {
  color: #a0aec0;
}

select.form-control {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%233a506b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  background-size: 1rem;
  padding-right: 2.5rem;
}

textarea.form-control {
  resize: vertical;
  min-height: 120px;
}

.char-count {
  display: block;
  text-align: right;
  font-size: 0.75rem;
  color: #718096;
  margin-top: 0.25rem;
}

.form-action {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

.submit-button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 2rem;
  background: linear-gradient(135deg, #5bc0be 0%, #3a506b 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-family: 'Poppins', sans-serif;
  font-weight: 500;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  gap: 0.5rem;
}

.submit-button:hover {
  background: linear-gradient(135deg, #4ca8a7 0%, #2d405a 100%);
  box-shadow: 0 4px 12px rgba(91, 192, 190, 0.3);
  transform: translateY(-2px);
}

.contact-info {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  flex: 1;
  min-width: 300px;
}

.info-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(91, 192, 190, 0.2);
  flex: 1 1 calc(33.333% - 1rem);
  min-width: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.info-icon {
  background: linear-gradient(135deg, #5bc0be 0%, #3a506b 100%);
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.info-icon .material-icons {
  color: white;
  font-size: 28px;
}

.info-card h3 {
  margin: 0 0 0.5rem;
  color: #1c2541;
  font-weight: 600;
}

.info-card p {
  margin: 0;
  color: #3a506b;
  font-size: 0.95rem;
  line-height: 1.5;
}

.info-card a {
  color: #5bc0be;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.info-card a:hover {
  color: #3a506b;
  text-decoration: underline;
}

/* Responsiveness */
@media (max-width: 1024px) {
  .main-content {
    flex-direction: column;
  }
  
  .contact-title {
    font-size: 1.8rem;
  }
}

@media (max-width: 768px) {
  .contact-title {
    font-size: 1.5rem;
  }
  
  .card-title {
    font-size: 1.3rem;
  }
  
  .contact-info {
    flex-direction: column;
  }
  
  .info-card {
    width: 100%;
  }
}

@media (max-width: 576px) {
  .contact-header {
    padding: 1.5rem 0 0.75rem;
  }
  
  .contact-title {
    font-size: 1.3rem;
  }
  
  .contact-title:after {
    width: 40px;
    height: 3px;
  }
  
  .main-content {
    margin: 1rem auto;
    padding: 0 1rem;
  }
  
  .contact-card-header {
    padding: 1rem;
  }
  
  .card-title {
    font-size: 1.1rem;
  }
  
  .contact-form-container {
    padding: 1rem;
  }
  
  .form-group {
    margin-bottom: 1rem;
  }
  
  .form-control {
    padding: 0.6rem 0.8rem;
    font-size: 0.9rem;
  }
  
  .submit-button {
    padding: 0.6rem 1.5rem;
    font-size: 0.9rem;
  }
  
  .info-icon {
    width: 50px;
    height: 50px;
  }
  
  .info-icon .material-icons {
    font-size: 24px;
  }
  
  .info-card h3 {
    font-size: 1.1rem;
  }
  
  .info-card p {
    font-size: 0.85rem;
  }
}

/* Accessibility improvements */
@media (prefers-reduced-motion: reduce) {
  .submit-button:hover {
    transform: none;
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .contact-container {
    background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
    color: #e2e8f0;
  }
  
  .contact-title {
    color: #f7fafc;
  }
  
  .contact-card,
  .info-card {
    background: #2d3748;
    border-color: rgba(91, 192, 190, 0.3);
  }
  
  .form-group label {
    color: #e2e8f0;
  }
  
  .form-control {
    background-color: #1a202c;
    border-color: #4a5568;
    color: #e2e8f0;
  }
  
  .form-control::placeholder {
    color: #718096;
  }
  
  .form-control:focus {
    border-color: #5bc0be;
    box-shadow: 0 0 0 3px rgba(91, 192, 190, 0.3);
  }
  
  .char-count {
    color: #a0aec0;
  }
  
  .info-card h3 {
    color: #f7fafc;
  }
  
  .info-card p {
    color: #e2e8f0;
  }
}
</style>