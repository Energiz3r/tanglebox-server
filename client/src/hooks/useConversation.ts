import { useState } from "react";
import { useSocketConversation } from "./socketConversation";
import { useApiConversation } from "./apiConversation";
import { conversationMessage } from "../components/Conversation/Conversation";

export const useConversation = ({
  shouldStreamResponses,
  shouldUseWebsockets,
}: {
  shouldStreamResponses: boolean;
  shouldUseWebsockets: boolean;
}) => {
  const [conversation, setConversation] = useState<Array<conversationMessage>>(
    [],
  );

  const [modelName, setModelName] = useState("loading model...");
  const [device, setDevice] = useState("");
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(512);

  const socketConversation = useSocketConversation({
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
  });
  const apiConversation = useApiConversation({
    conversation,
    setConversation,
    shouldStreamResponses,
    setModelName,
    setDevice,
    temperature,
    setTemperature,
    maxTokens,
    setMaxTokens,
  });

  const { isConnecting, isAwaitingResponse, sendMessage, discardConversation } =
    shouldUseWebsockets ? socketConversation : apiConversation;

  return {
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
  };
};
