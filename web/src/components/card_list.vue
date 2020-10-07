<template>
  <div :id="id" class="card_list">
    <div class="card" v-for="(ctype,index) in type_list" :key="index">
      <div class="card-header" :id="ctype.replace(/\s/g, '')+id">
        <h5 class="mb-0">
          <button class="btn btn-link" data-toggle="collapse" :data-target="'#collapse'+ctype.replace(/\s/g, '')" aria-expanded="true"
            :aria-controls="'collapse'+ctype.replace(/\s/g, '')">
          {{ ctype }} Cards ({{ number_of_cards(ctype) }})
          </button>
        </h5>
      </div>
      <div :id="'collapse'+ctype.replace(/\s/g, '')" class="collapse show" :aria-labelledby="ctype.replace(/\s/g, '')+id" :data-parent="`#${id}`">
        <div class="card-body table-responsive">
          <table class="table table-hover">
              <thead>
              <tr>
                <th v-if="should_diplay('Lock') && !duster">
                  <i class="fas fa-lock"
                  title="Locked in another tournament">
                  </i>
                </th>
                <th v-if="should_diplay('Rarity')" style="width: 10%">Rarity</th>
                <th v-if="should_diplay('Value')" style="width: 10%">Value</th>
                <th v-if="should_diplay('Name')">Name</th>
                <th v-if="should_diplay('Skills')">Skills</th>
                <th v-if="should_diplay('Race')">Race</th>
                <th v-if="should_diplay('Subtype')" class="d-none d-sm-table-cell">
                  Subtype
                </th>
                <th v-if="should_diplay('ShortSubtype')" class="d-none d-sm-table-cell" title="Subtype">
                  S
                </th>
                <th v-if="should_diplay('Uses') && !duster">Uses</th>
                <th v-if="quantity" class="d-none d-sm-table-cell">
                  Quantity
                </th>
                <th v-if="quantity" class="d-xs-table-cell d-sm-none">
                  Q
                </th>
                <th v-if="duster" style="width: 15%"></th>
                <th v-if="isDeck || $isMobile()"></th>
              </tr>
              </thead>
              <tbody>
              <template v-for="card in sorted(ctype)">
                <tr v-if="shouldDisplay(card)" @click="$emit('card-click', card)" :key="card.id" :class="[rarityclass(card), extra_type(card.deck_type), 'pointer', 'imperium_card']"
                  :title="card.template.name"
                  :data-toggle="'popover'" data-placement="top" data-html="true" :data-content="markdown.makeHtml(card.template.description)">
                  <td v-if="should_diplay('Lock') && !duster">
                    <i v-if="is_locked(card) && is_loggedcoach(owner.short_name)" class="fas fa-lock"></i>
                  </td>
                  <td v-if="should_diplay('Rarity')">
                    <img class="rarity" :src="'static/images/'+card.template.rarity+'.jpg'" :alt="card.template.rarity"
                      :title="card.template.rarity" width="20" height="25" />
                    </td>
                  <td v-if="should_diplay('Value')">{{ card.template.value }}</td>
                  <td v-if="should_diplay('Name')" :title="card.template.description">{{card.template.name}}
                    <i v-if="extra_type(card.deck_type)=='extra_card'" class="ml-2 fas fa-plus-circle" title="Extra card"></i>
                  </td>
                  <td v-if="should_diplay('Skills')"><span v-html="skills_for(card)"></span></td>
                  <td v-if="should_diplay('Race')">{{ card.template.race }}</td>
                  <td v-if="should_diplay('Subtype')" class="d-none d-sm-table-cell">
                    {{ card.template.subtype }}
                  </td>
                  <td v-if="should_diplay('ShortSubtype')" class="d-none d-sm-table-cell" :title="card.template.subtype">
                    {{ card.template.subtype.match(/\b(\w)/g).join('') }}
                  </td>
                  <td v-if="should_diplay('Uses') && !duster">{{ `${card.uses}/${max_uses(card)}` }} </td>
                  <td v-if="quantity">{{ card.quantity }}</td>
                  <td v-if="duster" class="text-right">
                    <button v-if="is_in_duster(card)" :disabled="processing"
                      type="button" class="col-12 btn btn-danger"
                      @click.stop="dust_remove(card)">Remove</button>
                    <button v-else type="button" :disabled="processing"
                      class="col-12 btn btn-success"
                      @click.stop="dust_add(card)">Add</button>
                  </td>
                  <td v-if="isDeck || $isMobile()" @click.stop>
                    <div :id="'player'+card_id_or_uuid(card)" class="float-right"><i class="fas fa-cog fa-2x"></i></div>
                    <b-popover :target="'player'+card_id_or_uuid(card)" triggers="hover" placement="left">
                      <template v-slot:title>{{ card.template.name }} ({{card.template.subtype}})</template>
                      <span v-html="markdown.makeHtml(card.template.description)"></span>
                      <template v-if="canEdit && isDeck">
                        <b-button class="m-1" v-if="isEnabled(card)" variant="danger" @click="$emit('card-disable', card)">Disable</b-button>
                        <b-button class="m-1" v-else variant="success" @click="$emit('card-enable', card)">Enable</b-button>
                        <b-button v-if="ctype=='Player'" class="m-1" variant="success" @click="$emit('card-addskill', card)">Skill</b-button>
                        <b-button class="m-1" variant="info" @click="$emit('card-unskill', card)">Unskill</b-button>
                      </template>
                    </b-popover>
                  </td>
                </tr>
                <template v-if="isDeck">
                  <tr :class="[rarityclass(card)]" v-for="(idx,index) in number_of_assignments(card)" :key="`assignment${index}${card_id_or_uuid(card)}`">
                    <td :colspan="column_list.length+1">
                      <select class="form-control" v-model="card.assigned_to_array[deck.id][idx-1]" v-on:click.stop @change="$emit('card-assign', card, idx-1)" :disabled="!canEdit">
                        <option default :value="undefined" disabled>Select Player</option>
                        <option v-for="(pcard,index) in sortedCards(assignable_player_card_list_for(card))" :disabled="!isEnabled(pcard) || is_guarded(pcard) || assigned_cards(pcard).includes(card)" :key="index" :value="card_id_or_uuid(pcard)">{{index+1}}. {{ pcard.template.name }}</option>
                      </select>
                    </td>
                  </tr>
                  <tr v-if="ctype=='Player'" :class="[rarityclass(card)]" :key="'player'+card_id_or_uuid(card)">
                    <td colspan="1">
                      <i class="fas fa-angle-double-right fa-2x"></i>
                    </td>
                    <td :colspan="column_list.length-1">
                      <span v-html="deck_skills_for(card)"></span>
                      <span v-if="is_guarded(card)" title="Immune">&#128170;</span>
                      <template v-if="canEdit">
                        <img v-if="injuryPickerOpened(card)" @click="openInjuryPicker(card)" class="skill_icon skill_single pointer" src="https://cdn2.rebbl.net/images/skills/SmashedHand.png" title="Add Injury">
                        <injury-picker v-else v-on:injured="addInjury(card,$event)"></injury-picker>
                      </template>
                    </td>
                    <td class="d-table-cell d-sm-none">
                    </td>
                    <td><div class="float-right"><b>Doubles:</b> {{doubles_count(card)}}</div></td>
                  </tr>
                </template>
              </template>
              </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex';
