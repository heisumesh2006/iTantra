
import { test, expect } from "@playwright/test";
import path from "node:path";
const audio = path.resolve("../research/results/smoke/en-synthetic.wav");
test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await expect(
    page.getByText("Backend connected", { exact: true }),
  ).toBeVisible({ timeout: 30000 });
});
test("navigation, upload, ideal Opus recovery and actual audio playback", async ({
  page,
}) => {
  await page.goto("/");
  await page.screenshot({
    path: "../docs/screenshots/overview.png",
    fullPage: true,
  });
  await expect(
    page.getByRole("heading", { name: "Less bandwidth. More meaning." }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Launch Transceiver" }).click();
  await page.getByLabel("Upload audio file").setInputFiles(audio);
  await expect(page.getByText("Source recording", { exact: true })).toBeVisible(
    { timeout: 30000 },
  );
  await page.getByLabel("Channel model").selectOption("ideal");
  await page.getByRole("button", { name: "Start Transmission" }).click();
  await expect(page.getByText("Payload recovered with valid CRCs")).toBeVisible(
    { timeout: 120000 },
  );
  await page.screenshot({
    path: "../docs/screenshots/transceiver.png",
    fullPage: true,
  });
  const receiver = page.locator("audio").last();
  await receiver.evaluate((element: HTMLAudioElement) => element.play());
  await expect
    .poll(() =>
      receiver.evaluate((element: HTMLAudioElement) => element.currentTime),
    )
    .toBeGreaterThan(0);
  await page
    .getByRole("link", { name: "Experiment History", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Experiment History." }),
  ).toBeVisible();
  await expect(page.locator("table tbody tr").first()).toBeVisible();
});
test("severe channel gives explicit failed recovery", async ({ page }) => {
  await page.goto("/studio");
  await page.getByLabel("Upload audio file").setInputFiles(audio);
  await expect(page.getByText("Source recording", { exact: true })).toBeVisible(
    { timeout: 30000 },
  );
  await page.getByLabel("Packet erasure (%)").fill("100");
  await page.getByRole("button", { name: "Start Transmission" }).click();
  await expect(
    page.getByText("Payload recovery failed", { exact: true }),
  ).toBeVisible({ timeout: 120000 });
  await expect(page.locator("audio")).toHaveCount(1);
});
test("real channel charts and every page render at mobile width", async ({
  page,
}) => {
  await page.goto("/channel");
  await page.getByLabel("Trials at each Es/N0").fill("2");
  await page.getByRole("button", { name: "Run SNR sweep" }).click();
  await expect(page.locator(".recharts-surface").first()).toBeVisible();
  await page.screenshot({
    path: "../docs/screenshots/channel-lab.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  for (const route of [
    "/",
    "/studio",
    "/channel",
    "/speech",
    "/compression",
    "/analytics",
    "/live",
    "/research",
    "/history",
  ]) {
    await page.goto(route);
    await expect(page.locator("h1")).toBeVisible();
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= window.innerWidth,
      ),
    ).toBe(true);
  }
});

for (const [mode, label] of [
  ["neural", "B · Neural / EnCodec"],
  ["semantic", "C · Semantic / STT → TTS"],
]) {
  test(`actual ${mode} browser transmission`, async ({ page }) => {
    await page.goto("/studio");
    await page.getByLabel("Upload audio file").setInputFiles(audio);
    await expect(
      page.getByText("Source recording", { exact: true }),
    ).toBeVisible({ timeout: 30000 });
    await page.getByLabel("Communication mode").selectOption(mode);
    await page.getByLabel("Channel model").selectOption("ideal");
    await page.getByRole("button", { name: "Start Transmission" }).click();
    await expect(
      page.getByText("Payload recovered with valid CRCs"),
    ).toBeVisible({ timeout: 120000 });
    await expect(page.locator("audio")).toHaveCount(2);
    if (mode === "semantic")
      await expect(
        page
          .getByText("The radio link carries our voice across the network.", {
            exact: true,
          })
          .last(),
      ).toBeVisible();
  });
}

test("invalid audio and missing language models have visible errors", async ({
  page,
}) => {
  await page.goto("/studio");
  await page.getByLabel("Upload audio file").setInputFiles({
    name: "invalid.wav",
    mimeType: "audio/wav",
    buffer: Buffer.from("not audio"),
  });
  await expect(page.getByRole("alert")).toContainText("could not decode");
  await page.goto("/speech");
  await page.getByRole("button", { name: "Tamil", exact: false }).click();
  await page
    .getByRole("button", { name: "Text to speech", exact: true })
    .click();
  await page.getByRole("textbox").fill("வணக்கம்");
  await page.getByRole("button", { name: "Run synthesis" }).click();
  await expect(page.getByRole("alert")).toContainText("TTS weights missing");
});

test("microphone record pause resume and upload with synthetic capture", async ({
  browser,
}) => {
  const context = await browser.newContext({ permissions: ["microphone"] });
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:5173/studio");
  await page.getByRole("button", { name: "Record voice", exact: true }).click();
  await expect(page.getByText(/Recording ·/)).toBeVisible();
  await page.getByRole("button", { name: "Pause", exact: true }).click();
  await expect(page.getByText(/Paused ·/)).toBeVisible();
  await page.getByRole("button", { name: "Resume", exact: true }).click();
  await expect(page.getByText(/Recording ·/)).toBeVisible();
  await expect
    .poll(async () => await page.getByText(/Recording ·/).textContent())
    .not.toContain("· 0s");
  await page.getByRole("button", { name: "Stop", exact: true }).click();
  await expect(page.getByText("Source recording", { exact: true })).toBeVisible(
    { timeout: 30000 },
  );
  await context.close();
});