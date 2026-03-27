
import { useState } from "react";
import { Mic, Cpu, Radio, Volume2, ArrowRight } from "lucide-react";
import { PageTitle, Panel } from "../components/ui";
const stages = [
  {
    name: "Source",
    icon: Mic,
    text: "Browser MediaRecorder captures speech. Backend FFmpeg validates, makes mono audio and resamples to the provider boundary. Original upload is stored separately.",
  },
  {
    name: "Encoder",
    icon: Cpu,
    text: "Opus encodes a conventional waveform. EnCodec emits quantized 10-bit indices. Semantic mode recognizes speech and encodes NFC UTF-8 text, optionally with reversible zlib compression.",
  },
  {
    name: "Radio chain",
    icon: Radio,
    text: "Binary packets include session, sequence, total, language, mode, payload length and CRC32. BPSK or QPSK traverses AWGN or IID flat Rayleigh fading with ideal coherent channel knowledge.",
  },
  {
    name: "Receiver",
    icon: Volume2,
    text: "Only CRC-valid, consistent packets are reassembled. Missing data fails the whole payload. Opus and EnCodec decode recovered bytes; MMS synthesizes recovered text. Sender text is never substituted.",
  },
];
export default function Research() {
  const [selected, setSelected] = useState(2);
  return (
    <><PageTitle
        tag="FOUNDATIONS / RESEARCH PROTOTYPE"
        title="Research & Architecture"
        description="Understand the assumptions, model boundaries and evidence behind each transmission."
      /><Panel
        title="Inside the transceiver"
        eyebrow="INTERACTIVE SYSTEM DIAGRAM"
      >
        <div className="architecture">
          {stages.map((stage, i) => (
            <div key={stage.name}>
              <button
                className={
                  "architecture-node " + (selected === i ? "selected" : "")
                }
                onClick={() => setSelected(i)}
              >
                <stage.icon size={28} />
                <strong>{stage.name}</strong>
                <small>0{i + 1}</small>
              </button>
              {i < 3 && <ArrowRight size={20} />}
            </div>
          ))}
        </div>
        <div className="architecture-detail">
          <span className="eyebrow">{stages[selected].name}</span>
          <p>{stages[selected].text}</p>
        </div>
      </Panel></>
  );
}