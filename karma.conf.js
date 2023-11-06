module.exports = function (config) {
  config.set({
    basePath: "",
    frameworks: ["jasmine", "@angular-devkit/build-angular"],
    plugins: [
      require("karma-coverage"),
      require("karma-firefox-launcher"),
      require("karma-jasmine"),
      require("karma-junit-reporter"),
      require("@angular-devkit/build-angular/plugins/karma"),
    ],
    client: {
      jasmine: {
        random: false,
      },
      clearContext: false,
    },
    junitReporter: {
      useBrowserName: false,
    },
    reporters: ["progress", "junit"],
    port: 9876,
    colors: true,
    logLevel: config.LOG_INFO,
    autoWatch: false,
    browsers: ["FirefoxHeadless"],
    singleRun: true,
  });
};
