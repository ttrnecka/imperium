const Cards = {
  methods: {
    has_keyword(card, keyword) {
      const regex = new RegExp(`\\*\\*${keyword}\\*\\*`, 'i');
      if (regex.exec(card.template.description) !== null) {
        return true;
      }
      return false;
    },
  },
};

export { Cards as default };
