<template>
  <div>
    <imperium-navbar @menu-change="setMenu" :user="user" :default="menu"></imperium-navbar>
    <div class="container-fluid pt-2" v-cloak>
      <flash-message transitionIn="animated swing" class="flashpool"></flash-message>
      <coach-content v-if="menu=='Coaches'"></coach-content>
      <tournament-content v-if="menu=='Tournaments'"></tournament-content>
      <div v-if="menu=='Leaderboard'" class="row">
        <div class="col-12 col-md-6 col-lg-4 table-responsive">
          <h4> TOP 10 Collectors </h4>
          <table id="leaderboard" class="table table-hover">
            <thead class="thead-dark">
              <tr>
                <th scope="col">#</th>
                <th scope="col">Name</th>
                <th class="text-right" scope="col">Value</th>
              </tr>
            </thead>
            <tbody>
              <tr :class="leaderboard_class(coach.short_name)"
                v-for="(coach, index) in collectors_sorted.slice(0,10)" :key="coach.id">
                <th scope="row">{{ index+1 }}.</th>
                <td>{{ coach.short_name }}</td>
                <td class="text-right">{{ coach.collection_value }}</td>
              </tr>
              <tr v-if="leaderboard_coach!=undefined &&
                collectors_sorted.indexOf(leaderboard_coach) > 9"
                :class="leaderboard_class(leaderboard_coach.short_name)">
                <th scope="row">{{ collectors_sorted.indexOf(leaderboard_coach)+1 }}.</th>
                <td>{{ leaderboard_coach.short_name }}</td>
                <td class="text-right">{{ leaderboard_coach.collection_value }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="col-12 col-md-6 col-lg-4 table-responsive">
          <h4> TOP 10 Earners </h4>
          <table id="leaderboard" class="table table-hover">
            <thead class="thead-dark">
              <tr>
                <th scope="col">#</th>
                <th scope="col">Name</th>
                <th class="text-right" scope="col">Coins</th>
              </tr>
            </thead>
            <tbody>
              <tr :class="leaderboard_class(coach.short_name)"
                v-for="(coach, index) in earners_sorted.slice(0,10)" :key="coach.id">
                <th scope="row">{{ index+1 }}.</th>
                <td>{{ coach.short_name }}</td>
                <td class="text-right">{{ coach.earned }}</td>
              </tr>
              <tr v-if="leaderboard_coach!=undefined
                && earners_sorted.indexOf(leaderboard_coach) > 9"
                :class="leaderboard_class(leaderboard_coach.short_name)">
                <th scope="row">{{ earners_sorted.indexOf(leaderboard_coach)+1 }}.</th>
                <td>{{ leaderboard_coach.short_name }}</td>
                <td class="text-right">{{ leaderboard_coach.earned }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="col-12 col-md-6 col-lg-4 table-responsive">
          <h4> TOP 10 Grinders </h4>
          <table id="leaderboard" class="table table-hover">
            <thead class="thead-dark">
              <tr>
                <th scope="col">#</th>
                <th scope="col">Name</th>
                <th class="text-right" scope="col">Matches</th>
              </tr>
            </thead>
            <tbody>
              <tr :class="leaderboard_class(coach.name)"
                v-for="(coach, index) in grinders_sorted.slice(0,10)" :key="coach.name">
                <th scope="row">{{ index+1 }}.</th>
                <td>{{ coach.name }}</td>
                <td class="text-right">{{ coach.matches }}</td>
              </tr>
              <tr v-if="stats_coach!=undefined &&
                grinders_sorted.indexOf(stats_coach) > 9"
                :class="leaderboard_class(stats_coach.name)">
                <th scope="row">{{ grinders_sorted.indexOf(stats_coach)+1 }}.</th>
                <td>{{ stats_coach.name }}</td>
                <td class="text-right">{{ stats_coach.matches }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="col-12 col-md-6 col-lg-4 table-responsive">
          <h4> TOP 10 Points </h4>
          <table id="leaderboard" class="table table-hover">
            <thead class="thead-dark">
              <tr>
                <th scope="col">#</th>
                <th scope="col">Name</th>
                <th class="text-right" scope="col">Points</th>
              </tr>
            </thead>
            <tbody>
              <tr :class="leaderboard_class(coach.name)"
                v-for="(coach, index) in points_sorted.slice(0,10)" :key="coach.name">
                <th scope="row">{{ index+1 }}.</th>
                <td>{{ coach.name }}</td>
                <td class="text-right">{{ coach.points }}</td>
              </tr>
              <tr v-if="stats_coach!=undefined &&
                points_sorted.indexOf(stats_coach) > 9"
                :class="leaderboard_class(stats_coach.name)">
                <th scope="row">{{ points_sorted.indexOf(stats_coach)+1 }}.</th>
                <td>{{ stats_coach.name }}</td>
                <td class="text-right">{{ stats_coach.points }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="col-12 col-md-6 col-lg-4 table-responsive">
          <h4> TOP 10 Points Per Game (min. 6 games) </h4>
          <table id="leaderboard" class="table table-hover">
            <thead class="thead-dark">
              <tr>
                <th scope="col">#</th>
                <th scope="col">Name</th>
                <th class="text-right" scope="col">PPG</th>
              </tr>
            </thead>
            <tbody>
              <tr :class="leaderboard_class(coach.name)"
                v-for="(coach, index) in ppg_sorted.slice(0,10)" :key="coach.name">
                <th scope="row">{{ index+1 }}.</th>
                <td>{{ coach.name }}</td>
                <td class="text-right">{{ per_game(coach.points,coach.matches).toFixed(2) }}</td>
              </tr>
              <tr v-if="stats_coach!=undefined &&
                ppg_sorted.indexOf(stats_coach) > 9"
                :class="leaderboard_class(stats_coach.name)">
                <th scope="row">{{ ppg_sorted.indexOf(stats_coach)+1 }}.</th>
                <td>{{ stats_coach.name }}</td>
                <td class="text-right">
                  {{ per_game(stats_coach.points,stats_coach.matches).toFixed(2)}}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="col-12 col-md-6 col-lg-4 table-responsive">
          <h4> TOP 10 Scorers </h4>
          <table id="leaderboard" class="table table-hover">
            <thead class="thead-dark">
              <tr>
                <th scope="col">#</th>
                <th scope="col">Name</th>
                <th class="text-right" scope="col">Touchdowns</th>
              </tr>
            </thead>
            <tbody>
              <tr :class="leaderboard_class(coach.name)"
                v-for="(coach, index) in scorers_sorted.slice(0,10)" :key="coach.name">
                <th scope="row">{{ index+1 }}.</th>
                <td>{{ coach.name }}</td>
                <td class="text-right">{{ coach.inflictedtouchdowns }}</td>
              </tr>
              <tr v-if="stats_coach!=undefined &&
                scorers_sorted.indexOf(stats_coach) > 9"
                :class="leaderboard_class(stats_coach.name)">
                <th scope="row">{{ scorers_sorted.indexOf(stats_coach)+1 }}.</th>
                <td>{{ stats_coach.name }}</td>
                <td class="text-right">{{stats_coach.inflictedtouchdowns}}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="col-12 col-md-6 col-lg-4 table-responsive">
          <h4> TOP 10 Touchdowns Per Game (min. 6 games) </h4>
          <table id="leaderboard" class="table table-hover">
            <thead class="thead-dark">
              <tr>
                <th scope="col">#</th>
                <th scope="col">Name</th>
                <th class="text-right" scope="col">TDPG</th>
              </tr>
            </thead>
            <tbody>
              <tr :class="leaderboard_class(coach.name)"
                v-for="(coach, index) in tpg_sorted.slice(0,10)" :key="coach.name">
                <th scope="row">{{ index+1 }}.</th>
                <td>{{ coach.name }}</td>
                <td class="text-right">
                  {{ per_game(coach.inflictedtouchdowns,coach.matches).toFixed(2) }}
                </td>
              </tr>
              <tr v-if="stats_coach!=undefined &&
                tpg_sorted.indexOf(stats_coach) > 9"
                :class="leaderboard_class(stats_coach.name)">
                <th scope="row">{{ tpg_sorted.indexOf(stats_coach)+1 }}.</th>
                <td>{{ stats_coach.name }}</td>
                <td class="text-right">
                  {{per_game(stats_coach.inflictedtouchdowns,stats_coach.matches).toFixed(2)}}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="col-12 col-md-6 col-lg-4 table-responsive">
          <h4> TOP 10 Bashers </h4>
          <table id="leaderboard" class="table table-hover">
            <thead class="thead-dark">
              <tr>
                <th scope="col">#</th>
                <th scope="col">Name</th>
                <th class="text-right" scope="col">Casualties</th>
              </tr>
            </thead>
            <tbody>
              <tr :class="leaderboard_class(coach.name)"
                v-for="(coach, index) in bashers_sorted.slice(0,10)" :key="coach.name">
                <th scope="row">{{ index+1 }}.</th>
                <td>{{ coach.name }}</td>
                <td class="text-right">{{ coach.inflictedcasualties }}</td>
              </tr>
              <tr v-if="stats_coach!=undefined &&
                bashers_sorted.indexOf(stats_coach) > 9"
                :class="leaderboard_class(stats_coach.name)">
                <th scope="row">{{ bashers_sorted.indexOf(stats_coach)+1 }}.</th>
                <td>{{ stats_coach.name }}</td>
                <td class="text-right">{{stats_coach.inflictedcasualties}}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="col-12 col-md-6 col-lg-4 table-responsive">
          <h4>TOP 10 Casualties Per Game (min. 6 games)</h4>
          <table id="leaderboard" class="table table-hover">
            <thead class="thead-dark">
              <tr>
                <th scope="col">#</th>
                <th scope="col">Name</th>
                <th class="text-right" scope="col">CPG</th>
              </tr>
            </thead>
            <tbody>
              <tr :class="leaderboard_class(coach.name)"
                v-for="(coach, index) in cpg_sorted.slice(0,10)" :key="coach.name">
                <th scope="row">{{ index+1 }}.</th>
                <td>{{ coach.name }}</td>
                <td class="text-right">
                  {{ per_game(coach.inflictedcasualties,coach.matches).toFixed(2) }}
                </td>
              </tr>
              <tr v-if="stats_coach!=undefined &&
                cpg_sorted.indexOf(stats_coach) > 9"
                :class="leaderboard_class(stats_coach.name)">
                <th scope="row">{{ cpg_sorted.indexOf(stats_coach)+1 }}.</th>
                <td>{{ stats_coach.name }}</td>
                <td class="text-right">
                  {{per_game(stats_coach.inflictedcasualties,stats_coach.matches).toFixed(2)}}
                  </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="col-12 col-md-6 col-lg-4 table-responsive">
          <h4> TOP 10 Hitmen </h4>
          <table id="leaderboard" class="table table-hover">
            <thead class="thead-dark">
              <tr>
                <th scope="col">#</th>
                <th scope="col">Name</th>
                <th class="text-right" scope="col">Kills</th>
              </tr>
            </thead>
            <tbody>
              <tr :class="leaderboard_class(coach.name)"
                v-for="(coach, index) in hitmen_sorted.slice(0,10)" :key="coach.name">
                <th scope="row">{{ index+1 }}.</th>
                <td>{{ coach.name }}</td>
                <td class="text-right">{{ coach.inflicteddead }}</td>
              </tr>
              <tr v-if="stats_coach!=undefined &&
                hitmen_sorted.indexOf(stats_coach) > 9"
                :class="leaderboard_class(stats_coach.name)">
                <th scope="row">{{ hitmen_sorted.indexOf(stats_coach)+1 }}.</th>
                <td>{{ stats_coach.name }}</td>
                <td class="text-right">{{stats_coach.inflicteddead}}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="col-12 col-md-6 col-lg-4 table-responsive">
          <h4> TOP 10 Passers </h4>
          <table id="leaderboard" class="table table-hover">
            <thead class="thead-dark">
              <tr>
                <th scope="col">#</th>
                <th scope="col">Name</th>
                <th class="text-right" scope="col">Passes</th>
              </tr>
            </thead>
            <tbody>
              <tr :class="leaderboard_class(coach.name)"
                v-for="(coach, index) in passers_sorted.slice(0,10)" :key="coach.name">
                <th scope="row">{{ index+1 }}.</th>
                <td>{{ coach.name }}</td>
                <td class="text-right">{{ coach.inflictedpasses }}</td>
              </tr>
              <tr v-if="stats_coach!=undefined &&
                passers_sorted.indexOf(stats_coach) > 9"
                :class="leaderboard_class(stats_coach.name)">
                <th scope="row">{{ passers_sorted.indexOf(stats_coach)+1 }}.</th>
                <td>{{ stats_coach.name }}</td>
                <td class="text-right">{{stats_coach.inflictedpasses}}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="col-12 col-md-6 col-lg-4 table-responsive">
          <h4> TOP 10 Surfers </h4>
          <table id="leaderboard" class="table table-hover">
            <thead class="thead-dark">
              <tr>
                <th scope="col">#</th>
                <th scope="col">Name</th>
                <th class="text-right" scope="col">Surfs</th>
              </tr>
            </thead>
            <tbody>
              <tr :class="leaderboard_class(coach.name)"
                v-for="(coach, index) in surfers_sorted.slice(0,10)" :key="coach.name">
                <th scope="row">{{ index+1 }}.</th>
                <td>{{ coach.name }}</td>
                <td class="text-right">{{ coach.inflictedpushouts }}</td>
              </tr>
              <tr v-if="stats_coach!=undefined &&
                surfers_sorted.indexOf(stats_coach) > 9"
                :class="leaderboard_class(stats_coach.name)">
                <th scope="row">{{ surfers_sorted.indexOf(stats_coach)+1 }}.</th>
                <td>{{ stats_coach.name }}</td>
                <td class="text-right">{{stats_coach.inflictedpushouts}}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <signup-modal :user="user" ref="signupModal"></signup-modal>
    </div><!-- /.container -->
  </div>
</template>

<script>
import Vue from 'vue';
import { mapState, mapGetters, mapActions } from 'vuex';
import Cards from '@/mixins/cards';
import Api from '@/mixins/api';
import signupModal from './components/signup-modal.vue';
import imperiumNavbar from './components/nav_bar.vue';
import coachContent from './components/coach_content.vue';
import tournamentContent from './components/tournament_content.vue';

export default {
  name: 'App',
  mixins: [Cards, Api],
  data() {
    return {
      menu: 'Coaches',
      leaderboard_loaded: false,
      leaderboard: {
        deck_values: [],
        earners: [],
        stats: [],
        coaches: [],
      },
    };
  },
  components: {
    'signup-modal': signupModal,
    imperiumNavbar,
    coachContent,
    tournamentContent,
  },
  methods: {
    setMenu(value) {
      this.menu = value;
    },
    updateTournament(tourn) {
      const idx = this.tournaments.findIndex((x) => x.id === parseInt(tourn.id, 10));
      Vue.set(this.tournaments, idx, tourn);
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

    getLeaderboard() {
      const path = '/coaches/leaderboard';
      Vue.axios.get(path)
        .then((res) => {
          this.leaderboard.coaches = res.data.coaches;
          this.leaderboard.stats = res.data.coach_stats;
        })
        .catch((error) => {
          console.error(error);
        });
    },

    leaderboard_class(name) {
      return this.is_loggedcoach(name) ? 'table-success' : '';
    },

    is_loggedcoach(name) {
      if (this.loggedCoach !== undefined
         && (this.loggedCoach.bb2_name === name || this.loggedCoach.short_name === name)) {
        return true;
      }
      return false;
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
    loaded_user_and_coaches() {
      if (this.loaded_user && this.loaded_coaches) {
        return true;
      }
      return false;
    },
    is_active() {
      if (this.user.id && this.loggedCoach && !this.loggedCoach.deleted) {
        return true;
      }
      return false;
    },
    stats_coach() {
      return this.leaderboard.stats.find((e) => this.is_loggedcoach(e.name));
    },
    leaderboard_coach() {
      return this.leaderboard.coaches.find((e) => this.is_loggedcoach(e.short_name));
    },
    collectors_sorted() {
      return this.leaderboard.coaches.slice().sort((a, b) => b.collection_value
        - a.collection_value);
    },
    earners_sorted() {
      return this.leaderboard.coaches.slice().sort((a, b) => b.earned - a.earned);
    },
    grinders_sorted() {
      return this.leaderboard.stats.slice().sort((a, b) => b.matches - a.matches);
    },
    points_sorted() {
      return this.leaderboard.stats.slice().sort((a, b) => b.points - a.points);
    },
    ppg_sorted() {
      return this.leaderboard.stats.slice().sort((a, b) => this.per_game(b.points, b.matches)
        - this.per_game(a.points, a.matches));
    },
    scorers_sorted() {
      return this.leaderboard.stats.slice().sort((a, b) => b.inflictedtouchdowns
        - a.inflictedtouchdowns);
    },
    tpg_sorted() {
      return this.leaderboard.stats.slice().sort(
        (a, b) => this.per_game(b.inflictedtouchdowns, b.matches)
          - this.per_game(a.inflictedtouchdowns, a.matches),
      );
    },
    bashers_sorted() {
      return this.leaderboard.stats.slice().sort((a, b) => b.inflictedcasualties
        - a.inflictedcasualties);
    },
    cpg_sorted() {
      return this.leaderboard.stats.slice().sort(
        (a, b) => this.per_game(b.inflictedcasualties, b.matches)
          - this.per_game(a.inflictedcasualties, a.matches),
      );
    },
    hitmen_sorted() {
      return this.leaderboard.stats.slice().sort((a, b) => b.inflicteddead - a.inflicteddead);
    },
    passers_sorted() {
      return this.leaderboard.stats.slice().sort((a, b) => b.inflictedpasses - a.inflictedpasses);
    },
    surfers_sorted() {
      return this.leaderboard.stats.slice().sort((a, b) => b.inflictedpushouts
        - a.inflictedpushouts);
    },
    ...mapState([
      'user', 'coaches', 'tournaments', 'bb2Names',
    ]),
    ...mapGetters([
      'loggedCoach',
    ]),
  },
  watch: {
    menu: function (newMenu) {
      if (newMenu === 'Leaderboard') {
        if (this.leaderboard_loaded === false) {
          this.getLeaderboard();
          this.leaderboard_loaded = true;
        }
      }
    },
    loaded_user_and_coaches: function (value) {
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
