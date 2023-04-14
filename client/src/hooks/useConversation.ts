import { useEffect, useState } from "react";
import { flushSync } from "react-dom";
import { conversationMessage } from "../components/Conversation/Conversation";

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
  //console.log(msgParts, msgProcessed);
  return msgProcessed;
};

// @ts-ignore
const isDev = import.meta.env.DEV;
const protocol = location.protocol === "https:" ? "wss" : "ws";
//const protocol = 'wss'
const host = isDev
  ? `${protocol}://localhost:8080`
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

  const socketHandler = (event: any) => {
    let thisMessage = event.data || "";
    if (thisMessage.includes("#-set-#")) return;
    if (thisMessage.includes("#-delete-#")) {
      setConversation([]);
      return;
    }
    if (thisMessage.includes("#-device-name-#")) {
      setDevice(thisMessage.replace("#-device-name-#", "").toUpperCase());
      return;
    }
    if (thisMessage.includes("#-max-new-tokens-#")) {
      setMaxTokens(parseInt(thisMessage.replace("#-max-new-tokens-#", "")));
      return;
    }
    if (thisMessage.includes("#-temperature-#")) {
      setTemperature(parseFloat(thisMessage.replace("#-temperature-#", "")));
      return;
    }
    if (thisMessage.includes("#-model-name-#")) {
      let model = thisMessage.replace("#-model-name-#", "");
      model = model.slice(model.lastIndexOf("\\") + 1);
      model = model.slice(model.lastIndexOf("/") + 1);
      setModelName(model);
      return;
    }
    const isCodeBlockBoundary = thisMessage.includes("```");
    const isAcknowdledgement = thisMessage.includes("#a-c-k#");
    const isServerFinished = thisMessage.includes("#f-i-n#");

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
      socket.send(`#-set-max-tokens-#${value}`);
      setMaxTokens(value);
    }
  };
  const changeTemperature = (value: number) => {
    if (socket) {
      socket.send(`#-set-temp-#${value}`);
      setTemperature(value);
    }
  };
  const changeStreaming = (value: boolean) => {
    if (socket) {
      socket.send(`#-set-streaming-#${value ? "true" : "false"}`);
    }
  };

  const socketConnectHandler = () => {
    console.log("Connected");
    setIsConnecting(false);
    if (socket) {
      socket.send(`#-get-config-#`);
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
    setIsConnecting(true);
    setTimeout(() => {
      console.log("Reconnecting...");
      connect();
    }, 1000);
  };

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
      socket.send("#-delete-#");
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
