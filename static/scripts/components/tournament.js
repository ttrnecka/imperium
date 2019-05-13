import deck from './deck.js';
export default {
    name: 'tournament',
    components: {
        deck
    },
    data () {
      return {
          processing:false,
          prize_menu:false,
          prizes:[],
          selected: {
              coach:{},
              deck_id:null,
          },
          show_deck:false,
      }
    },
    delimiters: ['[[',']]'],
    props: ['tournament','coaches','data-parent', 'user'],
    methods: {
        getProperty: function (name) {
          return this[name];
        },
        setprizes() {
            this.prize_menu=true;
            
            while(this.prizes.length<this.tournament.coach_limit) {
                // test for 1st: X pattern
                let reg = new RegExp("("+(this.prizes.length+1)+"\\S+):(\\s+\\d+)","g");
                let matches = reg.exec(this.tournament.prizes);
                let prize = (matches!=null ? matches[2].trim() : 0);
                let reason = (matches!=null ? matches[1].trim() : 0);
                if (prize==0) {
                    // test for imperium pattern
                    switch(this.prizes.length) {
                        case 0:
                            reason = "Winner";
                            break;
                        case 1:
                            reason = "Runner-Up";
                            break;
                        case 2:
                        case 3:
                            reason = "Semi-Final";
                            break;
                        case 4:
                        case 5:
                        case 6:
                        case 7:
                            reason = "Quarter-Final";
                            break;
                    }
                    reg = new RegExp(reason+":(\\s+\\d+)","g");
                    matches = reg.exec(this.tournament.prizes);
                    prize = (matches!=null ? matches[1].trim() : 0);
                }
                this.add_prize({
                    coach:'',
                    amount: prize,
                    reason: this.tournament.type+" "+this.tournament.mode+" "+reason, 
                });
            } 

            //sponsors
            if(this.tournament.sponsor!="None" && this.tournament.sponsor!="") {
                while(this.prizes.length<2*this.tournament.coach_limit) {
                    this.add_prize({
                        coach:'',
                        amount: 0,
                        reason: this.tournament.sponsor+" Bonus", 
                    });
                }
            }

        },
        add_prize(prize = {coach:'',amount:0, reason:''}) {
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
            for(let i=0;i<this.prizes.length;i++) {
                if(this.prizes[i].coach=="") {
                    this.flash("Coach not selected", 'error',{timeout: 3000});
                    return false;
                }
                if(this.prizes[i].reason=="") {
                    this.flash("Reason not specified", 'error',{timeout: 3000});
                    return false;
                }
            }
            return true;
        },
        award_and_stop() {
            if(this.check_prizes()) {
                this.processing=true;
                const path = "/tournaments/"+this.tournament.id+"/close";
                const processingMsg = this.flash("Processing...", 'info');
                axios.post(path,this.prizes)
                .then((res) => {
                    let msg = "Prizes awarded and tournament stopped";
                    this.flash(msg, 'success',{timeout: 3000});
                    this.prizes = [];
                    this.prize_menu = false;
                    this.$parent.$emit('updateTournament', res.data);
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
            }
        },
        sign() {
            this.call("sign");
        },
        resign() {
            this.call("resign");
        },
        update() {
            this.call("update");
        },
        call(method) {
            let path;
            if(method=="update") {
                path = "/tournaments/"+method;
                this.flash("Updating...", 'info',{timeout: 3000});
            } else {
                path = "/tournaments/"+this.tournament.id+"/"+method;
            }
            let msg;
            this.processing=true;
            axios.get(path)
            .then((res) => {
                if(method=="sign") {
                    msg = "Signup to "+this.tournament.name+" succeded";
                } else if(method=="resign") {
                    msg = "Resignation from "+this.tournament.name+" succeded";
                }
                else if(method=="update") {
                    msg = "Tournaments updated";
                }
                this.flash(msg, 'success',{timeout: 3000});
                if(this.tournament.fee>0 && ["sign","resign"].includes(method)) {
                    if(method=="sign") {
                        msg = "Charged registration fee "+this.tournament.fee+" coins";
                    } else if(method=="resign") {
                        msg = "Refunded registration fee "+this.tournament.fee+" coins";
                    }
                    this.flash(msg, 'info',{timeout: 3000});
                }
                if(["sign","resign"].includes(method)) {
                    this.$parent.$emit('updateTournament', res.data);
                } else if(method=="update") {
                    this.$parent.$emit('updateTournaments', res.data);
                }
            })
            .catch((error) => {
                if (error.response) {
                    this.flash(error.response.data.message, 'error',{timeout: 3000});
                } else {
                    console.error(error);
                }
            })
            .then(() => {
                this.processing=false;
            });
        },
        showDeck(coach) {
            let signup = this.tournament.tournament_signups.find((ts) => ts.coach==coach.id);
            this.selected.deck_id = signup.deck;
            this.selected.coach=coach;
            this.show_deck = true;
        },
        is_owner(coach) {
            if(this.loggedCoach && this.loggedCoach.id==coach.id) {
                return true;
            }
            return false;
        }
    },
    computed: {
        signed() {
            return this.tournament.tournament_signups.filter((e) => { return e.mode=="active"});
        },
        signed_ids() {
            return this.signed.map((e) => {return e.coach})
        },
        signed_coaches() {
            return this.coaches.filter((e)=> {return this.signed_ids.includes(e.id)})
        },
        signed_coaches_names() {
            return this.signed_coaches.map((e)=>{return e.short_name})
        },
        reserved() {
            return this.tournament.tournament_signups.filter((e) => { return e.mode!="active"});
        },
        is_user_signed() {
            if (this.user.username && this.signed_coaches.map((e)=>{ return e.short_name }).includes(this.user.username)) {
                return true;
            }
            return false;
        },
        loggedCoach() {
            if (this.user.id) {
              const coach = this.coaches.find((e) => {
                return e.disc_id == this.user.id;
              })
              return coach;
            }
            else {
              return undefined;
            }
        },
        is_webadmin() {
            if(this.loggedCoach && this.loggedCoach.web_admin) {
                return true;
            }
            return false;
        },
    },
    mounted() {
        this.$on('deckClosed', () => this.show_deck=false);
    },
    template: `<div class="tournament">
                <div class="card-header" :id="'tournament'+tournament.id">
                <h5 class="mb-0">
                    <div class="row">
                        <button class="col-md-9 btn btn-link btn-block" data-toggle="collapse" :data-target="'#collapseTournament'+tournament.id" aria-expanded="true" aria-controls="collapseTournament">
                            <div class="row">
                                <div class="col-6 col-md-5 text-left">[[ tournament.id ]]. [[ tournament.name ]]</div>
                                <div class="col-6 col-md-2 text-left">[[ tournament.status ]]</div>
                                <div class="col-6 col-md-2 text-left"> Signups: [[signed.length]]/[[ tournament.coach_limit ]]</div>
                                <div class="col-6 col-md-3 text-left">Channel: [[ tournament.discord_channel ]]</div>
                            </div>
                        </button>
                        <div class="col-md-3 text-right">
                            <button v-if="is_user_signed" :disabled="processing" type="button" class="col-12 m-1 btn btn-danger" @click="resign()">Resign</button>
                            <button v-else type="button" :disabled="processing" class="col-12 m-1 btn btn-success" @click="sign()">Sign</button>
                            <button v-if="is_user_signed" type="button" class="btn col-12 m-1 btn-primary"  @click="showDeck(loggedCoach)">My Deck</button>
                        </div>
                    </div>
                </h5>
            </div>
            <div :id="'collapseTournament'+tournament.id" class="collapse" :aria-labelledby="'Tournaments'+tournament.id" :data-parent="getProperty('data-parent')">
                <div class="card-body">
                    <div class="row tournament_info_line">
                        <div class="col-sm-3"><b>Signup By:</b>: [[ tournament.signup_close_date ]]</div>
                        <div class="col-sm-3"><b>Start</b>: [[ tournament.expected_start_date ]]</div>
                        <div class="col-sm-3"><b>End</b>: [[ tournament.expected_end_date ]]</div>
                        <div class="col-sm-3"><b>Deadline</b>: [[ tournament.deadline_date ]]</div>
                    </div>
                    <div class="row tournament_info_line">
                        <div class="col-sm-3"><b>Region</b>: [[ tournament.region ]]</div>
                        <div class="col-sm-3"><b>Type</b>: [[ tournament.type ]]</div>
                        <div class="col-sm-3"><b>Mode</b>: [[ tournament.mode ]]</div>
                        <div class="col-sm-3"><b>Deck Limit</b>: [[ tournament.deck_limit ]]</div>
                    </div>
                    <div class="row tournament_info_line">
                        <div class="col-sm-3"><b>Admin</b>: [[ tournament.admin ]]</div>
                        <div class="col-sm-3"><b>Fee</b>: [[ tournament.fee ]]</div>
                        <div class="col-sm-3"><b>Signups</b>: [[signed.length]]/[[ tournament.coach_limit ]]</div>
                        <div class="col-sm-3"><b>Reserves</b>: [[reserved.length]]/[[ tournament.reserve_limit ]]</div>
                    </div>
                    <div class="row tournament_info_line">
                        <div class="col-12"><b>Discord Channel</b>: #[[tournament.discord_channel]]</div>
                    </div>
                    <div class="row tournament_info_line">
                        <div class="col-12"><b>Signed</b>: <span v-for="coach in signed_coaches" :key="coach.id">[[coach.short_name]] (<a href="#" @click="showDeck(coach)">Deck</a>) </span></div>
                    </div>
                    <div class="row tournament_info_line">
                        <div class="col-12"><b>Prizes</b>:</div>
                    </div>
                    <div class="row tournament_info_line">
                        <div class="col-12">[[ tournament.prizes ]]</div>
                    </div>
                    <div class="row tournament_info_line">
                        <div class="col-12"><b>Special Rules</b>:</div>
                    </div>
                    <div class="row tournament_info_line">
                        <div class="col-12">[[ tournament.special_rules ]]</div>
                    </div>
                    <div class="row tournament_info_line">
                        <div class="col-12"><b>Sponsor</b>: [[ tournament.sponsor ]]</div>
                    </div>
                    <div class="row tournament_info_line">
                        <div class="col-12">[[ tournament.sponsor_description ]]</div>
                    </div>
                    <div class="row tournament_info_line">
                        <div class="col-12"><b>Unique Prize</b>:</div>
                    </div>
                    <div class="row tournament_info_line">
                        <div class="col-12">[[ tournament.unique_prize ]]</div>
                    </div>
                    <div v-if="is_webadmin" class="row tournament_info_line">
                        <div class="col-12"><b>Management:</b></div>
                    </div>
                    <div v-if="is_webadmin" class="row tournament_webadmin tournament_info_line">
                        <div class="col-sm-6"><button :disabled="processing" type="button" class="col-12 m-1 btn btn-info" @click="update()">Update</button></div>
                        <div class="col-sm-6">
                            <button v-if="prize_menu" :disabled="processing" type="button" class="col-12 m-1 btn btn-danger" @click="award_and_stop()">Award & Stop</button>
                            <button v-else :disabled="processing" type="button" class="col-12 m-1 btn btn-success" @click="setprizes()">Set Prizes</button>
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
                            <div class="col-md-3">
                                <div class="form-group">
                                    <select class="form-control" v-model="prize.coach" v-bind:class="{'is-invalid': prize.coach==''}">
                                        <option selected disabled value="">Coach:</option>
                                        <option v-for="coach in signed_coaches" :value="coach.id" :key="coach.id">[[ coach.short_name ]]</option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="form-group">
                                    <input class="form-control" type="number" placeholder="Cash" v-model="prize.amount" >
                                </div>
                            </div>
                            <div class="col-md-5">
                                <div class="form-group">
                                    <input type="text" class="form-control" placeholder="Reason" v-model="prize.reason" v-bind:class="{'is-invalid': prize.reason==''}">
                                </div>
                            </div>
                            <div class="col-md-2 text-right">
                            <button class="btn m-1 btn-sm btn-danger" @click="remove_prize(index)">remove</button>
                            </div>
                        </template>            
                    </div>
                </div>
            </div>
            <deck v-if="show_deck" :coach="selected.coach" :tournament="tournament" :deck_id="selected.deck_id" :is_owner="is_owner(selected.coach)"></deck>
        </div>`
}