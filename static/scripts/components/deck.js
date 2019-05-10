export default {
    name: 'deck',
    data () {
      return {
          processing:false,
          selected_team:"All",
          show_starter: 1,
          deck: {
              cards:[],
              mixed_team:"",
              team_name:""
          }
      }
    },
    methods: {
        sortedCards(cards) {
          var order = this.rarityorder;
          function compare(a,b) {
            return (order[a.rarity] - order[b.rarity]) || a.name.localeCompare(b.name);
          }
          return cards.slice().sort(compare);
        },
    
        sortedCardsWithoutQuantity(cards,filter="") {
          let tmp_cards;
          if (!this.show_starter) {
            tmp_cards =  cards.filter(function(i) { return i.id != null});
          }
          else {
            tmp_cards =  cards
          }
          if (filter!="") {
            tmp_cards =  tmp_cards.filter(function(i) { return i.card_type == filter});
          }
    
          if (this.selected_team!="All" && filter=="Player") {
            const races = this.mixed_teams.find((e) => { return e.name == this.selected_team }).races;
            tmp_cards =  tmp_cards.filter(function(i) { return i.race.split("/").some((r) => races.includes(r))});
          }
          return this.sortedCards(tmp_cards);
        },
        addToDeck(card) {
            if (this.development) {
                card.in_development_deck = true;
            } else {
                card.in_imperium_deck = true;
            }
            this.deck.cards.push(card);
            console.log(this.deck);
        },
        removeFromDeck(card) {
            if (this.development) {
                card.in_development_deck = false;
            } else {
                card.in_imperium_deck = false;
            }
            const idx = this.deck.cards.indexOf(card);
            this.deck.cards.splice(idx,1);
        },
        isInDeck(card) {
            if (this.development) {
                return card.in_development_deck;
            } else {
                return card.in_imperium_deck;
            }
        }
    },
    watch: {
        selected_team: function(newValue,oldValue) { 
            this.deck.mixed_team = newValue;
        }
    },
    computed: {
        id() {
            return 'C'+this.coach.id+'T'+this.tournament.id;
        },
        development() {
            return this.tournament.type=="Development";
        }
    },
    beforeMount() {

    },
    delimiters: ['[[',']]'],
    props: ['coach','tournament','deck_id'],
    template:   `<div class="modal fade deck" :id="'deck'+id" tabindex="-1" role="dialog" aria-labelledby="deck" aria-hidden="true">
                    <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Deck for [[coach.short_name]] in [[tournament.name ]]</h5>
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                            </button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="form-group col-6">
                                    <select class="form-control" v-model="selected_team">
                                        <option selected value="All">Select team</option>
                                        <option v-for="team in mixed_teams" :value="team.name" :key="team.code">[[ team.name ]] ([[ team.races.join() ]])</option>
                                    </select>
                                </div>
                                <div class="form-group col-6">
                                    <input type="text" class="form-control" placeholder="Team Name" v-model="deck.team_name">
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-3">
                                    <h5>Collection</h5>
                                </div>
                                <div class="col-3">
                                    <div class="custom-control custom-checkbox mr-sm-2 text-right">
                                        <input type="checkbox" class="custom-control-input" :id="'sptoggle'+id" v-model="show_starter">
                                        <label class="custom-control-label" :for="'sptoggle'+id">Toggle Starter Pack</label>
                                    </div>
                                </div>
                                <div class="col-3">
                                    <h5>Deck</h5>
                                </div>
                                <div class="col-3 text-right">
                                    <h5>Value: [[ cardsValue(deck.cards) ]]</h5>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-6">
                                    <div :id="'accordionCardsCollection'+id">
                                        <div class="card" v-for="ctype in card_types">
                                            <div class="card-header" :id="ctype.replace(/\\s/g, '')+'CardsCollection'+id">
                                                <h5 class="mb-0">
                                                    <button class="btn btn-link" data-toggle="collapse" :data-target="'#collapseCollection'+ctype.replace(/\\s/g, '')+id" aria-expanded="true" :aria-controls="'collapse'+ctype.replace(/\\s/g, '')">
                                                    [[ ctype ]] Cards
                                                    </button>
                                                </h5>
                                            </div>
                                            <div :id="'collapseCollection'+ctype.replace(/\\s/g, '')+id" class="deck_ctype collapse show" :aria-labelledby="ctype.replace(/\\s/g, '')+'Cards'" :data-parent="'#accordionCardsCollection'+id">
                                                <div class="card-body table-responsive">
                                                    <table class="table  table-striped table-hover">
                                                        <thead>
                                                        <tr>
                                                            <th>Rarity</th>
                                                            <th>Value</th>
                                                            <th>Name</th>
                                                            <th>Race</th>
                                                            <th class="d-none d-sm-table-cell">Subtype</th>
                                                        </tr>
                                                        </thead>
                                                        <tbody>
                                                        <tr v-if="!isInDeck(card)" @click="addToDeck(card)" v-for="card in sortedCardsWithoutQuantity(coach.cards.concat(starter_cards()),ctype)" :key="card.id" :class="rarityclass(card.rarity)">
                                                            <td><img class="rarity" :src="'static/images/'+card.rarity+'.jpg'" :alt="card.rarity" :title="card.rarity" width="20" height="25" /></td>
                                                            <td>[[ card.value ]]</td>
                                                            <td :title="card.description">[[ card.name ]]</td>
                                                            <td>[[ card.race ]]</td>
                                                            <td class="d-none d-sm-table-cell">[[ card.subtype ]]</td>
                                                        </tr>
                                                        </tbody>
                                                    </table>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-6">
                                    <div :id="'accordionCardsDeck'+id">
                                        <div class="card" v-for="ctype in card_types">
                                            <div class="card-header" :id="ctype.replace(/\\s/g, '')+'CardsDeck'+id">
                                                <h5 class="mb-0">
                                                    <button class="btn btn-link" data-toggle="collapse" :data-target="'#collapseDeck'+ctype.replace(/\\s/g, '')+id" aria-expanded="true" :aria-controls="'collapse'+ctype.replace(/\\s/g, '')">
                                                    [[ ctype ]] Cards
                                                    </button>
                                                </h5>
                                            </div>
                                            <div :id="'collapseDeck'+ctype.replace(/\\s/g, '')+id" class="deck_ctype collapse show" :aria-labelledby="ctype.replace(/\\s/g, '')+'Cards'" :data-parent="'#accordionCardsDeck'+id">
                                                <div class="card-body table-responsive">
                                                    <table class="table  table-striped table-hover">
                                                        <thead>
                                                        <tr>
                                                            <th>Rarity</th>
                                                            <th>Value</th>
                                                            <th>Name</th>
                                                            <th>Race</th>
                                                            <th class="d-none d-sm-table-cell">Subtype</th>
                                                        </tr>
                                                        </thead>
                                                        <tbody>
                                                        <tr @click="removeFromDeck(card)" v-for="card in sortedCardsWithoutQuantity(deck.cards,ctype)" :key="card.id" :class="rarityclass(card.rarity)">
                                                            <td><img class="rarity" :src="'static/images/'+card.rarity+'.jpg'" :alt="card.rarity" :title="card.rarity" width="20" height="25" /></td>
                                                            <td>[[ card.value ]]</td>
                                                            <td :title="card.description">[[ card.name ]]</td>
                                                            <td>[[ card.race ]]</td>
                                                            <td class="d-none d-sm-table-cell">[[ card.subtype ]]</td>
                                                        </tr>
                                                        </tbody>
                                                    </table>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    </div>
                </div>`
}