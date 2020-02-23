<template>
    <div>
        <select v-model="selected_injury" class="form-control">
            <option value="DISABLED" disabled selected>Injury?</option>
            <option value="">Cancel</option>
            <option value="X">Reset</option>
            <option v-for="(cas,index) in injuries" :title="cas[0]" :value="cas[0]" :key="index">{{ cas[1] }}</option>
        </select>
    </div>
</template>
<script>
export default {
  name: 'injury-picker',
  data() {
    return {
      injuries: [
        ['SmashedKnee', 'Niggle'], ['DamagedBack', 'Niggle'], ['SmashedAnkle', 'MA-'], ['SmashedHip', 'MA-'], ['SeriousConcussion', 'AV-'], ['FracturedSkull', 'AV-'],
        ['BrokenNeck', 'AG-'], ['SmashedCollarBone', 'STR-'],
      ],
      selected_injury: 'DISABLED',
    };
  },
  watch: {
    selected_injury: function (newValue) {
      this.$emit('injured', newValue);
    },
  },
};
</script>
