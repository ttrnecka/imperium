export default {
    name: 'tournament',
    data () {
      return {}
    },
    delimiters: ['[[',']]'],
    props: ['tournament','coaches','data-parent'],
    methods: {
        getProperty: function (name) {
          return this[name];
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
        }
    },
    template: `<div class="tournament">
                <div class="card-header" :id="'tournament'+tournament.id">
                <h5 class="mb-0">
                    <button class="btn btn-link btn-block" data-toggle="collapse" :data-target="'#collapseTournament'+tournament.id" aria-expanded="true" aria-controls="collapseTournament">
                    <div class="row"><div class="col-9 text-left">[[ tournament.id ]]. [[ tournament.name ]]</div><div class="col-3 text-left">[[ tournament.status ]]</div></div>
                    </button>
                </h5>
            </div>
            <div :id="'collapseTournament'+tournament.id" class="collapse" :aria-labelledby="'Tournaments'+tournament.id" :data-parent="getProperty('data-parent')">
                <div class="card-body">
                    <div class="row">
                        <div class="col-3"><b>Signup By:</b>: [[ tournament.signup_close_date ]]</div>
                        <div class="col-3"><b>Start</b>: [[ tournament.expect_start_date ]]</div>
                        <div class="col-3"><b>End</b>: [[ tournament.expect_end_date ]]</div>
                        <div class="col-3"><b>Deadline</b>: [[ tournament.deadline_date ]]</div>
                    </div>
                    <div class="row">
                        <div class="col-3"><b>Region</b>: [[ tournament.region ]]</div>
                        <div class="col-3"><b>Type</b>: [[ tournament.type ]]</div>
                        <div class="col-3"><b>Mode</b>: [[ tournament.mode ]]</div>
                        <div class="col-3"><b>Deck Limit</b>: [[ tournament.deck_limit ]]</div>
                    </div>
                    <div class="row">
                        <div class="col-3"><b>Admin</b>: [[ tournament.admin ]]</div>
                        <div class="col-3"><b>Fee</b>: [[ tournament.fee ]]</div>
                        <div class="col-3"><b>Signups</b>: [[signed.length]]/[[ tournament.coach_limit ]]</div>
                        <div class="col-3"><b>Reserves</b>: [[reserved.length]]/[[ tournament.reserve_limit ]]</div>
                    </div>
                    <div class="row">
                        <div class="col-12"><b>Signed</b>: [[signed_coaches_names.join(", ")]]</div>
                    </div>
                    <div class="row">
                        <div class="col-12"><b>Prizes</b>:</div>
                    </div>
                    <div class="row">
                        <div class="col-12">[[ tournament.prizes ]]</div>
                    </div>
                    <div class="row">
                        <div class="col-12"><b>Special Rules</b>:</div>
                    </div>
                    <div class="row">
                        <div class="col-12">[[ tournament.special_rules ]]</div>
                    </div>
                    <div class="row">
                        <div class="col-12"><b>Sponsor</b>: [[ tournament.sponsor ]]</div>
                    </div>
                    <div class="row">
                        <div class="col-12">[[ tournament.sponsor_description ]]</div>
                    </div>
                    <div class="row">
                        <div class="col-12"><b>Unique Prize</b>:</div>
                    </div>
                    <div class="row">
                        <div class="col-12">[[ tournament.unique_prize ]]</div>
                    </div>
                </div>
            </div></div>`
}