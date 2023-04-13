import { globalStyle } from "@vanilla-extract/css";

globalStyle("body", {
  margin: 0,
  fontFamily:
    '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif',
});

globalStyle("code", {
  fontFamily:
    'source-code-pro, Menlo, Monaco, Consolas, "Courier New", monospace',
});

globalStyle("html, body, #root", {
  height: "100%",
});
