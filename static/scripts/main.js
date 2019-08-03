import tournament from './components/tournament.js?1.13';
import signupModal from './components/signup-modal.js?1.0';
import VueFlashMessage from './components/VueFlashMessage/index.js?1.1';
Vue.use(VueFlashMessage);


Vue.mixin({
  data () {
    return {
      rarityorder: {"Starter":10,"Common":6, "Rare":5, "Epic":4, "Inducement":3,"Legendary":2, "Unique":1},
      mixed_teams: [
        {"idraces":38, "code":"aog", "tier_tax":10,  "name":"Alliance of Goodness",   "races":['Bretonnian' , 'Human', 'Dwarf', 'Halfling', 'Wood Elf'] },
        {"idraces":42, "code":"au",  "tier_tax":-10, "name":'Afterlife United',       "races":['Undead','Necromantic','Khemri','Vampire']},
        {"idraces":37, "code":"afs", "tier_tax":0,   "name":'Anti-Fur Society',       "races":['Kislev' , 'Norse', 'Amazon', 'Lizardman']},
        {"idraces":34, "code":"cgs", "tier_tax":-10, "name":'Chaos Gods Selection',   "races":['Chaos' , 'Nurgle']},
        {"idraces":33, "code":"cpp", "tier_tax":10,  "name":'Chaotic Player Pact',    "races":['Chaos' , 'Skaven', 'Dark Elf', 'Underworld']},
        {"idraces":36, "code":"egc", "tier_tax":10,  "name":'Elfic Grand Coalition',  "races":['High Elf' , 'Dark Elf', 'Wood Elf', 'Pro Elf']},
        {"idraces":35, "code":"fea", "tier_tax":0,   "name":'Far East Association',   "races":['Chaos Dwarf' , 'Orc', 'Goblin', 'Skaven', 'Ogre']},
        {"idraces":39, "code":"hl",  "tier_tax":0,   "name":'Human League',           "races":['Bretonnian' , 'Human', 'Kislev', 'Norse', 'Amazon']},
        {"idraces":32, "code":"sbr", "tier_tax":0,   "name":'Superior Being Ring',    "races":['Bretonnian' , 'High Elf', 'Vampire', 'Chaos Dwarf']},
        {"idraces":41, "code":"uosp", "tier_tax":-10, "name":'Union of Small People',  "races":['Ogre', 'Goblin','Halfling']},
        {"idraces":40, "code":"vt",  "tier_tax":0, "name":'Violence Together',      "races":['Ogre' , 'Goblin','Orc', 'Lizardman']}
      ],
      skills: {
        G: ["Dauntless","Dirty Player","Fend","Kick-Off Return","Pass Block","Shadowing","Tackle","Wrestle","Block","Frenzy","Kick","Pro","Strip Ball","Sure Hands"],
        A: ["Catch","Diving Catch","Diving Tackle","Jump Up","Leap","Sidestep","SideStep","Sneaky Git","Sprint","Dodge","Sure Feet"],
        P: ["Accurate","Dump-Off","Hail Mary Pass","Nerves of Steel","Pass","Safe Throw","Leader"],
        S: ["Break Tackle","Grab","Juggernaut","Multiple Block","Piling On","Stand Firm","Strong Arm","Thick Skull","Guard","Mighty Blow"],
        M: ["Big Hand","Disturbing Presence","Extra Arms","Foul Appearance","Horns","Prehensile Tail","Tentacles","Two Heads","Very Long Legs","Claw"]
      },
      card_types: ["Player","Training","Special Play","Staff","Upgrade"],
      show_starter:1,
      rarity_order:1,
      skillreg: /(Safe Throw|Shadowing|Disturbing Presence|Sneaky Git|Horns|Guard|Mighty Blow|ST\+|\+ST|MA\+|\+MA|AG\+|\+AG|AV\+|\+AV|Block|Accurate|Strong Arm|Dodge|Juggernaut|Claw|Sure Feet|Break Tackle|Jump Up|Two Heads|Wrestle|Frenzy|Multiple Block|Tentacles|Pro|Strip Ball|Sure Hands|Stand Firm|Grab|Hail Mary Pass|Dirty Player|Extra Arms|Foul Appearance|Dauntless|Thick Skull|Tackle|Nerves of Steel|Catch|Pass Block|Piling On|Pass|Fend|Sprint|Grab|Kick|Pass Block|Leap|Sprint|Leader|Diving Tackle|Tentacles|Prehensile Tail|Sidestep|Dump-Off)( |,|\.|$)/g,
    }
  },
  methods: {
    is_skill_double(player_card,skill) {
      if (["Strength Up!", "Agility Up!", "Movement Up!", "Armour Up!"].includes(skill)) {
        return false;
      }
      if (player_card.template.skill_access.indexOf(this.skill_to_group_map[skill]) > -1 ) {
        // single
        return false;
      } else {
        //double
        return true;
      }
    },
    skill_access_for(access) {
      const groups = access.split("");
      const skill_array = groups.map(e => this.skills[e]);
      return Array.prototype.concat.apply([], skill_array)
    },
    race(raceid) {
      const team = this.mixed_teams.find((t) => t.idraces==raceid)
      if(team) {
        return team.name;
      } else {
        return "Unknown race";
      }
    },
    positional_from_api(positional) {
      const names = positional.split("_");
      names.shift();
      return names.join(" ");
    },
    stadium_enhacement(team) {
      const building = team.cards.find((c) => c.type=="Building")
      if(building) {
        switch(building.name) {
          case "Bazar":
            return "Magician's Shop";
          case "SecurityArea":
            return "Security Gate";
          case "RefreshmentArea":
            return "Beer Stand";
          case "RefereeArea":
            return "Referee Rest Area";
          case "Astrogranit":
            return "Astrogranite";
          case "ElfTurf":
            return "Elf Turf";
          case "VIPArea":
            return "Royal Box";
          case "FoodArea":
            return "Squig Sandwich Kiosk";
          case "Nuffle":
            return "Nuffle Altar";
          case "Roof":
            return "Magic Dome";
        }
      } else {
        return "None";
      }
    },
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
        case "Inducement":
          klass = "table-inducement";
          break;
      }
      return klass;
    },
    cardsValue(cards) {
      return cards.reduce((total, e)=> { 
        if (e.is_starter)
          return total+0;
        else 
          return total+e.template.value;
      },0);
    },
    sortedCards(cards) {
      if (this.rarity_order==0) {
        return cards;
      }
      var order = this.rarityorder;
      function compare(a,b) {
        return (order[a.template.rarity] - order[b.template.rarity]) || a.template.name.localeCompare(b.template.name);
      }
      return cards.slice().sort(compare);
    },

    sortedCardsWithoutQuantity(cards,filter="",mixed_filter=true) {
      let tmp_cards;
      if (!this.show_starter) {
        tmp_cards =  cards.filter(function(i) { return !i.is_starter});
      }
      else {
        tmp_cards =  cards
      }
      if (filter!="") {
        tmp_cards =  tmp_cards.filter(function(i) { return i.template.card_type == filter});
      }

      if (this.selected_team!="All" && filter=="Player" && mixed_filter) {
        const races = this.mixed_teams.find((e) => { return e.name == this.selected_team }).races;
        tmp_cards =  tmp_cards.filter(function(i) { return i.template.race.split("/").some((r) => races.includes(r))});
      }
      return this.sortedCards(tmp_cards);
    },

    sortedCardsWithQuantity(cards,filter="") {
      let new_collection = {}
      const sorted = this.sortedCardsWithoutQuantity(cards,filter);
      for (let i=0, len = sorted.length; i<len; i++) {
        let name = sorted[i].template.name;
        if (new_collection.hasOwnProperty(name)) {
          new_collection[name]['quantity'] += 1
        }
        else {
          new_collection[name] = {}
          new_collection[name]["card"] = sorted[i]
          new_collection[name]["quantity"] = 1
        }
      }
      return new_collection;
    },
    is_locked(card) {
      if(card.in_development_deck || card.in_imperium_deck)
        return true
      else
        return false
    },

    imgs_for_skill(skill,double=false) {
      let name;
      switch(skill) {
        case "Strength Up!":
        case "ST+":
        case "+ST":
          name = "IncreaseStrength";
          break;
        case "Agility Up!":
        case "AG+":
        case "+AG":
          name = "IncreaseAgility";
          break;
        case "Movement Up!":
        case "MA+":
        case "+MA":
          name = "IncreaseMovement";
          break;
        case "Armour Up!":
        case "AV+":
        case "+AV":
          name = "IncreaseArmour";
          break;
        case "Nerves of Steel":
          name = "NervesOfSteel";
          break;
        case "Sidestep":
            name = "SideStep";
            break;
        default:
          name = skill.replace(/[\s-]/g, '')
      }
      const url = "https://cdn2.rebbl.net/images/skills/";
      const double_class = double ? "skill_double" : "skill_single"; 
      return "<img class=\"skill_icon "+double_class+"\" src=\""+url+name+".png\" title=\""+skill+"\"></img>";  
    },

    skills_for_player(card) {
      if(card.template.card_type!="Player") {
        return card.name;
      }
      let str;
      if(["Unique","Legendary","Inducement"].includes(card.template.rarity)) {
        str = card.template.description
      } else {
        str = card.template.name
      }
      let matches=[];
      let match;
      while (match = this.skillreg.exec(str)) {
        if(!(match.input.match("Pro Elf") && match[1]=="Pro")) {
          if(match[1]) {
            matches.push(match[1]);
          } else if (match[2]) {
            matches.push(match[2]);
          }
        }

        if (this.skillreg.lastIndex === match.index) {
          this.skillreg.lastIndex++;
        }
      }
      return matches.map((s) => this.imgs_for_skill(s)).join("");
    },
    skills_for_special_and_staff(card) {
      if(!["Special Play","Staff","Upgrade"].includes(card.card_type)) {
        return card.template.name;
      }
      let str = card.template.description
      let matches=[];
      let match;
      while (match = this.skillreg.exec(str)) {
        if(!(card.name=="The Apple Pie Killer" && match[1]=="Block")) {
          if(match[1]) {
            matches.push(match[1]);
          } else if (match[2]) {
            matches.push(match[2]);
          }
        }

        if (this.skillreg.lastIndex === match.index) {
          this.skillreg.lastIndex++;
        }
      }
      return matches.map((s) => this.imgs_for_skill(s)).join("");
    },
    skill_names_for(card) {
      let skills=[];
      switch(card.template.name) {
        case "Block Party":
          skills = ["Block"];
          break;
        case "Dodge like a Honeybadger, Sting like the Floor":
          skills = ["Tackle"];
          break;
        case "Gengar Mode":
          skills = ["DirtyPlayer"];
          break;
        case "Roger Dodger":
          skills = ["Dodge"];
          break;
        case "Packing a Punch":
          skills = ["MightyBlow"];
          break;
        case "Ballhawk":
          skills = ["Wrestle","Tackle","StripBall"];
          break;
        case "Roadblock":
          skills = ["Block","Dodge","StandFirm"];
          break;
        case "Cold-Blooded Killer":
          skills = ["MightyBlow","PilingOn"];
          break;
        case "Sniper":
          skills = ["Accurate","StrongArm"];
          break;
        case "A Real Nuisance":
          skills = ["SideStep","DivingTackle"];
          break;
        case "Insect DNA":
          skills = ["TwoHeads","ExtraArms"];
          break;
        case "Super Wildcard":
          skills = ["MVPCondition"];
          break;
        case "I Didn't Read The Rules":
          skills = ["MVPCondition","MVPCondition","MVPCondition"];
          break;
        case "Training Wildcard":
          skills = ["MVPCondition2"];
          break;
        case "Sidestep":
          skills = ["SideStep"];
          break;
        case "Bodyguard":
          skills = [];
          break;
        default:
          skills = [card.template.name]
      }
      return skills;
    },
    skills_for(card,double=false) {
      if(card.template.card_type=="Player") {
        return this.skills_for_player(card);
      }
      if(["Special Play", "Staff","Upgrade"].includes(card.template.card_type)) {
        return this.skills_for_special_and_staff(card);
      } 
      let skills = this.skill_names_for(card);
      const imgs = skills.map((s) => {
        return this.imgs_for_skill(s,double);  
      })
      return imgs.join("");
    },
    number_of_assignments(card) {
      if(card.template.name=="Bodyguard")
        return 1;
      if(card.template.card_type!="Training") {
        return 0;
      }
      if(card.template.name=="Super Wildcard") {
        return 3;
      }
      if(card.template.description.match(/ one /)) {
        return 1;
      }
      if(card.template.description.match(/ three /)) {
        return 3;
      }
      return 1;
    },
    print_date(pdate) {
      const jdate = new Date(pdate);
      const options = { year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric'};
      return jdate.toLocaleDateString('default',options);
    },
  },
  computed: {
    skill_to_group_map() {
      let map = {};
      ["G","A","P","S","M"].forEach((g) => {
        this.skills[g].forEach((e) => map[e]=g);
        this.skills[g].forEach((e) => map[e.replace(/[\s-]/g, '')]=g);
      });
      return map;
    }
  }
})

