import Vue from 'vue';
import axios from 'axios';
import VueAxios from 'vue-axios';
import 'bootstrap';
import { BootstrapVue } from 'bootstrap-vue';
import $ from 'jquery';
import showdown from 'showdown';
import VueMobileDetection from 'vue-mobile-detection';
import { library, dom } from '@fortawesome/fontawesome-svg-core';
import { fas } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import App from './App.vue';
import VueFlashMessage from './components/VueFlashMessage/index';

import './assets/scss/main.scss';
import store from './store';
import 'bootstrap-vue/dist/bootstrap-vue.css';

dom.watch();

library.add(fas);

Vue.component('font-awesome-icon', FontAwesomeIcon);
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
  methods: {
    skillPicker() {
      return this.$root.$children[0].$refs.skillPickerComponent;
    },
  },
});

new Vue({
  store,
  render: (h) => h(App),
}).$mount('#app');
