import injuryPicker from './injury_picker.js';

export default {
    name: 'deck',
    components: {
        'injury-picker': injuryPicker,
    },
    data () {
      return {
          processing:false,
          selected_team:"All",
          show_starter: 1,
          rarity_order: 1,
          extra_card:"",
          deck: {
              cards:[],
              extra_cards:[],
              unused_extra_cards:[],
              mixed_team:"",
              team_name:"",
              comment:"",
              search_timeout: null,
              id:null,
              log:""
          },
          team:{},
          team_check: {
            apothecary: {
                msg: "OK",
                value: true
            },
            rerolls: {
                msg: "OK",
                value: true
            },
            roster: {
                msg: "OK",
                value: true
            }
          },
          phases: {
            deck_building:"Deck Building",
            locked:"Locked",
            special_play:"Special Play",
            inducement:"Inducement",
            reaction:"Reaction",
            blood_bowl:"Blood Bowl",
          }
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

            // check limits if not added by extra cards interface
            if((card.deck_type!="extra" && card.deck_type!="extra_inducement")) {
                // ignore first SP card
                if (card.template.card_type!="Special Play" || this.user_special_plays.length!=0) {
                    if(this.deck_size==this.tournament.deck_limit) {
                        this.flash("Cannot add card - deck limit reached!", 'error',{timeout: 3000});
                        return false;
                    }
                }
                if(this.deck_value + card.template.value > this.tournament.deck_value_limit) {
                    this.flash("Cannot add card - deck value limit reached!", 'error',{timeout: 3000});
                    return false;
                }
            }

            if(this.selected_team=="All") {
                this.flash("Cannot add card - team not selected!", 'error',{timeout: 3000});
                return false;
            }
            if(this.deck_player_size>=16 && card.template.card_type=="Player") {
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
                this.deck=res.data;
                this.selected_team = (this.deck.mixed_team=="") ? "All" : this.deck.mixed_team;
                this.modal().modal('show');
            })
            .catch(this.async_error)
            .then(() => {
                processingMsg.destroy();
            });
        },
        getTeam(name) {
            const path = "/teams/"+encodeURIComponent(name);
            const processingMsg = this.flash("Loading team...", 'info');
            axios.get(path)
            .then((res) => {
                if (res.data==false) {
                    this.flash("Team "+name+" does not exist", 'error',{timeout: 3000});     
                } else {
                    this.team=res.data;
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
                    msg: "OK",
                    value: true
                },
                rerolls: {
                    msg: "OK",
                    value: true
                },
                roster: {
                    msg: "OK",
                    value: true
                }
              };
        },
        checkApo() {
            if(this.team.team.apothecary != this.hasApo()) {
                this.team_check['apothecary']['value'] = false;
                if(this.team.team.apothecary) {
                    this.team_check['apothecary']['msg'] = "Apothecary should not be included";
                }
                else {
                    this.team_check['apothecary']['msg'] = "Apothecary is missing";
                }
            }
        },
        checkRRs() {
            if(this.team.team.rerolls != this.numberOfRerolls()) {
                this.team_check['rerolls']['value'] = false;
                this.team_check['rerolls']['msg'] = "Number of RRs do not match";
            }
        },
        checkRoster() {
            // roster size
            if(this.team.roster.length != this.deck_cards.filter(c => c.template.card_type=="Player").length) {
                this.team_check['roster']['value'] = false;
                this.team_check['roster']['msg'] = "Number of players does not match";
            }
            let ignore = [];

            this.team.roster.forEach((player) => {
                player.check = {
                    value: false,
                    msg: "Player not found"
                }
                this.deck_cards.forEach((c) => {
                    // if the cards has been linked with another -> skip
                    if (ignore.includes(this.card_id_or_uuid(c)))
                      return
                    // if the player is already valid -> skip
                    if(player.check.value)
                      return
                    // is not a player card -> skip
                    if(c.template.card_type!="Player")
                      return
                    // positional check
                    //console.log(this.positional_from_api(player.type))
                    //console.log(this.positional_mapping(c))
                    if(!this.positional_mapping(c).includes(this.positional_from_api(player.type)))
                      return
                    // skill check
                    //console.log(this.skill_names_for_player_card(c).concat(this.assigned_skills(c)));
                    //console.log(player.skills)
                    if(!this.equal_sets(this.skill_names_for_player_card(c).concat(this.assigned_skills(c)), player.skills))
                        return
                    // injury check
                    if(!this.equal_sets(this.assigned_injuries(c), player.casualties_state))
                        return
                    
                    // if we came this far the player is valid
                    ignore.push(this.card_id_or_uuid(c))
                    player.check = {
                        value: true,
                        msg: "Player found"
                    }
                })
            })
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
            if(player.check.value)
                return true
            return false;
        },
        equal_sets(set1,set2) {
            let BreakException = {};
            if(set1.length != set2.length)
              return false;
            try {
                set1.forEach((i1) => {
                    let count1 = set1.filter((e) => e == i1).length;
                    let count2 = set2.filter((e) => e == i1).length;
                    if(count1!=count2) throw BreakException;
                })
            } catch (e) {
                if (e !== BreakException) throw e;
                return false;
            }
            return true
        },
        positional_mapping(card) {
            let races = card.template.race.split("/");
            let positionals = races.map((race) => {
                race = race.replace(/\s/g, '');
                if (race == "Bretonnian") {
                    race = "Bretonnia";
                }
                let position = card.template.position;
                position = position.replace(/\s/g, '');
                return race + " " + position;
            });
            return positionals;
        },
        hasApo() {
            let race = this.race(this.team.team.idraces);
            // AU has no apo
            if(race == "Afterlife United") {
                return false;
            }
            if(this.deck.cards.find((c) => ["Apothecary", "Clever Management", "Inspirational Boss"].includes(c.template.name))!=undefined) {
                return true;
            }
            return false;
        },
        numberOfRerolls() {
            // harcoded
            let r1 = this.deck.cards.filter((c) => c.template.name == "Inspirational Boss").length * 2;
            let r2 = this.deck.cards.filter((c) => c.template.name == "Motivational Speaker").length * 2;
            let r3 = this.deck.cards.filter((c) => c.template.name == "Clever Management").length * 1;
            return this.deck.cards.filter((c) => c.template.name == "Re-roll").length + r1 + r2 + r3;
        },
        cloneExtraCard(card) {
            this.addExtraCard(card.template.name);
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
                this.removeAllInjuries(card);
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
            let found_card = training_cards.find((c)=> {return this.get_card_assignment(c).length==0 || this.get_card_assignment(c).includes(undefined) || this.get_card_assignment(c).includes(null)});
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
                if(card.id && card.deck_type!="extra" && card.deck_type!="extra_inducement") {
                    const check = (this.development) ? "in_development_deck" : "in_imperium_deck";
                    ccard = this.coach.cards.find((c) => c.id == card.id);
                    ccard[check] = false;
                }
                this.removeAllInjuries(card);
            })
            .catch(this.async_error)
            .then(() => {
                processingMsg.destroy();
                this.processing=false;
            });
        },
        phaseDone() {
            this.deck.phase_done = true;
            this.updateDeck();
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
                injury_map:this.deck.injury_map,
                phase_done:this.deck.phase_done,
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
            return this.deck_cards.filter((e) => e.template.card_type==type).length;
        },
        card_id_or_uuid(card) {
            if(card.id) {
                return String(card.id);
            } else {
                return String(card.uuid);
            }
        },
        assigned_cards(card) {
            return this.deck_cards.filter((c) => this.get_card_assignment(c).includes(String(this.card_id_or_uuid(card))));
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
                let skills = this.skill_names_for(c);
                return skills.map((s) => this.skill_to_api_skill(s));
            }).flat();
        },
        deck_skills_for(card) {
            const assigned_cards = this.assigned_cards(card);
            let injuries;
            if (this.deck.injury_map[this.card_id_or_uuid(card)]) {
                injuries = this.deck.injury_map[this.card_id_or_uuid(card)];
            } else {
                injuries = [];
            }
            return assigned_cards.map((c) => {
                let double = false; 
                let skills = this.skill_names_for(c);
                skills.forEach((skill) => {
                    if(this.is_skill_double(card,skill)) {
                        double = true;
                    }
                })
                return this.skills_for(c,double);
            }).join("") + injuries.map((c) => this.imgs_for_skill(c)).join('');
        },
        get_card_assignment(card) {
            if (card.assigned_to_array[this.deck.id]) {
                return card.assigned_to_array[this.deck.id];
            } else {
                return [];
            }
        },
        is_tr_card_assigned_as_double(tr_card) {
            let assigned_to = this.get_card_assignment(tr_card);
            let is_double = false;
            assigned_to.forEach((id) => {
                const p_card = this.deck_cards.find((c) => {
                    if (String(c.id) == String(id) || String(c.uuid) == String(id))
                      return true;
                });
                if (p_card) {
                    let skills = this.skill_names_for(tr_card);
                    skills.forEach((skill) => {
                        if(this.is_skill_double(p_card,skill)) {
                            is_double = true;
                        }
                    })
                }
            });
            return is_double;
        },
        doubles_count(card) {
            const assigned_cards = this.deck_cards.filter((c) => this.get_card_assignment(c).includes(String(this.card_id_or_uuid(card))));
            let doubles = 0;

            assigned_cards.forEach((tcard) => {
                // ignore extra cards
                if(tcard.deck_type=="extra") {
                    return;
                }
                let skills = this.skill_names_for(tcard);
                let card_doubles = 0;
                // only count 1 double for a multiskill card
                skills.forEach((skill) => {
                    if(this.is_skill_double(card,skill)) {
                        card_doubles = 1;
                    }
                })
                doubles += card_doubles;
            })
            return doubles;
        },
        is_guarded(card) {
            if (card.template.card_type!="Player")
              return false;
            const assigned_cards = this.deck_cards.filter((c) => this.get_card_assignment(c).includes(String(this.card_id_or_uuid(card))));
            if (assigned_cards.find((c) => ["Bodyguard", "Hired Muscle", "Personal Army"].includes(c.template.name))!=undefined)
              return true;
            return false;
        },
        injuryPickerOpened(card) {
            if (card.cas_pick) {
                return false;
            }
            return true;
        },
        openInjuryPicker(card) {
            card.cas_pick = true;
            this.$forceUpdate();
        },
        addInjury(card,injury) {
            let id = this.card_id_or_uuid(card);
            if(this.deck.injury_map[id]) {

            } else {
                this.deck.injury_map[id] = [];
            }
            if(injury!="" && injury!="X") {
                this.deck.injury_map[id].push(injury);
            }
            card.cas_pick = false;
            if(injury=="X") {
                this.removeAllInjuries(card);
            } else {
                this.updateDeck();
            }
        },
        removeAllInjuries(card) {
            let id = this.card_id_or_uuid(card);
            this.deck.injury_map[id] = [];
            this.updateDeck();
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
            return 'C'+this.coach.id+'T'+this.tournament.tournament_id;
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
            return this.deck.cards;
        },

        assignable_deck_player_cards() {
            return this.deck_player_cards.filter((e) => !["Legendary","Inducement","Unique"].includes(e.template.rarity));
        },

        deck_player_cards() {
            return this.deck_cards.filter((e) => e.template.card_type=="Player");
        },

        deck_player_size() {
            return this.deck_size_for("Player");
        },

        // all cards in deck
        deck_cards() {
            return this.deck.cards.concat(this.deck.extra_cards);
        },

        // user collection + extra cards
        collection_cards() {
            return this.coach.cards.concat(this.deck.unused_extra_cards);
        },

        // special cards in deck that belong to user
        user_special_plays() {
            return this.user_deck_cards.filter((e) => e.template.card_type=="Special Play");
        },

        // size of user cards in deck
        deck_size() {
            const special_plays = this.user_special_plays.length;
            const deduct =(special_plays>0) ? 1 : 0
            return this.user_deck_cards.length-deduct;
        },

        extra_card_placeholder() {
            if(this.tournament.phase=="deck_building") {
                return "Type exact name of Sponsor Card and click Add";
            }
            if(this.tournament.phase=="special_play") {
                return "Type exact name of Card and click Add";
            }
            if(this.tournament.phase=="inducement") {
                return "Type exact name of Inducement Card and click Add";
            }
            if(this.tournament.phase=="reaction") {
                return "Type exact name of Card and click Add";
            }
            return ""
        },
        doneable_phase() {
            if(["special_play","inducement"].includes(this.tournament.phase)) {
                return true;
            }
            return false;
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
            return this.tournament.phase=="locked" || this.tournament.phase=="blood_bowl";
        },
        sorted_roster() {
            if ('roster' in this.team) {
                return this.team.roster.sort((a,b) => a.number - b.number);
            } else {
                return []
            }
        },
        deck_doubles_count() {
            let count = 0;
            this.deck_cards.forEach((card) => {
                if(card.template.card_type=="Training" && card.deck_type!="extra") {
                    count += this.is_tr_card_assigned_as_double(card) ? 1 : 0;
                }
            });
            return count;
        },
        deck_value() {
            let value = this.user_deck_cards.reduce((total, e)=> {  
                return total+e.template.value;
            },0);
            return value + this.tier_tax;
        },
        has_deck_upgrade() {
            return this.deck_upgrades.length > 0;
        },
        deck_upgrades() {
            return this.coach.cards.filter((c) => c.template.subtype == "Deck Upgrade");
        }
    },
    beforeMount() {
        this.getDeck();
        this.$parent.$emit('reloadTournament');
    },
    mounted() {
        this.modal().on('hidden.bs.modal', () => this.$parent.$emit('deckClosed'));
        $(function () {
            $('[data-toggle="tooltip"]').tooltip();
        })
    },
    delimiters: ['[[',']]'],
    props: ['coach','tournament','deck_id','is_owner'],
    template:   `<div class="modal fade deck" :id="'deck'+id" tabindex="-1" role="dialog" aria-labelledby="deck" aria-hidden="true">
                    <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header deck_header">
                            <h5 class="modal-title">Deck for [[coach.short_name]] in [[tournament.name]] - Phase: [[ phases[tournament.phase] ]]
                                <template v-if="doneable_phase">
                                    <button v-if="deck.phase_done" type="button" disabled class="btn btn-success">Done</button>
                                    <button v-if="!deck.phase_done && is_owner" type="button" class="btn btn-danger" @click="phaseDone()">Done</button>
                                </template>
                            </h5>
                            <button type="button" :disabled="processing" class="btn btn-danger" v-if="is_owner && !deck.commited && !locked && started" @click="commit()">Commit</button>
                            <button type="button" disabled class="btn btn-success" v-if="deck.commited && !locked">Committed</button>
                            <button type="button" disabled class="btn btn-info" v-if="locked">Locked</button>
                            <button type="button" disabled class="btn btn-info" v-if="!started">Not Started</button>
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
                                        <option v-for="team in mixed_teams" :value="team.name" :key="team.code">[[ team.name ]] ([[ team.races.join() ]])</option>
                                    </select>
                                </div>
                                <div class="form-group col-lg-6">
                                    <input type="text" :disabled="!is_owner || locked" class="form-control" placeholder="Team Name (max 25 characters)" maxlength="25" v-bind:value="deck.team_name" v-on:input="debounceUpdateName($event.target.value)">
                                </div>
                            </div>
                            <div class="row">
                                <div :id="'teamInfoAccordion'+id" class="col-12 mb-3 mt-3" v-if="extra_allowed && 'coach' in team">
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
                                                <div class="col-sm-4"><b>Team:</b> [[team.team.name]]</div>
                                                <div class="col-sm-4"><b>Race:</b> [[race(team.team.idraces)]]</div>
                                                <div class="col-sm-4"><b>Coach:</b> [[team.coach.name]]</div>
                                                <div class="col-sm-4"><b>TV:</b> [[team.team.value]]</div>
                                                <div class="col-sm-4">
                                                <b>Apothecary:</b> [[ team.team.apothecary ? "Yes" : "No"]]
                                                    <span v-if="team_check.apothecary.value" class="deck_valid_check">✓</span>
                                                    <span :title="team_check.apothecary.msg" v-else class="deck_invalid_check">✗</span>
                                                </div>
                                                <div class="col-sm-4"><b>Rerolls:</b> [[team.team.rerolls]]
                                                    <span v-if="team_check.rerolls.value" class="deck_valid_check">✓</span>
                                                    <span :title="team_check.rerolls.msg" v-else class="deck_invalid_check">✗</span>
                                                </div>
                                                <div class="col-sm-4"><b>Assistant Coaches:</b> [[team.team.assistantcoaches]]</div>
                                                <div class="col-sm-4"><b>Cheerleaders:</b> [[team.team.cheerleaders]]</div>
                                                <div class="col-sm-4"><b>Stadium Enhancement:</b> [[stadium_enhacement(team.team)]]</div>
                                            </div>
                                            <h6 class="mt-2">Roster:
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
                                                    <td>[[player.number]]</td>
                                                    <td>[[player.level]]</td>
                                                    <td>[[player.xp]]</td>
                                                    <td>[[player.value]]</td>
                                                    <td>[[player.name]]</td>
                                                    <td>[[positional_from_api(player.type)]]</td>
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
                                <h6>Sponsor: [[tournament.sponsor]]</h6>
                                </div>
                                <div class="col-12">
                                [[tournament.special_rules]]
                                </div>
                            </div>
                            <div class="row mb-3">
                                <div class="col-12">
                                <h6>Comment:</h6>
                                </div>
                                <div class="col-12">
                                <textarea class="form-control" :disabled="!is_owner || locked" rows="3" v-bind:value="deck.comment" v-on:input="debounceUpdateComment($event.target.value)"></textarea>
                                </div>
                            </div>
                            <div class="row">
                                <div :id="'extraCardsAccordion'+id" class="col-12 mb-3 mt-3">
                                    <div class="card" v-if="extra_allowed && is_owner">
                                    <div class="card-header" :id="'extraCards'+id">
                                        <h6 class="mb-0">
                                            <button class="btn btn-link" data-toggle="collapse" :data-target="'#collapseExtraCards'+id" aria-expanded="true" aria-controls="collapseExtraCards">
                                            <span data-toggle="tooltip" data-placement="top" title="Use this to add Sponsor, Inducement or Reaction Cards to the collection for this tournament only">Sponsor & Extra Cards</span>
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
                                                    <div class="col-md-6 pt-1 pl-4">
                                                    <h6 class="extra_card">[[card.template.name]]</h6>
                                                    </div>
                                                    <div class="col-md-3">
                                                        <button type="button" :disabled="processing || !is_owner || locked" class="btn-sm mb-1 btn btn-success btn-block" @click="cloneExtraCard(card)">Clone</button>
                                                    </div>
                                                    <div class="col-md-3">
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
                                                <template v-for="line in deck.log.split(/\\r?\\n/).reverse().slice(1)">
                                                [[line]] <br>
                                                </template>
                                            </div>
                                        </div>
                                    </div>
                                    </div>
                                    <div v-if="has_deck_upgrade" class="card">
                                    <div class="card-header" :id="'deck_upgrade'+id">
                                        <h6 class="mb-0">
                                            <button class="btn btn-link" data-toggle="collapse show" :data-target="'#collapsedeckupgrade'+id" aria-expanded="true" aria-controls="collapsedeckupgrade">
                                            Deck Upgrade
                                            </button>
                                        </h6>
                                    </div>
                                    <div v-if="has_deck_upgrade" :id="'collapsedeckupgrade'+id" class="collapse hide" aria-labelledby="log'" :data-parent="'#extraCardsAccordion'+id">
                                        <div class="card-body">
                                            <div class="row" v-for="card in deck_upgrades">
                                                <div class="col-md-3">
                                                    <b>[[card.template.name]]:</b>
                                                </div>
                                                <div class="col-md-9">
                                                    [[card.template.description]]
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-lg-6">
                                    <div class="row mt-1 deck_header">
                                    <div class="col-6">
                                        <h6>Collection</h6>
                                    </div>
                                    <div class="col-6">
                                        <div class="custom-control custom-checkbox mr-sm-2 text-right">
                                            <input type="checkbox" class="custom-control-input" :id="'sptoggle'+id" v-model="show_starter">
                                            <label class="custom-control-label" :for="'sptoggle'+id">Toggle Starter Pack</label>
                                        </div>
                                    </div>
                                    </div>
                                    <div :id="'accordionCardsCollection'+id">
                                        <div class="card" v-for="ctype in deck_card_types">
                                            <div class="card-header" :id="ctype.replace(/\\s/g, '')+'CardsCollection'+id">
                                                <h6 class="mb-0">
                                                    <button class="btn btn-link" data-toggle="collapse" :data-target="'#collapseCollection'+ctype.replace(/\\s/g, '')+id" aria-expanded="true" :aria-controls="'collapse'+ctype.replace(/\\s/g, '')">
                                                    [[ ctype ]] Cards
                                                    </button>
                                                </h6>
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
                                                        <tr v-if="!isInDeck(card)" @click="addToDeck(card)" v-for="card in sortedCardsWithoutQuantity(collection_cards,ctype)" :key="card.id" :class="[rarityclass(card.template.rarity), extra_type(card.deck_type)]">
                                                            <td><img class="rarity" :src="'static/images/'+card.template.rarity+'.jpg'" :alt="card.template.rarity" :title="card.template.rarity" width="20" height="25" /></td>
                                                            <td>[[ card.template.value ]]</td>
                                                            <td :title="card.template.description">[[ card.template.name ]]</td>
                                                            <td v-if="ctype=='Training' || ctype=='Special Play'"><span v-html="skills_for(card)"></span></td>
                                                            <td v-if="ctype=='Player'">[[ card.template.race ]]</td>
                                                            <td v-if="ctype=='Player' || ctype=='Training'" class="d-none d-sm-table-cell">[[ card.template.subtype ]]</td>
                                                        </tr>
                                                        </tbody>
                                                    </table>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-lg-6">
                                    <div class="row mt-1 deck_header">
                                    <div class="col-3">
                                        <h6>Deck [[deck_size]]/[[tournament.deck_limit]]</h6>
                                    </div>
                                    <div class="col-3 text-center">
                                        <h6>Value: [[ deck_value ]]/[[ tournament.deck_value_limit ]]</h6>
                                    </div>
                                    <div class="col-3 text-center">
                                        <h6>Doubles: [[ deck_doubles_count ]]</h6>
                                    </div>
                                    <div class="col-3">
                                        <div class="custom-control custom-checkbox mr-sm-2 text-right">
                                            <input type="checkbox" class="custom-control-input" :id="'raritytoggle'+id" v-model="rarity_order">
                                            <label class="custom-control-label" :for="'raritytoggle'+id">Rarity order</label>
                                        </div>
                                    </div>
                                    </div>
                                    <div :id="'accordionCardsDeck'+id">
                                        <div class="card" v-for="ctype in deck_card_types">
                                            <div class="card-header" :id="ctype.replace(/\\s/g, '')+'CardsDeck'+id">
                                                <h6 class="mb-0">
                                                    <button class="btn btn-link" data-toggle="collapse" :data-target="'#collapseDeck'+ctype.replace(/\\s/g, '')+id" aria-expanded="true" :aria-controls="'collapse'+ctype.replace(/\\s/g, '')">
                                                    [[ ctype ]] Cards ([[deck_size_for(ctype)]])
                                                    </button>
                                                </h6>
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
                                                        <tr @click="removeFromDeck(card)" :key="card.id" :class="[rarityclass(card.template.rarity), extra_type(card.deck_type)]">
                                                            <td><img class="rarity" :src="'static/images/'+card.template.rarity+'.jpg'" :alt="card.template.rarity" :title="card.template.rarity" width="20" height="25" /></td>
                                                            <td>[[ card.template.value ]]</td>
                                                            <td :title="card.template.description">[[ card.template.name ]]<span v-if="is_guarded(card)" title="No Special Play effects possible">&#128170;</span></td>
                                                            <td v-if="ctype=='Training' || ctype=='Special Play'"><span v-html="skills_for(card)"></span></td>
                                                            <td v-if="ctype=='Player'">[[ card.template.race ]]</td>
                                                            <td v-if="ctype=='Player' || ctype=='Training'" class="d-none d-sm-table-cell">[[ card.template.subtype ]]</td>
                                                        </tr>
                                                        <tr :class="[rarityclass(card.template.rarity)]" v-for="idx in number_of_assignments(card)">
                                                            <th colspan="1">Assigned to:</th>
                                                            <td colspan="3">
                                                                <select v-if="ctype=='Training'" class="form-control" v-model="card.assigned_to_array[deck.id][idx-1]" v-on:click.stop @change="assignCard(card)" :disabled="!is_owner || locked">
                                                                    <option default :value="null">Select Player</option>
                                                                    <option v-for="(card,index) in assignable_deck_player_cards" :key="index" :value="card_id_or_uuid(card)">[[index+1]]. [[ card.template.name ]]</option>
                                                                </select>
                                                                <select v-else class="form-control" v-model="card.assigned_to_array[deck.id][idx-1]" v-on:click.stop @change="assignCard(card)" :disabled="!is_owner || locked">
                                                                    <option default :value="null">Select Player</option>
                                                                    <option v-for="(card,index) in deck_player_cards" :key="index" :value="card_id_or_uuid(card)">[[index+1]]. [[ card.template.name ]]</option>
                                                                </select>
                                                            </td>
                                                            <td class="d-none d-sm-table-cell"></td>
                                                        </tr>
                                                        <tr v-if="ctype=='Player'" :class="[rarityclass(card.template.rarity)]">
                                                            <th colspan="1">Skills:</th>
                                                            <td colspan="2">
                                                                <span v-html="skills_for(card)"></span>
                                                                <span v-html="deck_skills_for(card)"></span>
                                                            </td>
                                                            <td>
                                                                <img v-if="injuryPickerOpened(card)" @click="openInjuryPicker(card)" class="skill_icon skill_single" src="https://cdn2.rebbl.net/images/skills/SmashedHand.png" title="Add Injury">
                                                                <injury-picker v-else v-on:injured="addInjury(card,$event)"></injury-picker>
                                                            </td>
                                                            <td class="d-none d-sm-table-cell"><b>Doubles:</b> [[doubles_count(card)]]</td>
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