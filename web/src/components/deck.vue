<template>
  <div class="modal fade deck" :id="'deck'+id" tabindex="-1" role="dialog" aria-labelledby="deck" aria-hidden="true">
    <div class="modal-dialog modal-xl">
      <div class="modal-content">
        <div class="modal-header deck_header">
          <h5 class="modal-title">Deck for {{coach.short_name}} in {{tournament.name}} - Phase: {{ phases[tournament.phase] }}
            <template v-if="doneable_phase">
              <button v-if="deck.phase_done" type="button" disabled class="btn btn-success">Done</button>
              <button v-if="!deck.phase_done && is_owner" type="button" class="btn btn-danger" @click="phaseDone()">Done</button>
            </template>
            <template>
              <button type="button" :disabled="processing" class="btn btn-danger" v-if="is_owner && !deck.commited && !locked" @click="reset()">Reset</button>
              <button type="button" disabled class="btn btn-success" v-if="deck.commited && !locked">Committed</button>
              <button type="button" disabled class="btn btn-info" v-if="locked">Locked</button>
              <button type="button" disabled class="btn btn-info" v-if="!started">Not Started</button>
            </template>
          </h5>
          <button type="button" :disabled="processing" class="btn btn-danger" v-if="is_owner && !deck.commited && !locked && started" @click="commit()">Commit</button>
          <button type="button" class="close" data-dismiss="modal" aria-label="Close">
              <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="row">
            <div class="col-12">
              <h6 class="d-inline-block">Team:</h6>
              <button v-if="deck.team_name" class="mb-2 ml-3 btn btn-sm btn-info" @click="getTeam(deck.team_name)">Load Team</button>
            </div>
            <div class="form-group col-lg-6">
              <select class="form-control" v-model="selected_team" :disabled="deck_player_size>0 || !is_owner || locked">
                <option selected value="All">Select team</option>
                <option v-for="team in mixed_teams" :value="team.name" :key="team.code">{{ team.name }} ({{ team.races.join() }})</option>
              </select>
            </div>
            <div class="form-group col-lg-6">
              <input type="text" :disabled="!is_owner || locked" class="form-control" placeholder="Team Name (max 25 characters)" maxlength="25" v-bind:value="deck.team_name" v-on:input="debounceUpdateName($event.target.value)">
            </div>
          </div>
          <div class="row">
            <div :id="'teamInfoAccordion'+id" class="col-12 mb-3 mt-3" v-if="'coach' in team">
              <div class="card">
                <div class="card-header" :id="'teamInfo'+id">
                  <h6 class="mb-0">
                    <button class="btn btn-link" data-toggle="collapse" :data-target="'#collapseTeamInfo'+id" aria-expanded="true" aria-controls="collapseTeamInfo">
                    BB2 Team Details
                    </button>
                  </h6>
                </div>
                <div :id="'collapseTeamInfo'+id" class="collapse hide" aria-labelledby="teamInfo'" :data-parent="'#teamInfoAccordion'+id">
                  <div class="card-body table-responsive">
                    <div class="row">
                      <div class="col-sm-4"><b>Team:</b> {{team.team.name}}</div>
                      <div class="col-sm-4"><b>Race:</b> {{race(team.team.idraces)}}</div>
                      <div class="col-sm-4"><b>Coach:</b> {{team.coach.name}}</div>
                      <div class="col-sm-4"><b>TV:</b> {{team.team.value}}</div>
                      <div class="col-sm-4">
                      <b>Apothecary:</b> {{ team.team.apothecary ? "Yes" : "No"}}
                        <span v-if="team_check.apothecary.value" class="deck_valid_check">✓</span>
                        <span :title="team_check.apothecary.msg" v-else class="deck_invalid_check">✗</span>
                      </div>
                      <div class="col-sm-4"><b>Rerolls:</b> {{team.team.rerolls}}
                        <span v-if="team_check.rerolls.value" class="deck_valid_check">✓</span>
                        <span :title="team_check.rerolls.msg" v-else class="deck_invalid_check">✗</span>
                      </div>
                      <div class="col-sm-4"><b>Assistant Coaches:</b> {{team.team.assistantcoaches}}</div>
                      <div class="col-sm-4"><b>Cheerleaders:</b> {{team.team.cheerleaders}}</div>
                      <div class="col-sm-4"><b>Stadium Enhancement:</b> {{stadium_enhacement(team.team)}}</div>
                      <div class="col-sm-4"><b>Cash:</b> {{team.team.cash}}</div>
                    </div>
                    <h6 class="mt-2">Roster size:
                      <span v-if="team_check.roster.value" class="deck_valid_check">✓</span>
                      <span :title="team_check.roster.msg" v-else class="deck_invalid_check">✗</span>
                    </h6>
                    <div class="row">
                      <table class="table  table-striped table-hover">
                        <thead>
                          <tr>
                            <th>N.</th>
                            <th>Lvl.</th>
                            <th>SPP</th>
                            <th>TV</th>
                            <th>Name</th>
                            <th>Position</th>
                            <th>Skills</th>
                            <th>Injuries</th>
                            <th>Valid</th>
                          </tr>
                        </thead>
                        <tbody>
                        <tr v-for="player in sorted_roster" :key="player.id">
                          <td>{{player.number}}</td>
                          <td>{{player.level}}</td>
                          <td>{{player.xp}}</td>
                          <td>{{player.value}}</td>
                          <td>{{player.name}}</td>
                          <td>{{positional_from_api(player.type)}}</td>
                          <td><span v-html="player.skills.map((s) => imgs_for_skill(s)).join('')"></span></td>
                          <td><span v-html="player.casualties_state.map((c) => imgs_for_skill(c)).join('')"></span></td>
                          <td>
                            <span v-if="valid(player)" class="deck_valid_check">✓</span>
                            <span v-else class="deck_invalid_check">✗</span>
                          </td>
                        </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="row mb-3">
            <div class="col-12">
            <h6>Sponsor: {{tournament.sponsor}}</h6>
            </div>
            <div class="col-12">
            {{tournament.sponsor_description}}
            </div>
            <div class="col-12">
            {{tournament.special_rules}}
            </div>
            <div class="col-12" v-if="tournament.banned_cards!=''">
            <h6>Banned Cards: {{tournament.banned_cards.replace(';', ', ')}}</h6>
            </div>
          </div>
          <div class="row mb-3">
            <div class="col-12">
            <h6>Comment:</h6>
            </div>
            <div class="col-12">
              <b-form-textarea rows="3" max-rows="8" class="p-2" :plaintext="!is_owner || locked" placeholder="Provide deck comments here" :value="deck.comment" @update="debounceUpdateComment($event)"></b-form-textarea>
            </div>
          </div>
          <div class="row">
            <div :id="'extraCardsAccordion'+id" class="col-12 mb-3 mt-3">
              <div class="card" v-if="is_owner">
                <div class="card-header" :id="'extraCards'+id">
                  <h6 class="mb-0">
                    <button class="btn btn-link" data-toggle="collapse" :data-target="'#collapseExtraCards'+id" aria-expanded="true" aria-controls="collapseExtraCards">
                      <span data-toggle="tooltip" data-placement="top" title="Use this to add extra cards to the collection for this tournament only">Sponsor & Extra Cards</span>
                    </button>
                  </h6>
                </div>
                <div :id="'collapseExtraCards'+id" class="collapse hide" aria-labelledby="extraCards'" :data-parent="'#extraCardsAccordion'+id">
                  <div class="card-body">
                    <div class="row">
                      <div class="col-md-6">
                        <input type="text" :disabled="!is_owner || locked" class="d-inline  form-control" :placeholder="extra_card_placeholder" v-model="extra_card">
                      </div>
                      <div class="col-md-6">
                        <button type="button" :disabled="processing || !is_owner || locked" class="btn-sm btn btn-success btn-block mb-1" @click="addExtraCard(extra_card)">Add</button>
                      </div>
                      <template v-for="card in deck.unused_extra_cards">
                        <div class="col-md-6 pt-1 pl-4" :key="'name' + card_id_or_uuid(card)">
                        <h6 class="extra_card">{{card.template.name}}</h6>
                        </div>
                        <div class="col-md-3" :key="'clone' + card_id_or_uuid(card)">
                          <button type="button" :disabled="processing || !is_owner || locked" class="btn-sm mb-1 btn btn-success btn-block" @click="cloneExtraCard(card)">Clone</button>
                        </div>
                        <div class="col-md-3" :key="'remove' + card_id_or_uuid(card)">
                          <button type="button" :disabled="processing || !is_owner || locked" class="btn-sm mb-1 btn btn-danger btn-block" @click="removeExtraCard(card)">Remove</button>
                        </div>
                      </template>
                    </div>
                  </div>
                </div>
              </div>
              <div class="card">
                <div class="card-header" :id="'log'+id">
                  <h6 class="mb-0">
                    <button class="btn btn-link" data-toggle="collapse" :data-target="'#collapselog'+id" aria-expanded="true" aria-controls="collapselog">
                      Deck Log
                    </button>
                  </h6>
                </div>
                <div :id="'collapselog'+id" class="collapse hide" aria-labelledby="log'" :data-parent="'#extraCardsAccordion'+id">
                  <div class="card-body">
                    <div class="row">
                      <template v-for="(line, index) in deck.log.split(/\r?\n/).reverse().slice(1)">
                        {{line}} <br :key="index" />
                      </template>
                    </div>
                  </div>
                </div>
              </div>
              <div v-if="has_deck_upgrade" class="card">
                <div class="card-header" :id="'deck_upgrade'+id">
                  <h6 class="mb-0">
                    <button class="btn btn-link" data-toggle="collapse" :data-target="'#collapsedeckupgrade'+id" aria-expanded="true" aria-controls="collapsedeckupgrade">
                      Deck Upgrade
                    </button>
                  </h6>
                </div>
                <div v-if="has_deck_upgrade" :id="'collapsedeckupgrade'+id" class="collapse show" aria-labelledby="log'" :data-parent="'#extraCardsAccordion'+id">
                  <div class="card-body deck_upgrade">
                    <div class="row" v-for="card in deck_upgrades" :key="card.id">
                      <div class="col-md-3">
                        <b>{{card.template.name}}:</b>
                      </div>
                      <div class="col-md-9">
                        <span v-html="markdown.makeHtml(card.template.description)"></span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="row">
            <div v-if="canEdit" class="col-lg-6">
              <div class="row mt-1 deck_header">
                <div class="col-6">
                  <h6>Collection</h6>
                </div>
                <div class="col-6">
                  <div class="custom-control custom-checkbox mr-sm-2 text-right">
                    <input type="checkbox" class="custom-control-input" :id="'sptoggle'+id" v-model="starter">
                    <label class="custom-control-label" :for="'sptoggle'+id">Toggle Starter Pack</label>
                  </div>
                </div>
              </div>
              <card-list id="accordionCardsCollection" :cards="collection_cards" :selected_team="selected_team" :owner="coach"
                  :starter="starter" :quantity="false" :type_list="deck_card_types" :column_list="collection_colums"
                  @card-click="addToDeck"></card-list>
            </div>
            <div :class="cardListClass">
              <div class="row mt-1 deck_header">
                <div class="col-3">
                  <h6>Deck {{deck_size}}/{{tournament.deck_limit}}</h6>
                </div>
                <div class="col-3 text-center">
                  <h6>Value: {{ deck_value }}/{{ tournament.deck_value_limit }}</h6>
                </div>
                <div class="col-3 text-center">
                   <h6>Doubles: {{ deck_doubles_count }}</h6>
                </div>
                <div class="col-3">
                  <div class="custom-control custom-checkbox mr-sm-2 text-right">
                    <input type="checkbox" class="custom-control-input" :id="'raritytoggle'+id" v-model="rarity_order">
                    <label class="custom-control-label" :for="'raritytoggle'+id">Rarity order</label>
                  </div>
                </div>
              </div>
              <card-list id="accordionCardsDeck" :cards="deck_cards" :selected_team="selected_team" :owner="coach"
                  :starter="starter" :quantity="false" :type_list="deck_card_types" :column_list="collection_colums"
                  @card-click="removeFromDeck" @card-assign="assignCard" :rarity_sort="rarity_order" :deck="deck" :edit="canEdit"
                  @update-deck="updateDeck" @card-disable="disableCard" @card-enable="enableCard" @card-unskill="unskillCard" ></card-list>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import Cards from '@/mixins/cards';
