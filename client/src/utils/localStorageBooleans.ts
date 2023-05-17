export const getLocalStorageBooleanValue = (name: string) => {
  return (localStorage.getItem(name) ?? "true") === "true" ? true : false;
};

export const setLocalStorageBooleanValue = (name: string, value: boolean) => {
  localStorage.setItem(name, value ? "true" : "false");
};
