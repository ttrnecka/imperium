<template>
    <b-modal v-model="modalShow" id="skill_picker" title="Pick Skill" hide-footer>
      <template v-for="(value, propertyName) in skills">
        <span :key="propertyName">
          <h6>{{ skill_group(propertyName) }}</h6>
          <div class="m-1 d-inline-block" v-for="skill in value" :key="skill" @click="select(skill)" v-html="imgs_for_skill(skill, false, 'skill_icon_picker')"></div>
        </span>
      </template>
    </b-modal>
</template>

<script>
import Cards from '@/mixins/cards';

const timeout = async (ms) => new Promise((res) => setTimeout(res, ms));

export default {
  mixins: [Cards],
  name: 'skillPicker',
  props: {
  },
  data() {
    return {
      modalShow: false,
      selectedSkill: '',
    };
  },
  methods: {
    skill_group(letter) {
      switch (letter) {
        case 'G':
          return 'General';
        case 'A':
          return 'Agility';
        case 'P':
          return 'Passing';
        case 'S':
          return 'Strength';
        case 'M':
          return 'Mutation';
        default:
          return '';
      }
    },
    select(skill) {
      this.selectedSkill = skill;
    },
    open() {
      this.selectedSkill = '';
      this.modalShow = true;
    },
    async waitUserInput() {
      /* eslint-disable */
      while (this.selectedSkill === '') await timeout(50); // pauses script
      /* eslint-enable */
      return this.selectedSkill;
    },
    async openAndWaitForSkill() {
      this.open();
      const skill = await this.waitUserInput();
      this.modalShow = false;
      return skill;
    },
  },
  computed: {
  },
  watch: {
  },
};
</script>
