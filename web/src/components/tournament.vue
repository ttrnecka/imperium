<template>
    <div class="tournament border rounded border-primary border-bottom-0">
        <div class="card-header" :id="'tournament'+tournament.tournament_id">
        <h5 class="mb-0">
            <div class="row" @click="load_leaderboard">
                <button class="col-md-9 btn btn-link btn-block" data-toggle="collapse" :data-target="'#collapseTournament'+tournament.tournament_id" aria-expanded="true" aria-controls="collapseTournament">
                    <div class="row">
                        <div class="col-6 col-md-5 text-left">{{ tournament.tournament_id }}. {{ tournament.name }}</div>
                        <div class="col-6 col-md-2 text-left">{{ tournament.status }} {{show_date}}</div>
                        <div class="col-6 col-md-2 text-left"> Signups: {{signed.length}}/{{ tournament.coach_limit }}</div>
                        <div class="col-6 col-md-3 text-left">Channel: {{ tournament.discord_channel }}<br/>Phase: {{ phase.desc }}</div>
                    </div>
                </button>
                <div class="col-md-3 text-right">
                    <template v-if="is_user_signed && !is_running" :disabled="processing">
                        <confirmation-button class="col-12 m-1"
                            :messages="['Resign','Are you sure?', 'Ok']"
                            v-on:confirmation-success="resign()"
                        >Resign</confirmation-button>
                    </template>
                    <button v-if="!is_user_signed && !is_full && !is_running" type="button" :disabled="processing" class="col-12 m-1 btn btn-success" @click="sign()">Sign</button>
                    <button v-if="is_user_signed" type="button" class="btn col-12 m-1 btn-primary"  @click="showDeck(user.coach)">My Deck</button>
                    <button v-if="!is_user_signed && is_full && !is_running" disabled type="button" class="col-12 m-1 btn btn-info">Full</button>
                    <button v-if="!is_user_signed && is_running" disabled type="button" class="col-12 m-1 btn btn-info">In Progress</button>
                </div>
            </div>
        </h5>
        </div>
        <div :id="'collapseTournament'+tournament.tournament_id" class="collapse" :aria-labelledby="'Tournaments'+tournament.tournament_id" :data-parent="getProperty('data-parent')">
            <div class="card-body">
                <div class="row tournament_info_line">
                    <div class="col-sm-3"><b>Signup By:</b>: {{ tournament.signup_close_date }}</div>
                    <div class="col-sm-3"><b>Start</b>: {{ tournament.expected_start_date }}</div>
                    <div class="col-sm-3"><b>End</b>: {{ tournament.expected_end_date }}</div>
                    <div class="col-sm-3"><b>Deadline</b>: {{ tournament.deadline_date }}</div>
                </div>
                <div class="row tournament_info_line">
                    <div class="col-sm-3"><b>Region</b>: {{ tournament.region }}</div>
                    <div class="col-sm-3"><b>Type</b>: {{ tournament.type }}</div>
                    <div class="col-sm-3"><b>Mode</b>: {{ tournament.mode }}</div>
                    <div class="col-sm-3"><b>Deck Limits</b>:
                        <span title="Card Limit">{{ tournament.deck_limit }}</span>
                        / <span title="Deck Value Target">{{ tournament.deck_value_target }}</span>
                        / <span title="Deck Value Limit">{{ tournament.deck_value_limit }}</span>
                        </div>
                </div>
                <div class="row tournament_info_line">
                    <div class="col-12"><b>Conclave Ranges</b>:</div>
                </div>
                <div class="row tournament_info_line">
                    <div class="col-sm-2 col-4">{{ tournament.conclave_ranges.blessing3.start }} - {{ tournament.conclave_ranges.blessing3.stop }}</div>
                    <div class="col-sm-10 col-8"><b>3 Blessing points</b></div>
                    <div class="col-sm-2 col-4">{{ tournament.conclave_ranges.blessing2.start }} - {{ tournament.conclave_ranges.blessing2.stop }}</div>
                    <div class="col-sm-10 col-8"><b>2 Blessing points</b></div>
                    <div class="col-sm-2 col-4">{{ tournament.conclave_ranges.blessing1.start }} - {{ tournament.conclave_ranges.blessing1.stop }}</div>
                    <div class="col-sm-10 col-8"><b>1 Blessing point</b></div>
                    <div class="col-sm-2 col-4">{{ tournament.deck_value_target }}</div>
                    <div class="col-sm-10 col-8"><b>Conclave equilibrium</b></div>
                    <div class="col-sm-2 col-4">{{ tournament.conclave_ranges.curse1.start }} - {{ tournament.conclave_ranges.curse1.stop }}</div>
                    <div class="col-sm-10 col-8"><b>1 Curse point</b></div>
                    <div class="col-sm-2 col-4">{{ tournament.conclave_ranges.curse2.start }} - {{ tournament.conclave_ranges.curse2.stop }}</div>
                    <div class="col-sm-10 col-8"><b>2 Curse points</b></div>
                    <div class="col-sm-2 col-4">{{ tournament.conclave_ranges.curse3.start }} - {{ tournament.conclave_ranges.curse3.stop }}</div>
                    <div class="col-sm-10 col-8"><b>3 Curse points</b></div>
                </div>
                <div class="row tournament_info_line">
                    <div class="col-sm-3"><b>Admin</b>: {{ tournament.admin }}</div>
                    <div class="col-sm-3"><b>Fee</b>: {{ tournament.fee }}</div>
                    <div class="col-sm-3"><b>Signups</b>: {{signed.length}}/{{ tournament.coach_limit }}</div>
                    <div class="col-sm-3"><b>Reserves</b>: {{reserved.length}}/{{ tournament.reserve_limit }}</div>
                </div>
                <div class="row tournament_info_line">
                    <div class="col-6"><b>Discord Channel</b>: #{{tournament.discord_channel}}</div>
                    <div class="col-3"><b>Deck Phase:</b></div>
                    <div class="col-3" v-if="!is_tournament_admin && !is_superadmin">{{phase.desc}}</div>
                    <div class="col-3" v-else>
                        <select class="form-control" v-model="selected.phase" @change="set_phase()">
                            <option v-for="phase in phases" :value="phase.name" :key="phase.name">{{ phase.desc }}</option>
                        </select>
                    </div>
                </div>
                <div v-if="is_webadmin || is_running" class="row tournament_info_line">
                    <div class="col-12"><b>Signed</b>: <span v-for="coach in signed_coaches" :key="coach.id">{{coach.short_name}} <b-badge class="mr-1" href="#" @click="showDeck(coach)" variant="primary">Deck</b-badge></span></div>
                </div>
                <div v-if="is_webadmin || is_running" class="row tournament_info_line">
                    <div class="col-12"><b>Reserves</b>: <span v-for="coach in reserved_coaches" :key="coach.id">{{coach.short_name}} <b-badge class="mr-1" href="#" @click="showDeck(coach)" variant="primary">Deck</b-badge></span></div>
                </div>
                <div class="row tournament_info_line">
                    <div class="col-12"><b>Prizes</b>:</div>
                </div>
                <div class="row tournament_info_line">
                    <div class="col-12">{{ tournament.prizes }}</div>
                </div>
                <div class="row tournament_info_line">
                    <div class="col-12"><b>Special Rules</b>:</div>
                </div>
                <div class="row tournament_info_line">
                    <div class="col-12">{{ tournament.special_rules }}</div>
                </div>
                <div class="row tournament_info_line">
                    <div class="col-12"><b>Banned Cards</b>:</div>
                </div>
                <div class="row tournament_info_line">
                    <div class="col-12">{{ tournament.banned_cards.replace(/;/g, ', ') }}</div>
                </div>
                <div class="row tournament_info_line">
                    <div class="col-12"><b>Sponsor</b>: {{ tournament.sponsor }}</div>
                </div>
                <div class="row tournament_info_line">
                    <div class="col-12">{{ tournament.sponsor_description }}</div>
                </div>
                <div class="row tournament_info_line">
                    <div class="col-12"><b>Unique Prize</b>:</div>
                </div>
                <div class="row tournament_info_line">
                    <div class="col-12">{{ tournament.unique_prize }}</div>
                </div>
                <div class="row tournament_info_line">
                  <b-table class="col-12" striped hover outlined small responsive caption-top :items="leaderboard" :fields="fields">
                    <template v-slot:table-caption><b>Leaderboard</b></template>
                  </b-table>
                </div>
                <div v-if="is_webadmin" class="row tournament_info_line">
                    <div class="col-12"><b>Management:</b></div>
                </div>
                <div v-if="is_webadmin" class="row tournament_webadmin tournament_info_line">
                    <div class="col-sm-4"><button :disabled="processing || !is_superadmin" type="button" class="col-12 m-1 btn btn-info" @click="update()">Update</button></div>
                    <div class="col-sm-4"><button :disabled="processing || !is_superadmin" type="button" class="col-12 m-1 btn btn-primary" @click="start()">Start</button></div>
                    <div class="col-sm-4">
                        <button v-if="prize_menu" :disabled="processing" type="button" class="col-12 m-1 btn btn-danger" @click="award_and_stop()">Award & Stop</button>
                        <button v-else :disabled="processing" type="button" class="col-12 m-1 btn btn-success" @click="reset_prizes()">Set Prizes</button>
                    </div>
                </div>
                <div v-if="is_webadmin && prize_menu" class="row">
                    <h5 class="col-12 col-sm-4 col-md-8 p-2">Prizes:</h5>
                    <div class="col-6 col-sm-4 col-md-2 text-right">
                        <button class="col-12 m-1 btn btn-sm btn-warning" @click="reset_prizes()">reset</button>
                    </div>
                    <div class="col-6 col-sm-4 col-md-2 text-right">
                        <button class="col-12 m-1 btn btn-sm btn-success" @click="add_prize()">add</button>
                    </div>
                    <template v-for="(prize,index) in prizes">
                        <div class="col-md-3" :key="'prize_coach' + index">
                            <div class="form-group">
                                <select class="form-control" v-model="prize.coach" v-bind:class="{'is-invalid': prize.coach==''}">
                                    <option selected disabled value="">Coach:</option>
                                    <option v-for="coach in signed_coaches" :value="coach.id" :key="coach.id">{{ coach.short_name }}</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-2" :key="'prize_amount' + index">
                            <div class="form-group">
                                <input class="form-control" type="number" placeholder="Cash" v-model="prize.amount" >
                            </div>
                        </div>
                        <div class="col-md-5" :key="'prize_reason' + index">
                            <div class="form-group">
                                <input type="text" class="form-control" placeholder="Reason" v-model="prize.reason" v-bind:class="{'is-invalid': prize.reason==''}">
                            </div>
                        </div>
                        <div class="col-md-2 text-right" :key="'prize_button' + index">
                        <button class="btn m-1 btn-sm btn-danger" @click="remove_prize(index)">remove</button>
                        </div>
                    </template>
                </div>
            </div>
        </div>
        <!--
        <deck v-if="show_deck" :coach="selected.coach" :tournament="tournament" :deck_id="selected.deck_id" :is_owner="is_owner(selected.coach)"></deck>
        -->
        <deck v-if="show_deck" :coach="selected.coach" :tournament="tournament" :deck_id="selected.deck_id" :is_owner="is_owner(selected.coach)"></deck>
    </div>
