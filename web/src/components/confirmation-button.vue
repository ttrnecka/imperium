<template>
  <button type="button"
    :class="[ 'btn', 'btn-danger']"
    :disabled='stepsComplete'
    v-on:click='incrementStep()'>
    {{ currentMessage }}
  </button>
</template>

<script>
export default {
  name: 'confirmation-button',
  data() {
    return {
      defaultSteps: [
        'Click to confirm',
        'Are you sure?',
        '✔',
      ],
      currentStep: 0,
    };
  },
  props: {
    messages: Array,
  },
  computed: {
    messageList() {
      return this.messages ? this.messages : this.defaultSteps;
    },
    currentMessage() {
      return this.messageList[this.currentStep];
    },
    lastMessageIndex() {
      return this.messageList.length - 1;
    },
    stepsComplete() {
      return this.currentStep === this.lastMessageIndex;
    },
  },
  methods: {
    incrementStep() {
      if (this.timeout) {
        clearTimeout(this.timeout);
      }
      this.currentStep += 1;
      if (this.stepsComplete) {
        this.$emit('confirmation-success');
        this.timeout = setTimeout(() => this.reset(), 1000);
      } else {
        this.$emit('confirmation-incremented');
        this.timeout = setTimeout(() => this.reset(), 3000);
      }
    },
    reset() {
      this.currentStep = 0;
      this.$emit('confirmation-reset');
    },
  },
};
</script>
