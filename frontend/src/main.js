import { createApp } from "vue";
import App from "./App.vue";
import axios from "axios";
import VueAxios from "vue-axios";
import router from "./router";
import { createStore } from "vuex";
import 'bootstrap/dist/css/bootstrap.min.css'
import 'font-awesome/css/font-awesome.min.css'

// Set the base URL for all axios requests
axios.defaults.baseURL = 'http://127.0.0.1:5000'; // Change this to your Flask backend URL and port

const store = createStore({
  state() {
    return {
      isLoggedIn: false,
    };
  },
  mutations: {
    setLogin(state, status) {
      state.isLoggedIn = status;
    },
  },
});

const app = createApp(App);

app.use(VueAxios, axios);
app.use(router);
app.use(store);

app.mount("#app");