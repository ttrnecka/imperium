const path = require('path');
const CompressionPlugin = require('compression-webpack-plugin');

module.exports = {
  assetsDir: process.env.NODE_ENV === 'production' ? '../static/' : '',
  publicPath: '',
  outputDir: path.resolve(__dirname, '../templates'),
  devServer: {
    proxy: 'http://127.0.0.1:5000',
  },
  chainWebpack(config) {    
    // and this line 
    config.plugin('CompressionPlugin').use(CompressionPlugin);
  }
};
