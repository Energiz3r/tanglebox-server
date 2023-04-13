import {
  GlobalStyles,
  ThemeName,
  ThemeProvider,
} from "@energiz3r/component-library/src/theme";

export const parameters = {
  actions: { argTypesRegex: "^on[A-Z].*" },
  controls: {
    matchers: {
      color: /(background|color)$/i,
      date: /Date$/,
    },
  },
};

export const decorators = [
  (Story) => (
    <ThemeProvider theme={ThemeName.dark}>
      <GlobalStyles>
        <Story />
      </GlobalStyles>
    </ThemeProvider>
  ),
];
