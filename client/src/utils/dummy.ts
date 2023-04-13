import { conversationMessage } from "../components/Conversation/Conversation";

export const testConversationMarkup = [
  {
    role: "User",
    message: "write me a hello world python function",
    timestampReceived: 1680732181587,
  },
  {
    role: "AI",
    message: `Certainly! Here is a "Hello, World!" function written in Python:
\`\`\`py
def hello_world():
  print("Hello, World!")

hello_world()
\`\`\`
This function will print the string "Hello, World!" when it is called. To run the function, you can simply call it at the end of the script, like you see above.

I hope this helps! Let me know if you have any questions.`,
    timestampReceived: 1680732200173,
  },
  {
    role: "User",
    message: `what do you think of the software ooga- er, ooberg -- ooga booga - um oobabooba?`,
    timestampReceived: 1680732200173,
  },
];

export const testConversation: Array<conversationMessage> = [
  {
    role: "AI",
    message: "How can I help you?",
    timestampReceived: 1680731908442,
  },
  {
    role: "User",
    message: "How do magnets work?",
    timestampReceived: 1680731995770,
  },
  {
    role: "AI",
    message:
      "Magnets work on the principle of magnetic fields. When two magnets are placed close to each other, their magnetic fields interact and produce an attractive or repulsive force. This force is responsible for the phenomenon of magnetism.",
    timestampReceived: 1680732001049,
  },
];
