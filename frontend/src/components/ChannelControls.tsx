import type { Channel } from "../types";
export function ChannelControls({
  value,
  onChange,
}: {
  value: Channel;
  onChange: (value: Channel) => void;
}) {
  const set = (key: keyof Channel, v: string | number) =>
    onChange({ ...value, [key]: v });
  return (
    <div className="controls-grid">
      <label>
        Channel model
        <select
          value={value.channel}
          onChange={(e) => set("channel", e.target.value)}
        >
          <option value="ideal">Ideal / noiseless</option>
          <option value="awgn">AWGN</option>
          <option value="rayleigh">Flat Rayleigh · perfect CSI</option>
        </select>
      </label>
      <label>
        Modulation
        <select
          value={value.modulation}
          onChange={(e) => set("modulation", e.target.value)}
        >
          <option>BPSK</option>
          <option>QPSK</option>
        </select>
      </label>
      <label className="span-two">
        Es/N0 <span className="cyan">{value.snr_db} dB</span>
        <input
          type="range"
          min={-10}
          max={30}
          value={value.snr_db}
          onChange={(e) => set("snr_db", +e.target.value)}
        />
        <div className="range-labels">
          <span>Severe</span>
          <span>Moderate</span>
          <span>Excellent</span>
        </div>
      </label>
      <label>
        Packet payload (bytes)
        <input
          type="number"
          min={32}
          max={1024}
          value={value.packet_size}
          onChange={(e) => set("packet_size", +e.target.value)}
        />
      </label>
      <label>
        Error correction
        <select
          value={value.repetition}
          onChange={(e) => set("repetition", +e.target.value)}
        >
          <option value={1}>None · CRC detection</option>
          <option value={3}>Repetition 3 · majority</option>
        </select>
      </label>
      <label>
        Packet erasure (%)
        <input
          type="number"
          min={0}
          max={100}
          step={1}
          value={value.erasure_rate * 100}
          onChange={(e) => set("erasure_rate", +e.target.value / 100)}
        />
      </label>
      <label>
        Post-demod bit flip (%)
        <input
          type="number"
          min={0}
          max={50}
          step={0.01}
          value={value.bit_flip_rate * 100}
          onChange={(e) => set("bit_flip_rate", +e.target.value / 100)}
        />
      </label>
      <label>
        Random seed
        <input
          type="number"
          min={0}
          max={4294967295}
          value={value.seed}
          onChange={(e) => set("seed", +e.target.value)}
        />
      </label>
      <label>
        Symbol rate (baud)
        <input
          type="number"
          min={100}
          max={1000000}
          value={value.symbol_rate}
          onChange={(e) => set("symbol_rate", +e.target.value)}
        />
      </label>
    </div>
  );
}
