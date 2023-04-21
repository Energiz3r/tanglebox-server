import { useEffect, useState } from "react";
import { flushSync } from "react-dom";
import { conversationMessage } from "../components/Conversation/Conversation";
import { useInterval } from "@energiz3r/component-library/src/utils/useInterval";
import { msg } from "./conversationConsts";

const processLinebreaks = (msg: string, isStreaming: boolean) => {
  const replacePiece = (piece: string) => {
    return piece.replace(/(?<!\n)\n(?!\n)/, "<br />");
  };
  if (isStreaming) return replacePiece(msg);
  const msgParts = msg.split(/(?= )/g);
  let msgProcessed = "";
  let processingCode = false;
  for (let i = 0; i < msgParts.length; i++) {
    const piece = msgParts[i];
    if (piece.includes("```")) processingCode = !processingCode;
    if (processingCode) msgProcessed += piece;
    else msgProcessed += replacePiece(piece);
  }
  return msgProcessed;
};

// @ts-ignore
const isDev = import.meta.env.DEV;
const protocol = location.protocol === "https:" ? "wss" : "ws";
const host = isDev
  ? `${protocol}://localhost:8081`
  : `${protocol}://${location.host}`;
if (isDev) console.log(`Dev mode - using ${host} for websocket endpoint`);

export const useConversation = ({
  shouldStreamResponses,
}: {
  shouldStreamResponses: boolean;
}) => {
  const [socket, setSocket] = useState<any>(null);
  const [isAwaitingResponse, setIsAwaitingResponse] = useState(false);
  const [conversation, setConversation] = useState<Array<conversationMessage>>(
    [],
  );
  const [messageBuffer, setMessageBuffer] = useState("");
  const [isProcessingBackticks, setIsProcessingBackticks] = useState(false);
  const [isConnecting, setIsConnecting] = useState(true);
  const [modelName, setModelName] = useState("loading model...");
  const [device, setDevice] = useState("");
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(512);

  const resetStatePartial = () => {
    setIsAwaitingResponse(false);
    setConversation([]);
    setMessageBuffer("");
    setIsProcessingBackticks(false);
  };

  const socketHandler = (event: any) => {
    let thisMessage = event.data || "";
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
    const isCodeBlockBoundary = thisMessage.includes("```");
    const isAcknowdledgement = thisMessage.includes(msg.ack);
    const isServerFinished = thisMessage.includes(msg.fin);

    if (isCodeBlockBoundary) {
      const numOfBacktickSets = (thisMessage.match(/```/g) || []).length;
      if (numOfBacktickSets % 2 === 1) {
        flushSync(() => {
          setIsProcessingBackticks(!isProcessingBackticks);
        });
      }
    }

    if (isAcknowdledgement) {
      setIsAwaitingResponse(true);
      if (!shouldStreamResponses) return;
      const newConvo = conversation;
      newConvo.push({
        role: "AI",
        message: "",
        timestampReceived: new Date().valueOf(),
      });
      flushSync(() => {
        setConversation(newConvo);
      });
      return;
    }

    if (isServerFinished) {
      setIsAwaitingResponse(false);
      setIsProcessingBackticks(false);
      if (shouldStreamResponses) return;
      const thisMsg = messageBuffer;
      const newConvo = conversation;
      newConvo.push({
        role: "AI",
        message: thisMsg,
        timestampReceived: new Date().valueOf(),
      });
      flushSync(() => {
        setConversation(newConvo);
        setMessageBuffer("");
      });
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
      flushSync(() => {
        setMessageBuffer(messageBuffer + thisMessage);
      });
      return;
    }

    const aiMessages = conversation.filter((msg) => msg.role === "AI");
    const lastAiMessage = aiMessages[aiMessages.length - 1];
    const newConvo = conversation.filter(
      (msg: any) => msg.timestampReceived !== lastAiMessage.timestampReceived,
    );
    newConvo.push({
      role: "AI",
      message: lastAiMessage.message + thisMessage,
      timestampReceived: new Date().valueOf(),
    });
    flushSync(() => {
      setConversation(newConvo);
    });
  };

  const changeMaxTokens = (value: number) => {
    if (socket) {
      socket.send(`${msg.setMaxNewTokens}${value}`);
      setMaxTokens(value);
    }
  };
  const changeTemperature = (value: number) => {
    if (socket) {
      socket.send(`${msg.setTemperature}${value}`);
      setTemperature(value);
    }
  };
  const changeStreaming = (value: boolean) => {
    if (socket) {
      socket.send(`${msg.setShouldStream}${value ? "true" : "false"}`);
    }
  };

  const socketConnectHandler = () => {
    console.log("Connected");
    setIsConnecting(false);
    if (socket) {
      socket.send(msg.getConfig);
    }
  };

  const connect = () => {
    try {
      const sock = new WebSocket(host);
      setSocket(sock);
    } catch (e) {}
  };

  const socketDisconnectHandler = () => {
    console.log("Disconnected");
    resetStatePartial();
    setIsConnecting(true);
    setTimeout(() => {
      console.log("Reconnecting...");
      connect();
    }, 1000);
  };

  const ping = () => {
    if (socket) socket.send(msg.ping);
  };

  useInterval(ping, 3000);

  useEffect(() => {
    connect();
  }, []);

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
  }, [
    socket,
    conversation,
    messageBuffer,
    shouldStreamResponses,
    isProcessingBackticks,
  ]);

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
    changeStreaming,
    sendMessage,
    discardConversation,
  };
};
