import { Copy, Mic, Square, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useTranscriptionSession } from "@/features/transcription/state/useTranscriptionSession";

const statusTone = {
  idle: "neutral",
  connecting: "amber",
  recording: "green",
  stopped: "neutral",
  error: "red",
} as const;

export function TranscriptionConsole() {
  const session = useTranscriptionSession();
  const canStart =
    session.status === "idle" || session.status === "stopped" || session.status === "error";
  const canStop = session.status === "connecting" || session.status === "recording";
  const transcript =
    session.partialText.length > 0
      ? `${session.finalText}\n${session.partialText}`.trim()
      : session.finalText;

  const copyTranscript = async () => {
    await navigator.clipboard.writeText(transcript);
  };

  return (
    <main className="min-h-screen px-4 py-6 sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-6xl flex-col gap-5">
        <header className="flex flex-col gap-4 border-b border-border pb-5 md:flex-row md:items-end md:justify-between">
          <div className="space-y-2">
            <p className="text-sm font-medium text-muted-foreground">Streaming ASR</p>
            <h1 className="text-3xl font-semibold tracking-normal text-foreground">
              Live meeting transcription
            </h1>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone={statusTone[session.status]}>{session.status}</Badge>
            <Button
              variant="outline"
              size="icon"
              onClick={copyTranscript}
              disabled={transcript.length === 0}
              aria-label="Copy transcript"
              title="Copy transcript"
            >
              <Copy className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={session.clear}
              aria-label="Clear transcript"
              title="Clear transcript"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </header>

        <section className="grid gap-5 lg:grid-cols-[280px_1fr]">
          <aside className="rounded-md border border-border bg-white p-4">
            <div className="flex flex-col gap-3">
              <Button onClick={session.start} disabled={!canStart}>
                <Mic className="h-4 w-4" />
                Start
              </Button>
              <Button variant="destructive" onClick={session.stop} disabled={!canStop}>
                <Square className="h-4 w-4" />
                Stop
              </Button>
            </div>

            <dl className="mt-6 space-y-4 text-sm">
              <div>
                <dt className="text-muted-foreground">Audio</dt>
                <dd className="mt-1 font-medium">16 kHz mono PCM</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Transport</dt>
                <dd className="mt-1 font-medium">WebSocket</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Session</dt>
                <dd className="mt-1 break-all font-medium">{session.sessionId ?? "Not started"}</dd>
              </div>
            </dl>
          </aside>

          <section className="min-h-[540px] rounded-md border border-border bg-white">
            <div className="border-b border-border px-4 py-3">
              <h2 className="text-base font-semibold">Transcript</h2>
            </div>
            <div className="h-[492px] overflow-auto p-5">
              {session.error !== null ? (
                <p className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                  {session.error}
                </p>
              ) : transcript.length > 0 ? (
                <div className="whitespace-pre-wrap text-base leading-7">
                  <span>{session.finalText}</span>
                  {session.partialText.length > 0 ? (
                    <span className="text-muted-foreground">
                      {session.finalText.length > 0 ? "\n" : ""}
                      {session.partialText}
                    </span>
                  ) : null}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">
                  Transcript text will appear here when recording starts.
                </p>
              )}
            </div>
          </section>
        </section>
      </div>
    </main>
  );
}
