export const processLinebreaks = (msg: string, isStreaming: boolean) => {
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
