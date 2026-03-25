
import { Link } from "react-router-dom";
import { ArrowUpRight, ArrowRight, AudioLines, Radio, Cpu, ShieldCheck } from "lucide-react";
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
      </section></>
  );
}