
export function Waveform({ data }: { data: number[] }) {
  return (
    <div className="waveform" aria-label="Measured waveform envelope">
      {data.map((peak, i) => (
        <i key={i} style={{ height: Math.max(3, peak * 86) + "%" }} />
      ))}
    </div>
  );
}