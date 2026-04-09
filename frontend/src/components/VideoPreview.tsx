import { useState } from "react";
import { Play, Film } from "lucide-react";

interface VideoPreviewProps {
  videoUrl: string | null;
  videoMonth: string;
}

export default function VideoPreview({ videoUrl, videoMonth }: VideoPreviewProps) {
  const [isPlaying, setIsPlaying] = useState(false);

  if (!videoUrl) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
        <Film className="w-16 h-16 mb-4 opacity-30" />
        <p className="text-lg font-display font-medium">No video generated yet</p>
        <p className="text-sm mt-1">Generate a video to preview it here</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="relative aspect-video rounded-xl overflow-hidden border border-border bg-secondary glow-ring">
        <video
          src={videoUrl}
          controls
          className="w-full h-full object-contain bg-background"
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
        />
        {!isPlaying && (
          <div className="absolute inset-0 flex items-center justify-center bg-background/40 pointer-events-none">
            <div className="w-16 h-16 rounded-full bg-primary flex items-center justify-center">
              <Play className="w-7 h-7 text-primary-foreground ml-1" />
            </div>
          </div>
        )}
      </div>
      <p className="text-center text-sm text-muted-foreground">
        Video for <span className="text-primary font-semibold">{videoMonth}</span>
      </p>
    </div>
  );
}
