<template>
  <nav class="navbar-container">
    <!-- Logo and Brand Section -->
    <div class="brand-section">
      <div class="logo-container">
        <div class="logo-icon">
          <span class="material-icons">admin_panel_settings</span>
        </div>
      </div>
      <a class="brand-name" href="#">QuizQuest Admin</a>
    </div>
    
    <!-- Main Navigation Links -->
    <div class="nav-links-container" :class="{ 'active': isMenuOpen }">
      <ul class="nav-links">
        <li class="nav-item">
          <router-link to="/admindashboard" class="nav-link" @click="closeMenu">
            <span class="material-icons">dashboard</span>
            <span>Dashboard</span>
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/adminsubjects" class="nav-link" @click="closeMenu">
            <span class="material-icons">subject</span>
            <span>Subjects</span>
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/adminchapters" class="nav-link" @click="closeMenu">
            <span class="material-icons">book</span>
            <span>Chapters</span>
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/adminquestions" class="nav-link" @click="closeMenu">
            <span class="material-icons">help</span>
            <span>Questions</span>
          </router-link>
        </li>
        
      </ul>
    </div>

    <!-- Right Section: Search, Profile, Logout -->
    <div class="right-section" :class="{ 'active': isMenuOpen }">
      <!-- Search Form -->
      <form class="search-form" @submit.prevent="search">
        <div class="search-container">
          <span class="material-icons search-icon">search</span>
          <input 
            type="search" 
            placeholder="Search..." 
            v-model="searchQuery"
            class="search-input"
            aria-label="Search"
          >
        </div>
      </form>

      <!-- Student Management Dropdown -->
      <div class="profile-dropdown" ref="studentDropdown">
        <button 
          class="profile-btn" 
          @click="toggleStudentMenu"
          aria-haspopup="true"
          :aria-expanded="isStudentOpen ? 'true' : 'false'"
        >
          <span class="material-icons">people</span>
          <span class="profile-text">Students</span>
          <span class="material-icons dropdown-arrow" :class="{ 'rotate': isStudentOpen }">
            expand_more
          </span>
        </button>
        <div class="dropdown-content" v-show="isStudentOpen">
          <router-link to="/admin/student/personal" class="dropdown-item" @click="closeStudentMenu">
            <span class="material-icons">person</span>
            <span>Personal Details</span>
          </router-link>
          <router-link to="/admin/student/academic" class="dropdown-item" @click="closeStudentMenu">
            <span class="material-icons">school</span>
            <span>Academic Details</span>
          </router-link>
        </div>
      </div>

      <!-- Admin Profile Dropdown -->
      <div class="profile-dropdown" ref="profileDropdown">
        <button 
          class="profile-btn" 
          @click="toggleProfileMenu"
          aria-haspopup="true"
          :aria-expanded="isProfileOpen ? 'true' : 'false'"
        >
          <span class="material-icons">account_circle</span>
          <span class="profile-text">Admin</span>
          <span class="material-icons dropdown-arrow" :class="{ 'rotate': isProfileOpen }">
            expand_more
          </span>
        </button>
        <div class="dropdown-content" v-show="isProfileOpen">
          <router-link to="/admin/settings" class="dropdown-item" @click="closeProfileMenu">
            <span class="material-icons">settings</span>
            <span>Settings</span>
          </router-link>
          <a href="#" class="dropdown-item logout-btn" @click.prevent="logout">
            <span class="material-icons">logout</span>
            <span>Logout</span>
          </a>
        </div>
      </div>

      <!-- Mobile Menu Toggle -->
      <button class="menu-toggle" @click="toggleMenu" aria-label="Toggle navigation menu">
        <span class="material-icons">{{ isMenuOpen ? 'close' : 'menu' }}</span>
      </button>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'AdminNavbarComponent',
  data() {
    return {
      searchQuery: '',
      isMenuOpen: false,
      isProfileOpen: false,
      isStudentOpen: false
    };
  },
  mounted() {
    // Close dropdowns when clicking outside
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
  },
  methods: {
    search() {
      if (this.searchQuery.trim()) {
        this.$emit('search', this.searchQuery);
        this.closeMenu();
      }
    },
    logout() {
      localStorage.removeItem('adminToken');
      localStorage.removeItem('adminName');
      localStorage.removeItem('adminId');
      this.$router.push('/');
    },
    toggleMenu() {
      this.isMenuOpen = !this.isMenuOpen;
      if (this.isMenuOpen) {
        document.body.classList.add('menu-open');
      } else {
        document.body.classList.remove('menu-open');
      }
    },
    closeMenu() {
      this.isMenuOpen = false;
      document.body.classList.remove('menu-open');
    },
    toggleProfileMenu(event) {
      event.stopPropagation();
      this.isProfileOpen = !this.isProfileOpen;
      if (this.isProfileOpen) {
        this.isStudentOpen = false;
      }
    },
    closeProfileMenu() {
      this.isProfileOpen = false;
    },
    toggleStudentMenu(event) {
      event.stopPropagation();
      this.isStudentOpen = !this.isStudentOpen;
      if (this.isStudentOpen) {
        this.isProfileOpen = false;
      }
    },
    closeStudentMenu() {
      this.isStudentOpen = false;
    },
    handleClickOutside(event) {
      if (this.$refs.profileDropdown && !this.$refs.profileDropdown.contains(event.target)) {
        this.isProfileOpen = false;
      }
      if (this.$refs.studentDropdown && !this.$refs.studentDropdown.contains(event.target)) {
        this.isStudentOpen = false;
      }
    }
  }
}
</script>

