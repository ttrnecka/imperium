<template>
    <b-modal v-model="modalShow" id="skill_picker" title="Pick Skill">
      <template v-for="(value, propertyName) in skills">
        <span :key="propertyName">
          <h6>{{ skill_group(propertyName) }}</h6>
          <div class="m-1 d-inline-block" v-for="skill in value" :key="skill" v-html="imgs_for_skill(skill, false, 'skill_icon_picker')"></div>
        </span>
      </template>
    </b-modal>
</template>

<script>
import Cards from '@/mixins/cards';

export default {
  mixins: [Cards],
  name: 'skillPicker',
  props: {
  },
  data() {
    return {
      modalShow: false,
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
  },
  computed: {
  },
  watch: {
  },
};
</script>