</template>
<script>
import { mapGetters, mapMutations } from 'vuex';
// import deck from './deck.vue';
import deck from './deck.vue';
import confirmationButton from './confirmation-button.vue';
import Cards from '../mixins/cards';

export default {
  name: 'tournament',
  mixins: [Cards],
  components: {
    deck: deck,
    // 'deck': deck,
    'confirmation-button': confirmationButton,
  },
  data() {
    return {
      processing: false,
      prize_menu: false,
      prizes: [],
      selected: {
        coach: {},
        deck_id: null,
        phase: 'deck_building',
      },
      leaderboard: [],
      show_deck: false,
      phases: [
        { name: 'deck_building', desc: 'Deck Building' },
        { name: 'locked', desc: 'Locked' },
        { name: 'special_play', desc: 'Special Play' },
        { name: 'inducement', desc: 'Inducement' },
        { name: 'blood_bowl', desc: 'Blood Bowl' },
      ],
      fields: [
        { key: 'name', stickyColumn: true },
        { key: 'matches', sortable: true, formatter: 'nonZero' },
        { key: 'points', sortable: true, formatter: 'nonZero' },
        { key: 'wins', sortable: true, formatter: 'nonZero' },
        { key: 'draws', sortable: true, formatter: 'nonZero' },
        { key: 'losses', sortable: true, formatter: 'nonZero' },
        {
          key: 'inflictedtouchdowns', label: 'TD⁺', sortable: true, formatter: 'nonZero',
        },
        {
          key: 'sustainedtouchdowns', label: 'TD⁻', sortable: true, formatter: 'nonZero',
        },
        {
          key: 'inflictedtackles', label: 'Blocks⁺', sortable: true, formatter: 'nonZero',
        },
        {
          key: 'sustainedtackles', label: 'Blocks⁻', sortable: true, formatter: 'nonZero',
        },
        {
          key: 'inflictedinjuries', label: 'AB⁺', sortable: true, formatter: 'nonZero',
        },
        {
          key: 'sustainedinjuries', label: 'AB⁻', sortable: true, formatter: 'nonZero',
        },
        {
          key: 'opponentinflictedinjuries', label: 'ABᵒ', headerTitle: 'Armor Breaks by opponent', sortable: true, formatter: 'nonZero',
        },
        {
          key: 'inflictedko', label: 'KO⁺', sortable: true, formatter: 'nonZero',
        },
        {
          key: 'sustainedko', label: 'KO⁻', sortable: true, formatter: 'nonZero',
        },
        {
          key: 'opponentinflictedko', label: 'KOᵒ', headerTitle: 'KOs by opponent', sortable: true, formatter: 'nonZero',
        },
        {
          key: 'inflictedcasualties', label: 'CAS⁺', sortable: true, formatter: 'nonZero',
        },
        {
          key: 'sustainedcasualties', label: 'CAS⁻', sortable: true, formatter: 'nonZero',
        },
        {
          key: 'opponentinflictedcasualties', label: 'CASᵒ', headerTitle: 'Casualties by opponent', sortable: true, formatter: 'nonZero',
        },
        {
          key: 'inflicteddead', label: 'Dead⁺', sortable: true, formatter: 'nonZero',
        },
        {
          key: 'sustaineddead', label: 'Dead⁻', sortable: true, formatter: 'nonZero',
        },
        {
          key: 'opponentinflicteddead', label: 'Deadᵒ', headerTitle: 'Deaths by opponent', sortable: true, formatter: 'nonZero',
        },
        {
          key: 'inflictedpasses', label: 'Pass', sortable: true, formatter: 'nonZero',
        },
        {
          key: 'inflictedmeterspassing', label: 'Pass[m]', sortable: true, formatter: 'nonZero',
        },
        {
          key: 'inflictedmetersrunning', label: 'Run[m]', sortable: true, formatter: 'nonZero',
        },
        {
          key: 'inflictedpushouts', label: 'Surfs', sortable: true, formatter: 'nonZero',
        },
        {
          key: 'inflictedinterceptions', label: 'Int.', headerTitle: 'Interceptions', sortable: true, formatter: 'nonZero',
        },
        {
          key: 'sustainedexpulsions', label: 'Exp.', headerTitle: 'Expulsions', sortable: true, formatter: 'nonZero',
        },
      ],
    };
  },
  props: ['tournament', 'coaches', 'data-parent', 'user'],
  methods: {
    nonZero(value) {
      if (value) {
        return value;
      }
      return 0;
    },
    getProperty: function (name) {
      return this[name];
    },
    setprizes() {
      this.prize_menu = true;
      this.call('cards');
      while (this.prizes.length < this.tournament.coach_limit) {
        // test for 1st: X pattern
        let reg = new RegExp(`(${(this.prizes.length + 1)}\\S+):(\\s+\\d+)`, 'g');
        let matches = reg.exec(this.tournament.prizes);
        let prize = (matches !== null ? matches[2].trim() : 0);
        let reason = (matches !== null ? matches[1].trim() : 0);
        if (prize === 0) {
          // test for imperium pattern
          switch (this.prizes.length) {
            case 0:
              reason = 'Winner';
              break;
            case 1:
              reason = 'Runner-Up';
              break;
            case 2:
            case 3:
              reason = 'Semi-Final';
              break;
            case 4:
            case 5:
            case 6:
            case 7:
              reason = 'Quarter-Final';
              break;
            default:
              reason = '';
          }
          reg = new RegExp(`${reason}:(\\s+\\d+)`, 'g');
          matches = reg.exec(this.tournament.prizes);
          prize = (matches !== null ? matches[1].trim() : 0);
        }
        let coach;
        if (this.leaderboard.length > this.prizes.length) {
          coach = this.coaches.find((c) => c.bb2_name === this.leaderboard[this.prizes.length].name);
        }
        this.add_prize({
          coach: coach ? coach.id : '',
          amount: prize,
          reason: `${this.tournament.type} ${this.tournament.mode} ${reason}`,
        });
      }

      // sponsors
      if (this.tournament.sponsor !== 'None' && this.tournament.sponsor !== '') {
        this.add_prize({ coach: '', amount: 20, reason: `${this.tournament.sponsor} Bonus 1st` });
        this.add_prize({ coach: '', amount: 15, reason: `${this.tournament.sponsor} Bonus 2nd` });
        this.add_prize({ coach: '', amount: 10, reason: `${this.tournament.sponsor} Bonus 3rd` });
        this.add_prize({ coach: '', amount: 5, reason: `${this.tournament.sponsor} Bonus 4th` });
      }
    },
    add_prize(prize = { coach: '', amount: 0, reason: '' }) {
      this.prizes.push(prize);
    },
    remove_prize(idx) {
      this.prizes.splice(idx, 1);
    },
    reset_prizes() {
      this.prizes = [];
      this.setprizes();
    },
    check_prizes() {
      for (let i = 0; i < this.prizes.length; i += 1) {
        if (this.prizes[i].coach === '') {
          this.flash('Coach not selected', 'error', { timeout: 3000 });
          return false;
        }
        if (this.prizes[i].reason === '') {
          this.flash('Reason not specified', 'error', { timeout: 3000 });
          return false;
        }
      }
      return true;
    },
    load_leaderboard() {
      const path = `/tournaments/${this.tournament.id}/leaderboard`;
      this.axios.get(path)
        .then((res) => {
          this.leaderboard = res.data;
        })
        .catch((error) => {
          if (error.response) {
            this.flash(error.response.data.message, 'error', { timeout: 3000 });
          } else {
            console.error(error);
          }
        });
    },
    award_and_stop() {
      if (this.check_prizes()) {
        this.processing = true;
        const path = `/tournaments/${this.tournament.id}/close`;
        const processingMsg = this.flash('Processing...', 'info');
        this.axios.post(path, this.prizes)
          .then((res) => {
            const msg = 'Prizes awarded and tournament stopped';
            this.flash(msg, 'success', { timeout: 3000 });
            this.prizes = [];
            this.prize_menu = false;
            this.updateTournament(res.data);
          })
          .catch((error) => {
            if (error.response) {
              this.flash(error.response.data.message, 'error', { timeout: 3000 });
            } else {
              console.error(error);
            }
          })
          .then(() => {
            processingMsg.destroy();
            this.processing = false;
          });
      }
    },
    set_phase() {
      this.processing = true;
      const path = `/tournaments/${this.tournament.id}/set_phase`;
      const processingMsg = this.flash('Processing...', 'info');
      this.axios.post(path, { phase: this.selected.phase })
        .then((res) => {
          const msg = 'Phase updated!';
          this.flash(msg, 'success', { timeout: 3000 });
          this.updateTournament(res.data);
        })
        .catch((error) => {
          if (error.response) {
            this.flash(error.response.data.message, 'error', { timeout: 3000 });
          } else {
            console.error(error);
          }
        })
        .then(() => {
          processingMsg.destroy();
          this.processing = false;
        });
    },
    start() {
      this.call('start');
    },
    cards() {
      this.call('cards');
    },
    sign() {
      this.call('sign');
    },
    resign() {
      this.call('resign');
    },
    update() {
      this.call('update');
    },
    get() {
      this.call('get');
    },
    call(method) {
      let path;
      let updatingMsg;
      if (method === 'update') {
        path = `/tournaments/${method}`;
        updatingMsg = this.flash('Updating...', 'info');
      } else if (method === 'get') {
        path = `/tournaments/${this.tournament.id}`;
      } else {
        path = `/tournaments/${this.tournament.id}/${method}`;
      }
      let msg;
      let displayFlash = true;
      this.processing = true;
      this.axios.get(path)
        .then((res) => {
          if (method === 'sign') {
            msg = `Signup to ${this.tournament.name} succeded`;
          } else if (method === 'resign') {
            msg = `Resignation from ${this.tournament.name} succeded`;
          } else if (method === 'start') {
            msg = `Start of ${this.tournament.name} initiated. Check discord!`;
          } else if (method === 'update') {
            msg = 'Tournaments updated';
          } else if (method === 'get' || method === 'cards') {
            displayFlash = false;
          }
          if (displayFlash) {
            this.flash(msg, 'success', { timeout: 3000 });
          }
          if (this.tournament.fee > 0 && ['sign', 'resign'].includes(method)) {
            if (method === 'sign') {
              msg = `Charged registration fee ${this.tournament.fee} coins`;
            } else if (method === 'resign') {
              msg = `Refunded registration fee ${this.tournament.fee} coins`;
            }
            this.flash(msg, 'info', { timeout: 3000 });
          }
          if (['sign', 'resign', 'get', 'start'].includes(method)) {
            this.updateTournament(res.data);
          } else if (method === 'update') {
            this.storeTournaments(res.data);
          } else if (method === 'cards') {
            res.data.forEach((card) => {
              if (this.has_keyword(card, 'Payout')) {
                this.add_prize({
                  coach: card.coach_data.id,
                  amount: this.payout(card),
                  reason: card.template.name,
                });
              }
            });
          }
        })
        .catch((error) => {
          if (error.response) {
            this.flash(error.response.data.message, 'error', { timeout: 3000 });
          } else {
            console.error(error);
          }
        })
        .then(() => {
          this.processing = false;
          if (typeof updatingMsg !== 'undefined') {
            updatingMsg.destroy();
          }
        });
    },
    showDeck(coach) {
      const signup = this.tournament.tournament_signups.find((ts) => ts.coach === coach.id);
      this.selected.deck_id = signup.deck;
      // this is workaround if we user is openign their own deck, use the user collection instead of coach array
      if (this.user.coach.id === coach.id) {
        this.selected.coach = this.user.coach;
      } else {
        this.selected.coach = coach;
      }
      this.show_deck = true;
    },
    payout(card) {
      const stats = this.leaderboard.find((e) => e.name === card.coach_data.bb2_name);
      if (stats === undefined) {
        return 0;
      }
      if (card.template.name === 'Cash Incorporated') {
        return (stats.inflictedcasualties - stats.inflicteddead) * 2 + (stats.inflicteddead * 5);
      }
      if (card.template.name === 'Fruity Kisses Machine') {
        return (stats.inflictedpasses) * 1 + (stats.inflictedinterceptions * 5);
      }
      if (card.template.name === 'Pleasing the Sponsors') {
        return 20;
      }
      if (card.template.name === 'For Whom The Bell Tolls') {
        return (stats.inflictedko) * 2;
      }
      if (card.template.name === 'Strife Insurance') {
        return (stats.opponentinflictedcasualties - stats.opponentinflicteddead) * 2 + (stats.opponentinflicteddead * 5);
      }
      if (card.template.name === 'Junior Investment Banker') {
        return 5;
      }
      if (card.template.name === 'Senior Investment Banker') {
        return 10;
      }
      if (card.template.name === 'Investment Partner') {
        return 15;
      }
      if (card.template.name === 'CabalVision Executive') {
        return 20;
      }
      if (card.template.name === 'Cheere Khan') {
        return 15;
      }
      if (card.template.name === 'Sam Allyerdice') {
        return 15;
      }
      return 0;
    },
    ...mapMutations([
      'updateTournament', 'storeTournaments',
    ]),
  },
  computed: {
    selected_phase() {
      return this.selected.phase;
    },
    signed() {
      return this.tournament.tournament_signups.filter((e) => e.mode === 'active');
    },
    reserved() {
      return this.tournament.tournament_signups.filter((e) => e.mode !== 'active');
    },
    signed_ids() {
      return this.signed.map((e) => e.coach);
    },
    reserved_ids() {
      return this.reserved.map((e) => e.coach);
    },
    signed_coaches() {
      return this.coaches.filter((e) => this.signed_ids.includes(e.id));
    },
    reserved_coaches() {
      return this.coaches.filter((e) => this.reserved_ids.includes(e.id));
    },
    signed_coaches_names() {
      return this.signed_coaches.map((e) => e.short_name);
    },
    reserved_coaches_names() {
      return this.reserved_coaches.map((e) => e.short_name);
    },
    is_user_signed() {
      if (this.user.username && (this.signed_coaches_names.concat(this.reserved_coaches_names)).includes(this.user.username)) {
        return true;
      }
      return false;
    },
    loggedCoach() {
      if (this.user.id) {
        const coach = this.coaches.find((e) => e.id === this.user.coach.id);
        return coach;
      }
      return undefined;
    },
    is_tournament_admin() {
      if (this.loggedCoach && this.loggedCoach.short_name === this.tournament.admin) {
        return true;
      }
      return false;
    },
    phase() {
      const found = this.phases.find((p) => p.name === this.tournament.phase);
      if (found) {
        return found;
      }
      return this.phases[0];
    },
    show_date() {
      if (this.tournament.status === 'OPEN') {
        return `(${this.tournament.expected_start_date})`;
      }
      if (this.tournament.status === 'RUNNING') {
        return `(${this.tournament.deadline_date})`;
      }
      return '';
    },
    is_full() {
      const active = this.tournament.coach_limit === this.tournament.tournament_signups.filter((e) => e.mode === 'active').length;
      const reserve = this.tournament.reserve_limit === this.tournament.tournament_signups.filter((e) => e.mode !== 'active').length;
      return active && reserve;
    },
    is_running() {
      return this.tournament.status !== 'OPEN';
    },
    ...mapGetters([
      'loggedCoach', 'is_webadmin', 'is_owner', 'is_superadmin',
    ]),
  },
  mounted() {
    this.$on('deckClosed', () => { this.show_deck = false; });
    this.$on('reloadTournament', this.get);
    this.selected.phase = this.tournament.phase;
  },
};
</script>