import Cards from '@/mixins/cards';
import injuryPicker from '@/components/injury_picker.vue';

export default {
  name: 'card-list',
  mixins: [Cards],
  components: {
    injuryPicker,
  },
  props: {
    id: String,
    cards: Array,
    external_cards: Array,
    selected_team: {
      type: String,
      default: 'All',
    },
    owner: Object,
    starter: {
      type: Boolean,
      default: true,
    },
    rarity_sort: {
      type: Boolean,
      default: true,
    },
    quantity: {
      type: Boolean,
      default: false,
    },
    duster: {
      type: Boolean,
      default: false,
    },
    edit: {
      type: Boolean,
      default: false,
    },
    type_list: {
      type: Array,
      default() {
        return ['Player', 'Training', 'Special Play', 'Reaction', 'Staff', 'High Command', 'Upgrade'];
      },
    },
    column_list: {
      type: Array,
      default() {
        return ['Lock', 'Rarity', 'Value', 'Name', 'Skills', 'Race', 'Uses', 'Subtype'];
      },
    },
    // if provided for deck list purposes
    deck: {
      type: Object,
      default() {
        return {};
      },
    },
  },
  data() {
    return {
      processing: false,
    };
  },
  methods: {
    should_diplay(column) {
      return (this.column_list.includes(column));
    },
    sortedCardsWithQuantity(filter = '') {
      const newCollection = {};
      const sorted = this.sortedCardsWithoutQuantity(filter);
      for (let i = 0, len = sorted.length; i < len; i += 1) {
        const { name, uses } = sorted[i].template;
        const tag = name + uses;
        if (Object.prototype.hasOwnProperty.call(newCollection, tag)) {
          newCollection[tag].quantity += 1;
        } else {
          newCollection[tag] = Object.assign({}, sorted[i]);
          // newCollection[name].card = sorted[i];
          newCollection[tag].quantity = 1;
        }
      }
      return newCollection;
    },
    sortedCardsWithoutQuantity(filter = '') {
      let tmCards;
      if (!this.starter) {
        tmCards = this.cards.filter((i) => !i.is_starter);
      } else {
        tmCards = this.cards;
      }
      if (filter !== '') {
        tmCards = tmCards.filter((i) => i.template.card_type === filter);
      }

      if (this.selected_team !== 'All') {
        const { races } = this.mixed_teams.find((e) => e.name === this.selected_team);
        tmCards = tmCards.filter((i) => i.template.race.split('/').some((r) => r === 'All' || races.includes(r)));
      }

      return this.sortedCards(tmCards);
    },
    sortedCards(cards) {
      if (this.rarity_sort === false) {
        return cards;
      }
      const order = this.rarityorder;
      const that = this;
      function compare(a, b) {
        return (order[a.template.rarity] - order[b.template.rarity])
          || a.template.name.localeCompare(b.template.name) || that.card_id_or_uuid(a).localeCompare(that.card_id_or_uuid(b));
      }
      return cards.slice().sort(compare);
    },
    rarityclass(card) {
      let klass;
      if (!this.isEnabled(card)) {
        return 'table-secondary';
      }
      switch (card.template.rarity) {
        case 'Common':
        case 'Starter':
          klass = 'table-common';
          break;
        case 'Rare':
          klass = 'table-rare';
          break;
        case 'Epic':
          klass = 'table-epic';
          break;
        case 'Legendary':
          klass = 'table-legendary';
          break;
        case 'Unique':
          klass = 'table-unique';
          break;
        case 'Inducement':
        case 'Blessed':
        case 'Cursed':
          klass = 'table-inducement';
          break;
        default:
          klass = 'table-light';
      }
      return klass;
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
    sorted(filter) {
      if (this.quantity) {
        return this.sortedCardsWithQuantity(filter);
      }
      return this.sortedCardsWithoutQuantity(filter);
    },
    is_in_duster(card) {
      return (this.is_duster ? this.loggedCoach.duster.cards.includes(card.id) : false);
    },

    is_guarded(card) {
      if (card.template.card_type !== 'Player') { return false; }
      const assignedCards = this.cards.concat(this.external_cards).filter((c) => this.get_card_assignment(c).includes(String(this.card_id_or_uuid(card))));
      if (assignedCards.find((c) => this.guards.includes(c.template.name)) !== undefined) { return true; }
      return false;
    },
    deck_skills_for(card) {
      const assignedCards = this.assigned_cards(card);
      const injuries = this.player_injuries(card);

      return assignedCards.map((c) => {
        let double = false;
        const skills = this.skill_names_for(c);
        skills.forEach((skill) => {
          if (this.is_skill_double(card, skill)) {
            double = true;
          }
        });
        return this.skills_for(c, double);
      }).join('') + injuries.map((c) => this.imgs_for_skill(c)).join('');
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
    doubles_count(card) {
      const assignedCards = this.cards.filter((c) => this.get_card_assignment(c).includes(String(this.card_id_or_uuid(card))));
      let doubles = 0;

      assignedCards.forEach((tcard) => {
        // ignore extra cards
        if (tcard.deck_type === 'extra') {
          return;
        }
        const skills = this.skill_names_for(tcard);
        let cardDoubles = 0;
        // only count 1 double for a multiskill card
        skills.forEach((skill) => {
          if (this.is_skill_double(card, skill)) {
            cardDoubles = 1;
          }
        });
        doubles += cardDoubles;
      });
      return doubles;
    },
    openInjuryPicker(card) {
      card.cas_pick = true;
      this.$forceUpdate();
    },
    addInjury(card, injury) {
      const id = this.card_id_or_uuid(card);
      if (!this.deck.injury_map[id]) {
        this.deck.injury_map[id] = [];
      }
      if (injury !== '' && injury !== 'X') {
        this.deck.injury_map[id].push(injury);
      }
      card.cas_pick = false;
      if (injury === 'X') {
        this.removeAllInjuries(card);
      } else {
        this.$emit('update-deck');
      }
    },
    removeAllInjuries(card) {
      const id = this.card_id_or_uuid(card);
      this.deck.injury_map[id] = [];
      this.$emit('update-deck');
    },
    number_of_cards(ctype) {
      return this.cards.filter((c) => c.template.card_type === ctype && (this.starter || !c.is_starter) && this.isEnabled(c)).length;
    },
    assignable_player_card_list_for(card) {
      if (this.guards.includes(card.template.name)) {
        return this.immunable_player_cards;
      }
      return this.assignable_player_cards;
    },
    // do not display locked cards in the deck
    shouldDisplay(card) {
      if (this.duster && this.is_locked(card)) {
        return false;
      }
      return true;
    },
  },
  computed: {
    isDeck() {
      return (Object.keys(this.deck).length !== 0);
    },
    assignable_player_cards() {
      return this.player_cards.concat(this.external_player_cards).filter((e) => !['Legendary', 'Inducement', 'Unique', 'Blessed', 'Cursed'].includes(e.template.rarity) || this.nonassignable_exceptions.includes(e.template.name));
    },

    immunable_player_cards() {
      return this.player_cards.concat(this.external_player_cards).filter((e) => !['Inducement', 'Blessed', 'Cursed'].includes(e.template.rarity) || this.nonassignable_exceptions.includes(e.template.name));
    },

    player_cards() {
      return this.cards.filter((e) => e.template.card_type === 'Player');
    },
    external_player_cards() {
      return this.external_cards.filter((e) => e.template.card_type === 'Player');
    },
    canEdit() {
      return (this.is_loggedcoach(this.owner.short_name) && this.edit);
    },
    ...mapState([
      'user',
    ]),
    ...mapGetters([
      'is_loggedcoach', 'loggedCoach', 'is_duster',
    ]),
  },
};
</script>

<style scoped>
.pointer {
  cursor: pointer;
}

.imperium_card {
  font-weight: bold;
}

.extra_card td {
  font-style: italic;
}

</style>
