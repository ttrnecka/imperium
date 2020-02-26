const Api = {
  data() {
    return {
    };
  },
  methods: {
    signin() {
      const path = '/signin';
      this.axios.get(path)
        .catch((error) => {
          console.error(error);
        });
    },
    signout() {
      const path = '/signout';
      this.axios.get(path)
        .catch((error) => {
          console.error(error);
        });
    },
    me() {
      const path = '/me';
      return this.axios.get(path);
    },
    getCoaches() {
      const path = '/coaches';
      return this.axios.get(path);
    },
    getTournaments() {
      const path = '/tournaments';
      return this.axios.get(path);
    },
    getBBNames() {
      const path = '/bb2_names';
      return this.axios.get(path);
    },
  },
  computed: {
  },
};

export { Api as default };
