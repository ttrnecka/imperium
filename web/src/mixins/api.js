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
  },
  computed: {
  },
};

export { Api as default };
