import { style, globalStyle } from "@vanilla-extract/css";
import { palette, breakpoints } from "@energiz3r/component-library/src/theme";

const user = "#1f4613";
const ai = "#3a1f56";
const br = "10px";
const brRight = `0 ${br} ${br} 0`;
const brLeft = `${br} 0 0 ${br}`;

const messageTextMarkdown = style({});

globalStyle(`${messageTextMarkdown} > p`, {
  color: "white",
});

export const styles = {
  container: style([
    {
      background: palette.theme.darkShade,
      color: palette.theme.lightShade,
      padding: "0.5rem",
    },
    breakpoints.desktop({
      padding: "1rem",
    }),
  ]),
  conversationContainer: style({
    paddingBottom: "15px",
  }),
  inputContainer: style({}),

  messageRow: style({
    display: "flex",
    position: "relative",
    marginBottom: ".5rem",
    alignItems: "stretch",
  }),

  roleCell: style({
    padding: ".5rem",
  }),
  roleCellUser: style({
    marginRight: 0,
    marginLeft: "1px",
    backgroundColor: user,
    borderRadius: brRight,
  }),
  roleCellAi: style({
    marginRight: "1px",
    backgroundColor: ai,
    borderRadius: brLeft,
  }),

  messageCell: style({
    padding: ".5rem",
  }),
  messageCellUser: style({
    marginRight: 0,
    marginLeft: "auto",
    maxWidth: "85%",
    backgroundColor: user,
    borderRadius: brLeft,
  }),
  messageCellAi: style({
    maxWidth: "85%",
    backgroundColor: ai,
    borderRadius: brRight,
  }),

  inputLabel: style({
    color: palette.theme.darkAccent,
  }),
  badge: style({
    fill: palette.theme.textHighlight,
    marginTop: "2px",
  }),
  messageTextMarkdown,
  isTyping: style({
    padding: "1rem 1rem 0 1rem",
    fontSize: "10px",
  }),
  bin: style({
    fontSize: "30px",
    fill: palette.colors.red,
    cursor: "pointer",
  }),
  clearConvo: style({
    padding: "1rem 1rem .5rem 1rem",
    textAlign: "center",
  }),
};
