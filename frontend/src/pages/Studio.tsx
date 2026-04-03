
import { PageTitle } from "../components/ui";
export default function Studio({ live = false }: { live?: boolean }) {
  return (
    <><PageTitle
        tag={
          live ? "TURN-BASED · LOCAL DEMONSTRATION" : "WORKSPACE / TRANSCEIVER"
        }
        title={live ? "Push. Send. Listen" : "Neural Transceiver Studio"}
        description={
          live
            ? "Send each voice turn through the actual encode, simulated radio, and receiver pipeline."
            : "One voice. Three representations. A measurable journey across a simulated radio link."
        }
        action={
          <span className="badge">
            <i />
            SIMULATION MODE
          </span>
        }
      /></>
  );
}