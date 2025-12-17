export default {
  testEnvironment: "jsdom",
  setupFilesAfterEnv: ["<rootDir>/setupTests.js"],
  moduleFileExtensions: ["js", "jsx"],
  testMatch: [
    "**/__tests__/**/*.(test|spec).(js|jsx)"
  ],
  transform: {
    "^.+\\.[tj]sx?$": "babel-jest"
  },
  moduleNameMapper: {
    "^astro:schema$": "<rootDir>/__mocks__/astroSchemaMock.js"
  }
};
