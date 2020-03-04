<template>
  <div>
    <imperium-navbar @menu-change="setMenu" :default="menu"></imperium-navbar>
    <div class="container-fluid pt-2" v-cloak>
      <flash-message transitionIn="animated swing" class="flashpool"></flash-message>
      <coach-content v-if="menu=='Coaches'"></coach-content>
      <tournament-content v-if="menu=='Tournaments'"></tournament-content>
      <leaderboard-content v-if="menu=='Leaderboard'"></leaderboard-content>
      <signup-modal :user="user" ref="signupModal"></signup-modal>
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
  },
  methods: {
    setMenu(value) {
      this.menu = value;
    },
    getInitialData() {
      this.axios.all([this.getMe(), this.getCoaches(), this.getTournaments(), this.getBBNames()])
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
    },
    ...mapActions([
      'getCoaches', 'getTournaments', 'getBBNames', 'getMe',
    ]),
  },
  computed: {
    is_active() {
      if (this.user.id && this.loggedCoach && !this.loggedCoach.deleted) {
        return true;
      }
      return false;
    },
    ...mapState([
      'user', 'initially_loaded',
    ]),
    ...mapGetters([
      'loggedCoach',
    ]),
  },
  watch: {
    initially_loaded: function (value) {
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
