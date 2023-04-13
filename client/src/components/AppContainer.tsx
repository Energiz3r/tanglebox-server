import { useState } from "react";
import { styles } from "./AppContainer.css";
import { palette } from "@energiz3r/component-library/src/theme";

import { Header } from "@energiz3r/component-library/src/components/Header/Header";
import { Menu } from "@energiz3r/component-library/src/components/Menu/Menu";
import { MenuItem } from "@energiz3r/component-library/src/components/Menu/MenuItem";
import { IntegerInput } from "@energiz3r/component-library/src/components/Inputs/IntegerInput/IntegerInput";
import { FloatInput } from "@energiz3r/component-library/src/components/Inputs/FloatInput/FloatInput";
import { ContentSection } from "@energiz3r/component-library/src/components/ContentSection/ContentSection";
import { ContentHeader } from "@energiz3r/component-library/src/components/ContentHeader/ContentHeader";
import { Conversation } from "./Conversation/Conversation";
import { useConversation } from "../hooks/useConversation";

import { ReactComponent as SvgLink } from "@energiz3r/component-library/src/Icons/regular/link.svg";
import { ReactComponent as SvgCoffee } from "@energiz3r/component-library/src/Icons/regular/coffee.svg";
import logoUrl from "../../assets/logo.png";
import discordLogo from "../../assets/discord-white.png";
import githubLogo from "../../assets/github-mark.png";

export const AppContainer = () => {
  const [isMenuVisible, setIsMenuVisible] = useState(false);

  const shouldStreamResponses = true;

  const {
    socket,
    isConnecting,
    isAwaitingResponse,
    modelName,
    device,
    temperature,
    maxTokens,
    conversation,
    changeMaxTokens,
    changeTemperature,
    sendMessage,
    discardConversation,
  } = useConversation({ shouldStreamResponses });

  const handleMenuClick = () => {
    setIsMenuVisible(!isMenuVisible);
  };

  return (
    <>
      <Header
        onMenuToggle={handleMenuClick}
        shouldUseLogin={false}
        pageTitle="tanglebox.ai"
        logo={<img src={logoUrl} style={{ width: "52px" }} />}
        menuIconVariant="settings"
      >
        <p>
          {modelName} {device ? `(${device})` : null}
        </p>
        <a
          href="https://github.com/Energiz3r/tanglebox-model-runner"
          style={{ display: "flex" }}
          target="_blank"
        >
          <img
            src={githubLogo}
            style={{
              width: "30px",
              height: "30px",
              marginLeft: "1rem",
              marginRight: ".5rem",
              marginTop: "10px",
            }}
          />
          <p>
            <span className={styles.headerLink}>GitHub</span>
            <SvgLink
              style={{ fill: palette.theme.textHighlight, fontSize: "12px" }}
            />
          </p>
        </a>
        <a
          href="https://www.paypal.me/Teastwood"
          style={{ display: "flex" }}
          target="_blank"
        >
          <SvgCoffee
            style={{
              fill: palette.theme.textHighlight,
              fontSize: "30px",
              marginLeft: "1rem",
              marginRight: ".5rem",
              marginTop: "11px",
            }}
          />
          <p>
            <span className={styles.headerLink}>Buy me coffee</span>
            <SvgLink
              style={{ fill: palette.theme.textHighlight, fontSize: "12px" }}
            />
          </p>
        </a>
        <a
          href="https://discord.com/invite/76zAeaP"
          style={{ display: "flex" }}
          target="_blank"
        >
          <img
            src={discordLogo}
            style={{
              width: "32px",
              height: "25px",
              marginLeft: "1rem",
              marginRight: ".5rem",
              marginTop: "14px",
            }}
          />
          <p>
            <span className={styles.headerLink}>Join Discord</span>
            <SvgLink
              style={{ fill: palette.theme.textHighlight, fontSize: "12px" }}
            />
          </p>
        </a>
      </Header>
      {isMenuVisible ? (
        <Menu onMenuClose={handleMenuClick}>
          {isConnecting ? (
            <MenuItem>
              <center>
                <span style={{ color: palette.colors.red }}>
                  Not connected!
                </span>
              </center>
            </MenuItem>
          ) : null}

          <MenuItem>
            <p>Temperature</p>
            <FloatInput
              onChange={changeTemperature}
              defaultValue={temperature}
              maxValue={100}
              fullWidth
              step={0.1}
              enabled={Boolean(socket)}
            />
          </MenuItem>

          <MenuItem>
            <p>Max Tokens</p>
            <IntegerInput
              onChange={changeMaxTokens}
              defaultValue={maxTokens}
              maxValue={10000}
              fullWidth
              enabled={Boolean(socket)}
            />
          </MenuItem>
        </Menu>
      ) : null}

      <ContentSection>
        <ContentHeader label="conversation" color="green" isCentered />
        <Conversation
          isConnecting={isConnecting}
          isAwaitingResponse={isAwaitingResponse}
          conversation={conversation}
          shouldShowTyping={shouldStreamResponses}
          sendMessage={sendMessage}
          discardConversation={discardConversation}
        />
      </ContentSection>

      <ContentSection isContentCentered>
        <p>&copy; Tanglebox 2023</p>
        <p>
          <a
            href="https://tanglebox.ai"
            target="_blank"
            style={{ color: palette.theme.textNormal }}
          >
            tanglebox.ai
          </a>
          {" | "}
          <a
            href="https://github.com/Energiz3r"
            target="_blank"
            style={{ color: palette.theme.textNormal }}
          >
            github.com/energiz3r
          </a>
          {" | "}
          <a
            href="https://www.paypal.me/teastwood"
            target="_blank"
            style={{ color: palette.theme.textNormal }}
          >
            paypal.me/teastwood
          </a>
        </p>
      </ContentSection>
    </>
  );
};
