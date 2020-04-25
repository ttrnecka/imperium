<template>
  <div class="row">
    <div class="col-lg-auto" >
        <div class="form-group">
            <input type="text" class="form-control" id="coach_filter"
              placeholder="Search..." v-bind:value="coach_filter"
              v-on:input="debounceCoachSearch($event.target.value)">
        </div>
        <div class="list-group" id="coach-list" role="tablist">
            <a data-toggle="list" v-for="coach in filteredCoaches"
              @click="getCoach(coach.id)" :key="coach.id"
              class="list-group-item list-group-item-action"
              href="#coachDisplay" role="tab"
              aria-controls="home"
              :class="{ active: coach.short_name == selectedCoach.short_name }">{{ coach.short_name }}</a>
        </div>
    </div>
    <div class="col-lg-8">
      <div class="tab-content show" id="nav-tabContent">
        <div class="tab-pane fade show active" id="coachDisplay"
          role="tabpanel" aria-labelledby="coach">
          <ul class="nav nav-tabs" id="coachTab" role="tablist">
              <li class="nav-item">
                <a class="nav-link active" id="cards-tab" data-toggle="tab"
                  href="#coach_cards" role="tab" aria-controls="coach_cards">
                  {{ selectedCoach.short_name }}'s Cards
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" id="info-tab" data-toggle="tab" href="#coach_info"
                  role="tab" aria-controls="coach_info" aria-selected="true">
                  {{ selectedCoach.short_name}}'s Info
                </a>
              </li>
              <li v-if="is_owner(selectedCoach)" class="nav-item">
                <a class="nav-link" id="dusting-tab" data-toggle="tab"
                  href="#coach_dusting" role="tab" aria-controls="coach_dusting"
                  aria-selected="false">Dusting</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" id="stats-tab" data-toggle="tab"
                  href="#coach_stats" role="tab" aria-controls="coach_stats"
                  aria-selected="false">Stats</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" id="stats-tab" data-toggle="tab"
                  href="#coach_achievements" role="tab"
                  aria-controls="coach_achievements"
                  aria-selected="false">Achievements</a>
              </li>
          </ul>
          <div class="tab-content" id="coachTabContent">
            <div class="tab-pane fade" id="coach_info" role="tabpanel"
              aria-labelledby="info-tab">
                <div class="row">
                    <div class="col-6">
                      <h5 class="coach_info">
                      Bank: <small class="text-muted">
                              {{ selectedCoach.account.amount}} coins
                            </small>
                      </h5>
                    </div>
                    <div class="col-3 text-right">
                        <h5 class="coach_info">BB2 Name:</h5>
                    </div>
                    <div class="col-3">
                        <div v-if="is_webadmin" class="form-group">
                            <select class="form-control col-11 coach_info"
                              @change="linkBB2Name()" id="bb2_name"
                              v-model="selectedCoach.bb2_name">
                                <option selected value="">None</option>
                                <option v-for="name in bb2Names" :key="name" :value="name">{{name}}</option>
                            </select>
                        </div>
                        <div v-else>
                            <h5 class="coach_info">
                              <small class="text-muted">
                                {{selectedCoach.bb2_name}}
                              </small>
                            </h5>
                        </div>
                    </div>
                    <div class="col-12">
                        <h5 class="coach_info">
                          Free Packs:
                          <small class="text-muted">
                            {{ getFreePacks(selectedCoach) }}
                          </small>
                        </h5>
                    </div>
                    <div class="tab-content show col-12"
                      id="accordionTournamentsCoach">
                        <h5 class="coach_info">Joined Tournaments:</h5>
                        <tournament
                          v-for="tournament in tournamentsFor(selectedCoach)"
                          :key="tournament.tournament_id"
                          :id="'tourn'+tournament.tournament_id+'coach'"
                          role="tabpanel" aria-labelledby="tournament"
                          :tournament="tournament" :coaches="coaches"
                          data-parent="#accordionTournamentsCoach" :user="user">
                        </tournament>
                    </div>
                    <div class="tab-content show col-12"
                      id="accordionTournamentsAdmined">
                        <h5 class="coach_info">Admined Tournaments:</h5>
                        <tournament
                          v-for="tournament in tournamentsAdminedBy(selectedCoach)"
                          :key="tournament.tournament_id"
                          :id="'tourn'+tournament.tournament_id+'coach'"
                          role="tabpanel" aria-labelledby="tournament"
                          :tournament="tournament" :coaches="coaches"
                          data-parent="#accordionTournamentsCoach" :user="user">
                        </tournament>
                    </div>
                    <div class="col-12">
                    <h5 class="coach_info">Transactions:</h5>
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th class="th-lg">Date</th>
                                <th class="th-lg">Bank Change</th>
                                <th class="th-lg">Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr
                              v-for="transaction in
                              selectedCoach.account.transactions.slice()"
                              :key="transaction.id">
                                <td>
                                  {{ print_date(transaction.date_confirmed) }}
                                </td>
                                <td>{{ transaction.price*-1 }}</td>
                                <td>{{ transaction.description }}</td>
                            </tr>
                        </tbody>
                    </table>
                    </div>
                </div>
            </div>
            <div class="tab-pane fade show active" id="coach_cards"
              role="tabpanel" aria-labelledby="cards-tab">
              <div class="col-auto my-1">
                <div class="form-group">
                  <label for="mixed_team_select">Select team:</label>
                  <select class="form-control"
                    id="mixed_team"
                    v-model="selected_team">
                      <option selected value="All">All</option>
                      <option v-for="team in mixed_teams"
                        :value="team.name" :key="team.code">
                        {{ team.name }} ({{ team.races.join() }})
                      </option>
                  </select>
                </div>
                <div class="row">
                  <div class="col-6">
                    <h5>
                    Collection value: {{ cardsValue(selectedCoach.cards) }}
                    </h5>
                  </div>
                  <div class="col-6">
                  <div
                    class="custom-control custom-checkbox mr-sm-2 text-right">
                    <input type="checkbox" class="custom-control-input"
                      id="sptoggle" v-model="starter">
                    <label class="custom-control-label"
                      for="sptoggle">Toggle Starter Pack</label>
                  </div>
                  </div>
                </div>
                <card-list id="accordionCards" :cards="selectedCoach.cards" :selected_team="selected_team" :owner="selectedCoach"
                  :starter="starter" :quantity="true"></card-list>
              </div>
            </div>
            <div v-if="is_owner(selectedCoach)" class="tab-pane fade"
              id="coach_dusting" role="tabpanel" aria-labelledby="dusting-tab">
              <div class="col-auto my-1">
                <div class="row duster_info">
                  <div class="col-9 col-md-6"><h4>{{duster_type}}</h4></div>
                  <div class="col-3 col-md-6 text-right">
                    <button v-if="is_duster_open" type="button" :disabled="processing"
                      class="btn btn-info" @click="dust_cancel()">Cancel</button>
                    <button v-if="is_duster_full" :disabled="processing" type="button"
                      class="btn btn-info" @click="dust_commit()">Commit</button>
                  </div>
                </div>
                <card-list id="accordionCardsDusting" :cards="selectedCoach.cards" :owner="selectedCoach"
                  :starter="false" :duster="true"></card-list>
              </div>
            </div>
            <div class="tab-pane fade" id="coach_achievements"
              role="tabpanel" aria-labelledby="coach-achievements">
              <div class="col-auto my-1">
                <div class="row">
                  <h4 class="col-12">Achievements</h4>
                </div>
                <div class="row">
                  <h5 class="col-12">Hidden Quests</h5>
                </div>
                <imperium-achievement v-for="(ach,index) in quest_achievements(selectedCoach)"
                  :key="'quest'+index" :data="ach" :hidden="true">
                </imperium-achievement>

                <div class="row">
                    <h5 class="col-12">Conclave Achievements</h5>
                </div>
                <imperium-achievement v-for="(ach,index) in conclave_achievements(selectedCoach)"
                  :key="'conclave'+index" :data="ach">
                </imperium-achievement>

                <div class="row">
                    <h5 class="col-12">Match Achievements (Any Team)</h5>
                </div>
                <imperium-achievement v-for="(ach,index) in match_achievements(selectedCoach)"
                  :key="'match_ach'+index" :data="ach">
                </imperium-achievement>

                <div class="row">
                    <h5 class="col-12">Mixed Team Achievements</h5>
                </div>
                <template v-for="(ta,index) in team_achievements(selectedCoach)">
                  <div :key="index" class="row">
                  <h6 class="col-12">{{ta.team_name}}</h6>
                  </div>
                  <template v-for="stat in
                    ['played','touchdowns','casualties','kills','passes','wins']">
                    <template v-for="n in [1,2,3]">
                      <imperium-achievement :key="`${index}${stat}${n}`" :data="ta.achievements[stat][n]">
                      </imperium-achievement>
                    </template>
                  </template>
                </template>
              </div>
            </div>
            <div class="tab-pane fade" id="coach_stats"
              role="tabpanel" aria-labelledby="coach-stats">
              <div class="col-auto my-1">
                <b-form-select v-model="season" :options="seasons" size="lg" @change="getCoachStats"></b-form-select>
                <div class="tab-pane fade show active"
                  id="coachStatsDisplay" role="tabpanel"
                  aria-labelledby="coachStats">
                  <ul class="nav nav-tabs" id="coachStatsTab" role="tablist">
                    <li class="nav-item">
                      <a class="nav-link active" id="stats-tab"
                        data-toggle="tab" href="#stats_summary"
                        role="tab" aria-controls="stats_summary">Summary</a>
                    </li>
                    <li class="nav-item" v-for="(team,index)
                      in team_stats(selectedCoach)" :key="index">
                      <a class="nav-link" :id="'stats-tab'+index" data-toggle="tab"
                      :href="'#stats_'+index" role="tab"
                      aria-controls="stats_team">{{team.team_name}}</a>
                    </li>
                  </ul>
                  <div class="tab-content" id="coachStatsTabContent">
                    <div class="tab-pane fade show active" id="stats_summary"
                      role="tabpanel" aria-labelledby="stats-summary-tab">
                      <div class="row mt-2">
                        <div class="col-3"><h5>Wins:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'wins')}}</small></h5></div>
                        <div class="col-3"><h5>Draws:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'draws')}}</small></h5></div>
                        <div class="col-3"><h5>Losses:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'losses')}}</small></h5></div>
                        <div class="col-3"><h5>Matches:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'matches')}}</small></h5></div>
                        <div class="col-3"><h5>Points:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'points')}}</small></h5></div>
                        <div class="col-3"><h5 title="Points Per Game">PPG:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{(getStat(selectedCoach,'points')
                          /
                          getStat(selectedCoach,'matches')).toFixed(2)}}
                          </small></h5>
                        </div>

                        <div class="col-3"><h5>Blocks:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'inflictedtackles')}}</small></h5></div>
                        <div class="col-3"><h5 title="Armor Breaks">ABs:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'inflictedinjuries')}}</small></h5></div>
                        <div class="col-3"><h5>KOs:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'inflictedko')}}</small></h5></div>
                        <div class="col-3"><h5 title="Casualties">Cas:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'inflictedcasualties')}}</small></h5></div>
                        <div class="col-3"><h5>Kills:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'inflicteddead')}}</small></h5></div>
                        <div class="col-3"><h5 title="Blocks Per Game">BPG:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{(getStat(selectedCoach,'inflictedtackles')
                          /
                          getStat(selectedCoach,'matches')).toFixed(2)}}
                          </small></h5>
                        </div>

                        <div class="col-3"><h5>TDs:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'inflictedtouchdowns')}}</small></h5></div>
                        <div class="col-3"><h5>Passes:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'inflictedpasses')}}</small></h5></div>
                        <div class="col-3"><h5>Passed [m]:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'inflictedmeterspassing')}}</small></h5>
                        </div>
                        <div class="col-3"><h5>Ran [m]:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'inflictedmetersrunning')}}</small></h5>
                        </div>
                        <div class="col-3"><h5 title="Interceptions">Int:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'inflictedinterceptions')}}</small></h5>
                        </div>
                        <div class="col-3"><h5 title="Touchdowns Per Game">TDPG:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{(getStat(selectedCoach,'inflictedtouchdowns')
                          /
                          getStat(selectedCoach,'matches')).toFixed(2)}}
                          </small></h5>
                        </div>
                      </div>
                    </div>
                    <div v-for="(team,index) in team_stats(selectedCoach)"
                      class="tab-pane fade" :key="index"
                      :id="'stats_'+index" role="tabpanel" aria-labelledby="stats-team-tab">
                      <div class="row mt-2">
                        <div class="col-3"><h5>Wins:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'wins')}}</small></h5></div>
                        <div class="col-3"><h5>Draws:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'draws')}}</small></h5></div>
                        <div class="col-3"><h5>Losses:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'losses')}}</small></h5></div>
                        <div class="col-3"><h5>Matches:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'matches')}}</small></h5></div>
                        <div class="col-3"><h5>Points:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'points')}}</small></h5></div>
                        <div class="col-3"><h5 title="Points Per Game">PPG:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{(getTeamStat(team,'points')
                          /
                          getTeamStat(team,'matches')).toFixed(2)}}
                          </small></h5>
                        </div>

                        <div class="col-3"><h5>Blocks:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'inflictedtackles')}}</small></h5></div>
                        <div class="col-3"><h5 title="Armor Breaks">ABs:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'inflictedinjuries')}}</small></h5></div>
                        <div class="col-3"><h5>KOs:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'inflictedko')}}</small></h5></div>
                        <div class="col-3"><h5 title="Casualties">Cas:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'inflictedcasualties')}}</small></h5></div>
                        <div class="col-3"><h5>Kills:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'inflicteddead')}}</small></h5></div>
                        <div class="col-3"><h5 title="Blocks Per Game">BPG:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{(getTeamStat(team,'inflictedtackles')
                          /
                          getTeamStat(team,'matches')).toFixed(2)}}
                          </small></h5>
                        </div>

                        <div class="col-3"><h5>TDs:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'inflictedtouchdowns')}}</small></h5></div>
                        <div class="col-3"><h5>Passes:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'inflictedpasses')}}</small></h5></div>
                        <div class="col-3"><h5>Passed [m]:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'inflictedmeterspassing')}}</small></h5></div>
                        <div class="col-3"><h5>Ran [m]:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'inflictedmetersrunning')}}</small></h5></div>
                        <div class="col-3"><h5 title="Interceptions">Int:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'inflictedinterceptions')}}</small></h5></div>
                        <div class="col-3"><h5 title="Touchdowns Per Game">TDPG:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{(getTeamStat(team,'inflictedtouchdowns')
                          /
                          getTeamStat(team,'matches')).toFixed(2)}}
                          </small></h5>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex';
