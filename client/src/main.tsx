import "../assets/react.production.min.js";
import "../assets/react-dom.production.min.js";
import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import { AppContainer } from "./components/AppContainer";
import {
  GlobalStyles,
  ThemeName,
  ThemeProvider,
} from "@energiz3r/component-library/src/theme";
import { consoleBranding } from "./utils/brand";

consoleBranding();

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <ThemeProvider theme={ThemeName.dark}>
      <GlobalStyles>
        <AppContainer />
      </GlobalStyles>
    </ThemeProvider>
  </React.StrictMode>,
);
