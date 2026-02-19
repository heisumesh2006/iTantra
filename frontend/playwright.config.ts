import { defineConfig } from "@playwright/test";
import path from "node:path";
export default defineConfig({
  testDir: "tests",
  timeout: 180000,
  use: {
    baseURL: "http://127.0.0.1:5173",
    headless: true,
    launchOptions: {
      args: [
        "--use-fake-device-for-media-stream",
        "--use-fake-ui-for-media-stream",
        `--use-file-for-fake-audio-capture=${path.resolve("../research/results/smoke/en-synthetic.wav")}`,
      ],
    },
  },
  reporter: [
    [
      "json",
      {
        outputFile: "../research/results/resume-2026-10-13/browser-tests.json",
      },
    ],
    ["list"],
    ["html", { open: "never" }],
  ],
});
