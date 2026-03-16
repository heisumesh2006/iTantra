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
export type Language = {
  code: string;
  name: string;
  native: string;
  status: string;
  stt_installed: boolean;
  tts_installed: boolean;
  stt_verified: boolean;
  tts_verified: boolean;
  tts_model: string;
  stt_model: string;
};
export type Capabilities = {
  simulation_mode: boolean;
  languages: Language[];
  neural: {
    installed: boolean;
    verified: boolean;
    model: string;
    bandwidths: number[];
  };
  stt: { provider: string; model: string };
  privacy: string;
};