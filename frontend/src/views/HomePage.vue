<template>
  <div class="main-container">
    <div class="card-wrapper">
      <!-- Admin Login -->
      <div class="card admin-card" :class="{ flipped: currentCard === 'admin' }">
        <AdminLogin @toggle-register-form="toggleRegisterForm" />
      </div>

      <!-- User Login -->
      <div class="card user-card" :class="{ flipped: currentCard === 'user' }">
        <UserLogin @toggle-register-form="toggleRegisterForm" />
      </div>

      <!-- User Registration -->
      <div class="card register-card" :class="{ flipped: currentCard === 'register' }">
        <UserRegister />
      </div>
    </div>
  </div>
</template>

<script>
import AdminLogin from "@/components/AdminLogin.vue";
import UserLogin from "@/components/UserLogin.vue";
import UserRegister from "@/components/UserRegister.vue";

export default {
  components: {
    AdminLogin,
    UserLogin,
    UserRegister
  },
  data() {
    return {
      currentCard: 'user'  // default to 'user' login screen
    };
  },
  methods: {
    toggleRegisterForm() {
      if (this.currentCard === 'user') {
        this.currentCard = 'register';  // Switch to registration form
      } else {
        this.currentCard = 'user';  // Switch back to user login
      }
    },
    toggleAdminForm() {
      this.currentCard = this.currentCard === 'admin' ? 'user' : 'admin'; // Toggle admin and user login
    }
  }
};
</script>

<style scoped>
.main-container {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 30px;
  margin-top: 60px;
  background-color: #f4f7fc;
  position: relative;
}

.card-wrapper {
  display: flex;
  justify-content: center;
  gap: 20px;
  max-width: 1200px;
  width: 100%;
  flex-wrap: wrap;
  perspective: 1000px;  /* Add perspective for 3D effect */
}

.card {
  width: 350px;
  height: 450px;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  background-color: #fff;
  transition: transform 0.5s ease;
  transform-style: preserve-3d;
  position: relative;
  transform: rotateY(0deg);
}

.card.flipped {
  transform: rotateY(180deg);  /* Flip the card */
}

.card-content {
  text-align: center;
  padding: 20px;
  backface-visibility: hidden;
}

h1 {
  font-size: 24px;
  color: #333;
  margin-bottom: 20px;
  font-weight: 600;
}

input, button {
  width: 100%;
  padding: 12px;
  margin: 10px 0;
  border-radius: 10px;
  border: 1px solid #ccc;
  background-color: #f7f7f7;
  transition: border-color 0.3s ease;
}

input:focus {
  border-color: #008cba;
  outline: none;
}

button {
  background-color: #008cba;
  color: white;
  border: none;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: #007fa6;
}

footer {
  margin-top: 15px;
  text-align: center;
  font-size: 12px;
  color: #777;
}

footer a {
  color: #008cba;
  text-decoration: none;
  font-weight: bold;
}

footer a:hover {
  text-decoration: underline;
}
</style>
