import { useState } from "react";
import { styles } from "./Conversation.css";
import { palette } from "@energiz3r/component-library/src/theme";
import { TextInput } from "@energiz3r/component-library/src/components/Inputs/TextInput/TextInput";
import { TextWithMarkdown } from "../TextWithMarkdown/TextWithMarkdown";
import { Bouncer } from "@energiz3r/component-library/src/components/Bouncer/Bouncer";
import { ReactComponent as SvgMicrochip } from "@energiz3r/component-library/src/Icons/regular/microchip.svg";
import { ReactComponent as SvgUser } from "@energiz3r/component-library/src/Icons/regular/user.svg";
import { ReactComponent as SvgTrashAlt } from "@energiz3r/component-library/src/Icons/regular/trash-alt.svg";
import { ReactComponent as SvgQuestionCircle } from "@energiz3r/component-library/src/Icons/regular/question-circle.svg";

export type conversationMessage = {
  role: string;
  message: string;
  timestampReceived: number;
};

export interface ConversationProps {
  conversation: Array<conversationMessage>;
  shouldShowTyping: boolean;
  isConnecting: boolean;
  isAwaitingResponse: boolean;
  sendMessage: (message: string) => void;
  discardConversation: () => void;
}

export const Conversation = ({
  conversation,
  shouldShowTyping,
  isConnecting,
  isAwaitingResponse,
  sendMessage,
  discardConversation,
}: ConversationProps) => {
  const [inputText, setInputText] = useState("");
  const isOtherPersonTyping = !shouldShowTyping && isAwaitingResponse;

  const handleInputChange = (value: string) => {
    setInputText(value);
  };
  const handleEnterPress = () => {
    sendMessage(inputText);
  };
  const handleClickDiscardConversation = () => {
    discardConversation();
  };

  const roleContent = (role: string) => {
    if (role === "User") return <SvgUser className={styles.badge} />;
    if (role === "AI") return <SvgMicrochip className={styles.badge} />;
    if (role === "Question")
      return <SvgQuestionCircle className={styles.badge} />;
    return <b>{role}</b>;
  };

  const roleToClass = (role: string) => {
    return `${styles.roleCell} ${
      role === "User" ? styles.roleCellUser : styles.roleCellAi
    }`;
  };

  const drawRole = (role: string) => {
    return <div className={roleToClass(role)}>{roleContent(role)}</div>;
  };

  return (
    <div className={styles.container}>
      {isConnecting ? (
        <center>
          <p>connecting</p>
          <Bouncer />
        </center>
      ) : (
        <>
          <div className={styles.conversationContainer}>
            {conversation.length === 0 ? (
              <div className={styles.messageRow}>
                {drawRole("Question")}
                <div
                  className={`${styles.messageCell} ${styles.messageCellAi}`}
                >
                  <TextWithMarkdown
                    textWithMarkdown="Type a message to start a conversation"
                    className={styles.messageTextMarkdown}
                  />
                </div>
              </div>
            ) : null}
            {conversation?.map((message) => {
              return (
                <div className={styles.messageRow}>
                  {message.role !== "Empty" && message.role === "AI"
                    ? drawRole(message.role)
                    : null}
                  <div
                    className={`${styles.messageCell} ${
                      message.role === "User"
                        ? styles.messageCellUser
                        : styles.messageCellAi
                    }`}
                  >
                    <TextWithMarkdown
                      textWithMarkdown={message.message}
                      className={styles.messageTextMarkdown}
                    />
                  </div>
                  {message.role !== "Empty" && message.role === "User"
                    ? drawRole(message.role)
                    : null}
                </div>
              );
            })}
            {isOtherPersonTyping ? (
              <div className={styles.messageRow}>
                {drawRole("AI")}
                <div
                  className={`${styles.messageCell} ${styles.messageCellAi} ${styles.isTyping}`}
                >
                  <Bouncer color={palette.theme.textHighlight} />
                </div>
              </div>
            ) : null}
          </div>
          <div className={styles.inputContainer}>
            <TextInput
              onChange={handleInputChange}
              onEnterPress={handleEnterPress}
              fullWidth
              emptyOnEnter
              enabled={!isAwaitingResponse}
            />
            <span className={styles.inputLabel}>
              type your input and press enter to send
            </span>
            <div className={styles.clearConvo}>
              <SvgTrashAlt
                className={styles.bin}
                onClick={handleClickDiscardConversation}
              />
            </div>
          </div>
        </>
      )}
    </div>
  );
};