import cardList from '@/components/card_list.vue';

export default {
  name: 'deck',
  mixins: [Cards],
  components: {
    cardList,
  },
  data() {
    return {
      processing: false,
      selected_team: 'All',
      starter: true,
      rarity_order: true,
      extra_card: '',
      deck: {
        cards: [],
        extra_cards: [],
        unused_extra_cards: [],
        deck_upgrade_cards: [],
        mixed_team: '',
        team_name: '',
        comment: '',
        search_timeout: null,
        id: null,
        log: '',
      },
      team: {},
      team_check: {
        apothecary: {
          msg: 'OK',
          value: true,
        },
        rerolls: {
          msg: 'OK',
          value: true,
        },
        roster: {
          msg: 'OK',
          value: true,
        },
      },
      phases: {
        deck_building: 'Deck Building',
        locked: 'Locked',
        special_play: 'Special Play',
        inducement: 'Inducement',
        blood_bowl: 'Blood Bowl',
      },
      deck_card_types: ['Player', 'Training', 'Special Play', 'Staff'],
      collection_colums: ['Rarity', 'Value', 'Name', 'Skills', 'ShortSubtype'],
    };
  },
  methods: {
    canAddToDeck(card) {
      if (!this.is_owner) {
        return false;
      }
      if (this.locked) {
        this.flash('Deck is locked!', 'info', { timeout: 3000 });
        return false;
      }
      if (this.processing === true) {
        return false;
      }

      if (card.duster) {
        this.flash('Cannot add card - card is flagged for dusting!', 'error', { timeout: 3000 });
        return false;
      }

      // check limits if not added by extra cards interface
      if ((card.deck_type !== 'extra' && card.deck_type !== 'extra_inducement')) {
        // ignore first SP card
        if (card.template.card_type !== 'Special Play' || this.user_special_plays.length !== 0) {
          if (this.deck_size === this.tournament.deck_limit) {
            this.flash('Cannot add card - deck limit reached!', 'error', { timeout: 3000 });
            return false;
          }
        }
        if (this.deck_value + card.template.value > this.tournament.deck_value_limit) {
          this.flash('Cannot add card - deck value limit reached!', 'error', { timeout: 3000 });
          return false;
        }
      }

      if (this.selected_team === 'All') {
        this.flash('Cannot add card - team not selected!', 'error', { timeout: 3000 });
        return false;
      }
      if (this.deck_player_size >= 16 && card.template.card_type === 'Player') {
        this.flash('Cannot add card - 16 Player cards are already in the deck!', 'error', { timeout: 3000 });
        return false;
      }
      return true;
    },
    addToDeck(card) {
      if (!this.canAddToDeck(card)) {
        return;
      }
      this.addCard(card);
    },
    removeFromDeck(card) {
      if (!this.isEditable()) {
        return;
      }
      this.removeCard(card);
    },
    async_error(error) {
      if (error.response) {
        const message = (error.response.data.message) ? error.response.data.message : `Unknown error: ${error.response.status}`;
        this.flash(message, 'error', { timeout: 3000 });
      } else {
        console.error(error);
      }
    },
    getDeck() {
      const path = `/decks/${this.deck_id}`;
      const processingMsg = this.flash('Loading deck...', 'info');
      this.axios.get(path)
        .then((res) => {
          this.deck = res.data;
          this.selected_team = (this.deck.mixed_team === '') ? 'All' : this.deck.mixed_team;
          this.modal().modal('show');
        })
        .catch(this.async_error)
        .then(() => {
          processingMsg.destroy();
        });
    },
    getTeam(name) {
      const path = `/teams/${encodeURIComponent(name)}`;
      const processingMsg = this.flash('Loading team...', 'info');
      this.axios.get(path)
        .then((res) => {
          if (res.data === false) {
            this.flash(`Team ${name} does not exist`, 'error', { timeout: 3000 });
          } else {
            this.team = res.data;
            this.checkTeam();
          }
        })
        .catch(this.async_error)
        .then(() => {
          processingMsg.destroy();
        });
    },
    resetTeamCheck() {
      this.team_check = {
        apothecary: {
          msg: 'OK',
          value: true,
        },
        rerolls: {
          msg: 'OK',
          value: true,
        },
        roster: {
          msg: 'OK',
          value: true,
        },
      };
    },
    checkApo() {
      if (this.team.team.apothecary !== this.hasApo()) {
        this.team_check.apothecary.value = false;
        if (this.team.team.apothecary) {
          this.team_check.apothecary.msg = 'Apothecary should not be included';
        } else {
          this.team_check.apothecary.msg = 'Apothecary is missing';
        }
      }
    },
    checkRRs() {
      if (this.team.team.rerolls !== this.numberOfRerolls()) {
        this.team_check.rerolls.value = false;
        this.team_check.rerolls.msg = 'Number of RRs do not match';
      }
    },
    checkRoster() {
      // roster size
      if (this.team.roster.length !== this.deck_cards.filter((c) => c.template.card_type === 'Player' && this.isEnabled(c)).length) {
        this.team_check.roster.value = false;
        this.team_check.roster.msg = 'Number of players does not match';
      }
      const ignore = [];

      this.team.roster.forEach((player) => {
        player.check = {
          value: false,
          msg: 'Player not found',
        };
        this.deck_cards.forEach((c) => {
          // ignore disabled cards
          if (!this.isEnabled(c)) { return; }
          // if the cards has been linked with another -> skip
          if (ignore.includes(this.card_id_or_uuid(c))) { return; }
          // if the player is already valid -> skip
          if (player.check.value) { return; }
          // is not a player card -> skip
          if (c.template.card_type !== 'Player') { return; }
          // positional check
          if (!this.positional_mapping(c).includes(this.positional_from_api(player.type))) { return; }
          // skill check
          if (!this.equal_sets(this.skill_names_for_player_card(c).concat(this.assigned_skills(c)), player.skills)) { return; }
          // injury check
          if (!this.equal_sets(this.player_injuries(c), player.casualties_state)) { return; }

          // if we came this far the player is valid
          ignore.push(this.card_id_or_uuid(c));
          player.check = {
            value: true,
            msg: 'Player found',
          };
        });
      });
    },
    checkTeam() {
      this.resetTeamCheck();
      // apo
      this.checkApo();
      // RRs
      this.checkRRs();

      // roster
      this.checkRoster();
    },
    valid(player) {
      if (player.check.value) { return true; }
      return false;
    },
    equal_sets(set1, set2) {
      const BreakException = {};
      if (set1.length !== set2.length) { return false; }
      try {
        set1.forEach((i1) => {
          const count1 = set1.filter((e) => e === i1).length;
          const count2 = set2.filter((e) => e === i1).length;
          if (count1 !== count2) throw BreakException;
        });
      } catch (e) {
        if (e !== BreakException) throw e;
        return false;
      }
      return true;
    },
    positional_mapping(card) {
      const races = card.template.race.split('/');
      const positionals = races.map((race) => {
        race = race.replace(/\s/g, '');
        if (race === 'Bretonnian') {
          race = 'Bretonnia';
        }
        let { position } = card.template;
        position = position.replace(/\s/g, '');
        return `${race} ${position}`;
      });
      return positionals;
    },
    hasApo() {
      const race = this.race(this.team.team.idraces);
      // AU has no apo
      if (race === 'Afterlife United') {
        return 0;
      }
      if (this.deck_cards.find((c) => ['Apothecary', 'Clever Management', 'Inspirational Boss'].includes(c.template.name) && this.isEnabled(c)) !== undefined) {
        return 1;
      }
      return 0;
    },
    numberOfRerolls() {
      const race = this.race(this.team.team.idraces);
      let rrs = [2, 2, 1];
      if (race === 'Afterlife United') {
        rrs = [3, 2, 2];
      }
      const r1 = this.deck_cards.filter((c) => c.template.name === 'Inspirational Boss' && this.isEnabled(c)).length * rrs[0];
      const r2 = this.deck_cards.filter((c) => c.template.name === 'Motivational Speaker' && this.isEnabled(c)).length * rrs[1];
      const r3 = this.deck_cards.filter((c) => c.template.name === 'Clever Management' && this.isEnabled(c)).length * rrs[2];
      return this.deck_cards.filter((c) => c.template.name === 'Re-roll' && this.isEnabled(c)).length + r1 + r2 + r3;
    },
    cloneExtraCard(card) {
      this.addExtraCard(card.template.name);
    },
    isEditable() {
      if (!this.is_owner) {
        return false;
      }
      if (this.locked) {
        this.flash('Deck is locked!', 'info', { timeout: 3000 });
        return false;
      }
      return true;
    },
    addExtraCard(name) {
      if (!this.isEditable()) {
        return;
      }
      const path = `/decks/${this.deck_id}/addcard/extra`;
      this.processing = true;
      const processingMsg = this.flash('Processing...', 'info');
      this.axios.post(path, { name: name })
        .then((res) => {
          const msg = 'Extra card added!';
          this.flash(msg, 'success', { timeout: 1000 });
          this.deck = res.data;
          this.extra_card = '';
        })
        .catch(this.async_error)
        .then(() => {
          processingMsg.destroy();
          this.processing = false;
        });
    },
    removeExtraCard(card) {
      if (!this.isEditable()) {
        return;
      }
      const path = `/decks/${this.deck_id}/removecard/extra`;
      this.processing = true;
      const processingMsg = this.flash('Processing...', 'info');
      this.axios.post(path, card)
        .then((res) => {
          const msg = 'Extra card removed!';
          this.flash(msg, 'success', { timeout: 1000 });
          this.deck = res.data;
          this.removeAllInjuries(card);
        })
        .catch(this.async_error)
        .then(() => {
          processingMsg.destroy();
          this.processing = false;
        });
    },
    deck_valid() {
      if (this.deck_player_size < 11) {
        this.flash('You need to include at least 11 player cards!', 'error', { timeout: 3000 });
        return false;
      }
      if (this.deck_size !== this.tournament.deck_limit) {
        this.flash(`You need to include ${this.tournament.deck_limit} cards!`, 'error', { timeout: 3000 });
        return false;
      }

      if (this.deck.team_name === '') {
        this.flash('Team name is not specified!', 'error', { timeout: 3000 });
        return false;
      }

      if (this.deck.mixed_team === 'All') {
        this.flash('Team mixed race is not specified!', 'error', { timeout: 3000 });
        return false;
      }

      const trainingCards = this.deck_cards.filter((e) => e.template.card_type === 'Training');
      const foundCard = trainingCards.find((c) => this.get_card_assignment(c).length === 0 || this.get_card_assignment(c).includes(undefined) || this.get_card_assignment(c).includes(null));
      if (foundCard !== undefined) {
        this.flash('Not all training cards are assigned to players!', 'error', { timeout: 3000 });
        return false;
      }
      return true;
    },
    commit() {
      if (!this.isEditable()) {
        return;
      }
      if (!this.deck_valid()) {
        return;
      }
      const path = `/decks/${this.deck_id}/commit`;
      this.processing = true;
      const processingMsg = this.flash('Processing...', 'info');
      this.axios.get(path)
        .then((res) => {
          const msg = 'Deck commited!';
          this.flash(msg, 'success', { timeout: 1000 });
          this.deck = res.data;
          this.$parent.$emit('reloadTournament');
        })
        .catch(this.async_error)
        .then(() => {
          processingMsg.destroy();
          this.processing = false;
        });
    },
    reset() {
      if (!this.isEditable()) {
        return;
      }
      const path = `/decks/${this.deck_id}/reset`;
      this.processing = true;
      const processingMsg = this.flash('Processing...', 'info');
      this.axios.get(path)
        .then((res) => {
          const msg = 'Deck reset!';
          this.flash(msg, 'success', { timeout: 1000 });
          this.deck.cards.forEach((card) => {
            this.clearCard(card);
          });
          this.deck = res.data;
        })
        .catch(this.async_error)
        .then(() => {
          processingMsg.destroy();
          this.processing = false;
        });
    },
    addCard(card) {
      const path = `/decks/${this.deck_id}/addcard`;
      this.processing = true;
      const processingMsg = this.flash('Processing...', 'info');
      this.axios.post(path, card)
        .then((res) => {
          const msg = 'Card added!';
          this.flash(msg, 'success', { timeout: 1000 });
          this.deck = res.data;
          const check = (this.development) ? 'in_development_deck' : 'in_imperium_deck';
          card[check] = true;
        })
        .catch(this.async_error)
        .then(() => {
          processingMsg.destroy();
          this.processing = false;
        });
    },

    assignCard(card, idx) {
      if (!this.isEditable()) {
        return;
      }
      const path = `/decks/${this.deck_id}/assign`;
      this.processing = true;
      const processingMsg = this.flash('Processing...', 'info');
      this.axios.post(path, card)
        .then((res) => {
          const msg = 'Card re-assigned!';
          this.flash(msg, 'success', { timeout: 1000 });
          this.deck = res.data;
        })
        .catch((error) => {
          this.$set(card.assigned_to_array[this.deck.id], idx, undefined);
          throw error;
        })
        .catch(this.async_error)
        .then(() => {
          processingMsg.destroy();
          this.processing = false;
        });
    },

    unskillCard(card) {
      if (!this.isEditable()) {
        return;
      }
      this.assigned_cards(card).forEach((c) => {
        const newAssignmentToArray = c.assigned_to_array[this.deck.id].filter((id) => String(id) !== this.card_id_or_uuid(card));
        c.assigned_to_array[this.deck.id] = newAssignmentToArray;
        this.assignCard(c);
      });

      if (card.assigned_to_array[this.deck.id].length !== 0) {
        card.assigned_to_array[this.deck.id] = [];
        this.assignCard(card);
      }
    },

    disableCard(card) {
      if (!this.isEditable()) {
        return;
      }
      const path = `/decks/${this.deck_id}/disable`;
      this.processing = true;
      const processingMsg = this.flash('Processing...', 'info');
      this.axios.post(path, card)
        .then((res) => {
          const msg = 'Card disabled!';
          this.flash(msg, 'success', { timeout: 1000 });
          this.deck = res.data;
          this.unskillCard(card);
        })
        .catch(this.async_error)
        .then(() => {
          processingMsg.destroy();
          this.processing = false;
        });
    },

    enableCard(card) {
      if (!this.isEditable()) {
        return;
      }
      const path = `/decks/${this.deck_id}/enable`;
      this.processing = true;
      const processingMsg = this.flash('Processing...', 'info');
      this.axios.post(path, card)
        .then((res) => {
          const msg = 'Card enabled!';
          this.flash(msg, 'success', { timeout: 1000 });
          this.deck = res.data;
        })
        .catch(this.async_error)
        .then(() => {
          processingMsg.destroy();
          this.processing = false;
        });
    },

    removeCard(card) {
      const path = `/decks/${this.deck_id}/remove`;
      this.processing = true;
      const processingMsg = this.flash('Processing...', 'info');
      this.axios.post(path, card)
        .then((res) => {
          const msg = 'Card removed!';
          this.flash(msg, 'success', { timeout: 1000 });
          this.deck = res.data;
          if (card.id && card.deck_type !== 'extra' && card.deck_type !== 'extra_inducement') {
            this.clearCard(card);
          }
          this.removeAllInjuries(card);
          this.unskillCard(card);
        })
        .catch(this.async_error)
        .then(() => {
          processingMsg.destroy();
          this.processing = false;
        });
    },
    phaseDone() {
      this.deck.phase_done = true;
      this.updateDeck();
    },
    clearCard(card) {
      const check = (this.development) ? 'in_development_deck' : 'in_imperium_deck';
      const ccard = this.coach.cards.find((c) => c.id === card.id);
      ccard[check] = false;
    },
    updateDeck() {
      if (!this.isEditable()) {
        return;
      }
      const path = `/decks/${this.deck_id}`;
      this.processing = true;
      // const processingMsg = this.flash("Processing...", 'info');
      const sendDeck = {
        team_name: this.deck.team_name,
        mixed_team: this.deck.mixed_team,
        comment: this.deck.comment,
        injury_map: this.deck.injury_map,
        phase_done: this.deck.phase_done,
      };
      this.axios.post(path, { deck: sendDeck })
        .then((res) => {
          // let msg = "Deck saved!";
          // this.flash(msg, 'success',{timeout: 3000});
          this.deck = res.data;
        })
        .catch(this.async_error)
        .then(() => {
          //    processingMsg.destroy();
          this.processing = false;
        });
    },
    debounceUpdateName(val) {
      if (this.search_timeout) clearTimeout(this.search_timeout);
      const that = this;
      this.search_timeout = setTimeout(() => {
        that.deck.team_name = val;
        that.updateDeck();
      }, 1000);
    },
    debounceUpdateComment(val) {
      if (this.search_timeout) clearTimeout(this.search_timeout);
      const that = this;
      this.search_timeout = setTimeout(() => {
        that.deck.comment = val;
        that.updateDeck();
      }, 1000);
    },
    modal() {
      return this.$(`#deck${this.id}`);
    },
    extra_type(type) {
      switch (type) {
        case 'base':
        case null:
          return '';
        default:
          return 'extra_card';
      }
    },
    deck_size_for(type) {
      return this.deck_cards.filter((e) => e.template.card_type === type && this.isEnabled(e)).length;
    },
    assigned_cards(card) {
      return this.deck_cards.filter((c) => this.get_card_assignment(c).includes(this.card_id_or_uuid(card)));
    },
    player_injuries(card) {
      return this.assigned_injuries(card).concat(this.injury_names_for_player_card(card));
    },
    assigned_injuries(card) {
      let injuries;
      if (this.deck.injury_map[this.card_id_or_uuid(card)]) {
        injuries = this.deck.injury_map[this.card_id_or_uuid(card)];
      } else {
        injuries = [];
      }
      return injuries;
    },
    assigned_skills(card) {
      return this.assigned_cards(card).map((c) => {
        const skills = this.skill_names_for(c);
        return skills.map((s) => this.skill_to_api_skill(s));
      }).flat();
    },
    get_card_assignment(card) {
      if (card.assigned_to_array[this.deck.id]) {
        return card.assigned_to_array[this.deck.id];
      }
      return [];
    },
    is_tr_card_assigned_as_double(trCard) {
      const assignedTo = this.get_card_assignment(trCard);
      let isDouble = false;
      assignedTo.forEach((id) => {
        const pCard = this.deck_cards.find((c) => {
          if (String(c.id) === String(id) || String(c.uuid) === String(id)) { return true; }
          return false;
        });
        if (pCard) {
          const skills = this.skill_names_for(trCard);
          skills.forEach((skill) => {
            if (this.is_skill_double(pCard, skill)) {
              isDouble = true;
            }
          });
        }
      });
      return isDouble;
    },
    removeAllInjuries(card) {
      const id = this.card_id_or_uuid(card);
      this.deck.injury_map[id] = [];
      this.updateDeck();
    },
    isInDeck(card) {
      if (this.development) {
        return card.in_development_deck;
      }
      return card.in_imperium_deck;
    },
    isNotInDeck(card) {
      return !this.isInDeck(card);
    },
    positional_from_api(positional) {
      const names = positional.split('_');
      names.shift();
      return names.join(' ');
    },
    stadium_enhacement(team) {
      const building = team.cards.find((c) => c.type === 'Building');
      if (building) {
        switch (building.name) {
          case 'Bazar':
            return 'Magician\'s Shop';
          case 'SecurityArea':
            return 'Security Gate';
          case 'RefreshmentArea':
            return 'Beer Stand';
          case 'RefereeArea':
            return 'Referee Rest Area';
          case 'Astrogranit':
            return 'Astrogranite';
          case 'ElfTurf':
            return 'Elf Turf';
          case 'VIPArea':
            return 'Royal Box';
          case 'FoodArea':
            return 'Squig Sandwich Kiosk';
          case 'Nuffle':
            return 'Nuffle Altar';
          case 'Roof':
            return 'Magic Dome';
          default:
            return 'None';
        }
      }
      return 'None';
    },
    race(raceid) {
      const team = this.mixed_teams.find((t) => t.idraces === raceid);
      if (team) {
        return team.name;
      }
      return 'Unknown race';
    },
  },
  watch: {
    selected_team: function (newValue) {
      this.deck.mixed_team = newValue;
      this.updateDeck();
    },
    deck_id: function () {
      this.getDeck();
    },
  },
  computed: {
    id() {
      return `C${this.coach.id}T${this.tournament.tournament_id}`;
    },
    tier_tax() {
      const team = this.mixed_teams.find((t) => t.name === this.selected_team);
      return (team) ? team.tier_tax : 0;
    },
    development() {
      return this.tournament.type === 'Development';
    },

    // cards in deck that belong to user collection
    user_deck_cards() {
      return this.deck.cards;
    },

    assignable_deck_player_cards() {
      return this.deck_player_cards.filter((e) => !['Legendary', 'Inducement', 'Unique', 'Blessed', 'Cursed'].includes(e.template.rarity));
    },

    deck_player_cards() {
      return this.deck_cards.filter((e) => e.template.card_type === 'Player');
    },

    deck_player_size() {
      return this.deck_size_for('Player');
    },

    // all cards in deck
    deck_cards() {
      return this.deck.cards.concat(this.deck.extra_cards);
    },

    // user collection + extra cards
    collection_cards() {
      return this.coach.cards.concat(this.deck.unused_extra_cards).filter(this.isNotInDeck);
    },

    // special cards in deck that belong to user
    user_special_plays() {
      return this.user_deck_cards.filter((e) => e.template.card_type === 'Special Play');
    },

    // size of user cards in deck
    deck_size() {
      const specialPlays = this.user_special_plays.length;
      const deduct = (specialPlays > 0) ? 1 : 0;
      return this.user_deck_cards.length - deduct;
    },

    extra_card_placeholder() {
      if (this.tournament.phase === 'deck_building') {
        return 'Type exact name of Sponsor Card and click Add';
      }
      if (this.tournament.phase === 'special_play') {
        return 'Type exact name of Card and click Add';
      }
      if (this.tournament.phase === 'inducement') {
        return 'Type exact name of Inducement Card and click Add';
      }
      return '';
    },
    doneable_phase() {
      if (['special_play', 'inducement'].includes(this.tournament.phase)) {
        return true;
      }
      return false;
    },
    started() {
      if (this.tournament.status === 'OPEN') {
        return false;
      }
      return true;
    },
    locked() {
      return this.tournament.phase === 'locked' || this.tournament.phase === 'blood_bowl';
    },
    sorted_roster() {
      if ('roster' in this.team) {
        const { roster } = this.team;
        return roster.sort((a, b) => a.number - b.number);
      }
      return [];
    },
    deck_doubles_count() {
      let count = 0;
      this.deck_cards.forEach((card) => {
        if (card.template.card_type === 'Training' && card.deck_type !== 'extra') {
          count += this.is_tr_card_assigned_as_double(card) ? 1 : 0;
        }
      });
      return count;
    },
    deck_value() {
      const value = this.user_deck_cards.reduce((total, e) => total + e.template.value, 0);
      return value + this.tier_tax;
    },
    has_deck_upgrade() {
      return this.deck_upgrades.length > 0;
    },
    deck_upgrades() {
      return this.deck.deck_upgrade_cards;
    },
    canEdit() {
      return (this.is_owner && !this.locked);
    },
    cardListClass() {
      return this.canEdit ? 'col-lg-6' : 'col-lg-12';
    },
  },
  beforeMount() {
    this.getDeck();
    this.$parent.$emit('reloadTournament');
  },
  mounted() {
    this.modal().on('hidden.bs.modal', () => this.$parent.$emit('deckClosed'));
    this.$(() => {
      this.$('[data-toggle="tooltip"]').tooltip();
    });
  },
  props: ['coach', 'tournament', 'deck_id', 'is_owner'],
};
</script>
