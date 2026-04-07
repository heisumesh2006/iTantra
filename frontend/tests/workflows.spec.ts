
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