import Cards from '@/mixins/cards';
import tournament from '@/components/tournament.vue';
import imperiumAchievement from '@/components/achievement.vue';
import cardList from '@/components/card_list.vue';

export default {
  name: 'coach-content',
  mixins: [Cards],
  components: {
    tournament,
    imperiumAchievement,
    cardList,
  },
  data() {
    return {
      coach_filter: '',
      search_timeout: null,
      selected_team: 'All',
      processing: false,
      starter: true,
      selectedCoach: {
        short_name: '',
        account: {
          amount: 0,
          transactions: [],
        },
        tournaments: [],
        cards: [],
        id: 0,
        achievements: {},
        stats: {},
        free_packs: '',
      },
    };
  },
  methods: {
    getFreePacks(coach) {
      return coach.free_packs.split(',').map((e) => {
        switch (e) {
          case 'player':
            return 'Player';
          case 'training':
            return 'Training';
          case 'special':
            return 'Special Play';
          case 'booster_budget':
            return 'Booster';
          case 'booster_premium':
            return 'Booster Premium';
          default:
            return '';
        }
      }).join(', ');
    },
    tournamentsFor(coach) {
      return this.tournaments.filter((e) => coach.tournaments.includes(e.id));
    },
    tournamentsAdminedBy(coach) {
      return this.tournaments.filter((e) => e.admin === coach.short_name);
    },
    quest_achievements(coach) {
      if (coach.achievements.quests) {
        return ['collect3legends', 'buildyourownlegend'].map((e) => coach.achievements.quests[e]);
      }
      return [];
    },
    conclave_achievements(coach) {
      if (coach.achievements.conclave) {
        return ['getcursed1', 'getcursed2', 'getcursed3', 'getblessed1', 'getblessed2',
          'getblessed3'].map((e) => coach.achievements.conclave[e]);
      }
      return [];
    },
    team_achievements(coach) {
      if (coach.achievements.team) {
        return [32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42].map((e) => ({
          team_name: this.mixed_teams.find((t) => t.idraces === e).name,
          achievements: coach.achievements.team[e],
        }));
      }
      return [];
    },
    match_achievements(coach) {
      if (coach.achievements.match) {
        return ['passingtotal1', 'passingtotal2', 'runningtotal1', 'runningtotal2',
          'surfstotal1', 'surfstotal2', 'blocks1game1', 'blocks1game2',
          'breaks1game1', 'breaks1game2', 'cas1game1', 'cas1game2',
          'int1game1', 'score1game1', 'score1game2', 'sufferandwin1',
          'sufferandwin2', 'winwithall', 'win500down'].map((e) => coach.achievements.match[e]);
      }
      return [];
    },
    team_stats(coach) {
      if (coach.stats.teams) {
        return [32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42].map((e) => ({
          team_name: this.mixed_teams.find((t) => t.idraces === e).name,
          stats: coach.stats.teams[e],
        }));
      }
      return [];
    },
    getStat(coach, ...args) {
      let pointer = coach.stats;
      for (let i = 0; i < args.length; i += 1) {
        if (pointer[args[i]]) {
          pointer = pointer[args[i]];
        } else {
          return 0;
        }
      }
      return pointer;
    },
    getTeamStat(team, ...args) {
      if (team.stats && team.stats[args[0]]) {
        return team.stats[args[0]];
      }
      return 0;
    },
    getCoach(id) {
      const path = `/coaches/${id}`;
      this.axios.get(path)
        .then((res) => {
          const idx = this.coaches.findIndex((x) => x.id === parseInt(id, 10));
          this.$set(this.coaches, idx, res.data);
          this.selectedCoach = this.coaches[idx];
          this.$nextTick(() => {
            this.$('[data-toggle="popover"]').popover();
          });
        })
        .catch((error) => {
          console.error(error);
        });
    },
    getCoachStats() {
      const { id } = this.selectedCoach;
      const path = `/coaches/${id}/stats?season=${this.season}`;
      this.axios.get(path)
        .then((res) => {
          const idx = this.coaches.findIndex((x) => x.id === parseInt(id, 10));
          // this.$set(this.coaches, idx, res.data);
          this.coaches[idx].stats = res.data;
          // this.selectedCoach = this.coaches[idx];
        })
        .catch((error) => {
          console.error(error);
        });
    },
    debounceCoachSearch(val) {
      const that = this;
      if (this.search_timeout) clearTimeout(this.search_timeout);
      this.search_timeout = setTimeout(() => {
        that.coach_filter = val;
      }, 300);
    },
    linkBB2Name() {
      const { id } = this.selectedCoach;
      const path = `/coaches/${id}`;
      this.axios.put(path, { name: this.selectedCoach.bb2_name })
        .then((res) => {
          const idx = this.coaches.findIndex((x) => x.id === parseInt(id, 10));
          this.$set(this.coaches, idx, res.data);
          this.selectedCoach = this.coaches[idx];
          this.flash('BB2 name updated', 'success', { timeout: 3000 });
        })
        .catch((error) => {
          if (error.response) {
            this.flash(error.response.data.message, 'error', { timeout: 3000 });
          } else {
            console.error(error);
          }
        });
    },

    selectCoach() {
      const c = this.loggedCoach;
      if (c && c.deleted === false) {
        this.getCoach(this.loggedCoach.id);
      } else if (this.coaches.length > 0) {
        this.getCoach(this.coaches[0].id);
      }
    },
    init() {
      this.selectCoach();
      this.$nextTick(() => {
        this.$('[data-toggle="popover"]').popover();
      });
    },
    print_date(pdate) {
      const jdate = new Date(pdate);
      const options = {
        year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric',
      };
      return jdate.toLocaleDateString('default', options);
    },
  },
  computed: {
    orderedCoaches() {
      const { coaches } = this;
      return coaches.sort((a, b) => a.name.localeCompare(b.name));
    },
    filteredCoaches() {
      return this.orderedCoaches.filter((coach) => coach.name
        .toLowerCase().includes(this.coach_filter.toLowerCase()));
    },
    season: {
      get() {
        return this.$store.state.season;
      },
      set(value) {
        this.$store.commit('updateSeason', value);
      },
    },
    ...mapState([
      'user', 'coaches', 'tournaments', 'bb2Names', 'initial_load', 'seasons',
    ]),
    ...mapGetters([
      'loggedCoach', 'is_webadmin', 'is_loggedcoach', 'is_duster', 'is_duster_full', 'is_duster_open', 'duster_type', 'is_owner',
    ]),
  },
  watch: {
    initial_load: function (newValue) {
      if (newValue) {
        this.init();
      }
    },
  },
  mounted() {
    if (this.initial_load) {
      this.init();
    }
  },
};
</script>
