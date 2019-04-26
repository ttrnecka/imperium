
Vue.mixin({
  data () {
    return {
      rarityorder: {"Starter":5,"Common":4, "Rare":3, "Epic":2, "Legendary":1},
      mixed_teams: [
        {"code":"aog",  "name":"Alliance of Goodness",   "races":['Bretonnian' , 'Human', 'Dwarf', 'Halfling', 'Wood Elf'] },
        {"code":"au",   "name":'Afterlife United',       "races":['Undead','Necromantic','Khemri','Vampire']},
        {"code":"afs",  "name":'Anti-Fur Society',       "races":['Kislev' , 'Norse', 'Amazon', 'Lizardman']},
        {"code":"cgs",  "name":'Chaos Gods Selection',   "races":['Chaos' , 'Nurgle']},
        {"code":"cpp",  "name":'Chaotic Player Pact',    "races":['Chaos' , 'Skaven', 'Dark Elf', 'Underworld']},
        {"code":"egc",  "name":'Elfic Grand Coalition',  "races":['High Elf' , 'Dark Elf', 'Wood Elf', 'Pro Elf']},
        {"code":"fea",  "name":'Far East Association',   "races":['Chaos Dwarf' , 'Orc', 'Goblin', 'Skaven', 'Ogre']},
        {"code":"hl",   "name":'Human League',           "races":['Bretonnian' , 'Human', 'Kislev', 'Norse', 'Amazon']},
        {"code":"sbr",  "name":'Superior Being Ring',    "races":['Bretonnian' , 'High Elf', 'Vampire', 'Chaos Dwarf']},
        {"code":"uosp", "name":'Union of Small People',  "races":['Ogre' , 'Goblin','Halfling']},
        {"code":"vt",   "name":'Violence Together',      "races":['Ogre' , 'Goblin','Orc', 'Lizardman']}
      ],
      card_types: ["Player","Training","Special Play","Utility"]
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
        selected_team:"All",
        coach_filter:""
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
      getCoach(id) {
        const path = "/coaches/"+id;
        axios.get(path)
          .then((res) => {
            idx = this.coaches.findIndex(x => x.id === parseInt(id));
            Vue.set(this.coaches, idx, res.data);
          })
          .catch((error) => {
            console.error(error);
          });
      },
      getCoaches() {
        const path = "/coaches";
        axios.get(path)
          .then((res) => {
            for(i=0,len=res.data.length;i<len;i++) {
              res.data[i].cards = [];
              res.data[i].account = {};
              res.data[i].account.transactions = [];
            }
            this.coaches = res.data;
            this.$nextTick(function () {
              // register one time event to load the first coach, then show it
              $('#coach-list a:first-child').on("show.bs.tab", (e) => {
                this.getCoach(e.currentTarget.getAttribute("coach_id"));
                $('#coach-list a:first-child').off("show.bs.tab");
              });
              $('#coach-list a:first-child').tab("show");
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

      sortedCardsWithQuantity(cards,filter="") {
        if (!this.show_starter) {
          tmp_cards =  cards.filter(function(i) { return i.id != null});
        }
        else {
          tmp_cards =  cards
        }
        if (filter!="") {
          tmp_cards =  tmp_cards.filter(function(i) { return i.card_type == filter});
        }

        if (this.selected_team!="All" && filter=="Player") {
          races = this.mixed_teams.find((e) => { return e.name == this.selected_team }).races;
          tmp_cards =  tmp_cards.filter(function(i) { return races.includes(i.race)});
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
      },
      filteredCoaches() {
        return this.orderedCoaches.filter((coach) => {
          return coach.name.toLowerCase().includes(this.coach_filter.toLowerCase())
        })
      }
    },
    mounted() {
      this.getCoaches();
      this.getStarterCards();
    },
});
