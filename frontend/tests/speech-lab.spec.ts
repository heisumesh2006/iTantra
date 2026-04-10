import { test, expect } from "@playwright/test";
import path from "node:path";
test("speech-lab-roundtrip with native Kannada provider", async ({ page }) => {
  await page.goto("/speech");
  await page
    .getByLabel("Upload audio file")
    .setInputFiles(path.resolve("../research/results/smoke/kn-synthetic.wav"));
  await expect(page.getByText("Source recording", { exact: true })).toBeVisible(
    { timeout: 30000 },
  );
  await page.getByRole("button", { name: "Kannada", exact: false }).click();
  await page
    .getByRole("button", { name: "Run speech round trip", exact: true })
    .click();
  await expect(page.locator("audio")).toHaveCount(2, { timeout: 120000 });
  await expect(
    page.getByText("ನಮಸ್ಕಾರ ಇದು ನಮ್ಮ ಧ್ವನಿಯ ಪರೀಕ್ಷೆ", { exact: true }).last(),
  ).toBeVisible();
  await expect(
    page.getByText("STT: Harveenchadha/vakyansh-wav2vec2-kannada-knm-560", {
      exact: false,
    }),
  ).toBeVisible();
  const output = page.locator("audio").last();
  await output.evaluate((element: HTMLAudioElement) => element.play());
  await expect
    .poll(() =>
      output.evaluate((element: HTMLAudioElement) => element.currentTime),
    )
    .toBeGreaterThan(0);
  await page.screenshot({
    path: "../docs/screenshots/kannada-speech-lab.png",
    fullPage: true,
  });
});
