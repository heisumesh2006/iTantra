export type Mode = "conventional" | "neural" | "semantic" | "adaptive";
export type Channel = {
  modulation: "BPSK" | "QPSK";
  channel: "ideal" | "awgn" | "rayleigh";
  snr_db: number;
  packet_size: number;
  repetition: 1 | 3;
  erasure_rate: number;
  bit_flip_rate: number;
  seed: number;
  symbol_rate: number;
};