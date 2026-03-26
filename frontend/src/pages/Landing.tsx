
import { Link } from "react-router-dom";
import { ArrowUpRight, ArrowRight, AudioLines, Radio, Cpu, Languages, ShieldCheck } from "lucide-react";
import { Panel } from "../components/ui";
export default function Landing() {
  return (
    <><section className="hero">
        <span className="hero-tag">
          <i />
          INDIAN MULTILINGUAL COMMUNICATION RESEARCH
        </span>
        <h1>
          Less bandwidth.
          <br />
          More <em>meaning.</em>
        </h1>
        <p>
          A local research laboratory for voice communication across constrained
          links. Explore the trade-offs between waveforms, neural codes and
          linguistic meaning.
        </p>
        <div className="button-row">
          <Link className="button" to="/studio">
            Launch Transceiver <ArrowUpRight size={18} />
          </Link>
          <Link className="button secondary" to="/analytics">
            Explore measured results <ArrowRight size={16} />
          </Link>
        </div>
        <div className="hero-footnote">
          <ShieldCheck size={15} />
          Local-first speech processing <span>·</span> Explicit software radio
          simulation
        </div>
        <div className="orbital-visual" aria-hidden="true">
          <div className="orbit o1" />
          <div className="orbit o2" />
          <div className="orbit o3" />
          <div className="orb-core">
            <Radio size={48} />
          </div>
          <div className="satellite s1">
            <AudioLines size={23} />
          </div>
          <div className="satellite s2">
            <Cpu size={23} />
          </div>
          <span className="orbit-label l1">VOICE / INPUT</span>
          <span className="orbit-label l2">RECOVER / SYNTHESIZE</span>
          <span className="orbit-label l3">SIMULATED RADIO LINK</span>
        </div>
      </section><div className="flow-ribbon">
        <span>
          <AudioLines size={20} />
          Voice
        </span>
        <ArrowRight size={17} />
        <span>
          <Cpu size={20} />
          Encode
        </span>
        <ArrowRight size={17} />
        <span className="cyan">
          <Radio size={20} />
          Simulate radio
        </span>
        <ArrowRight size={17} />
        <span>
          <Cpu size={20} />
          Recover
        </span>
        <ArrowRight size={17} />
        <span>
          <AudioLines size={20} />
          Reconstruct
        </span>
        <small>CONCEPTUAL PIPELINE</small>
      </div><div className="section-heading">
        <div>
          <span className="eyebrow">THREE PATHS / ONE SOURCE</span>
          <h2>Choose what your link carries.</h2>
        </div>
        <Link className="text-link" to="/research">
          View architecture <ArrowUpRight size={16} />
        </Link>
      </div><div className="three-col mode-cards">
        {[
          {
            tag: "MODE A",
            title: "The waveform",
            icon: AudioLines,
            text: "A conventional Opus baseline. Preserve the acoustic signal and measure its actual transport cost.",
            link: "/compression",
            color: "cyan",
          },
          {
            tag: "MODE B",
            title: "The neural code",
            icon: Cpu,
            text: "Pretrained EnCodec turns audio into quantized indices. Serialize, transmit and decode the real tokens.",
            link: "/compression",
            color: "violet-text",
          },
          {
            tag: "MODE C",
            title: "The meaning",
            icon: Languages,
            text: "Recognize speech, transmit compact Unicode text, then synthesize speech from recovered information.",
            link: "/speech",
            color: "cyan",
          },
        ].map((m) => (
          <Link className="panel mode-card" to={m.link} key={m.tag}>
            <div className="split-label">
              <span className="eyebrow">{m.tag}</span>
              <ArrowUpRight size={18} />
            </div>
            <m.icon size={33} className={m.color} />
            <h3>{m.title}</h3>
            <p>{m.text}</p>
            <span className="text-link">
              Explore pathway <ArrowRight size={14} />
            </span>
          </Link>
        ))}
      </div><div className="two-col"><Panel
          title="Built for Indian scripts"
          eyebrow="SIX CONFIGURABLE LANGUAGES"
        >
          <div className="script-display">
            हिन्दी <span>ಕನ್ನಡ</span> தமிழ்
            <br />
            తెలుగు മലയാളം <span>English</span>
          </div>
          <p>
            Unicode-safe packets and language-specific synthesis. The Speech Lab
            reports actual installed and verified model capabilities.
          </p>
          <Link className="text-link" to="/speech">
            Inspect language coverage <ArrowUpRight size={15} />
          </Link>
        </Panel></div></>
  );
}