<template>
    <b-modal v-model="modalShow" id="skill_picker" title="Pick Skill">
      <h6>General</h6>
      <span v-for="skill in skills['G']" :key="skill" v-html="imgs_for_skill(skill)"></span>
      <h6>Agility</h6>
      <span v-for="skill in skills['A']" :key="skill" v-html="imgs_for_skill(skill)"></span>
      <h6>Passing</h6>
      <span v-for="skill in skills['P']" :key="skill" v-html="imgs_for_skill(skill)"></span>
      <h6>Strength</h6>
      <span v-for="skill in skills['S']" :key="skill" v-html="imgs_for_skill(skill)"></span>
      <h6>Mutation</h6>
      <span v-for="skill in skills['M']" :key="skill" v-html="imgs_for_skill(skill)"></span>
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
  },
  computed: {
  },
  watch: {
  },
};
</script>
