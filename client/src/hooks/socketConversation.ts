import { useEffect, useState, useRef } from "react";
import { conversationMessage } from "../components/Conversation/Conversation";
import { useInterval } from "@energiz3r/component-library/src/utils/useInterval";
import { msg } from "./conversationConsts";
import { processLinebreaks } from "../utils/conversations";

// @ts-ignore
const isDev = import.meta.env.DEV;
const protocol = location.protocol === "https:" ? "wss" : "ws";
const host = isDev
  ? `${protocol}://localhost:8080`
  : `${protocol}://${location.host}`;
if (isDev) console.log(`Dev mode - using ${host} for websocket endpoint`);

export const useSocketConversation = ({
  shouldUseWebsockets,
  conversation,
  setConversation,
  shouldStreamResponses,
  setModelName,
  setDevice,
  temperature,
  setTemperature,
  maxTokens,
  setMaxTokens,
}: {
  shouldUseWebsockets: boolean;
  conversation: Array<conversationMessage>;
  setConversation: React.Dispatch<
    React.SetStateAction<Array<conversationMessage>>
  >;
  shouldStreamResponses: boolean;
  setModelName: React.Dispatch<React.SetStateAction<string>>;
  setDevice: React.Dispatch<React.SetStateAction<string>>;
  temperature: number;
  setTemperature: React.Dispatch<React.SetStateAction<number>>;
  maxTokens: number;
  setMaxTokens: React.Dispatch<React.SetStateAction<number>>;
}) => {
  const [socket, setSocket] = useState<any>(null);
  const [isAwaitingResponse, setIsAwaitingResponse] = useState(false);
  const messageBufferRef = useRef("");
  const isProcessingBackticksRef = useRef(false);
  const [isConnecting, setIsConnecting] = useState(true);

  const resetStatePartial = () => {
    setIsAwaitingResponse(false);
    setConversation([]);
    messageBufferRef.current = "";
    isProcessingBackticksRef.current = false;
  };

  const socketHandler = (event: any) => {
    const isProcessingBackticks = isProcessingBackticksRef.current;
    const messageBuffer = messageBufferRef.current;
    let thisMessage = event?.data || "";
    if (thisMessage.includes(msg.set)) return;
    if (thisMessage.includes(msg.pong)) return;
    if (thisMessage.includes(msg.delete)) {
      setConversation([]);
      return;
    }
    if (thisMessage.includes(msg.deviceName)) {
      setDevice(thisMessage.replace(msg.deviceName, "").toUpperCase());
      return;
    }
    if (thisMessage.includes(msg.maxNewTokens)) {
      setMaxTokens(parseInt(thisMessage.replace(msg.maxNewTokens, "")));
      return;
    }
    if (thisMessage.includes(msg.temperature)) {
      setTemperature(parseFloat(thisMessage.replace(msg.temperature, "")));
      return;
    }
    if (thisMessage.includes(msg.modelName)) {
      let model = thisMessage.replace(msg.modelName, "");
      model = model.slice(model.lastIndexOf("\\") + 1);
      model = model.slice(model.lastIndexOf("/") + 1);
      setModelName(model);
      return;
    }
    const isAcknowdledgement = thisMessage.includes(msg.ack);
    const isCodeBlockBoundary = thisMessage.includes("```");
    const isServerFinished = thisMessage.includes(msg.fin);

    if (isCodeBlockBoundary) {
      const numOfBacktickSets = (thisMessage.match(/```/g) || []).length;
      if (numOfBacktickSets % 2 === 1) {
        isProcessingBackticksRef.current = !isProcessingBackticks;
      }
    }

    if (isAcknowdledgement) {
      setIsAwaitingResponse(true);
      if (!shouldStreamResponses) return;
      setConversation((prev) => {
        const newConvo = prev;
        newConvo.push({
          role: "AI",
          message: "",
          timestampReceived: new Date().valueOf(),
        });
        return newConvo;
      });
      return;
    }

    if (isServerFinished) {
      setIsAwaitingResponse(false);
      isProcessingBackticksRef.current = false;
      if (shouldStreamResponses) return;
      const thisMsg = messageBuffer;
      setConversation((prev) => {
        const newConvo = prev;
        newConvo.push({
          role: "AI",
          message: thisMsg,
          timestampReceived: new Date().valueOf(),
        });
        return newConvo;
      });
      messageBufferRef.current = "";
      return;
    }

    if (
      !isCodeBlockBoundary &&
      !isProcessingBackticks &&
      thisMessage.includes("\n")
    ) {
      thisMessage = processLinebreaks(thisMessage, shouldStreamResponses);
    }

    if (!shouldStreamResponses) {
      messageBufferRef.current = messageBuffer + thisMessage;
      return;
    }

    setConversation((prev) => {
      const aiMessages = prev.filter((msg) => msg.role === "AI");
      const lastAiMessage = aiMessages[aiMessages.length - 1];
      const newConvo = prev.filter(
        (msg: any) => msg.timestampReceived !== lastAiMessage.timestampReceived,
      );
      newConvo.push({
        role: "AI",
        message: lastAiMessage.message + thisMessage,
        timestampReceived: new Date().valueOf(),
      });
      return newConvo;
    });
  };

  useEffect(() => {
    if (socket) {
      socket.send(`${msg.setMaxNewTokens}${maxTokens}`);
    }
  }, [maxTokens]);

  useEffect(() => {
    if (socket) {
      socket.send(`${msg.setTemperature}${temperature}`);
    }
  }, [temperature]);

  useEffect(() => {
    if (socket) {
      socket.send(
        `${msg.setShouldStream}${shouldStreamResponses ? "true" : "false"}`,
      );
    }
  }, [shouldStreamResponses]);

  const socketConnectHandler = () => {
    console.log("Connected");
    setIsConnecting(false);
    if (socket) {
      socket.send(msg.getConfig);
    }
  };

  const connect = () => {
    if (!shouldUseWebsockets) return;
    try {
      const sock = new WebSocket(host);
      setSocket(sock);
    } catch (e) {}
  };

  const socketDisconnectHandler = () => {
    if (!shouldUseWebsockets) return;
    console.log("Disconnected");
    resetStatePartial();
    setIsConnecting(true);
    setTimeout(() => {
      console.log("Reconnecting...");
      connect();
    }, 1000);
  };

  const ping = () => {
    if (!isConnecting && shouldUseWebsockets) socket.send(msg.ping);
  };

  useInterval(ping, 3000);

  useEffect(() => {
    if (shouldUseWebsockets) {
      connect();
    } else {
      if (socket) {
        socket.close();
      }
    }
  }, [shouldUseWebsockets]);

  useEffect(() => {
    if (!socket) {
      return;
    }
    socket.addEventListener("message", socketHandler);
    socket.addEventListener("open", socketConnectHandler);
    socket.addEventListener("close", socketDisconnectHandler);
    return () => {
      socket.removeEventListener("message", socketHandler);
      socket.removeEventListener("open", socketConnectHandler);
      socket.removeEventListener("close", socketDisconnectHandler);
    };
  }, [socket, conversation, shouldStreamResponses, shouldUseWebsockets]);

  const sendMessage = (inputText: string) => {
    const newConvo = conversation;
    newConvo.push({
      role: "User",
      message: inputText,
      timestampReceived: new Date().valueOf(),
    });
    setConversation(newConvo);
    setIsAwaitingResponse(true);
    if (socket) {
      socket.send(inputText);
    }
  };
  const discardConversation = () => {
    if (socket) {
      socket.send(msg.delete);
    }
  };

  return {
    isConnecting,
    isAwaitingResponse,
    sendMessage,
    discardConversation,
  };
};