<style scoped>
/* Import Google Material Icons */
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

/* Main Navbar Container */
.navbar-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  /* Dark theme for admin panel - slightly different from user */
  background: linear-gradient(135deg, #1a1b2e 0%, #2c3145 100%);
  color: #fff;
  padding: 0.8rem 2rem;
  position: sticky;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  font-family: 'Poppins', sans-serif;
}

/* Brand Section */
.brand-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-icon {
  /* Different color scheme for admin */
  background: linear-gradient(135deg, #ff7e67 0%, #d45d50 100%);
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 10px rgba(255, 126, 103, 0.4);
  transition: all 0.3s ease;
}

.logo-icon:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 15px rgba(255, 126, 103, 0.5);
}

.brand-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: #fff;
  text-decoration: none;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
}

.brand-name:hover {
  color: #ff7e67;
  transform: scale(1.05);
}

/* Navigation Links Container */
.nav-links-container {
  display: flex;
}

.nav-links {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 0.5rem;
}

.nav-item {
  position: relative;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 0.8rem 1.2rem;
  color: #d1d7e0;
  text-decoration: none;
  font-weight: 500;
  border-radius: 8px;
  gap: 0.5rem;
  transition: all 0.3s ease;
}

.nav-link:hover {
  background-color: rgba(255, 126, 103, 0.15);
  color: #ff7e67;
  transform: translateY(-2px);
}

.nav-link.router-link-active {
  background-color: rgba(255, 126, 103, 0.25);
  color: #ff7e67;
}

/* Right Section */
.right-section {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

/* Search Form */
.search-form {
  position: relative;
}

.search-container {
  display: flex;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 50px;
  padding: 0.3rem 1rem;
  transition: all 0.3s ease;
}

.search-container:focus-within {
  background-color: rgba(255, 255, 255, 0.2);
  box-shadow: 0 0 0 2px rgba(255, 126, 103, 0.5);
}

.search-icon {
  color: #d1d7e0;
  font-size: 1.2rem;
  margin-right: 0.5rem;
}

.search-input {
  background: transparent;
  border: none;
  color: #fff;
  padding: 0.5rem 0;
  width: 180px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.95rem;
}

.search-input:focus {
  outline: none;
}

.search-input::placeholder {
  color: #989eb8;
}

/* Profile Dropdown */
.profile-dropdown {
  position: relative;
}

.profile-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  color: #d1d7e0;
  padding: 0.5rem 1rem;
  font-family: 'Poppins', sans-serif;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.profile-btn:hover {
  background-color: rgba(255, 126, 103, 0.15);
  color: #ff7e67;
}

.dropdown-arrow {
  transition: transform 0.3s ease;
}

.dropdown-arrow.rotate {
  transform: rotate(180deg);
}

.dropdown-content {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  background-color: #2c3145;
  min-width: 240px;
  border-radius: 8px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
  z-index: 1001;
  overflow: hidden;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.8rem 1.2rem;
  color: #d1d7e0;
  text-decoration: none;
  transition: all 0.2s ease;
}

.dropdown-item:hover {
  background-color: rgba(255, 126, 103, 0.15);
  color: #ff7e67;
}

.logout-btn {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  color: #ff7e67;
}

.logout-btn:hover {
  background-color: rgba(255, 126, 103, 0.2);
  color: #ff7e67;
}

/* Mobile Menu Toggle */
.menu-toggle {
  display: none;
  background: none;
  border: none;
  color: #fff;
  font-size: 1.5rem;
  cursor: pointer;
}

/* Responsive Design */
@media (max-width: 992px) {
  .navbar-container {
    padding: 0.8rem 1rem;
  }
  
  .nav-links-container {
    position: fixed;
    top: 70px;
    left: 0;
    right: 0;
    background-color: #1a1b2e;
    flex-direction: column;
    padding: 1rem;
    transform: translateY(-150%);
    transition: transform 0.3s ease-in-out;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    z-index: 999;
  }
  
  .nav-links-container.active {
    transform: translateY(0);
  }
  
  .nav-links {
    flex-direction: column;
    width: 100%;
  }
  
  .nav-link {
    padding: 1rem;
    border-radius: 8px;
  }
  
  .right-section {
    position: fixed;
    top: 70px;
    left: 0;
    right: 0;
    background-color: #1a1b2e;
    flex-direction: column;
    padding: 1rem;
    transform: translateY(-150%);
    transition: transform 0.3s ease-in-out;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    z-index: 999;
    margin-top: 280px; /* Adjusted for more nav items */
  }
  
  .right-section.active {
    transform: translateY(0);
  }
  
  .search-form, .profile-dropdown {
    width: 100%;
    margin-bottom: 1rem;
  }
  
  .search-container {
    width: 100%;
  }
  
  .search-input {
    width: 100%;
  }
  
  .profile-btn {
    width: 100%;
    justify-content: space-between;
  }
  
  .dropdown-content {
    position: relative;
    width: 100%;
    margin-top: 0.5rem;
  }
  
  .menu-toggle {
    display: block;
    position: absolute;
    right: 1rem;
  }
}

@media (max-width: 576px) {
  .brand-name {
    font-size: 1.2rem;
  }
  
  .logo-icon {
    width: 2rem;
    height: 2rem;
  }
}
</style>