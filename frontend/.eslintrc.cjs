const { resolve } = require("path");

module.exports = {
  root: true,
  env: {
    node: true,
  },
  extends: [
    "airbnb-base",
    "plugin:vue/vue3-recommended",
    "plugin:prettier/recommended",
  ],
  plugins: ["vue", "prettier"],
  rules: {
    "import/extensions": ["error", "always"],
    "import/no-extraneous-dependencies": [
      "error",
      {
        optionalDependencies: false,
        devDependencies: [
          "**/vite.config.{js,cjs,mjs}",
          "**/.eslintrc.{js,cjs,mjs}",
        ],
      },
    ],
  },
  settings: {
    "import/resolver": {
      alias: [["@", resolve(__dirname, "src")]],
    },
  },
};
