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
      }
    },
    delimiters: ['[[',']]'],
    props: {
        messages: Array,
    },
    computed: {
        messageList() {
          return this.messages ? this.messages : this.defaultSteps
        },
        currentMessage() {
          return this.messageList[this.currentStep]
        },
        lastMessageIndex() {
          return this.messageList.length - 1
        },
        stepsComplete() {
          return this.currentStep === this.lastMessageIndex
        }
    },
    methods: {
        incrementStep() {
          if (this.timeout) {
              clearTimeout(this.timeout);
          }
          this.currentStep++
          if (this.stepsComplete) {
            this.$emit('confirmation-success')
          }
          else {
            this.$emit('confirmation-incremented')
            this.timeout = setTimeout(() => this.reset(), 3000);
          }
        },
        reset() {
          this.currentStep = 0
          this.$emit('confirmation-reset')
        },
    },
    template: `<button type="button"
        :class="[ 'btn', 'btn-danger', 'col-12', 'm-1']"
        :disabled='stepsComplete'
        v-on:click='incrementStep()'>
        [[ currentMessage ]]
    </button>`
}