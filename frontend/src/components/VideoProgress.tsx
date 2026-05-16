// components/VideoProgress.tsx
import { CheckCircle2, Circle, Loader2, Mic, FileAudio, Film, Sparkles } from "lucide-react";

export interface ProgressStep {
  id: string;
  label: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  message?: string;
  timestamp?: Date;
}

interface VideoProgressProps {
  steps: ProgressStep[];
  currentStep?: string;
}

const stepIcons = {
  llm: Sparkles,
  tts: Mic,
  slideshow: Film,
  audio: FileAudio,
};

export const VideoProgress = ({ steps }: VideoProgressProps) => {
  return (
    <div className="mt-6 space-y-4">
      <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
        Generation Progress
      </h3>
      <div className="space-y-3">
        {steps.map((step) => (
          <div key={step.id} className="relative">
            <div className="flex items-start gap-3">
              {/* Icon/Status */}
              <div className="flex-shrink-0 mt-0.5">
                {step.status === 'completed' && (
                  <CheckCircle2 className="w-5 h-5 text-green-500" />
                )}
                {step.status === 'processing' && (
                  <Loader2 className="w-5 h-5 text-primary animate-spin" />
                )}
                {step.status === 'pending' && (
                  <Circle className="w-5 h-5 text-muted-foreground" />
                )}
                {step.status === 'error' && (
                  <div className="w-5 h-5 rounded-full bg-red-500/20 flex items-center justify-center">
                    <div className="w-2 h-2 rounded-full bg-red-500" />
                  </div>
                )}
              </div>

              {/* Content */}
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <p className={`text-sm font-medium ${
                    step.status === 'completed' ? 'text-foreground' :
                    step.status === 'processing' ? 'text-primary' :
                    step.status === 'error' ? 'text-red-500' :
                    'text-muted-foreground'
                  }`}>
                    {step.label}
                  </p>
                  {step.timestamp && (
                    <span className="text-xs text-muted-foreground">
                      {step.timestamp.toLocaleTimeString()}
                    </span>
                  )}
                </div>
                
                {step.message && (
                  <p className="text-xs text-muted-foreground mt-1">
                    {step.message}
                  </p>
                )}

                {/* Progress bar for processing steps */}
                {step.status === 'processing' && (
                  <div className="mt-2 h-1 bg-secondary rounded-full overflow-hidden">
                    <div className="h-full bg-primary rounded-full animate-pulse" 
                         style={{ width: '100%' }} />
                  </div>
                )}
              </div>
            </div>

            {/* Connector line between steps */}
            {steps.indexOf(step) < steps.length - 1 && (
              <div className="absolute left-2 top-5 bottom-0 w-px bg-border"
                   style={{ height: 'calc(100% - 1rem)' }} />
            )}
          </div>
        ))}
      </div>
    </div>
  );
};