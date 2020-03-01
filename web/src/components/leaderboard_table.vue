<template>
  <div class="col-12 col-md-6 col-lg-4 table-responsive">
    <h4> {{ title }} </h4>
    <table id="leaderboard" class="table table-hover">
      <thead class="thead-dark">
        <tr>
          <th scope="col">#</th>
          <th scope="col">Name</th>
          <th class="text-right" scope="col">Value</th>
        </tr>
      </thead>
      <tbody>
        <tr :class="leaderboard_class(coach_name(coach))"
          v-for="(coach, index) in coaches.slice(0,10)" :key="coach.id">
          <th scope="row">{{ index+1 }}.</th>
          <td>{{ coach_name(coach) }}</td>
          <td class="text-right">{{ coach[attr] }}</td>
        </tr>
        <tr v-if="coach!=undefined &&
          coaches.indexOf(coach) > 9"
          :class="leaderboard_class(coach_name(coach))">
          <th scope="row">{{ coaches.indexOf(coach)+1 }}.</th>
          <td>{{ coach_name(coach) }}</td>
          <td class="text-right">{{ coach[attr] }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'leaderboard-table',
  props: {
    title: String,
    coaches: Array,
    attr: String,
    coach: Object,
  },
  data() {
    return {
    };
  },
  methods: {
    coach_name(coach) {
      if (coach.short_name) {
        return coach.short_name;
      }
      return coach.name;
    },
  },
  computed: {
    ...mapGetters([
      'is_loggedcoach',
    ]),
  },
  watch: {
  },
};
</script>
