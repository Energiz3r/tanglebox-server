const { vanillaExtractPlugin } = require("@vanilla-extract/vite-plugin");
const svgr = require('vite-plugin-svgr');
const svgrConfig =require( "../svgr.config.json");

module.exports = {
  stories: ["../src/**/*.stories.mdx", "../src/**/*.stories.@(js|jsx|ts|tsx)"],
  addons: [
    "@storybook/addon-links",
    "@storybook/addon-essentials",
    "@storybook/addon-interactions",
  ],
  framework: "@storybook/react",
  core: {
    builder: "@storybook/builder-vite",
  },
  features: {
    storyStoreV7: true,
  },
  // @ts-ignore
  async viteFinal(config) {
    config.plugins.push(vanillaExtractPlugin());
    config.plugins.push(svgr({ ...svgrConfig }));
    return config;
  },
};
