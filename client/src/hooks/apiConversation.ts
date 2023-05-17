import { useRef, useState } from "react";
import { conversationMessage } from "../components/Conversation/Conversation";
import { processLinebreaks } from "../utils/conversations";

// @ts-ignore
const isDev = import.meta.env.DEV;
const host = isDev
  ? `${location.protocol}//localhost:8080`
  : `${location.protocol}//${location.host}`;
if (isDev) console.log(`Dev mode - using ${host} for API endpoint`);

export const useApiConversation = ({
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
  const [isAwaitingResponse, setIsAwaitingResponse] = useState(false);
  const isProcessingBackticksRef = useRef(false);

  const processChunk = (chunk: string) => {
    const isProcessingBackticks = isProcessingBackticksRef.current;
    let thisMessage = chunk || "";
    const isCodeBlockBoundary = thisMessage.includes("```");

    if (isCodeBlockBoundary) {
      const numOfBacktickSets = (thisMessage.match(/```/g) || []).length;
      if (numOfBacktickSets % 2 === 1) {
        isProcessingBackticksRef.current = !isProcessingBackticks;
      }
    }

    if (
      !isCodeBlockBoundary &&
      !isProcessingBackticks &&
      thisMessage.includes("\n")
    ) {
      thisMessage = processLinebreaks(thisMessage, shouldStreamResponses);
    }

    if (shouldStreamResponses) {
      setConversation((prev) => {
        const aiMessages = prev.filter((msg) => msg.role === "AI");
        const lastAiMessage = aiMessages[aiMessages.length - 1];
        const newConvo = prev.filter(
          (msg: any) =>
            msg.timestampReceived !== lastAiMessage.timestampReceived,
        );
        newConvo.push({
          role: "AI",
          message: lastAiMessage.message + thisMessage,
          timestampReceived: new Date().valueOf(),
        });
        return newConvo;
      });
    } else {
      const newConvo = conversation;
      newConvo.push({
        role: "AI",
        message: thisMessage,
        timestampReceived: new Date().valueOf(),
      });
      setConversation(newConvo);
    }
  };

  const sendMessage = async (inputText: string) => {
    setIsAwaitingResponse(true);
    const newConvo = conversation;
    const timestamp = new Date().valueOf();
    newConvo.push({
      role: "User",
      message: inputText,
      timestampReceived: timestamp,
    });
    if (shouldStreamResponses) {
      newConvo.push({
        role: "AI",
        message: "",
        timestampReceived: timestamp + 1,
      });
    }
    setConversation(newConvo);
    const data = {
      userPrompt: inputText,
      shouldStream: shouldStreamResponses,
      temperature: temperature,
      maxNewTokens: maxTokens,
    };
    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    };
    try {
      const response = await fetch(`${host}/conversation`, requestOptions);
      const decoder = new TextDecoder();
      const reader = response.body?.getReader();
      const readStream = () => {
        return reader?.read().then(({ value, done }) => {
          const chunk = decoder.decode(value);
          if (done) {
            //console.log("received DONE chunk:", chunk);
            if (shouldStreamResponses) {
              processChunk(chunk);
            }
            setIsAwaitingResponse(false);
            return;
          } else {
            //console.log("received chunk:", chunk);
            processChunk(chunk);
          }
          readStream();
        });
      };
      readStream();
    } catch (error) {
      setIsAwaitingResponse(false);
      console.error("Error fetching data:", error);
    }
  };

  const discardConversation = () => {
    setConversation([]);
  };

  return {
    isConnecting: false,
    isAwaitingResponse,
    sendMessage,
    discardConversation,
  };
};
