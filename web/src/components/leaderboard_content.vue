<template>
  <div class="row">
    <div class="col-12">
      <b-form-select v-model="season" :options="seasons" size="lg" @change="getLeaderboard"></b-form-select>
    </div>
    <leaderboard-table title="TOP 10 Collectors" :coaches="collectors_sorted" attr="collection_value" :coach="leaderboard_coach" ></leaderboard-table>
    <leaderboard-table title="TOP 10 Earners" :coaches="earners_sorted" attr="earned" :coach="leaderboard_coach" ></leaderboard-table>
    <leaderboard-table title="TOP 10 Grinders" :coaches="grinders_sorted" attr="matches" :coach="stats_coach" ></leaderboard-table>
    <leaderboard-table title="TOP 10 Points" :coaches="points_sorted" attr="points" :coach="stats_coach" ></leaderboard-table>
    <leaderboard-table title="TOP 10 Points Per Game (min. 6 games)" :coaches="ppg_sorted" attr="ppg" :coach="stats_coach" ></leaderboard-table>
    <leaderboard-table title="TOP 10 Scorers" :coaches="scorers_sorted" attr="inflictedtouchdowns" :coach="stats_coach" ></leaderboard-table>
    <leaderboard-table title="TOP 10 Touchdowns Per Game (min. 6 games)" :coaches="tpg_sorted" attr="tpg" :coach="stats_coach" ></leaderboard-table>
    <leaderboard-table title="TOP 10 Bashers" :coaches="bashers_sorted" attr="inflictedcasualties" :coach="stats_coach" ></leaderboard-table>
    <leaderboard-table title="TOP 10 Casualties Per Game (min. 6 games)" :coaches="cpg_sorted" attr="cpg" :coach="stats_coach" ></leaderboard-table>
    <leaderboard-table title="TOP 10 Hitmen" :coaches="hitmen_sorted" attr="inflicteddead" :coach="stats_coach" ></leaderboard-table>
    <leaderboard-table title="TOP 10 Passers" :coaches="passers_sorted" attr="inflictedpasses" :coach="stats_coach" ></leaderboard-table>
    <leaderboard-table title="TOP 10 Surfers" :coaches="surfers_sorted" attr="inflictedpushouts" :coach="stats_coach" ></leaderboard-table>
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import leaderboardTable from '@/components/leaderboard_table.vue';

export default {
  name: 'leaderboard-content',
  components: {
    leaderboardTable,
  },
  data() {
    return {
      leaderboard: {
        deck_values: [],
        earners: [],
        stats: [],
        coaches: [],
      },
      initial_load: false,
    };
  },
  methods: {
    getLeaderboard() {
      const path = `/coaches/leaderboard?season=${this.season}`;
      this.axios.get(path)
        .then((res) => {
          this.leaderboard.coaches = res.data.coaches;
          this.leaderboard.stats = res.data.coach_stats;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    init() {
      this.getLeaderboard();
      this.init = true;
    },
    per_game(total, games) {
      // at least minimum of 6 games
      if (games >= 6) {
        return total / games;
      }
      return 0;
    },
  },
  computed: {
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
      this.leaderboard.stats.forEach((e) => { e.ppg = this.per_game(e.points, e.matches).toFixed(2); });
      return this.leaderboard.stats.slice().sort((a, b) => b.ppg - a.ppg);
    },
    scorers_sorted() {
      return this.leaderboard.stats.slice().sort((a, b) => b.inflictedtouchdowns
        - a.inflictedtouchdowns);
    },
    tpg_sorted() {
      this.leaderboard.stats.forEach((e) => { e.tpg = this.per_game(e.inflictedtouchdowns, e.matches).toFixed(2); });
      return this.leaderboard.stats.slice().sort((a, b) => b.tpg - a.tpg);
    },
    bashers_sorted() {
      return this.leaderboard.stats.slice().sort((a, b) => b.inflictedcasualties
        - a.inflictedcasualties);
    },
    cpg_sorted() {
      this.leaderboard.stats.forEach((e) => { e.cpg = this.per_game(e.inflictedcasualties, e.matches).toFixed(2); });
      return this.leaderboard.stats.slice().sort((a, b) => b.cpg - a.cpg);
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
    season: {
      get() {
        return this.$store.state.season;
      },
      set(value) {
        this.$store.commit('updateSeason', value);
      },
    },
    ...mapGetters([
      'is_loggedcoach',
    ]),
    ...mapState([
      'seasons',
    ]),
  },
  watch: {
  },
  mounted() {
    if (!this.initial_load) {
      this.init();
    }
  },
};
</script>
