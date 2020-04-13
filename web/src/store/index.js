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
    updateTournament(state, tourn) {
      const idx = state.tournaments.findIndex((x) => x.id === parseInt(tourn.id, 10));
      Vue.set(state.tournaments, idx, tourn);
    },
  },
  actions: {
    getCoaches({ commit }) {
      const path = '/coaches';
      return Vue.axios.get(path)
        .then((res) => {
          const { data } = res;
          for (let i = 0, len = data.length; i < len; i += 1) {
            data[i].cards = [];
            data[i].tournaments = [];
            data[i].account = {};
            data[i].account.transactions = [];
          }
          commit('storeCoaches', data);
        });
    },
    getTournaments({ commit }) {
      const path = '/tournaments';
      return Vue.axios.get(path)
        .then((res) => {
          commit('storeTournaments', res.data);
        });
    },
    getBBNames({ commit }) {
      const path = '/bb2_names';
      return Vue.axios.get(path)
        .then((res) => {
          commit('storeBBNames', res.data);
        });
    },
    getMe({ commit }) {
      const path = '/me';
      return Vue.axios.get(path)
        .then((res) => {
          commit('storeUser', res.data.user);
        });
    },
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
    is_superadmin: (state, getters) => {
      if (getters.loggedCoach && getters.loggedCoach.super_admin) {
        return true;
      }
      return false;
    },

    is_loggedcoach: (state, getters) => (name) => {
      if (getters.loggedCoach !== undefined
         && (getters.loggedCoach.bb2_name === name || getters.loggedCoach.short_name === name)) {
        return true;
      }
      return false;
    },
    is_owner: (state, getters) => (coach) => (getters.loggedCoach && coach && getters.loggedCoach.id === coach.id),
    is_duster: (state, getters) => (getters.loggedCoach.duster && getters.loggedCoach.duster.type),
    is_duster_full: (state, getters) => (getters.is_duster ? getters.loggedCoach.duster.cards.length === 10 : false),
    is_duster_open: (state, getters) => (getters.is_duster && getters.loggedCoach.duster.status === 'OPEN'),
    duster_type: (state, getters) => {
      if (getters.is_duster) {
        return getters.loggedCoach.duster.type;
      }
      return 'No dusting in progress';
    },
  },
});
