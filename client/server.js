const publicFilesDir = "./client/dist";
const webPort = 4100;

import path from "path";
import express from "express";
import { dirname } from "path";
import { fileURLToPath } from "url";

if (process.env.NODE_ENV)
  console.log("NODE_ENV was defined, it was:", process.env.NODE_ENV);
if (process.env.PORT)
  console.log("PORT was defined, it was:", process.env.PORT);

const dev = process.env.NODE_ENV === "development";
const port = process.env.PORT || webPort;

const app = express();
const __dirname = dirname(fileURLToPath(import.meta.url));
const publicPath = path.join(__dirname, publicFilesDir);

app.use(express.static(publicPath));
app.get("", (req, res) => {
  res.sendFile(path.join(publicPath, "index.html"));
});
app.listen(port, () => console.log(`\nServer online on port: ${port}\n`));
console.log("\nStarting server...\n");
console.log("Public root:", publicPath);
console.log("NODE_ENV set to:", process.env.NODE_ENV, "Dev mode:", dev);
