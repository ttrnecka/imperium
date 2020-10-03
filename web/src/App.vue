<template>
  <div>
    <imperium-navbar @menu-change="setMenu" :default="menu"></imperium-navbar>
    <div class="container-fluid pt-2" v-cloak>
      <flash-message transitionIn="animated swing" class="flashpool"></flash-message>
      <component v-bind:is="currentTabComponent" class="tab"></component>
      <signup-modal ref="signupModal"></signup-modal>
      <skill-picker></skill-picker>
    </div><!-- /.container -->
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex';
import Cards from '@/mixins/cards';
import Api from '@/mixins/api';
import signupModal from './components/signup-modal.vue';
import imperiumNavbar from './components/nav_bar.vue';
import coachContent from './components/coach_content.vue';
import tournamentContent from './components/tournament_content.vue';
import leaderboardContent from './components/leaderboard_content.vue';
import skillPicker from './components/skill_picker.vue';

export default {
  name: 'App',
  mixins: [Cards, Api],
  data() {
    return {
      menu: 'Coaches',
    };
  },
  components: {
    'signup-modal': signupModal,
    imperiumNavbar,
    coachContent,
    tournamentContent,
    leaderboardContent,
    skillPicker,
  },
  methods: {
    setMenu(value) {
      this.menu = value;
    },
    getInitialData() {
      this.axios.all([this.getMe(), this.getCoaches(), this.getTournaments(), this.getBBNames(), this.getConfig()])
        .then(this.axios.spread(() => {
          this.$store.commit('initially_loaded');
        }))
        .catch((error) => {
          console.error(error);
        });
    },

    signedCallback(coach) {
      this.user.coach = coach;
      this.getCoaches();
      this.$store.commit('toggleRefresh');
    },
    ...mapActions([
      'getCoaches', 'getTournaments', 'getBBNames', 'getMe', 'getConfig',
    ]),
  },
  computed: {
    currentTabComponent() {
      if (this.menu === 'Coaches') {
        return 'coach-content';
      }
      if (this.menu === 'Tournaments') {
        return 'tournament-content';
      }
      if (this.menu === 'Leaderboard') {
        return 'leaderboard-content';
      }
      return 'coach-content';
    },
    is_active() {
      if (this.user.id && this.loggedCoach && !this.loggedCoach.deleted) {
        return true;
      }
      return false;
    },
    ...mapState([
      'user', 'initial_load',
    ]),
    ...mapGetters([
      'loggedCoach',
    ]),
  },
  watch: {
    initial_load: function (value) {
      if (value === true && !this.is_active) {
        this.$refs.signupModal.open();
      }
    },
  },
  mounted() {
    this.$on('signedUpCoach', this.signedCallback);
  },
  beforeMount() {
    this.getInitialData();
  },
};
</script>

<style>
</style>
