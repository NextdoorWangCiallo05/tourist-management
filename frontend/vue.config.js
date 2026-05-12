const webpack = require('webpack')

module.exports = {
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    },
    client: {
      overlay: false,
      webSocketURL: {
        hostname: 'localhost',
        pathname: '/ws',
        port: 8081,
        protocol: 'ws'
      }
    },
    hot: true
  },
  configureWebpack: {
    plugins: [
      new webpack.DefinePlugin({
        'process.env.CLIENT_OVERLAY': JSON.stringify(false)
      })
    ]
  }
}