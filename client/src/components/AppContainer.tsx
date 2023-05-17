import { useState, useEffect } from "react";
import { styles } from "./AppContainer.css";
import { palette } from "@energiz3r/component-library/src/theme";

import { Header } from "@energiz3r/component-library/src/components/Header/Header";
import { HeaderUtility } from "@energiz3r/component-library/src/components/Header/HeaderUtility/HeaderUtility";
import { Menu } from "@energiz3r/component-library/src/components/Menu/Menu";
import { MenuItem } from "@energiz3r/component-library/src/components/Menu/MenuItem";
import { IntegerInput } from "@energiz3r/component-library/src/components/Inputs/IntegerInput/IntegerInput";
import { FloatInput } from "@energiz3r/component-library/src/components/Inputs/FloatInput/FloatInput";
import { ContentSection } from "@energiz3r/component-library/src/components/ContentSection/ContentSection";
import { ContentHeader } from "@energiz3r/component-library/src/components/ContentHeader/ContentHeader";
import { Conversation } from "./Conversation/Conversation";
import { useConversation } from "../hooks/useConversation";
import { DarkThemeToggle } from "@energiz3r/component-library/src/components/DarkThemeToggle/DarkThemeToggle";

import {
  getLocalStorageBooleanValue,
  setLocalStorageBooleanValue,
} from "../utils/localStorageBooleans";

import { ReactComponent as SvgCoffee } from "@energiz3r/component-library/src/Icons/regular/coffee.svg";
import logoUrl from "../../assets/logo.png";
import discordLogo from "../../assets/discord-white.png";
import githubLogo from "../../assets/github-mark.png";

export const AppContainer = () => {
  const [isMenuVisible, setIsMenuVisible] = useState(false);
  const [shouldStreamResponses, setShouldStreamResponses] = useState(
    getLocalStorageBooleanValue("shouldStreamResponses"),
  );
  const [shouldUseWebsockets, setShouldUseWebsockets] = useState(
    getLocalStorageBooleanValue("shouldUseWebsockets"),
  );

  const {
    isConnecting,
    isAwaitingResponse,
    modelName,
    device,
    temperature,
    maxTokens,
    conversation,
    setMaxTokens,
    setTemperature,
    sendMessage,
    discardConversation,
  } = useConversation({ shouldStreamResponses, shouldUseWebsockets });

  const handleMenuClick = () => {
    setIsMenuVisible(!isMenuVisible);
  };

  const handleToggleStreaming = () => {
    const shouldStream = !shouldStreamResponses;
    setLocalStorageBooleanValue("shouldStreamResponses", shouldStream);
    setShouldStreamResponses(shouldStream);
  };

  const handleToggleWebsockets = () => {
    const shouldWebsocket = !shouldUseWebsockets;
    setLocalStorageBooleanValue("shouldUseWebsockets", shouldWebsocket);
    setShouldUseWebsockets(shouldWebsocket);
  };

  return (
    <>
      <Header
        onMenuToggle={handleMenuClick}
        shouldUseLogin={false}
        pageTitle="tanglebox.ai"
        logo={<img src={logoUrl} style={{ width: "52px" }} />}
        shouldHaveMenu
        menuIconVariant="settings"
      >
        <p>
          {modelName} {device ? `(${device})` : null}
        </p>
        <HeaderUtility
          imageUrl={githubLogo}
          link="https://github.com/Energiz3r/tanglebox-model-runner"
          linkText="GitHub"
          linkShouldOpenNewTab
        />
        <HeaderUtility
          Icon={SvgCoffee}
          link="https://www.paypal.me/Teastwood"
          linkText="Buy me coffee"
          linkShouldOpenNewTab
        />
        <HeaderUtility
          imageUrl={discordLogo}
          iconOrImageClassName={styles.discordImage}
          link="https://discord.com/invite/76zAeaP"
          linkText="Join Discord"
          linkShouldOpenNewTab
        />
      </Header>

      <Menu isVisible={isMenuVisible} onMenuClose={handleMenuClick}>
        {isConnecting ? (
          <MenuItem>
            <center>
              <span style={{ color: palette.colors.red }}>Not connected!</span>
            </center>
          </MenuItem>
        ) : null}

        <MenuItem>
          <p>Use websockets</p>
          <div className={styles.toggleBackground}>
            <DarkThemeToggle
              defaultMode={shouldUseWebsockets ? "dark" : "light"}
              onClick={handleToggleWebsockets}
            />
          </div>
        </MenuItem>

        <MenuItem>
          <p>Stream responses {shouldStreamResponses}</p>
          <div className={styles.toggleBackground}>
            <DarkThemeToggle
              defaultMode={shouldStreamResponses ? "dark" : "light"}
              onClick={handleToggleStreaming}
            />
          </div>
        </MenuItem>

        <MenuItem>
          <p>Temperature</p>
          <FloatInput
            onChange={setTemperature}
            defaultValue={temperature}
            maxValue={100}
            fullWidth
            step={0.1}
            enabled={!isConnecting}
          />
        </MenuItem>

        <MenuItem>
          <p>Max Tokens</p>
          <IntegerInput
            onChange={setMaxTokens}
            defaultValue={maxTokens}
            maxValue={10000}
            fullWidth
            enabled={!isConnecting}
          />
        </MenuItem>

        <MenuItem>
          <p>More settings coming soon</p>
        </MenuItem>
      </Menu>

      <ContentSection>
        <ContentHeader label="conversation" presetColor="green" isCentered />
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
        <p>Tangles 2023</p>
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
