const MAP = {
  PRESENT: "success",
  APPROVED: "success",
  ACTIVE: "success",
  ABSENT: "danger",
  REJECTED: "danger",
  TERMINATED: "danger",
  SUSPENDED: "danger",
  PENDING: "pending",
  HALF_DAY: "neutral",
  LATE: "neutral",
  ON_LEAVE: "neutral",
  CANCELLED: "neutral",
};

export default function StatusBadge({ value }) {
  const tone = MAP[value] || "neutral";
  const label = value ? value.replace(/_/g, " ") : "—";
  return <span className={`badge badge-${tone}`}>{label}</span>;
}
