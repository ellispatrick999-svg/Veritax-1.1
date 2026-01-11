from datetime import datetime
import uuid

class DecisionLog:
    def __init__(self):
        self.entries: list[dict] = []

    def record(self, *, input_summary, output, confidence, risk):
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "input_summary": input_summary,
            "output": output,
            "confidence": confidence,
            "risk": risk,
        }
        self.entries.append(entry)
