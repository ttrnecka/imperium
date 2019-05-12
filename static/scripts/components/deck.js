export default {
    name: 'deck',
    data () {
      return {
          processing:false,
          selected_team:"All",
          show_starter: 1,
          coach_starter_cards:[],
          deck: {
              cards:[],
              starter_cards:[],
              mixed_team:"",
              team_name:"",
              packs:[],
              search_timeout: null,
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
    
        sortedCardsWithoutQuantity(cards,filter="",mixed_filter=true) {
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
    
          if (this.selected_team!="All" && filter=="Player" && mixed_filter) {
            const races = this.mixed_teams.find((e) => { return e.name == this.selected_team }).races;
            tmp_cards =  tmp_cards.filter(function(i) { return i.race.split("/").some((r) => races.includes(r))});
          }
          return this.sortedCards(tmp_cards);
        },
        addToDeck(card) {
            if(this.processing!=true) {
                this.addCard(card);
            }
        },
        removeFromDeck(card) {
            if(this.processing!=true) {
                this.removeCard(card);
            }
        },
        isInDeck(card) {
            if (this.development) {
                return card.in_development_deck;
            } else {
                return card.in_imperium_deck;
            }
        },
        getDeck() {
            const path = "/decks/"+this.deck_id;
            const processingMsg = this.flash("Loading deck...", 'info');
            axios.get(path)
            .then((res) => {
                this.deck=res.data.deck;
                this.coach_starter_cards = res.data.starter_cards;
                this.selected_team = (this.deck.mixed_team=="") ? "All" : this.deck.mixed_team;
                this.modal().modal('show');
            })
            .catch((error) => {
                if (error.response) {
                    let message = (error.response.data.message) ? error.response.data.message : "Unknown error: "+error.response.status;
                    this.flash(message, 'error',{timeout: 3000});
                } else {
                    console.error(error);
                }
            })
            .then(() => {
                processingMsg.destroy();
            });
        },
        addCard(card) {
            const path = "/decks/"+this.deck_id+"/addcard";
            this.processing= true;
            const processingMsg = this.flash("Processing...", 'info');
            axios.post(path,card)
            .then((res) => {
                let msg = "Card added!";
                this.flash(msg, 'success',{timeout: 1000});
                this.deck = res.data;
                const check = (this.development) ? "in_development_deck" : "in_imperium_deck";
                card[check] = true;                
            })
            .catch((error) => {
                if (error.response) {
                    this.flash(error.response.data.message, 'error',{timeout: 3000});
                } else {
                    console.error(error);
                }
            })
            .then(() => {
                processingMsg.destroy();
                this.processing=false;
            });
        },

        removeCard(card) {
            const path = "/decks/"+this.deck_id+"/remove";
            this.processing= true;
            const processingMsg = this.flash("Processing...", 'info');
            axios.post(path,card)
            .then((res) => {
                let msg = "Card removed!";
                let ccard;
                this.flash(msg, 'success',{timeout: 1000});
                this.deck = res.data;
                const check = (this.development) ? "in_development_deck" : "in_imperium_deck";
                if(card.id) {
                    ccard = this.coach.cards.find((c) => c.id == card.id);
                } else {
                    ccard = this.coach_starter_cards.find((c) => c.name == card.name && c[check]==true);
                }
                ccard[check] = false;
            })
            .catch((error) => {
                if (error.response) {
                    this.flash(error.response.data.message, 'error',{timeout: 3000});
                } else {
                    console.error(error);
                }
            })
            .then(() => {
                processingMsg.destroy();
                this.processing=false;
            });
        },
        updateDeck() {
            const path = "/decks/"+this.deck_id;
            this.processing= true;
            const processingMsg = this.flash("Processing...", 'info');
            axios.post(path,this.deck)
            .then((res) => {
                let msg = "Deck saved!";
                this.flash(msg, 'success',{timeout: 3000});
                this.deck = res.data;
            })
            .catch((error) => {
                if (error.response) {
                    this.flash(error.response.data.message, 'error',{timeout: 3000});
                } else {
                    console.error(error);
                }
            })
            .then(() => {
                processingMsg.destroy();
                this.processing=false;
            });
        },
        debounceUpdate(val){
            if(this.search_timeout) clearTimeout(this.search_timeout);
            var that=this;
            this.search_timeout = setTimeout(function() {
              that.deck.team_name = val;
              that.updateDeck();
            }, 1000);
        },
        modal() {
            return $('#deck'+this.id);
        }
    },
    watch: {
        selected_team: function(newValue,oldValue) { 
            this.deck.mixed_team = newValue;
            this.updateDeck();
        },
        deck_id: function(newValue,oldValue) { 
            this.getDeck();
        },
    },
    computed: {
        id() {
            return 'C'+this.coach.id+'T'+this.tournament.id;
        },
        development() {
            return this.tournament.type=="Development";
        },
        deck_cards() {
            return this.deck.cards.concat(this.deck.starter_cards);
        },
        collection_cards() {
            return this.coach.cards.concat(this.coach_starter_cards);
        }
    },
    beforeMount() {
        this.getDeck();
    },
    mounted() {
        this.modal().on('hidden.bs.modal', () => this.$parent.$emit('deckClosed'))
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
                                    <input type="text" class="form-control" placeholder="Team Name" v-bind:value="deck.team_name" v-on:input="debounceUpdate($event.target.value)">
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
                                    <h5>Value: [[ cardsValue(deck_cards) ]]</h5>
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
                                                        <tr v-if="!isInDeck(card)" @click="addToDeck(card)" v-for="card in sortedCardsWithoutQuantity(collection_cards,ctype)" :key="card.id" :class="rarityclass(card.rarity)">
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
                                                        <tr @click="removeFromDeck(card)" v-for="card in sortedCardsWithoutQuantity(deck_cards,ctype,false)" :key="card.id" :class="rarityclass(card.rarity)">
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