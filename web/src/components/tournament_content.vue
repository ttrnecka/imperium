<template>
  <div class="row">
    <div class="col-12">
      <div class="tab-content" id="accordionTournaments">
        <div class="tournament col-lg-9">
          <div class="row">
            <div class="form-group col-md-4">
              <select class="form-control" id="tournament_region" v-model="selected_t_region">
                <option selected disabled value="">Region:</option>
                <option value="">Reset</option>
                <option value="all">Cross-region</option>
                <option value="bigo">Big O</option>
                <option value="gman">GMAN</option>
                <option value="rel">REL</option>
              </select>
            </div>
            <div class="form-group col-md-4">
              <select class="form-control" id="tournament_state" v-model="selected_t_state">
                <option selected disabled value="">Occupation:</option>
                <option value="">Reset</option>
                <option value="free">Free</option>
                <option value="full">Full</option>
                <option value="entered">Entered</option>
                <option value="admined_by_me">Admined by me</option>
              </select>
            </div>
            <div class="form-group col-md-4">
              <select class="form-control" id="tournament_duration" v-model="selected_t_mode">
                <option selected disabled value="">Mode:</option>
                <option value="">Reset</option>
                <option value="regular">Regular</option>
                <option value="fasttrack">Fast Track</option>
                <option value="bootcamp">Boot Camp</option>
              </select>
            </div>
          </div>
        </div>
        <tournament class="show col-lg-9 border rounded border-primary border-bottom-0" v-for="tournament in filteredTournaments"
          :key="tournament.tournament_id" :id="'tourn'+tournament.tournament_id"
          role="tabpanel" aria-labelledby="tournament" :tournament="tournament"
          :coaches="coaches" :data-parent="'#accordionTournaments'" :user="user"></tournament>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex';
import tournament from '@/components/tournament.vue';

export default {
  name: 'tournament-content',
  components: {
    tournament,
  },
  data() {
    return {
      selected_t_region: '',
      selected_t_state: '',
      selected_t_mode: '',
    };
  },
  methods: {
  },
  computed: {
    filteredTournaments() {
      let filtered = this.tournaments;
      if (this.selected_t_region !== '') {
        filtered = filtered.filter((e) => e.region.toLowerCase().replace(/\s/g, '') === this.selected_t_region);
      }
      if (this.selected_t_mode !== '') {
        filtered = filtered.filter((e) => e.mode.toLowerCase().replace(/\s/g, '') === this.selected_t_mode);
      }
      if (this.selected_t_state === 'full') {
        filtered = filtered.filter((e) => e.coach_limit === e.tournament_signups.filter((el) => el.mode === 'active').length);
      } else if (this.selected_t_state === 'free') {
        filtered = filtered.filter((e) => e.coach_limit > e.tournament_signups.filter((el) => el.mode === 'active').length);
      } else if (this.selected_t_state === 'admined_by_me') {
        filtered = filtered.filter((e) => this.loggedCoach
          && this.loggedCoach.short_name === e.admin);
      } else if (this.selected_t_state === 'entered') {
        filtered = filtered.filter((e) => {
          if (this.loggedCoach !== undefined) {
            for (let i = 0; i < e.coach_limit; i += 1) {
              if (e.tournament_signups[i]) {
                if (e.tournament_signups[i].coach === this.loggedCoach.id) {
                  return e;
                }
              }
            }
          }
          return false;
        });
      }
      return filtered;
    },
    ...mapState([
      'user', 'coaches', 'tournaments',
    ]),
    ...mapGetters([
      'loggedCoach', 'is_webadmin',
    ]),
  },
  watch: {
  },
};
</script>
