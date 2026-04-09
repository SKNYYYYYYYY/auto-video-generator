import { useState } from "react";
import { Images, X, ChevronLeft, ChevronRight } from "lucide-react";

interface GalleryImage {
  id: string;
  url: string;
  name: string;
  month: string;
  date: string;
}

interface ImageGalleryProps {
  images: GalleryImage[];
}

export default function ImageGallery({ images }: ImageGalleryProps) {
  const [lightbox, setLightbox] = useState<number | null>(null);

  if (images.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
        <Images className="w-16 h-16 mb-4 opacity-30" />
        <p className="text-lg font-display font-medium">No images yet</p>
        <p className="text-sm mt-1">Upload some images to see them here</p>
      </div>
    );
  }

  return (
    <>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {images.map((img, i) => (
          <button
            key={img.id}
            onClick={() => setLightbox(i)}
            className="group relative aspect-square overflow-hidden rounded-lg border border-border bg-secondary hover:border-primary/50 transition-all duration-300"
          >
            <img
              src={img.url}
              alt={img.name}
              className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-background/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            <div className="absolute bottom-0 left-0 right-0 p-3 translate-y-full group-hover:translate-y-0 transition-transform duration-300">
              <p className="text-sm font-medium text-foreground truncate">{img.name}</p>
              <p className="text-xs text-muted-foreground">{img.month} {img.date}</p>
            </div>
          </button>
        ))}
      </div>

      {lightbox !== null && (
        <div className="fixed inset-0 z-50 bg-background/95 backdrop-blur-sm flex items-center justify-center p-4">
          <button
            onClick={() => setLightbox(null)}
            className="absolute top-6 right-6 p-2 rounded-full bg-secondary text-foreground hover:bg-primary hover:text-primary-foreground transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
          {lightbox > 0 && (
            <button
              onClick={() => setLightbox(lightbox - 1)}
              className="absolute left-4 p-2 rounded-full bg-secondary text-foreground hover:bg-primary hover:text-primary-foreground transition-colors"
            >
              <ChevronLeft className="w-6 h-6" />
            </button>
          )}
          {lightbox < images.length - 1 && (
            <button
              onClick={() => setLightbox(lightbox + 1)}
              className="absolute right-4 p-2 rounded-full bg-secondary text-foreground hover:bg-primary hover:text-primary-foreground transition-colors"
            >
              <ChevronRight className="w-6 h-6" />
            </button>
          )}
          <img
            src={images[lightbox].url}
            alt={images[lightbox].name}
            className="max-w-full max-h-[80vh] object-contain rounded-lg"
          />
          <div className="absolute bottom-8 text-center">
            <p className="text-lg font-display font-semibold text-foreground">{images[lightbox].name}</p>
            <p className="text-sm text-muted-foreground">{images[lightbox].month} {images[lightbox].date}</p>
          </div>
        </div>
      )}
    </>
  );
}
