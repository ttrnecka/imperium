import Vue from 'vue';
import axios from 'axios';
import VueAxios from 'vue-axios';
import 'bootstrap';
import { BootstrapVue } from 'bootstrap-vue';
import $ from 'jquery';
import showdown from 'showdown';
import VueMobileDetection from 'vue-mobile-detection';
import App from './App.vue';
import VueFlashMessage from './components/VueFlashMessage/index';

// import 'bootstrap/dist/css/bootstrap.css';
import 'bootswatch/dist/cerulean/bootstrap.min.css';
import './assets/css/main.css';
import '@fortawesome/fontawesome-free/css/all.css';
import '@fortawesome/fontawesome-free/js/all';
import store from './store';
import 'bootstrap-vue/dist/bootstrap-vue.css';

Vue.use(VueAxios, axios);
Vue.use(BootstrapVue);
// Vue.use(IconsPlugin);
Vue.use(VueFlashMessage);
Vue.use(VueMobileDetection);
Vue.prototype.$ = $;

Vue.config.productionTip = false;

Vue.mixin({
  data() {
    return {
      markdown: new showdown.Converter(),
    };
  },
});

new Vue({
  store,
  render: (h) => h(App),
}).$mount('#app');
