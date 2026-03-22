
import { useEffect, useRef } from "react";
import type { Media } from "../types";
export function Waveform({ data }: { data: number[] }) {
  return (
    <div className="waveform" aria-label="Measured waveform envelope">
      {data.map((peak, i) => (
        <i key={i} style={{ height: Math.max(3, peak * 86) + "%" }} />
      ))}
    </div>
  );
}
export function Spectrogram({ media }: { media: Media }) {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const canvas = ref.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;
    const values = media.spectrogram.values;
    canvas.width = values[0]?.length || 1;
    canvas.height = values.length;
    for (let y = 0; y < values.length; y++)
      for (let x = 0; x < values[y].length; x++) {
        const level = Math.max(0, Math.min(1, (values[y][x] + 100) / 100));
        ctx.fillStyle = `hsl(${250 - level * 90} 65% ${8 + level * 62}%)`;
        ctx.fillRect(x, values.length - 1 - y, 1, 1);
      }
  }, [media]);
  return (
    <figure className="spectrogram">
      <canvas ref={ref} />
      <figcaption>
        Measured STFT · 0–{media.sample_rate / 2} Hz · time →
      </figcaption>
    </figure>
  );
}