export default {
    name: 'singup-modal',
    delimiters: ['[[',']]'],
    props: ['coach','user'],
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
          team:{}
      }
    },
    methods: {
        newCoach() {
            const path = "/coaches";
            const processingMsg = this.flash("Initializing coach...", 'info');
            axios.post(path)
            .then((res) => {
                this.$parent.$emit('signedUpCoach');
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
            return false;
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
            if(this.coach == undefined) {
                return false;
            }
            return true;
        },
        is_active() {
            if(this.is_coach && this.coach.deleted == false) {
                return true;
            }
            return false;
        }
    },  
    template:   `<div class="modal fade" id="signup_modal" tabindex="-1" role="dialog" aria-labelledby="signup_modal" aria-hidden="true">
                    <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h4 v-if="!is_user" class="modal-title">Authenticate</h4>
                            <h4 v-if="is_user && !is_coach" class="modal-title">New Coach</h4>
                            <h4 v-if="is_active" class="modal-title">Done</h4>
                            <h4 v-if="is_coach && !is_active" class="modal-title">Sign back</h4>
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
                                <h5>Coach account has been succefully initialized!</h5>
                                <p>Check your info tab for your initial bank balance and free pack. Then head to <a target="_blank" href="https://discord.gg/hdSQhRf">Imperium Discord</a>
                                to generate your packs.
                                </p>
                                <button type="button" class="btn btn-success" @click="close()">Close</button>
                            </template>
                            <template v-if="is_coach && !is_active">
                                <h5>Welcome back to REBBL Imperium!</h5>
                                <p>We know you missed your dose of this mad game. As returning coach you can migrate some cards from previous season.</p>
                                <button type="button" class="btn btn-primary" @click="migrate()">Migrate</button>
                            </template>
                        </div>
                    </div>
                    </div>
                </div>`
}