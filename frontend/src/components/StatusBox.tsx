import { CheckCircle2, XCircle } from "lucide-react";

interface StatusBoxProps {
  status: { success?: boolean; error?: string; data?: any } | null;
}

export default function StatusBox({ status }: StatusBoxProps) {
  if (!status) return null;
  const ok = status.success;

  return (
    <div
      className={`status-pop mt-5 p-4 rounded-lg border flex items-start gap-3 ${
        ok
          ? "bg-green-500/10 border-green-500/30 text-green-400"
          : "bg-destructive/10 border-destructive/30 text-destructive"
      }`}
    >
      {ok ? <CheckCircle2 className="w-5 h-5 mt-0.5 shrink-0" /> : <XCircle className="w-5 h-5 mt-0.5 shrink-0" />}
      <div>
        <p className="font-medium">{ok ? (status.data?.message || "Success!") : status.error}</p>
        {ok && status.data?.response && (
          <pre className="mt-2 text-xs whitespace-pre-wrap break-all opacity-70">
            {JSON.stringify(status.data.response, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}
