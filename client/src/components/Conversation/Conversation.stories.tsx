import React from "react";
import { Conversation, conversationMessage } from "./Conversation";
import type { ComponentStory } from "@storybook/react";

import { testConversation, testConversationMarkup } from "../../utils/dummy";

const options = {
  title: "Conversation",
  component: Conversation,
};

export default options;

const Template: ComponentStory<typeof Conversation> = (args) => (
  <Conversation {...args} />
);

export const Default = Template.bind({});
Default.args = {
  conversation: { ...testConversation, ...testConversationMarkup },
};

export const NoMarkup = Template.bind({});
NoMarkup.args = {
  conversation: testConversation,
};

export const Waiting = Template.bind({});
Waiting.args = {
  conversation: testConversation,
};
