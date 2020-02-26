<template>
  <nav class="navbar navbar-dark fixed-top bg-dark navbar-expand-md">
      <div class="container-fluid">
          <a class="navbar-brand" href="#" @click="setMenu(options[0])">
              <img src="/static/images/Imperium.jpg" class="d-inline-block align-top" width="24" alt="">
              <div class="d-inline-block pl-2"> REBBL Imperium</div>
          </a>
          <button class="navbar-toggler" type="button" data-toggle="collapse"
                  data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent"
                  aria-expanded="false" aria-label="Toggle navigation">
              <span class="navbar-toggler-icon"></span>
          </button>
          <div class="collapse navbar-collapse" id="navbarSupportedContent">
              <ul class="navbar-nav mr-auto">
                  <li class="nav-item" v-for="option in options" :key="option.value" v-bind:class="{ active: menu == option.value }">
                      <a class="nav-link" :href="option.link" @click="setMenu(option)">{{ option.value }}</a>
                  </li>
                  <li class="nav-item">
                      <a class="nav-link" target="_blank" title="Only to get us wasted, not for buying packs!!!" href="https://www.paypal.me/rebblimperium">
                          <div class="d-inline-block">&#127867; Beer Fund</div>
                      </a>
                  </li>
                  <li class="nav-item">
                    <a class="nav-link" target="_blank" title="Discord" href="https://discord.gg/hdSQhRf">
                      <div class="d-inline-block">
                        <i class="fab fa-discord"
                          title="Discord">
                        </i>
                      </div>
                    </a>
                  </li>
              </ul>
              <ul class="navbar-nav" v-cloak>
                  <li v-if="user.username" class="nav-item">
                    <img class="ml-2 avatar" :src="'https://cdn.discordapp.com/avatars/'+user.id+'/'+user.avatar+'.png'"/>
                  </li>
                  <li v-if="user.username" class="nav-item dropdown">
                      <a class="nav-link dropdown-toggle ml-auto" href="#" id="navbarDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                        Profile
                      </a>
                      <div class="dropdown-menu" aria-labelledby="navbarDropdown">
                        <a class="dropdown-item" href="#">{{ user.username }}</a>
                        <a class="dropdown-item" href="#" @click="signout">Signout</a>
                      </div>
                  </li>
                  <li v-else class="nav-item">
                    <a class="nav-link" href="#" @click="signin">Signin</a>
                  </li>
              </ul>
          </div>
      </div>
    </nav>
</template>

<script>
import Api from '@/mixins/api';

export default {
  name: 'imperium-navbar',
  mixins: [Api],
  props: {
    user: Object,
    default: String,
  },
  data() {
    return {
      menu: '',
      options: [
        { value: 'Coaches', link: '#' },
        { value: 'Tournaments', link: '#' },
        { value: 'Leaderboard', link: '#' },
        { value: 'Rules', link: 'https://bit.ly/2P9Y07F' },
      ],
    };
  },
  methods: {
    setMenu(option) {
      this.menu = option.value;
      this.$emit('menu-change', option.value);
    },
  },

  created() {
    if (this.default) {
      this.menu = this.default;
    }
  },
};
</script>
