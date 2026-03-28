import { useState } from "react";
import {
  Mic,
  Cpu,
  Radio,
  Volume2,
  FileText,
  ArrowRight,
  ExternalLink,
} from "lucide-react";
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
    <>
      <PageTitle
        tag="FOUNDATIONS / RESEARCH PROTOTYPE"
        title="Research & Architecture"
        description="Understand the assumptions, model boundaries and evidence behind each transmission."
      />
      <Panel
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
      </Panel>
      <div className="two-col">
        <Panel title="The research question" eyebrow="MEANING VS. WAVEFORM">
          <p>
            How do conventional waveform coding, neural audio coding and STT/TTS
            semantic transmission compare under constrained and degraded links
            for Indian languages?
          </p>
          <p>
            Semantic transmission can reduce message size, but recognizer errors
            affect meaning and synthesized speech changes voice, prosody and
            identity. Low bitrate alone does not establish communication
            quality.
          </p>
          <p>
            Compare the same source recording under the same packet policy,
            channel configuration and seed. Use human reference transcripts for
            WER / CER and broader datasets before making language comparisons.
          </p>
        </Panel>
        <Panel
          title="Mathematical assumptions"
          eyebrow="EXPLICIT / REPRODUCIBLE"
        >
          <div className="formula">
            y = hx + n <br /> E[|x|²] = 1 · E[|n|²] = N₀
            <br /> Es/N₀ = 10^(dB / 10)
          </div>
          <p>
            AWGN: h = 1. Rayleigh: h ~ CN(0,1) independently per symbol; the
            receiver knows h exactly. Repetition changes transmitted bits; the
            noise is defined per symbol.
          </p>
          <p>
            BPSK reference: Q(√(2Es/N₀)). QPSK: Q(√(Es/N₀)) per bit. CRC detects
            corruption and does not correct errors.
          </p>
        </Panel>
      </div>
      <Panel title="Boundaries of this prototype" eyebrow="SCIENTIFIC HONESTY">
        <div className="three-col">
          <div>
            <FileText className="cyan" />
            <h3>Simulation, not physical RF</h3>
            <p>
              No SDR, carrier synchronization, multipath, hardware scheduling or
              RF calibration. Packet boundaries are provided by the simulator.
            </p>
          </div>
          <div>
            <Cpu className="violet-text" />
            <h3>Pretrained ≠ newly trained</h3>
            <p>
              Whisper, MMS and EnCodec are pretrained providers. The separate
              PyTorch latent-channel experiment is a small research extension,
              with its own train / validation / test split.
            </p>
          </div>
          <div>
            <Volume2 className="cyan" />
            <h3>Metrics have domains</h3>
            <p>
              SI-SDR evaluates waveform similarity and is omitted for semantic
              TTS. WER uses NFC normalization and whitespace tokenization. No
              fabricated confidence, STOI, PESQ or human listening score.
            </p>
          </div>
        </div>
      </Panel>
      <Panel title="Primary references" eyebrow="MODELS / IMPLEMENTATIONS">
        <div className="reference-list">
          {[
            [
              "Faster Whisper · CTranslate2 CPU inference",
              "https://github.com/SYSTRAN/faster-whisper",
            ],
            [
              "Meta MMS · multilingual speech synthesis",
              "https://huggingface.co/facebook/mms-tts-kan",
            ],
            [
              "Meta EnCodec · neural audio compression",
              "https://github.com/facebookresearch/encodec",
            ],
            [
              "AI4Bharat IndicConformer · future provider evaluation",
              "https://huggingface.co/ai4bharat/indicconformer-600m-multilingual",
            ],
            ["OpenSLR · licensed speech corpora", "https://www.openslr.org/"],
            [
              "FLEURS · multilingual evaluation dataset",
              "https://huggingface.co/datasets/google/fleurs",
            ],
          ].map(([name, url]) => (
            <a key={url} href={url} target="_blank" rel="noreferrer">
              {name}
              <ExternalLink size={15} />
            </a>
          ))}
        </div>
      </Panel>
    </>
  );
}
