import confirmationButton from './confirmation-button.js';

export default {
    name: 'singup-modal',
    delimiters: ['[[',']]'],
    props: ['user'],
    components: {
        'confirmation-button': confirmationButton,
    },
    data () {
      return {
          processing:false,
          old_cards: [],
          pack_cards: [],
          migration_on:false,
          selected_team:"All",
          show_starter:false,
          rarity_order:1,
          max_value: 35,
          max_cards: 5,
          max_legends:1,
          migrated:false,
      }
    },
    methods: {
        newCoach() {
            const path = "/coaches";
            const processingMsg = this.flash("Initializing coach...", 'info');
            axios.post(path)
            .then((res) => {
                this.$parent.$emit('signedUpCoach', res.data);
            })
            .catch(this.async_error)
            .then(() => {
                processingMsg.destroy();
            });
        },
        pull_inactive_cards() {
            const path = "/coaches/"+this.user.coach.id+"/cards/inactive";
            const processingMsg = this.flash("Getting last season cards...", 'info');
            axios.get(path)
            .then((res) => {
                this.old_cards = res.data;
            })
            .catch(this.async_error)
            .then(() => {
                processingMsg.destroy();
            });
        },
        async_error(error) {
            if (error.response) {
                let message = (error.response.data.message) ? error.response.data.message : "Unknown error: "+error.response.status;
                this.flash(message, 'error',{timeout: 3000});
            } else {
                console.error(error);
            }
        },
        modal() {
            return $('#signup_modal');
        },
        open() {
            this.modal().modal({show:true, backdrop: 'static', keyboard: false});
        },
        close() {
            this.modal().modal('hide');
        },
        migrate() {
            this.pull_inactive_cards();
            this.migration_on=true;
        },
        activate() {
            const path = "/coaches/"+this.user.coach.id+"/activate";
            const processingMsg = this.flash("Activating coach...", 'info');
            axios.put(path,{card_ids: this.to_migrate})
            .then((res) => {
                this.$parent.$emit('signedUpCoach', res.data);
                this.migration_on=false;
                this.migrated = true;
            })
            .catch(this.async_error)
            .then(() => {
                processingMsg.destroy();
            });
        },
        addToMigrationPack(card) {
            if(this.canAdd(card)) {
                this.pack_cards.push(card);
                let idx =  this.old_cards.indexOf(card);
                this.old_cards.splice(idx,1);
            }
        },
        removeFromMigrationPack(card) {
            if(this.canRemove(card)) {
                this.old_cards.push(card);
                let idx =  this.pack_cards.indexOf(card);
                this.pack_cards.splice(idx,1);
            }
        },
        canRemove(card) {
            if(this.uniques.includes(card)) {
                return false;
            }
            return true;
        },
        canAdd(card) {
            // check value
            if(this.pack_value+card.template.value > this.max_value) {
                this.flash("Cannot add card. Max value limit is "+this.max_value+"!","error",{timeout: 3000});
                return false;
            }
            if(this.pack_size+1 > this.max_cards) {
                this.flash("Cannot add card. Max card limit is "+this.max_cards+"!","error",{timeout: 3000});
                return false;
            }
            if(card.template.rarity=="Legendary" && this.pack_cards.filter((c) => c.template.rarity=="Legendary").length==this.max_legends) {
                this.flash("Cannot add card. Max Legendary limit is "+this.max_legends+"!","error",{timeout: 3000});
                return false;
            }
            return true;
        }
    },
    computed: {
        is_user() {
            if(this.user.id) {
                return true;
            }
            return false;
        },
        is_coach() {
            if(this.user.coach && this.user.coach.id) {
                return true;
            }
            return false;
        },
        is_active() {
            if(this.is_coach && this.user.coach.deleted == false) {
                return true;
            }
            return false;
        },
        eligible_cards() {
            return this.old_cards.filter((card) => {
                if(card.is_starter)
                  return false;
                if(card.template.rarity=="Unique")
                  return false;
                return true;
            });
        },
        uniques() {
            return this.old_cards.filter((card) => {
                if(card.template.rarity=="Unique" && card.template.name!="Beta Prepared") {
                    return true;
                }
                return false;
            })
        },
        pack_size() {
            return this.pack_cards.length;
        },
        pack_value() {
            return this.pack_cards.reduce((total, e)=> { 
              return total+e.template.value;
            },0);
        },
        to_migrate() {
            return this.pack_cards.concat(this.uniques).map((c) => c.id);
        }
    },  
    template:   `<div class="modal fade signup" id="signup_modal" tabindex="-1" role="dialog" aria-labelledby="signup_modal" aria-hidden="true">
                    <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h4 v-if="!is_user" class="modal-title">Authenticate</h4>
                            <h4 v-if="is_user && !is_coach" class="modal-title">New Coach</h4>
                            <h4 v-if="is_active" class="modal-title">Done</h4>
                            <h4 v-if="is_coach && !is_active" class="modal-title">Sign back</h4>
                            <confirmation-button v-if="migration_on"
                                :messages="['Confirm','Are you sure?','I will accept no complaints! Ok?', 'You done goofed!']"
                                v-on:confirmation-success="activate()"
                                >Confirm</confirmation-button>
                        </div>
                        <div class="modal-body">
                            <template v-if="!is_user">
                                <p>To be able to use this site you need to <a href="/signin">Sign in</a> using Discord credentials first!</p>
                            </template>
                            <template v-if="is_user && !is_coach">
                                <h5>Welcome to REBBL Imperium!</h5>
                                <p>We are not sure how it is possible that you have not played Imperium yet!!!
                                To fix that <a href="#" @click="newCoach()">initialize</a> your Imperium coach account please!</p>
                            </template>
                            <template v-if="is_active">
                                <h5 v-if="!migrated">Coach account has been succefully initialized!</h5>
                                <h5 v-else>Coach account has been succefully migrated!</h5>
                                
                                <p>Check your info tab for your initial bank balance and free pack. Then head to <a target="_blank" href="https://discord.gg/hdSQhRf">Imperium Discord</a>
                                to generate your packs.
                                </p>
                                <button type="button" class="btn btn-success" @click="close()">Close</button>
                            </template>
                            <template v-if="is_coach && !is_active">
                                <h5>Welcome back to REBBL Imperium!</h5>
                                <p>We know you missed your dose of this mad game. As returning coach you can migrate some cards from previous season.</p>
                                <button v-if="!migration_on" type="button" class="btn btn-primary" @click="migrate()">Migrate</button>
                            </template>
                            <div v-if="migration_on" class="row">
                                <div class="col-lg-6">
                                    <div class="row mt-1">
                                        <div class="col-12">
                                            <h5>Eligible Cards</h5>
                                        </div>
                                    </div>
                                    <div id="migrationCollection">
                                        <div class="card" v-for="ctype in card_types">
                                            <div class="card-header" :id="ctype.replace(/\\s/g, '')+'MigrationCollection'">
                                                <h5 class="mb-0">
                                                    <button class="btn btn-link" data-toggle="collapse" :data-target="'#collapseMigrationCollection'+ctype.replace(/\\s/g, '')" aria-expanded="true" :aria-controls="'collapse'+ctype.replace(/\\s/g, '')">
                                                    [[ ctype ]] Cards
                                                    </button>
                                                </h5>
                                            </div>
                                            <div :id="'collapseMigrationCollection'+ctype.replace(/\\s/g, '')" class="deck_ctype collapse show" :aria-labelledby="ctype.replace(/\\s/g, '')+'Cards'" data-parent="migrationCollection">
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
                                                        <tr @click="addToMigrationPack(card)" v-for="card in sortedCardsWithoutQuantity(eligible_cards,ctype)" :key="card.id" :class="[rarityclass(card.template.rarity)]">
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
                                    <div class="row mt-1">
                                        <div class="col-4">
                                            <h5>Migration Pack</h5>
                                        </div>
                                        <div class="col-4">
                                            <h5>Cards [[pack_size]]/[[max_cards]]</h5>
                                        </div>
                                        <div class="col-4">
                                            <h5>Value [[pack_value]]/[[max_value]]</h5>
                                        </div>
                                    </div>
                                    <div id="migrationPack">
                                        <div class="card" v-for="ctype in card_types">
                                            <div class="card-header" :id="ctype.replace(/\\s/g, '')+'MigrationPack'">
                                                <h5 class="mb-0">
                                                    <button class="btn btn-link" data-toggle="collapse" :data-target="'#migrationDeck'+ctype.replace(/\\s/g, '')" aria-expanded="true" :aria-controls="'collapse'+ctype.replace(/\\s/g, '')">
                                                    [[ ctype ]] Cards
                                                    </button>
                                                </h5>
                                            </div>
                                            <div :id="'migrationDeck'+ctype.replace(/\\s/g, '')" class="deck_ctype collapse show" :aria-labelledby="ctype.replace(/\\s/g, '')+'Cards'" data-parent="#migrationPack">
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
                                                        <template v-for="(card,index) in sortedCardsWithoutQuantity(pack_cards.concat(uniques),ctype,false)">
                                                        <tr @click="removeFromMigrationPack(card)" :key="card.id" :class="[rarityclass(card.template.rarity)]">
                                                            <td><img class="rarity" :src="'static/images/'+card.template.rarity+'.jpg'" :alt="card.template.rarity" :title="card.template.rarity" width="20" height="25" /></td>
                                                            <td>[[ card.template.value ]]</td>
                                                            <td :title="card.template.description">[[ card.template.name ]]</td>
                                                            <td v-if="ctype=='Training' || ctype=='Special Play'"><span v-html="skills_for(card)"></span></td>
                                                            <td v-if="ctype=='Player'">[[ card.template.race ]]</td>
                                                            <td v-if="ctype=='Player' || ctype=='Training'" class="d-none d-sm-table-cell">[[ card.template.subtype ]]</td>
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