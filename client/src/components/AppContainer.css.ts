import { palette, breakpoints } from "@energiz3r/component-library/src/theme";
import { style } from "@vanilla-extract/css";

export const styles = {
  menu: style({
    //padding: "0 1rem 1rem 1rem",
  }),
  headerLink: style([
    {
      display: "none",
    },
    breakpoints.desktopSmall({
      display: "none",
    }),
    breakpoints.min.lg({
      display: "initial",
    }),
  ]),
};