var app = new Vue({
    el: '#app',
    data () {
      return {
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
          achievements:{},
          stats:{},
          free_packs: "",
        },
        tournaments: [],
        selected_t_region:"",
        selected_t_state:"",
        selected_t_mode:"",
        selected_team:"All",
        coach_filter:"",
        menu: "Coaches",
        search_timeout: null,
        user:{},
        loaded_user:false,
        loaded_coaches:false,
        processing: false,
        leaderboard_loaded:false,
        leaderboard:{
          deck_values:[],
          earners:[],
          stats:[],
          coaches:[],
        },
      }
    },
    components: {
      tournament,
      'signup-modal': signupModal,
    },
    delimiters: ['[[',']]'],
    methods: {
      updateTournament(tournament) {
        const idx = this.tournaments.findIndex(x => x.id === parseInt(tournament.id));
        Vue.set(this.tournaments, idx, tournament);
        //this.selectCoach();
      },
      getCoach(id) {
        const path = "/coaches/"+id;
        axios.get(path)
          .then((res) => {
            const idx = this.coaches.findIndex(x => x.id === parseInt(id));
            Vue.set(this.coaches, idx, res.data);
            this.selectedCoach = this.coaches[idx];
            this.$nextTick(function() {
              $('[data-toggle="popover"]').popover();
            })
          })
          .catch((error) => {
            console.error(error);
          });
      },
      linkBB2Name() {
        const id = this.selectedCoach.id;
        const path = "/coaches/"+id;
        axios.put(path,{name: this.selectedCoach.bb2_name})
          .then((res) => {
            const idx = this.coaches.findIndex(x => x.id === parseInt(id));
            Vue.set(this.coaches, idx, res.data);
            this.selectedCoach = this.coaches[idx];
            this.flash("BB2 name updated", 'success',{timeout: 3000});
          })
          .catch((error) => {
            if (error.response) {
              this.flash(error.response.data.message, 'error',{timeout: 3000});
          } else {
              console.error(error);
          }
          });
      },
      getUser(id) {
        const path = "/me";
        axios.get(path)
          .then((res) => {
            this.user = res.data.user;
            this.loaded_user = true;
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
            this.loaded_coaches = true;
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
            this.leaderboard['coaches'] = res.data.coaches;
            this.leaderboard['stats'] = res.data.coach_stats;
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
                msg = "Card "+card.template.name+" flagged for dusting";
            } 
            else if(method=="remove") {
                msg = "Card "+card.template.name+" - dusting flag removed";
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
      is_loggedcoach(name) {
        if(this.loggedCoach!=undefined && (this.loggedCoach.bb2_name==name || this.loggedCoach.short_name==name)) {
          return true;
        } else {
          return false;
        }
      },
      leaderboard_class(name) {
        return this.is_loggedcoach(name) ? 'table-success' : ''
      },
      team_achievements(coach) {
        if (coach.achievements['team']) {
          return [32,33,34,35,36,37,38,39,40,41,42].map((e) => {
            return {
              team_name: this.mixed_teams.find((t) => t.idraces==e).name,
              achievements: coach.achievements.team[e]
            } 
          });
        }
        return [];
      },
      match_achievements(coach) {
        if (coach.achievements['match']) {
          return ['passingtotal1','passingtotal2','runningtotal1','runningtotal2','surfstotal1','surfstotal2','blocks1game1','blocks1game2',
                  'breaks1game1','breaks1game2','cas1game1','cas1game2','int1game1','score1game1','score1game2',
                  'sufferandwin1','sufferandwin2','winwithall','win500down'].map((e) => coach.achievements.match[e])
        }
        return [];
      },
      quest_achievements(coach) {
        if (coach.achievements['quests']) {
          return ['collect3legends','buildyourownlegend'].map((e) => coach.achievements.quests[e])
        }
        return [];
      },
      progress(number) {
        if(number > 1) {
          return 100;
        } else {
          return number*100;
        }
      },
      achievement_state_class(ach) {
        if(this.progress(ach.best/ach.target) == 100) {
            return 'btn-success';
        }
        return 'btn-secondary';
      },
      achievement_ready(ach) {
        if(this.progress(ach.best/ach.target) == 100 && !ach.completed) {
          return true;
        }
        return false;
      },
      getStat(coach) {
        let pointer = coach.stats;
        for (let i = 1; i < arguments.length; i++) {
          if(pointer[arguments[i]]) {
            pointer = pointer[arguments[i]];
          } else {
            return 0;
          }
        }
        return pointer;
      },
      team_stats(coach) {
        if (coach.stats['teams']) {
          return [32,33,34,35,36,37,38,39,40,41,42].map((e) => {
            return {
              team_name: this.mixed_teams.find((t) => t.idraces==e).name,
              stats: coach.stats.teams[e]
            } 
          });
        }
        return [];
      },
      getTeamStat(team) {
        if(team.stats && team.stats[arguments[1]]) {
          return team.stats[arguments[1]];
        }
        return 0;
      },
      getFreePacks(coach){
        return coach.free_packs.split(',').map((e) => {
          switch(e) {
            case "player":
              return "Player";
            case "training":
              return "Training";
            case "special":
              return "Special Play";
            case "booster_budget":
              return "Booster";
            case "booster_premium":
              return "Booster Premium";
          }
        }).join(", ");
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
        if(this.selected_t_mode!="") {
          filtered = filtered.filter((e) => {
            return e.mode.toLowerCase().replace(/\s/g, '') == this.selected_t_mode
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
        } else if (this.selected_t_state=="admined_by_me") {
          filtered = filtered.filter((e) => {
            return this.loggedCoach && this.loggedCoach.short_name==e.admin;
          })
        } else if (this.selected_t_state=="entered") {
          filtered = filtered.filter((e) => {
            if(this.loggedCoach!=undefined)
              for(var i=0;i<e.coach_limit;i++) {
                if(e.tournament_signups[i])
                  if(e.tournament_signups[i].coach==this.loggedCoach.id)
                    return e
              }
          })
        }        
        return filtered;
      },
      loggedCoach() {
        if (this.user.id && this.user.coach && this.user.coach.id) {
          return this.user.coach;
        }
        else {
          return undefined;
        }
      },

      loaded_user_and_coaches() {
        if(this.loaded_user && this.loaded_coaches) {
          return true;
        }
        return false;
      },
      is_active() {
        if (this.user.id && this.loggedCoach && !this.loggedCoach.deleted) {
          return true;
        }
        return false;
      },
      is_webadmin() {
        if(this.loggedCoach && this.loggedCoach.web_admin) {
            return true;
        }
        return false;
      },
      stats_coach() {
        return this.leaderboard.stats.find((e) => this.is_loggedcoach(e.name));
      },
      leaderboard_coach() {
        return this.leaderboard.coaches.find((e) => this.is_loggedcoach(e.short_name));
      },
      collectors_sorted() {
        return this.leaderboard['coaches'].slice().sort((a,b) => b.collection_value - a.collection_value);
      },
      earners_sorted() {
        return this.leaderboard['coaches'].slice().sort((a,b) => b.earned - a.earned);
      },
      grinders_sorted() {
        return this.leaderboard.stats.slice().sort((a,b) => b.matches - a.matches);
      },
      points_sorted() {
        return this.leaderboard.stats.slice().sort((a,b) => b.points - a.points);
      },
      ppg_sorted() {
        return this.leaderboard.stats.slice().sort((a,b) => b.points/b.matches - a.points/a.matches);
      },
      scorers_sorted() {
        return this.leaderboard.stats.slice().sort((a,b) => b.inflictedtouchdowns - a.inflictedtouchdowns);
      },
      tpg_sorted() {
        return this.leaderboard.stats.slice().sort((a,b) => b.inflictedtouchdowns/b.matches - a.inflictedtouchdowns/a.matches);
      },
      bashers_sorted() {
        return this.leaderboard.stats.slice().sort((a,b) => b.inflictedcasualties - a.inflictedcasualties);
      },
      cpg_sorted() {
        return this.leaderboard.stats.slice().sort((a,b) => b.inflictedcasualties/b.matches - a.inflictedcasualties/a.matches);
      },
      hitmen_sorted() {
        return this.leaderboard.stats.slice().sort((a,b) => b.inflicteddead - a.inflicteddead);
      },
      passers_sorted() {
        return this.leaderboard.stats.slice().sort((a,b) => b.inflictedpasses - a.inflictedpasses);
      },
      surfers_sorted() {
        return this.leaderboard.stats.slice().sort((a,b) => b.inflictedpushouts - a.inflictedpushouts);
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
        // pop over needs to be reenabled after you navige back to Coaches menu from the other sections
        if(newMenu == "Coaches") {
          this.$nextTick(function() {
            $('[data-toggle="popover"]').popover();
          })
        }
      },
      loaded_user_and_coaches: function(value) {
        if (value == true && !this.is_active) {
          this.$refs.signupModal.open();
        }
      }
    },
    mounted() {
      this.$on('loadedUser', this.selectCoach);
      this.$on('loadedCoaches', this.selectCoach);
      this.$on('signedUpCoach', this.getCoaches);
      this.$on('updateTournament', this.updateTournament);
      this.$on('updateTournaments', this.getTournaments);
    },
    beforeMount() {
      this.getUser();
      this.getCoaches();
      this.getTournaments();
    },
});
