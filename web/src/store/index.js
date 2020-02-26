import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    user: {},
    coaches: [],
    tournaments: [],
    bb2Names: [],
    initial_load: false,
  },
  mutations: {
    storeTournaments(state, tournaments) {
      state.tournaments = tournaments;
    },
    storeCoaches(state, coaches) {
      state.coaches = coaches;
    },
    storeUser(state, user) {
      state.user = user;
    },
    storeBBNames(state, bb2Names) {
      state.bb2Names = bb2Names;
    },
    initially_loaded(state) {
      state.initial_load = true;
    },
  },
  actions: {
    getCoaches({ commit }) {
      const path = '/coaches';
      Vue.axios.get(path)
        .then((res) => {
          
        });
    }
  },
  modules: {
  },
  getters: {
    loggedCoach: (state) => {
      if (state.user.id && state.user.coach && state.user.coach.id) {
        return state.user.coach;
      }
      return undefined;
    },
    is_webadmin: (state, getters) => {
      if (getters.loggedCoach && getters.loggedCoach.web_admin) {
        return true;
      }
      return false;
    },
  },
});
