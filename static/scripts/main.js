import tournament from './components/tournament.js';
import VueFlashMessage from './components/VueFlashMessage/index.js';
Vue.use(VueFlashMessage);

Vue.mixin({
  data () {
    return {
      rarityorder: {"Starter":10,"Common":5, "Rare":4, "Epic":3, "Legendary":2, "Unique":1},
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
      card_types: ["Player","Training","Special Play","Staff"]
    }
  },
  methods: { 
    rarityclass(rarity) {
      let klass;
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
        case "Unique":
          klass = "table-success";
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
        selectedCoach: {
          short_name: "",
          account: {
            amount:0,
            transactions: []
          },
          tournaments:[],
          cards:[],
          id:0,
        },
        tournaments: [],
        selected_t_region:"",
        selected_t_state:"",
        starter_cards: [],
        selected_team:"All",
        coach_filter:"",
        menu: "Coaches",
        search_timeout: null,
        user:{},
        processing: false,
        leaderboard_loaded:false,
        leaderboard:[],
      }
    },
    components: {
      tournament,
    },
    delimiters: ['[[',']]'],
    methods: {
      updateTournament(tournament) {
        const idx = this.tournaments.findIndex(x => x.id === parseInt(tournament.id));
        Vue.set(this.tournaments, idx, tournament);
        this.selectCoach();
      },
      getCoach(id) {
        const path = "/coaches/"+id;
        axios.get(path)
          .then((res) => {
            const idx = this.coaches.findIndex(x => x.id === parseInt(id));
            Vue.set(this.coaches, idx, res.data);
            this.selectedCoach = this.coaches[idx];
          })
          .catch((error) => {
            console.error(error);
          });
      },
      getUser(id) {
        const path = "/me";
        axios.get(path)
          .then((res) => {
            this.user = res.data.user;
            this.$emit('loadedUser');
          })
          .catch((error) => {
            console.error(error);
          });
      },
      getCoaches() {
        const path = "/coaches";
        axios.get(path)
          .then((res) => {
            for(let i=0,len=res.data.length;i<len;i++) {
              res.data[i].cards = [];
              res.data[i].tournaments = [];
              res.data[i].account = {};
              res.data[i].account.transactions = [];
            }
            this.coaches = res.data;
            this.$nextTick(function() {
              this.$emit('loadedCoaches');
            })
          })
          .catch((error) => {
            console.error(error);
          });
      },
      getLeaderboard() {
        const path = "/coaches/leaderboard";
        axios.get(path)
          .then((res) => {
            this.leaderboard = res.data.sort((a,b) => b.collection_value - a.collection_value).slice(0,10);
          })
          .catch((error) => {
            console.error(error);
          });
      },
      getTournaments() {
        const path = "/tournaments";
        axios.get(path)
          .then((res) => {
            this.tournaments = res.data;
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

      cardsValue(cards) {
        return cards.reduce((total, e)=> { return total+e.value},0);
      },
      sortedCardsWithoutQuantity(cards,filter="") {
        let tmp_cards;
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
          const races = this.mixed_teams.find((e) => { return e.name == this.selected_team }).races;
          tmp_cards =  tmp_cards.filter(function(i) { return i.race.split("/").some((r) => races.includes(r))});
        }
        return this.sortedCards(tmp_cards);
      },

      sortedCardsWithQuantity(cards,filter="") {
        let new_collection = {}
        const sorted = this.sortedCardsWithoutQuantity(cards,filter);
        for (let i=0, len = sorted.length; i<len; i++) {
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
      debounceCoachSearch(val){
        if(this.search_timeout) clearTimeout(this.search_timeout);
        var that=this;
        this.search_timeout = setTimeout(function() {
          that.coach_filter = val; 
        }, 300);
      },
      selectCoach() {
        const c = this.loggedCoach;
        if(c) {
          this.getCoach(this.loggedCoach.id);
        }
        else if(this.coaches.length>0){
          this.getCoach(this.coaches[0].id);
        }
      },
      tournamentsFor(coach) {
        return this.tournaments.filter((e)=>{
          return coach.tournaments.includes(e.id);
        })
      },
      is_duster() {
        return (this.loggedCoach.duster && this.loggedCoach.duster.type ? true : false);
      },
      is_in_duster(card) {
        return (this.is_duster() ? this.loggedCoach.duster.cards.includes(card.id) : false);
      },
      is_duster_full() {
        return (this.is_duster() ? this.loggedCoach.duster.cards.length==10 : false);
      },
      is_duster_open() {
        return (this.is_duster() && this.loggedCoach.duster.status=="OPEN" ? true : false);
      },
      dust_add(card) {
        this.dust("add",card);
      },
      dust_remove(card) {
        this.dust("remove",card);
      },
      dust_cancel() {
        this.dust("cancel");
      },
      dust_commit() {
        this.dust("commit");
      },
      dust(method,card) {
        let path;
        if(card) {
          path = "/duster/"+method+"/"+card.id;
        } else {
          path = "/duster/"+method;
        }
        let msg;
        this.processing=true;
        axios.get(path)
        .then((res) => {
            if(method=="add") {
                msg = "Card "+card.name+" flagged for dusting";
            } 
            else if(method=="remove") {
                msg = "Card "+card.name+" - dusting flag removed";
            }
            else if(method=="cancel") {
              msg = "Dusting cancelled";
            }
            else if(method=="commit") {
              const free_cmd = (res.data.type=="Tryouts" ? "!genpack player <type>" : "!genpack training or !genpack special");
              msg = "Dusting committed! Use "+free_cmd+" to generate a free pack!";
              this.getCoach(this.loggedCoach.id);
            }
            this.loggedCoach.duster=res.data;
            this.flash(msg, 'success',{timeout: 3000});
        })
        .catch((error) => {
            if (error.response) {
                this.flash(error.response.data.message, 'error',{timeout: 3000});
            } else {
                console.error(error);
            }
        })
        .then(() => {
            this.processing=false;
        });
    },
    },
    computed: {
      duster_type() {
        if(this.is_duster()) {
          return this.loggedCoach.duster.type;
        } else {
          return "No dusting in progress";
        }
      },
      orderedCoaches() {
        return this.coaches.sort(function(a,b) {
          return a.name.localeCompare(b.name);
        });
      },
      filteredCoaches() {
        return this.orderedCoaches.filter((coach) => {
          return coach.name.toLowerCase().includes(this.coach_filter.toLowerCase())
        })
      },
      filteredTournaments() {
        let filtered = this.tournaments;
        if(this.selected_t_region!="") {
          filtered = filtered.filter((e) => {
            return e.region.toLowerCase().replace(/\s/g, '') == this.selected_t_region
          })
        }
        if(this.selected_t_state=="full") {
          filtered = filtered.filter((e) => {
            return e.coach_limit == e.tournament_signups.filter((e) => { return e.mode=="active"}).length;
          })
        } else if (this.selected_t_state=="free") {
          filtered = filtered.filter((e) => {
            return e.coach_limit > e.tournament_signups.filter((e) => { return e.mode=="active"}).length;
          })
        }
        
        return filtered;
      },
      loggedCoach() {
        if (this.user.id) {
          const coach = this.coaches.find((e) => {
            return e.disc_id == this.user.id;
          })
          return coach;
        }
        else {
          return undefined;
        }
      }
    },
    watch: {
      menu: function(newMenu,oldMenu) {
        if(newMenu == "Leaderboard") {
          if(this.leaderboard_loaded==false) {
            this.getLeaderboard();
            this.leaderboard_loaded=true;
          }
        }
      }
    },
    mounted() {
      this.$on('loadedUser', this.selectCoach);
      this.$on('loadedCoaches', this.selectCoach);
      this.$on('updateTournament', this.updateTournament);
      this.$on('updateTournaments', this.getTournaments);
    },
    beforeMount() {
      this.getUser();
      this.getCoaches();
      this.getTournaments();
      this.getStarterCards();
    },
});
