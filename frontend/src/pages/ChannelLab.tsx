
import { PageTitle } from "../components/ui";
export default function ChannelLab() {
  return (
    <><PageTitle
        tag="RESEARCH / DIGITAL RADIO"
        title="Channel Simulation Lab"
        description="Explore symbol decisions, bit errors and packet integrity with reproducible numerical experiments."
        action={<span className="badge">Es/N0 · not Eb/N0</span>}
      /></>
  );
}