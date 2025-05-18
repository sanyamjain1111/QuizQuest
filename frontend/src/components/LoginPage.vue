<template>
  <div class="login-page">
    <h2 class="text-center">Sign in/up Form</h2>
    <div class="container" :class="{'right-panel-active': activePanel !== 'user-login'}">
      <!-- Sign Up Container -->
      <div class="form-container sign-up-container">
        <form v-if="activePanel === 'user-register'" @submit.prevent="submitRegister">
          <h3>Create Account</h3>
          
          <span>or use your email for registration</span>
          <input type="email" placeholder="Email" v-model="registerEmail" />
          <input type="text" placeholder="Full Name" v-model="registerName" />
          <input type="date" placeholder="Date of Birth" v-model="registerDob" />
          <input type="text" placeholder="Qualification" v-model="registerQualification" />
          <input type="password" placeholder="Password" v-model="registerPassword" />
          <button type="submit">Sign Up</button>
        </form>
        <form v-else-if="activePanel === 'admin-login'" @submit.prevent="submitAdminLogin">
          <h1>Admin Sign in</h1>
         
          <span>admin access only</span>
          <input type="email" placeholder="Email" v-model="ausername" />
          <input type="password" placeholder="Password" v-model="apassword" />
          <a href="#">Forgot your password?</a>
          <button type="submit">Sign In</button>
        </form>
      </div>
      
      <!-- Sign In Container -->
      <div class="form-container sign-in-container">
        <form v-if="activePanel === 'user-login'" @submit.prevent="submitUserLogin">
          <h1>Sign in</h1>
          
          <span>or use your account</span>
          <input type="email" placeholder="Email" v-model="username" />
          <input type="password" placeholder="Password" v-model="password" />
          <a href="#">Forgot your password?</a>
          <button type="submit">Sign In</button>
        </form>
      </div>

      <!-- Overlay Container -->
      <div class="overlay-container">
        <div class="overlay">
          <div class="overlay-panel overlay-left">
            <h1>Welcome Back!</h1>
            <p>To keep connected with us please login with your personal info</p>
            <button class="ghost" @click="activePanel = 'user-login'">Sign In</button>
          </div>
          <div class="overlay-panel overlay-right">
            <h1>Hello, Friend!</h1>
            <p>Enter your personal details and start journey with us</p>
            <button class="ghost" @click="activePanel = 'user-register'">Sign Up</button>
            <button class="ghost mt-2" @click="activePanel = 'admin-login'">Admin Login</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      // User login data
      username: "",
      password: "",
      
      // User register data
      registerName: "",
      registerEmail: "",
      registerPassword: "",
      registerDob: "",
      registerQualification: "",
      
      // Admin login data
      ausername: "",
      apassword: "",
      
      // Active panel tracking
      activePanel: "user-login" // Default to user login
    };
  },
  methods: {
    submitUserLogin() {
      console.log("User Login:", this.username, this.password);
      // Updated to match Flask backend route
      this.axios.post('/api/login', {
        username: this.username,
        password: this.password
      })
      .then(response => {
        console.log('Login successful:', response);
        // Store token in localStorage or Vuex
        localStorage.setItem('token', response.data.token);
        localStorage.setItem('fullname', response.data.fullname);
        localStorage.setItem('uid', response.data.uid);
        
        this.$store.commit('setLogin', true);
        this.$router.push('/dashboard');
      })
      .catch(error => {
        console.error('Login failed:', error);
        alert(error.response?.data?.error || 'Login failed');
      });
    },
    submitAdminLogin() {
      console.log("Admin Login:", this.ausername, this.apassword);
      // Updated to match Flask backend route
      this.axios.post('/api/admin', {
        ausername: this.ausername,
        apassword: this.apassword
      })
      .then(response => {
        console.log('Admin login successful:', response);
        // Store admin token
        localStorage.setItem('adminToken', response.data.token);
        
        this.$store.commit('setLogin', true);
        this.$router.push('/admindashboard');
      })
      .catch(error => {
        console.error('Admin login failed:', error);
        alert(error.response?.data?.error || 'Admin login failed');
      });
    },
    submitRegister() {
      console.log("User Registration:", this.registerEmail, this.registerName, this.registerDob, this.registerQualification, this.registerPassword);
      // Updated to match Flask backend route
      this.axios.post('/api/register/login', {
        username: this.registerEmail,
        fullname: this.registerName,
        dob: this.registerDob,
        qualification: this.registerQualification,
        password: this.registerPassword
      })
      .then(response => {
        console.log('Registration successful:', response);
        alert('Registration successful! Please login.');
        this.activePanel = 'user-login';
      })
      .catch(error => {
        console.error('Registration failed:', error);
        alert(error.response?.data?.error || 'Registration failed');
      });
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css?family=Montserrat:400,800');

* {
  box-sizing: border-box;
}

.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  font-family: 'Montserrat', sans-serif;
  height: 100vh;
  margin: -20px 0 50px;
}

h1 {
  font-weight: bold;
  margin: 0;
}

h2 {
  text-align: center;
}

p {
  font-size: 14px;
  font-weight: 100;
  line-height: 20px;
  letter-spacing: 0.5px;
  margin: 20px 0 30px;
}

span {
  font-size: 12px;
}

a {
  color: #333;
  font-size: 14px;
  text-decoration: none;
  margin: 15px 0;
}

button {
  border-radius: 20px;
  border: 1px solid #FF4B2B;
  background-color: #FF4B2B;
  color: #FFFFFF;
  font-size: 12px;
  font-weight: bold;
  padding: 12px 45px;
  letter-spacing: 1px;
  text-transform: uppercase;
  transition: transform 80ms ease-in;
}

button:active {
  transform: scale(0.95);
}

button:focus {
  outline: none;
}

button.ghost {
  background-color: transparent;
  border-color: #FFFFFF;
}

.mt-2 {
  margin-top: 10px;
}

form {
  background-color: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  padding: 0 50px;
  height: 100%;
  text-align: center;
}

input {
  background-color: #eee;
  border: none;
  padding: 12px 15px;
  margin: 8px 0;
  width: 100%;
}

.container {
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 14px 28px rgba(0,0,0,0.25), 
        0 10px 10px rgba(0,0,0,0.22);
  position: relative;
  overflow: hidden;
  width: 768px;
  max-width: 100%;
  min-height: 480px;
}

.form-container {
  position: absolute;
  top: 0;
  height: 100%;
  transition: all 0.6s ease-in-out;
}

.sign-in-container {
  left: 0;
  width: 50%;
  z-index: 2;
}

.container.right-panel-active .sign-in-container {
  transform: translateX(100%);
}

.sign-up-container {
  left: 0;
  width: 50%;
  opacity: 0;
  z-index: 1;
}

.container.right-panel-active .sign-up-container {
  transform: translateX(100%);
  opacity: 1;
  z-index: 5;
  animation: show 0.6s;
}

@keyframes show {
  0%, 49.99% {
    opacity: 0;
    z-index: 1;
  }
  
  50%, 100% {
    opacity: 1;
    z-index: 5;
  }
}

.overlay-container {
  position: absolute;
  top: 0;
  left: 50%;
  width: 50%;
  height: 100%;
  overflow: hidden;
  transition: transform 0.6s ease-in-out;
  z-index: 100;
}

.container.right-panel-active .overlay-container{
  transform: translateX(-100%);
}

.overlay {
  background: #FF416C;
  background: -webkit-linear-gradient(to right, #FF4B2B, #FF416C);
  background: linear-gradient(to right, #FF4B2B, #FF416C);
  background-repeat: no-repeat;
  background-size: cover;
  background-position: 0 0;
  color: #FFFFFF;
  position: relative;
  left: -100%;
  height: 100%;
  width: 200%;
  transform: translateX(0);
  transition: transform 0.6s ease-in-out;
}

.container.right-panel-active .overlay {
  transform: translateX(50%);
}

.overlay-panel {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  padding: 0 40px;
  text-align: center;
  top: 0;
  height: 100%;
  width: 50%;
  transform: translateX(0);
  transition: transform 0.6s ease-in-out;
}

.overlay-left {
  transform: translateX(-20%);
}

.container.right-panel-active .overlay-left {
  transform: translateX(0);
}

.overlay-right {
  right: 0;
  transform: translateX(0);
}

.container.right-panel-active .overlay-right {
  transform: translateX(20%);
}

.social-container {
  margin: 20px 0;
}

.social-container a {
  border: 1px solid #DDDDDD;
  border-radius: 50%;
  display: inline-flex;
  justify-content: center;
  align-items: center;
  margin: 0 5px;
  height: 40px;
  width: 40px;
}
</style>