<template>
  <div :id="id">
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
          <table class="table  table-striped table-hover">
              <thead>
              <tr>
                <th v-if="should_diplay('Lock')">
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
                <th v-if="quantity" class="d-none d-sm-table-cell">
                  Quantity
                </th>
                <th v-if="quantity" class="d-xs-table-cell d-sm-none">
                  Q
                </th>
                <th v-if="duster" style="width: 15%"></th>
              </tr>
              </thead>
              <tbody>
              <template v-for="card in sorted(ctype)">
                <tr @click="$emit('card-click', card)" :key="card.id" :class="[rarityclass(card.template.rarity), extra_type(card.deck_type), 'pointer']"
                  :title="card.template.name"
                  :data-toggle="duster ? '': 'popover'" data-placement="top" data-html="true" :data-content="markdown.makeHtml(card.template.description)">
                  <td v-if="should_diplay('Lock')">
                    <i v-if="is_locked(card) && is_loggedcoach(owner.short_name)" class="fas fa-lock"></i>
                  </td>
                  <td v-if="should_diplay('Rarity')">
                    <img class="rarity" :src="'static/images/'+card.template.rarity+'.jpg'" :alt="card.template.rarity"
                      :title="card.template.rarity" width="20" height="25" />
                    </td>
                  <td v-if="should_diplay('Value')">{{ card.template.value }}</td>
                  <td v-if="should_diplay('Name')" :title="card.template.description">{{card.template.name}}</td>
                  <td v-if="should_diplay('Skills')"><span v-html="skills_for(card)"></span></td>
                  <td v-if="should_diplay('Race')">{{ card.template.race }}</td>
                  <td v-if="should_diplay('Subtype')" class="d-none d-sm-table-cell">
                    {{ card.template.subtype }}
                  </td>
                  <td v-if="quantity">{{ card.quantity }}</td>
                  <td v-if="duster" class="text-right">
                    <button v-if="is_in_duster(card)" :disabled="processing"
                      type="button" class="col-12 btn btn-danger"
                      @click.prevent="dust_remove(card)">Remove</button>
                    <button v-else type="button" :disabled="processing"
                      class="col-12 btn btn-success"
                      @click.prevent="dust_add(card)">Add</button>
                  </td>
                </tr>
                <template v-if="isDeck">
                  <tr :class="[rarityclass(card.template.rarity)]" v-for="(idx,index) in number_of_assignments(card)" :key="`assignment${index}${card_id_or_uuid(card)}`">
                    <td :colspan="column_list.length">
                      <select class="form-control" v-model="card.assigned_to_array[deck.id][idx-1]" v-on:click.stop @change="$emit('card-assign', card)" :disabled="!edit">
                        <option default :value="undefined" disabled>Select Player</option>
                        <option v-for="(card,index) in sortedCards(assignable_player_cards)" :key="index" :value="card_id_or_uuid(card)">{{index+1}}. {{ card.template.name }}</option>
                      </select>
                    </td>
                  </tr>
                  <tr v-if="ctype=='Player'" :class="[rarityclass(card.template.rarity)]" :key="'player'+card_id_or_uuid(card)">
                    <th colspan="1"><i class="fas fa-angle-double-right fa-2x" title="Added skills and injuries"></i></th>
                    <td :colspan="column_list.length-2">
                      <span v-html="deck_skills_for(card)"></span>
                      <span v-if="is_guarded(card)" title="No Special Play effects possible">&#128170;</span>
                      <template v-if="is_loggedcoach(owner.short_name) && edit">
                        <img v-if="injuryPickerOpened(card)" @click="openInjuryPicker(card)" class="skill_icon skill_single pointer" src="https://cdn2.rebbl.net/images/skills/SmashedHand.png" title="Add Injury">
                        <injury-picker v-else v-on:injured="addInjury(card,$event)"></injury-picker>
                      </template>
                    </td>
                    <td class="d-none d-sm-table-cell"><b>Doubles:</b> {{doubles_count(card)}}</td>
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
        return ['Player', 'Training', 'Special Play', 'Reaction', 'Staff', 'Upgrade'];
      },
    },
    column_list: {
      type: Array,
      default() {
        return ['Lock', 'Rarity', 'Value', 'Name', 'Skills', 'Race', 'Subtype'];
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
        const { name } = sorted[i].template;
        if (Object.prototype.hasOwnProperty.call(newCollection, name)) {
          newCollection[name].quantity += 1;
        } else {
          newCollection[name] = Object.assign({}, sorted[i]);
          // newCollection[name].card = sorted[i];
          newCollection[name].quantity = 1;
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

      if (this.selected_team !== 'All' && filter === 'Player') {
        const { races } = this.mixed_teams.find((e) => e.name === this.selected_team);
        tmCards = tmCards.filter((i) => i.template.race.split('/').some((r) => races.includes(r)));
      }
      return this.sortedCards(tmCards);
    },
    sortedCards(cards) {
      if (this.rarity_sort === false) {
        return cards;
      }
      const order = this.rarityorder;
      function compare(a, b) {
        return (order[a.template.rarity] - order[b.template.rarity])
          || a.template.name.localeCompare(b.template.name);
      }
      return cards.slice().sort(compare);
    },
    rarityclass(rarity) {
      let klass;
      switch (rarity) {
        case 'Common':
        case 'Starter':
          klass = 'table-light';
          break;
        case 'Rare':
          klass = 'table-info';
          break;
        case 'Epic':
          klass = 'table-danger';
          break;
        case 'Legendary':
          klass = 'table-warning';
          break;
        case 'Unique':
          klass = 'table-success';
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
      const assignedCards = this.cards.filter((c) => this.get_card_assignment(c).includes(String(this.card_id_or_uuid(card))));
      if (assignedCards.find((c) => ['Bodyguard', 'Hired Muscle', 'Personal Army'].includes(c.template.name)) !== undefined) { return true; }
      return false;
    },
    get_card_assignment(card) {
      if (this.deck.id && card.assigned_to_array[this.deck.id]) {
        return card.assigned_to_array[this.deck.id];
      }
      return [];
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
    assigned_cards(card) {
      return this.cards.filter((c) => this.get_card_assignment(c).includes(this.card_id_or_uuid(card)));
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
      return this.cards.filter((c) => c.template.card_type === ctype && (this.starter || !c.is_starter)).length;
    },
  },
  computed: {
    isDeck() {
      return (Object.keys(this.deck).length !== 0);
    },
    assignable_player_cards() {
      return this.player_cards.filter((e) => !['Legendary', 'Inducement', 'Unique', 'Blessed', 'Cursed'].includes(e.template.rarity));
    },

    player_cards() {
      return this.cards.filter((e) => e.template.card_type === 'Player');
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
</style>
