const path = require('path');

module.exports = {
  assetsDir: process.env.NODE_ENV === 'production' ? '../static/' : '',
  publicPath: '',
  outputDir: path.resolve(__dirname, '../templates'),
  devServer: {
    proxy: 'http://127.0.0.1:5000',
  },
};
