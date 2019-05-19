export default {
    name: 'deck',
    data () {
      return {
          processing:false,
          selected_team:"All",
          show_starter: 1,
          rarity_order: 1,
          coach_starter_cards:[],
          extra_card:"",
          deck: {
              cards:[],
              starter_cards:[],
              extra_cards:[],
              unused_extra_cards:[],
              mixed_team:"",
              team_name:"",
              comment:"",
              packs:[],
              search_timeout: null,
          },
          team:{}
      }
    },
    methods: {
        canAddToDeck(card) {
            if(!this.is_owner) {
                return false;
            }
            if(this.locked) {
                this.flash("Deck is locked!", 'info',{timeout: 3000});
                return false;
            }
            if(this.processing==true) {
                return false;
            }
            
            if(card.duster) {
                this.flash("Cannot add card - card is flagged for dusting!", 'error',{timeout: 3000});
                    return false;
            }

            if(this.deck_size==this.tournament.deck_limit && card.deck_type!="extra") {
                if (card.card_type!="Special Play" || this.user_special_plays.length!=0) {
                    this.flash("Cannot add card - deck limit reached!", 'error',{timeout: 3000});
                    return false;
                }
            }
            if(this.selected_team=="All") {
                this.flash("Cannot add card - team not selected!", 'error',{timeout: 3000});
                return false;
            }
            if(this.deck_player_size>=16 && card.card_type=="Player") {
                this.flash("Cannot add card - 16 Player cards are already in the deck!", 'error',{timeout: 3000});
                return false;
            }
            return true;
        },
        addToDeck(card) {
            if(!this.canAddToDeck(card)) {
                return;
            }
            this.addCard(card);
        },
        canRemoveFromDeck(card) {
            if(!this.is_owner) {
                return false;
            }
            if(this.locked) {
                this.flash("Deck is locked!", 'info',{timeout: 3000});
                return false;
            }
            if(this.processing==true) {
                return false;
            }
            return true;
        },
        removeFromDeck(card) {
            if(!this.canRemoveFromDeck(card)) {
                return;
            }
            this.removeCard(card);
        },
        isInDeck(card) {
            if (this.development) {
                return card.in_development_deck;
            } else {
                return card.in_imperium_deck;
            }
        },
        async_error(error) {
            if (error.response) {
                let message = (error.response.data.message) ? error.response.data.message : "Unknown error: "+error.response.status;
                this.flash(message, 'error',{timeout: 3000});
            } else {
                console.error(error);
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
            .catch(this.async_error)
            .then(() => {
                processingMsg.destroy();
            });
        },
        getTeam(name) {
            const path = "/teams/"+name;
            const processingMsg = this.flash("Loading team...", 'info');
            axios.get(path)
            .then((res) => {
                if (res.data==false) {
                    this.flash("Team "+name+" does not exist", 'error',{timeout: 3000});     
                } else {
                    this.team=res.data;
                }
            })
            .catch(this.async_error)
            .then(() => {
                processingMsg.destroy();
            });
        },
        addExtraCard(name) {
            if(!this.is_owner) {
                return;
            }
            if(this.locked) {
                this.flash("Deck is locked!", 'info',{timeout: 3000});
                return;
            }
            const path = "/decks/"+this.deck_id+"/addcard/extra";
            this.processing= true;
            const processingMsg = this.flash("Processing...", 'info');
            axios.post(path,{name: name})
            .then((res) => {
                let msg = "Extra card added!";
                this.flash(msg, 'success',{timeout: 1000});
                this.deck = res.data;
                this.extra_card = "";
            })
            .catch(this.async_error)
            .then(() => {
                processingMsg.destroy();
                this.processing=false;
            });
        },
        removeExtraCard(card) {
            if(!this.is_owner) {
                return;
            }
            if(this.locked) {
                this.flash("Deck is locked!", 'info',{timeout: 3000});
                return;
            }
            const path = "/decks/"+this.deck_id+"/removecard/extra";
            this.processing= true;
            const processingMsg = this.flash("Processing...", 'info');
            axios.post(path,card)
            .then((res) => {
                let msg = "Extra card removed!";
                this.flash(msg, 'success',{timeout: 1000});
                this.deck = res.data;
            })
            .catch(this.async_error)
            .then(() => {
                processingMsg.destroy();
                this.processing=false;
            });
        },
        deck_valid() {
            if(this.deck_player_size<11) {
                this.flash("You need to include at least 11 player cards!", 'error',{timeout: 3000});
                return false;
            }
            if(this.deck_size!=this.tournament.deck_limit) {
                this.flash("You need to include "+this.tournament.deck_limit+" cards!", 'error',{timeout: 3000});
                return false;
            }

            if(this.deck.team_name=="") {
                this.flash("Team name is not specified!", 'error',{timeout: 3000});
                return false;
            }

            if(this.deck.mixed_team=="All") {
                this.flash("Team mixed race is not specified!", 'error',{timeout: 3000});
                return false;
            }

            let training_cards = this.sortedCardsWithoutQuantity(this.deck_cards,"Training",false);
            let found_card = training_cards.find((c)=> c.assigned_to=="");
            if(found_card!=undefined) {
                this.flash("Not all training cards are assigned to players!", 'error',{timeout: 3000});
                return false;
            }
            return true;
        },
        commit() {
            if(!this.is_owner) {
                return;
            }
            if(this.locked) {
                this.flash("Deck is locked!", 'info',{timeout: 3000});
                return;
            }
            if(!this.deck_valid()) {
                return;
            }
            const path = "/decks/"+this.deck_id+"/commit";
            this.processing= true;
            const processingMsg = this.flash("Processing...", 'info');
            axios.get(path)
            .then((res) => {
                let msg = "Deck commited!";
                this.flash(msg, 'success',{timeout: 1000});
                this.deck = res.data;
                this.$parent.$emit('reloadTournament');
            })
            .catch(this.async_error)
            .then(() => {
                processingMsg.destroy();
                this.processing=false;
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
            .catch(this.async_error)
            .then(() => {
                processingMsg.destroy();
                this.processing=false;
            });
        },

        assignCard(card) {
            if(!this.is_owner) {
                return;
            }
            if(this.locked) {
                this.flash("Deck is locked!", 'info',{timeout: 3000});
                return;
            }
            const path = "/decks/"+this.deck_id+"/assign";
            this.processing= true;
            const processingMsg = this.flash("Processing...", 'info');
            axios.post(path,card)
            .then((res) => {
                let msg = "Card assigned!";
                this.flash(msg, 'success',{timeout: 1000});
                this.deck = res.data;
            })
            .catch(this.async_error)
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
                if(card.deck_type!="extra") {
                    const check = (this.development) ? "in_development_deck" : "in_imperium_deck";
                    if(card.id) {
                        ccard = this.coach.cards.find((c) => c.id == card.id);
                    } else {
                        ccard = this.coach_starter_cards.find((c) => c.name == card.name && c[check]==true);
                    }
                    ccard[check] = false;
                }
            })
            .catch(this.async_error)
            .then(() => {
                processingMsg.destroy();
                this.processing=false;
            });
        },
        updateDeck() {
            if(!this.is_owner) {
                return;
            }
            if(this.locked) {
                this.flash("Deck is locked!", 'info',{timeout: 3000});
                return;
            }
            const path = "/decks/"+this.deck_id;
            this.processing= true;
            //const processingMsg = this.flash("Processing...", 'info');
            const send_deck = {
                team_name:this.deck.team_name,
                mixed_team:this.deck.mixed_team,
                comment:this.deck.comment,
            }
            axios.post(path,{deck:send_deck})
            .then((res) => {
                //let msg = "Deck saved!";
                //this.flash(msg, 'success',{timeout: 3000});
                this.deck = res.data;
            })
            .catch(this.async_error)
            .then(() => {
            //    processingMsg.destroy();
                this.processing=false;
            });
        },
        debounceUpdateName(val){
            if(this.search_timeout) clearTimeout(this.search_timeout);
            var that=this;
            this.search_timeout = setTimeout(function() {
              that.deck.team_name = val;
              that.updateDeck();
            }, 1000);
        },
        debounceUpdateComment(val){
            if(this.search_timeout) clearTimeout(this.search_timeout);
            var that=this;
            this.search_timeout = setTimeout(function() {
              that.deck.comment = val;
              that.updateDeck();
            }, 1000);
        },
        modal() {
            return $('#deck'+this.id);
        },
        extra_type(type) {
            switch(type) {
                case "base":
                case null:
                    return "";
                default:
                    return "extra_card";
            }
        },
        deck_size_for(type) {
            return this.deck_cards.filter((e) => e.card_type==type).length;
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
        tier_tax() {
            const team = this.mixed_teams.find((t)=> t.name==this.selected_team);
            return (team) ? team['tier_tax'] : 0;
        },
        development() {
            return this.tournament.type=="Development";
        },

        // cards in deck that belong to user collection
        user_deck_cards() {
            return this.deck.cards.concat(this.deck.starter_cards);
        },

        deck_player_cards() {
            return this.deck_cards.filter((e) => e.card_type=="Player")
        },
        deck_player_size() {
            return this.deck_size_for("Player");
        },

        // all cards in deck
        deck_cards() {
            return this.deck.cards.concat(this.deck.starter_cards,this.deck.extra_cards);
        },

        // user collection + starter + extra cards
        collection_cards() {
            return this.coach.cards.concat(this.coach_starter_cards,this.deck.unused_extra_cards);
        },

        // special cards in deck that belong to user
        user_special_plays() {
            return this.user_deck_cards.filter((e) => e.card_type=="Special Play");
        },

        // size of user cards in deck
        deck_size() {
            const special_plays = this.user_special_plays.length;
            const deduct =(special_plays>0) ? 1 : 0
            return this.user_deck_cards.length-deduct;
        },

        extra_card_placeholder() {
            if(this.tournament.phase=="deck_building") {
                return "Extra & Sponsor Cards";
            }
            if(this.tournament.phase=="special_play") {
                return "Special Play & Inducement";
            }
            if(this.tournament.phase=="inducement") {
                return "Special Play & Inducement";
            }
            return ""
        },

        // allows extra cards menu
        extra_allowed() {
            //if(this.tournament.status=="OPEN") {
            //    return false;
            //}
            return true;
        },
        started() {
            if(this.tournament.status=="OPEN") {
                return false;
            }
            return true;
        },
        locked() {
            return this.tournament.phase=="locked";
        },
        sorted_roster() {
            if ('roster' in this.team) {
                return this.team.roster.sort((a,b) => a.number - b.number);
            } else {
                return []
            }
        }
    },
    beforeMount() {
        this.getDeck();
    },
    mounted() {
        this.modal().on('hidden.bs.modal', () => this.$parent.$emit('deckClosed'))
    },
    delimiters: ['[[',']]'],
    props: ['coach','tournament','deck_id','is_owner'],
    template:   `<div class="modal fade deck" :id="'deck'+id" tabindex="-1" role="dialog" aria-labelledby="deck" aria-hidden="true">
                    <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header deck_header">
                            <h5 class="modal-title">Deck for [[coach.short_name]] in [[tournament.name ]]</h5>
                            <button type="button" :disabled="processing" class="btn btn-danger" v-if="is_owner && !deck.commited && !locked && started" @click="commit()">Commit</button>
                            <button type="button" disabled class="btn btn-success" v-if="deck.commited && !locked">Committed</button>
                            <button type="button" disabled class="btn btn-info" v-if="locked">Locked</button>
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                <span aria-hidden="true">&times;</span>
                            </button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-12">
                                    <h5 class="d-inline-block">Team:</h5>
                                    <button v-if="deck.team_name" class="mb-2 ml-3 btn btn-sm btn-info" @click="getTeam(deck.team_name)">Load Team</button>
                                </div>
                                <div class="form-group col-lg-6">
                                    <select class="form-control" v-model="selected_team" :disabled="deck_player_size>0 || !is_owner || locked">
                                        <option selected value="All">Select team</option>
                                        <option v-for="team in mixed_teams" :value="team.name" :key="team.code">[[ team.name ]] ([[ team.races.join() ]])</option>
                                    </select>
                                </div>
                                <div class="form-group col-lg-6">
                                    <input type="text" :disabled="!is_owner || locked" class="form-control" placeholder="Team Name" v-bind:value="deck.team_name" v-on:input="debounceUpdateName($event.target.value)">
                                </div>
                            </div>
                            <div class="row">
                                <div :id="'teamInfoAccordion'+id" class="col-12 mb-3 mt-3" v-if="extra_allowed && 'coach' in team">
                                    <div class="card-header" :id="'teamInfo'+id">
                                        <h5 class="mb-0">
                                            <button class="btn btn-link" data-toggle="collapse" :data-target="'#collapseTeamInfo'+id" aria-expanded="true" aria-controls="collapseTeamInfo">
                                            BB2 Team Details
                                            </button>
                                        </h5>
                                    </div>
                                    <div :id="'collapseTeamInfo'+id" class="collapse hide" aria-labelledby="teamInfo'" :data-parent="'#teamInfoAccordion'+id">
                                        <div class="card-body table-responsive">
                                            <div class="row">
                                                <div class="col-sm-4"><b>Team:</b> [[team.team.name]]</div>
                                                <div class="col-sm-4"><b>Race:</b> [[race(team.team.idraces)]]</div>
                                                <div class="col-sm-4"><b>Coach:</b> [[team.coach.name]]</div>
                                                <div class="col-sm-4"><b>TV:</b> [[team.team.value]]</div>
                                                <div class="col-sm-4"><b>Apothecary:</b> [[ team.team.apothecary ? "Yes" : "No"]]</div>
                                                <div class="col-sm-4"><b>Rerols:</b> [[team.team.rerolls]]</div>
                                                <div class="col-sm-4"><b>Assistant Coaches:</b> [[team.team.assistantcoaches]]</div>
                                                <div class="col-sm-4"><b>Cheerleaders:</b> [[team.team.cheerleaders]]</div>
                                            </div>
                                            <h5 class="mt-2">Roster:</h5>
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
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                <tr v-for="player in sorted_roster" :key="player.id">
                                                    <td>[[player.number]]</td>
                                                    <td>[[player.level]]</td>
                                                    <td>[[player.xp]]</td>
                                                    <td>[[player.value]]</td>
                                                    <td>[[player.name]]</td>
                                                    <td>[[positional_from_api(player.type)]]</td>
                                                    <td><span v-html="player.skills.map((s) => imgs_for_skill(s)).join('')"></span></td>
                                                    <td><span v-html="player.casualties_state.map((c) => imgs_for_skill(c)).join('')"></span></td>
                                                </tr>
                                                </tbody>
                                            </table>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="row mb-3">
                                <div class="col-12">
                                <h5>Sponsor: [[tournament.sponsor]]</h5>
                                </div>
                                <div class="col-12">
                                [[tournament.special_rules]]
                                </div>
                            </div>
                            <div class="row mb-3">
                                <div class="col-12">
                                <h5>Comment:</h5>
                                </div>
                                <div class="col-12">
                                <textarea class="form-control" :disabled="!is_owner || locked" rows="3" v-bind:value="deck.comment" v-on:input="debounceUpdateComment($event.target.value)"></textarea>
                                </div>
                            </div>
                            <div class="row">
                                <div :id="'extraCardsAccordion'+id" class="col-12 mb-3 mt-3" v-if="extra_allowed && is_owner">
                                    <div class="card-header" :id="'extraCards'+id">
                                        <h5 class="mb-0">
                                            <button class="btn btn-link" data-toggle="collapse" :data-target="'#collapseExtraCards'+id" aria-expanded="true" aria-controls="collapseExtraCards">
                                            Extra Cards
                                            </button>
                                        </h5>
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
                                                    <div class="col-md-6 pt-1 pl-4">
                                                    <h6 class="extra_card">[[card.name]]</h6>
                                                    </div>
                                                    <div class="col-md-6">
                                                        <button type="button" :disabled="processing || !is_owner || locked" class="btn-sm mb-1 btn btn-danger btn-block" @click="removeExtraCard(card)">Remove</button>
                                                    </div>
                                                </template>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-lg-6">
                                    <div class="row mt-1">
                                    <div class="col-6">
                                        <h5>Collection</h5>
                                    </div>
                                    <div class="col-6">
                                        <div class="custom-control custom-checkbox mr-sm-2 text-right">
                                            <input type="checkbox" class="custom-control-input" :id="'sptoggle'+id" v-model="show_starter">
                                            <label class="custom-control-label" :for="'sptoggle'+id">Toggle Starter Pack</label>
                                        </div>
                                    </div>
                                    </div>
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
                                                            <th class="d-none d-xl-table-cell">Rarity</th>
                                                            <th class="d-xl-none">R</th>
                                                            <th class="d-none d-xl-table-cell">Value</th>
                                                            <th class="d-xl-none">V</th>
                                                            <th>Name</th>
                                                            <th v-if="ctype=='Training' || ctype=='Special Play'">Skills</th>
                                                            <th v-if="ctype=='Player'">Race</th>
                                                            <th v-if="ctype=='Player' || ctype=='Training'" class="d-none d-sm-table-cell">Subtype</th>
                                                        </tr>
                                                        </thead>
                                                        <tbody>
                                                        <tr v-if="!isInDeck(card)" @click="addToDeck(card)" v-for="card in sortedCardsWithoutQuantity(collection_cards,ctype)" :key="card.id" :class="[rarityclass(card.rarity), extra_type(card.deck_type)]">
                                                            <td><img class="rarity" :src="'static/images/'+card.rarity+'.jpg'" :alt="card.rarity" :title="card.rarity" width="20" height="25" /></td>
                                                            <td>[[ card.value ]]</td>
                                                            <td :title="card.description">[[ card.name ]]</td>
                                                            <td v-if="ctype=='Training' || ctype=='Special Play'"><span v-html="skills_for(card)"></span></td>
                                                            <td v-if="ctype=='Player'">[[ card.race ]]</td>
                                                            <td v-if="ctype=='Player' || ctype=='Training'" class="d-none d-sm-table-cell">[[ card.subtype ]]</td>
                                                        </tr>
                                                        </tbody>
                                                    </table>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-lg-6">
                                    <div class="row mt-1">
                                    <div class="col-4">
                                        <h5>Deck [[deck_size]]/[[tournament.deck_limit]]</h5>
                                    </div>
                                    <div class="col-4 text-center">
                                        <h5>Value: [[ cardsValue(user_deck_cards) + tier_tax ]]</h5>
                                    </div>
                                    <div class="col-4">
                                        <div class="custom-control custom-checkbox mr-sm-2 text-right">
                                            <input type="checkbox" class="custom-control-input" :id="'raritytoggle'+id" v-model="rarity_order">
                                            <label class="custom-control-label" :for="'raritytoggle'+id">Toggle rarity order</label>
                                        </div>
                                    </div>
                                    </div>
                                    <div :id="'accordionCardsDeck'+id">
                                        <div class="card" v-for="ctype in card_types">
                                            <div class="card-header" :id="ctype.replace(/\\s/g, '')+'CardsDeck'+id">
                                                <h5 class="mb-0">
                                                    <button class="btn btn-link" data-toggle="collapse" :data-target="'#collapseDeck'+ctype.replace(/\\s/g, '')+id" aria-expanded="true" :aria-controls="'collapse'+ctype.replace(/\\s/g, '')">
                                                    [[ ctype ]] Cards ([[deck_size_for(ctype)]])
                                                    </button>
                                                </h5>
                                            </div>
                                            <div :id="'collapseDeck'+ctype.replace(/\\s/g, '')+id" class="deck_ctype collapse show" :aria-labelledby="ctype.replace(/\\s/g, '')+'Cards'" :data-parent="'#accordionCardsDeck'+id">
                                                <div class="card-body table-responsive">
                                                    <table class="table  table-striped table-hover">
                                                        <thead>
                                                        <tr>
                                                            <th class="d-none d-xl-table-cell">Rarity</th>
                                                            <th class="d-xl-none">R</th>
                                                            <th class="d-none d-xl-table-cell">Value</th>
                                                            <th class="d-xl-none">V</th>
                                                            <th>Name</th>
                                                            <th v-if="ctype=='Training' || ctype=='Special Play'">Skills</th>
                                                            <th v-if="ctype=='Player'">Race</th>
                                                            <th v-if="ctype=='Player' || ctype=='Training'" class="d-none d-sm-table-cell">Subtype</th>
                                                        </tr>
                                                        </thead>
                                                        <tbody>
                                                        <template v-for="(card,index) in sortedCardsWithoutQuantity(deck_cards,ctype,false)">
                                                        <tr @click="removeFromDeck(card)" :key="card.id" :class="[rarityclass(card.rarity), extra_type(card.deck_type)]">
                                                            <td><img class="rarity" :src="'static/images/'+card.rarity+'.jpg'" :alt="card.rarity" :title="card.rarity" width="20" height="25" /></td>
                                                            <td>[[ card.value ]]</td>
                                                            <td :title="card.description">[[ card.name ]]</td>
                                                            <td v-if="ctype=='Training' || ctype=='Special Play'"><span v-html="skills_for(card)"></span></td>
                                                            <td v-if="ctype=='Player'">[[ card.race ]]</td>
                                                            <td v-if="ctype=='Player' || ctype=='Training'" class="d-none d-sm-table-cell">[[ card.subtype ]]</td>
                                                        <tr v-if="ctype=='Training'" :class="[rarityclass(card.rarity)]">
                                                            <th colspan="1">Assigned to:</th>
                                                            <td colspan="3">
                                                                <select class="form-control" v-model="card.assigned_to" v-on:click.stop @change="assignCard(card)" :disabled="!is_owner || locked">
                                                                    <option default value="">Select Player</option>
                                                                    <option v-for="(card,index) in deck_player_cards" :key="index" :value="card.name+index">[[index+1]]. [[ card.name ]]</option>
                                                                </select>
                                                            </td>
                                                            <td class="d-none d-sm-table-cell"></td>
                                                        </tr>
                                                        </template>
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