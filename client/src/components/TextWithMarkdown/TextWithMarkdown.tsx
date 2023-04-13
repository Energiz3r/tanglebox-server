import MDEditor from "@uiw/react-md-editor";
import { styles } from "./TextWithMarkdown.css";

export const TextWithMarkdown = ({
  textWithMarkdown,
  className,
}: {
  textWithMarkdown?: string;
  className?: string;
}) => {
  return (
    <div style={{ textAlign: "left" }} data-color-mode="dark">
      <MDEditor.Markdown
        source={textWithMarkdown}
        className={`${styles.markdown} ${className}`}
      />
    </div>
  );
};
