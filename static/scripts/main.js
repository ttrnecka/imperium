
Vue.mixin({
  data () {
    return {
      rarityorder: {"Starter":5,"Common":4, "Rare":3, "Epic":2, "Legendary":1},
    }
  },
  methods: { 
    rarityclass(rarity) {
      switch(rarity) {
        case "Common":
        case "Starter":
          klass = "table-light";
          break;
        case "Rare":
          klass = "table-info";
          break;
        case "Epic":
          klass = "table-danger";
          break;
        case "Legendary":
          klass = "table-warning";
          break;
      }
      return klass;
    },
  }
})

var app = new Vue({
    el: '#app',
    data () {
      return {
        show_starter: 1,
        coaches: [],
        starter_cards: [],
      }
    },
    delimiters: ['[[',']]'],
    methods: {
      starter_state() {
        if (this.show_starter) {
          return "ON";
        }
        else {
          return "OFF";
        }
      },
      getCoaches() {
        const path = "coaches";
        axios.get(path)
          .then((res) => {
            this.coaches = res.data;
            console.log(this.coaches);
            this.$nextTick(function () {
              $('#coach-list a:first-child').tab('show') // Select first tab
            })
          })
          .catch((error) => {
            console.error(error);
          });
      },
      getStarterCards() {
        const path = "/cards/starter";
        axios.get(path)
          .then((res) => {
            this.starter_cards = res.data;
          })
          .catch((error) => {
            console.error(error);
          });
      },
      sortedCards(cards) {
        var order = this.rarityorder;
        function compare(a,b) {
          return (order[a.rarity] - order[b.rarity]) || a.name.localeCompare(b.name);
        }
        return cards.slice().sort(compare);
      },

      sortedCardsWithQuantity(cards) {
        if (!this.show_starter) {
          tmp_cards =  cards.filter(function(i) { return i.id != null});
        }
        else {
          tmp_cards =  cards
        }
        var new_collection = {}
        const sorted = this.sortedCards(tmp_cards);
        for (i=0, len = sorted.length; i<len; i++) {
          if (new_collection.hasOwnProperty(sorted[i].name)) {
            new_collection[sorted[i].name]['quantity'] += 1
          }
          else {
            new_collection[sorted[i].name] = {}
            new_collection[sorted[i].name]["card"] = sorted[i]
            new_collection[sorted[i].name]["quantity"] = 1
          }
        }
        return new_collection;
      },

    },
    computed: {
      orderedCoaches() {
        return this.coaches.slice().sort(function(a,b) {
          return a.name.localeCompare(b.name);
        });
      }
    },
    mounted() {
      this.getCoaches();
      this.getStarterCards();
    },
});
