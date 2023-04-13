import { defineConfig } from "vite";
//import react from "@vitejs/plugin-react";
import { vanillaExtractPlugin } from "@vanilla-extract/vite-plugin";
import svgr from "vite-plugin-svgr";
import svgrConfig from "./svgr.config";
//import { ViteFaviconsPlugin } from "vite-plugin-favicon";
import reactRefresh from "@vitejs/plugin-react-refresh";

// https://vitejs.dev/config/
export default defineConfig({
  base: "./",
  plugins: [
    //ViteFaviconsPlugin(),
    svgr({ ...svgrConfig }),
    //react(),
    reactRefresh(),
    vanillaExtractPlugin(),
  ],
  build: {
    assetsDir: "static",
  },
  // build: {
  //   rollupOptions: {
  //     external: ["react"],
  //     output: {
  //       globals: {
  //         react: "React",
  //       },
  //     },
  //   },
  // },
  // resolve: {
  //   alias: {
  //     react: "https://cdn.skypack.dev/react",
  //     "react-dom": "https://cdn.skypack.dev/react-dom",
  //   },
  // },
});
