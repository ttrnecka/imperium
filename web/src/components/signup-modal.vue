<template>
    <div class="modal fade signup" id="signup_modal" tabindex="-1" role="dialog" aria-labelledby="signup_modal" aria-hidden="true">
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
                    <p>Conclave is waiting for you to curse or bless you. As returning coach you can migrate some cards from previous season.</p>
                    <button v-if="!migration_on" type="button" class="btn btn-primary" @click="migrate()">Migrate</button>
                </template>
                <div v-if="migration_on" class="row">
                    <div class="col-lg-6">
                        <div class="row mt-1">
                            <div class="col-12">
                                <h5>Eligible Cards</h5>
                            </div>
                        </div>
                        <card-list id="migrationCollection" :cards="eligible_cards" :owner="user.coach"
                        :starter="false" :quantity="false" :column_list="collection_colums"
                        @card-click="addToMigrationPack"></card-list>
                    </div>
                    <div class="col-lg-6">
                        <div class="row mt-1">
                            <div class="col-4">
                                <h5>Migration Pack</h5>
                            </div>
                            <div class="col-4">
                                <h5>Cards {{pack_size}}/{{max_cards}}</h5>
                            </div>
                            <div class="col-4">
                                <h5>Value {{pack_value}}/{{max_value}}</h5>
                            </div>
                        </div>
                        <card-list id="migrationPack" :cards="pack_cards.concat(uniques)" :owner="user.coach"
                        :starter="false" :quantity="false" :column_list="collection_colums"
                        @card-click="removeFromMigrationPack"></card-list>
                    </div>
                </div>
            </div>
        </div>
        </div>
    </div>
</template>
<script>
import { mapState } from 'vuex';
import Api from '@/mixins/api';
import confirmationButton from '@/components/confirmation-button.vue';
import cardList from '@/components/card_list.vue';

export default {
  name: 'signup-modal',
  mixins: [Api],
  components: {
    'confirmation-button': confirmationButton,
    cardList,
  },
  data() {
    return {
      processing: false,
      old_cards: [],
      pack_cards: [],
      migration_on: false,
      selected_team: 'All',
      max_value: 35,
      max_cards: 5,
      max_legends: 1,
      migrated: false,
      collection_colums: ['Rarity', 'Value', 'Name', 'Skills', 'Race', 'Subtype'],
    };
  },
  methods: {
    newCoach() {
      const path = '/coaches';
      const processingMsg = this.flash('Initializing coach...', 'info');
      this.axios.post(path)
        .then((res) => {
          this.$parent.$emit('signedUpCoach', res.data);
        })
        .catch(this.async_error)
        .then(() => {
          processingMsg.destroy();
        });
    },
    pull_inactive_cards() {
      const path = `/coaches/${this.user.coach.id}/cards/inactive`;
      const processingMsg = this.flash('Getting last season cards...', 'info');
      this.axios.get(path)
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
        const message = (error.response.data.message) ? error.response.data.message : `Unknown error: ${error.response.status}`;
        this.flash(message, 'error', { timeout: 3000 });
      } else {
        console.error(error);
      }
    },
    modal() {
      return this.$('#signup_modal');
    },
    open() {
      this.modal().modal({ show: true, backdrop: 'static', keyboard: false });
    },
    close() {
      this.modal().modal('hide');
    },
    migrate() {
      this.pull_inactive_cards();
      this.migration_on = true;
    },
    activate() {
      const path = `/coaches/${this.user.coach.id}/activate`;
      const processingMsg = this.flash('Activating coach...', 'info');
      this.axios.put(path, { card_ids: this.to_migrate })
        .then((res) => {
          this.$parent.$emit('signedUpCoach', res.data);
          this.migration_on = false;
          this.migrated = true;
        })
        .catch(this.async_error)
        .then(() => {
          processingMsg.destroy();
        });
    },
    addToMigrationPack(card) {
      if (this.canAdd(card)) {
        this.pack_cards.push(card);
        const idx = this.old_cards.indexOf(card);
        this.old_cards.splice(idx, 1);
      }
    },
    removeFromMigrationPack(card) {
      if (this.canRemove(card)) {
        this.old_cards.push(card);
        const idx = this.pack_cards.indexOf(card);
        this.pack_cards.splice(idx, 1);
      }
    },
    canRemove(card) {
      if (this.uniques.includes(card)) {
        return false;
      }
      return true;
    },
    canAdd(card) {
      // check value
      if (this.pack_value + card.template.value > this.max_value) {
        this.flash(`Cannot add card. Max value limit is ${this.max_value}!`, 'error', { timeout: 3000 });
        return false;
      }
      if (this.pack_size + 1 > this.max_cards) {
        this.flash(`Cannot add card. Max card limit is ${this.max_cards}!`, 'error', { timeout: 3000 });
        return false;
      }
      if (card.template.rarity === 'Legendary' && this.pack_cards.filter((c) => c.template.rarity === 'Legendary').length === this.max_legends) {
        this.flash(`Cannot add card. Max Legendary limit is ${this.max_legends}!`, 'error', { timeout: 3000 });
        return false;
      }
      return true;
    },
  },
  computed: {
    is_user() {
      if (this.user.id) {
        return true;
      }
      return false;
    },
    is_coach() {
      if (this.user.coach && this.user.coach.id) {
        return true;
      }
      return false;
    },
    is_active() {
      if (this.is_coach && this.user.coach.deleted === false) {
        return true;
      }
      return false;
    },
    eligible_cards() {
      return this.old_cards.filter((card) => {
        if (card.is_starter) return false;
        if (card.template.rarity === 'Unique') return false;
        return true;
      });
    },
    uniques() {
      return this.old_cards.filter((card) => {
        if (card.template.rarity === 'Unique' && card.template.name !== 'Beta Prepared') {
          return true;
        }
        return false;
      });
    },
    pack_size() {
      return this.pack_cards.length;
    },
    pack_value() {
      return this.pack_cards.reduce((total, e) => total + e.template.value, 0);
    },
    to_migrate() {
      return this.pack_cards.concat(this.uniques).map((c) => c.id);
    },
    ...mapState([
      'user',
    ]),
  },
};
</script>
