const {getDefaultConfig, mergeConfig} = require('@react-native/metro-config');
const path = require('path');

/**
 * Metro configuration
 * https://facebook.github.io/metro/docs/configuration
 *
 * @type {import('metro-config').MetroConfig}
 */
const config = {
  resolver: {
    extraNodeModules: {
      '@store': path.resolve(__dirname, 'src/store'),
      '@controleonline': path.resolve(__dirname, 'modules/controleonline'),
    },
  },
};

module.exports = mergeConfig(getDefaultConfig(__dirname), config);
