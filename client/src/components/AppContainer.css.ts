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
  discordImage: style({
    width: "32px",
    height: "25px",
    marginLeft: "1rem",
    marginRight: ".5rem",
    marginTop: "14px",
  }),
  toggleBackground: style({
    backgroundColor: palette.theme.lightShade,
    borderRadius: "30px",
    width: "93px",
    paddingBottom: "12px",
  }),
};
