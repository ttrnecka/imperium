<template>
  <div class="row" v-if="display">
    <div class="col-9">
      <div class="progress position-relative mb-2">
        <div class="progress-bar"
          :class="data.completed ? 'bg-success' : ''" role="progressbar"
          :style="'width: '+progress+'%;'"
          aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">
        </div>
        <span class="justify-content-center d-flex position-absolute w-100">
          {{data.desc}} {{data.best}} / {{data.target}}
        </span>
      </div>
    </div>
    <div class="col-3">
      <button type="button" :disabled="!achievement_ready"
        :class="achievement_state_class"
        class="col-12 mb-2 ml-2 btn">
        {{data.award_text}}<span v-if="data.completed"> ✓</span>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'imperiumAchievement',
  props: {
    data: Object,
    hidden: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
    };
  },
  methods: {
  },
  computed: {
    achievement_ready() {
      if (this.progress === 100 && !this.data.completed) {
        return true;
      }
      return false;
    },
    progress() {
      const progress = this.data.best / this.data.target;
      if (progress > 1) {
        return 100;
      }
      return progress * 100;
    },
    achievement_state_class() {
      if (this.progress === 100) {
        return 'btn-success';
      }
      return 'btn-secondary';
    },
    display() {
      if (this.hidden && !this.data.completed) {
        return false;
      }
      return true;
    },
  },
  watch: {
  },
};
</script>
