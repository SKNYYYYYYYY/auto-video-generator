import { useState, useRef } from "react";
import { MonthSelector } from "@/components/MonthSelector";
import Cropper from "react-easy-crop";
import { getCroppedImg, blobToFile } from "../lib/utils";
import {
  Upload,
  Sparkles,
  Images,
  Play,
  Camera,
  Calendar,
  User,
  Type,
  Loader2,
} from "lucide-react";
import GenerationFields from "@/components/GenerationFields";
import ImageGallery from "@/components/ImageGallery";
import VideoPreview from "@/components/VideoPreview";
import StatusBox from "@/components/StatusBox";
import { VideoProgress } from "@/components/VideoProgress";

const MONTHS = [
  "January","February","March","April","May","June",
  "July","August","September","October","November","December",
];

const BASE_URL = "http://localhost:8000";

const TABS = [
  { id: "upload", label: "Upload", icon: Upload },
  { id: "gallery", label: "Gallery", icon: Images },
  { id: "generate", label: "Generate", icon: Sparkles },
  { id: "preview", label: "Preview", icon: Play },
] as const;
const getDaysInMonth = (month: string) => {
  if (!month) return 31;

  const monthIndex = new Date(`${month} 1, 2024`).getMonth();
  return new Date(2024, monthIndex + 1, 0).getDate();
};
const formatRelationName = (
  gender: string,
  name: string,
  generation: number
) => {
  if (!name) return "";

  if (generation < 3) return name;

  const prefix = gender === "male" ? "s-o" : "d-o";

  return `${prefix} ${name}`;
};
type TabId = (typeof TABS)[number]["id"];

export default function Index() {
  const [activeTab, setActiveTab] = useState<TabId>("upload");
const fileInputRef = useRef<HTMLInputElement>(null);
  // Upload state
   const initialForm = {
  name: "",
  month: "",
  date: "",
  gender: "",
  event: "",
  image: null,
};
  const [form, setForm] = useState(initialForm);  
  const [generation, setGeneration] = useState(1);
  const [parentName, setParentName] = useState("");
  const [grandparentName, setGrandparentName] = useState("");
  const [greatGrandparentName, setGreatGrandparentName] = useState("");
  const [image, setImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [uploadStatus, setUploadStatus] = useState<any>(null);
  const [monthOpen, setMonthOpen] = useState(false);  
  const [dateOpen, setDateOpen] = useState(false);
  const [isAnniversary, setisAnniversary] = useState(false)
  const [requiresGender, setisRequiresGender] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null);
  type Area = { x: number; y: number; width: number; height: number };

  const [crop, setCrop] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [croppedAreaPixels, setCroppedAreaPixels] = useState<Area | null>(null);
  const [showCrop, setShowCrop] = useState(false);
  // Gallery state (demo data — replace with real API)
  const [galleryImages] = useState<any[]>([]);

  // Generate state
  const [videoMonth, setVideoMonth] = useState("");
  const [videoStatus, setVideoStatus] = useState<any>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);

  const [uploading, setUploading] = useState(false);
  const [generating, setGenerating] = useState(false);

  const [progressSteps, setProgressSteps] = useState<ProgressStep[]>([
  { id: 'llm', label: 'Generating script with AI', status: 'pending' },
  { id: 'tts', label: 'Creating voiceover', status: 'pending' },
  { id: 'slideshow', label: 'Building slideshow', status: 'pending' },
  { id: 'audio', label: 'Mixing audio', status: 'pending' },
]);
const [currentStep, setCurrentStep] = useState<string>('');

  const handleCropConfirm = async () => {
    if (!imagePreview || !croppedAreaPixels) return;

    const blob = await getCroppedImg(imagePreview, croppedAreaPixels);
    const file = blobToFile(blob);

    setImage(file);
    setImagePreview(URL.createObjectURL(blob));
    setShowCrop(false);
  };


const handleUpload = async () => {
  // Basic validation
  if (!(image instanceof File)) {
    return setUploadStatus({ error: "Please select a valid image." });
  }
  if (!form.name || !form.month || !form.date || !form.event?.trim()) {
    return setUploadStatus({ error: "Please fill in all required fields." });
  }

  setUploading(true);
  setUploadStatus(null);

  try {
    const fd = new FormData();

    // Core fields
    fd.append("name", form.name);
    fd.append("month", form.month);
    console.log("Form EVENT = ", form.event)
    if (form.event === "anniversary"){
        fd.append("generation", "9anniversary");
    } else {
      fd.append("generation", String(generation));
    }

    fd.append("event", form.event); // "birthday" | "anniversary"
    
    console.log("requiresGender = ", requiresGender)
    setisRequiresGender(form.event === "birthday" && generation >= 3);
    // Relations (only when needed)
    if (generation >= 3 && parentName) {
      fd.append(
        "relation_1",
        formatRelationName(form.gender, parentName, generation)
      );
    }
    if (generation >= 4 && grandparentName) {
      fd.append("relation_2", grandparentName);
    }
    if (generation >= 5 && greatGrandparentName) {
      fd.append("relation_3", greatGrandparentName);
    }

    // Image
    fd.append("image", image);
    fd.append("date", form.date);
    const controller = new AbortController();

    const timeout = setTimeout(() => {
      controller.abort();
    }, 5000);

  const res = await fetch(`${BASE_URL}/upload`, {
    method: "POST",
    body: fd,
    signal: controller.signal,
  });
  clearTimeout(timeout);
    let data;
    try {
      data = await res.json();
    } catch {
      throw new Error("Server returned invalid JSON");
    }

    if (!res.ok) {
        const errorMessage =
          data?.detail
            ? typeof data.detail === "string"
              ? data.detail
              : JSON.stringify(data.detail)
            : "Upload failed";

        throw new Error(errorMessage);
    }

  setUploadStatus({ success: true, data });

  // reset form
  setForm(initialForm);
  setImage(null);
  setImagePreview(null);
  setGeneration(1)

  if (fileInputRef.current) {
    fileInputRef.current.value = "";
  }

  // keep spinner ONLY if you really want UX delay
  setTimeout(() => {
    setUploading(false);
    setUploadStatus(null)
  }, 2000);
  } catch (e: any) {
    console.error("Upload error:", e);

    if (e.name === "AbortError") {
      setUploadStatus({ error: "Upload timeout)" });
    } else {
      setUploadStatus({ error: e.message || "Something went wrong" });
    }

    setUploading(false);
  }
  };
 
const handleGenerateVideo = async () => {
  setGenerating(true);
  setVideoStatus(null);
  
  // Reset progress steps
  setProgressSteps([
    { id: 'llm', label: 'Generating script with AI', status: 'pending' },
    { id: 'tts', label: 'Creating voiceover', status: 'pending' },
    { id: 'slideshow', label: 'Building slideshow', status: 'pending' },
    { id: 'audio', label: 'Mixing audio', status: 'pending' },
  ]);
  
  try {
    // Use EventSource for SSE (Server-Sent Events)
    const eventSource = new EventSource(`${BASE_URL}/generate-video-stream/${videoMonth}`);
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("Progress update:", data);
      
      switch (data.type) {
        case 'step_start':
          setProgressSteps(prev => prev.map(step => 
            step.id === data.step 
              ? { ...step, status: 'processing', message: data.message, timestamp: new Date() }
              : step
          ));
          setCurrentStep(data.step);
          break;
          
        case 'step_complete':
          setProgressSteps(prev => prev.map(step => 
            step.id === data.step 
              ? { ...step, status: 'completed', message: data.message, timestamp: new Date() }
              : step
          ));
          break;
          
        case 'step_error':
          setProgressSteps(prev => prev.map(step => 
            step.id === data.step 
              ? { ...step, status: 'error', message: data.error, timestamp: new Date() }
              : step
          ));
          setVideoStatus({ error: data.error });
          break;
          
        case 'complete':
          setVideoStatus({ success: true, data: data.result });
          if (data.result.video_url) setVideoUrl(data.result.video_url);
          eventSource.close();
          setGenerating(false);
          break;
          
        case 'progress':
          // For detailed progress (e.g., TTS generation progress)
          if (data.step === 'tts' && data.progress) {
            setProgressSteps(prev => prev.map(step => 
              step.id === 'tts'
                ? { ...step, message: `Generating: ${data.progress}% complete` }
                : step
            ));
          }
          break;
      }
    };
    
    eventSource.onerror = (error) => {
      console.error("EventSource failed:", error);
      eventSource.close();
      setVideoStatus({ error: "Connection lost. Please try again." });
      setGenerating(false);
    };
    
    // Store eventSource to close on unmount
    return () => eventSource.close();
    
  } catch (e: any) {
    setVideoStatus({ error: e.message });
    setGenerating(false);
  }
};
  
  console.log("annive = ", isAnniversary)
    const isValid =
      form.name.trim() !== "" &&
      form.month.trim() !== "" &&
      form.date.trim() !== "" &&
      form.event.trim() !== "" &&
      
      (isAnniversary || !requiresGender && form.gender.trim() !== "") &&
      (generation < 3 || parentName.trim()) &&
      (generation < 4 || grandparentName.trim()) &&
      (generation < 5 || greatGrandparentName.trim()) &&
      image instanceof File;
  const inputClass =
    "w-full px-4 py-3 bg-secondary border border-border rounded-lg text-foreground font-body placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all";

  return (
    <div className="min-h-screen bg-background text-foreground relative overflow-hidden">
      {/* Ambient background effects */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-30%] left-[-10%] w-[60%] h-[60%] rounded-full bg-primary/[0.03] blur-[120px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-primary/[0.02] blur-[100px]" />
      </div>

      {/* Header */}
      <header className="relative z-10 text-center pt-12 pb-6 px-6">
        <div className="flex items-center justify-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-primary-foreground" />
          </div>
          <h1 className="text-3xl sm:text-4xl font-display font-bold tracking-tight text-foreground">
            Auto<span className="text-primary">Vid</span>
          </h1>
        </div>
        <p className="text-sm text-muted-foreground tracking-wide uppercase">
          Celebrate every moment beautifully
        </p>
      </header>

      {/* Navigation */}
      <nav className="relative z-10 flex justify-center px-4 mb-8">
        <div className="flex bg-card border border-border rounded-2xl p-1.5 gap-1 overflow-x-auto max-w-lg w-full">
          {TABS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-300 whitespace-nowrap ${
                activeTab === id
                  ? "bg-primary text-primary-foreground shadow-lg shadow-primary/25"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary"
              }`}
            >
              <Icon className="w-4 h-4" />
              <span className="hidden sm:inline">{label}</span>
            </button>
          ))}
        </div>
      </nav>

      {showCrop && imagePreview && (
      <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
        <div className="bg-card p-6 rounded-xl w-[90%] max-w-md">
          
        <p className="text-xs text-muted-foreground mb-2">
          Drag and zoom to position the face inside the frame
        </p>

          <div className="relative w-full h-[300px]">
            <Cropper
              image={imagePreview}
              crop={crop}
              zoom={zoom}
              aspect={1} // MUST match backend
              onCropChange={setCrop}
              onZoomChange={setZoom}
              onCropComplete={(_, croppedPixels) =>
                setCroppedAreaPixels(croppedPixels)
              }
            />

            {/* Frame overlay */}
            <div className="absolute inset-0 border-4 border-white/80 pointer-events-none rounded-lg" />

            {/* Safe line (face guide) */}
            <div className="absolute top-[35%] left-0 right-0 h-[1px] bg-white/40 pointer-events-none" />
          </div>

          {/* Zoom slider */}
          <input
            type="range"
            min={1}
            max={3}
            step={0.1}
            value={zoom}
            onChange={(e) => setZoom(Number(e.target.value))}
            className="w-full mt-4"
          />

          <div className="flex justify-between mt-4">
            <button
              onClick={() => setShowCrop(false)}
              className="px-4 py-2 bg-secondary rounded-lg"
            >
              Cancel
            </button>

            <button
              onClick={handleCropConfirm}
              className="px-4 py-2 bg-primary text-white rounded-lg"
            >
              Confirm
            </button>
          </div>
        </div>
      </div>
    )}
      {/* Main content */}
      <main className="relative z-10 max-w-2xl mx-auto px-4 pb-20">
        {/* Upload Tab */}
{activeTab === "upload" && (
  <div className="panel-enter space-y-6">
    <div className="card-shine bg-card border border-border rounded-2xl p-6 sm:p-8">
      <h2 className="text-2xl font-display font-bold mb-1">Upload Image</h2>
      <p className="text-muted-foreground text-sm mb-8">
        Add a photo to the celebration timeline
      </p>

      {(() => {
        const daysInMonth = getDaysInMonth(form.month);


        return (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">

            {/* Name */}
            <div>
              <label className="block text-xs font-medium uppercase tracking-widest text-muted-foreground mb-2">
                <User className="w-3 h-3 inline mr-1" />
                Celebrant's Name
              </label>
              <input
                className={inputClass}
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
              />
            </div>

          {/* Month Grid */}
          <div>
              <label className="block text-xs font-medium uppercase tracking-widest text-muted-foreground mb-2">
                <Calendar className="w-3 h-3 inline mr-1" />
                Month
              </label>
              <MonthSelector
                value={form.month}
                onChange={(month) => {
                  setForm({ ...form, month, date: "" });
                }}
                placeholder="Select month"
              />
          </div>

            <div className="flex gap-4 items-end">
              
          {/* Date Grid */}
            <div className="relative w-[160px]">
              <label className="block text-xs font-medium uppercase tracking-widest text-muted-foreground mb-2">
                Date
              </label>

              {/* Trigger */}
              <button
                type="button"
                onClick={() => setDateOpen(!dateOpen)}
                className="
                  w-full px-4 py-3 bg-secondary border border-border
                  rounded-xl text-left flex justify-between items-center
                  hover:border-primary/40 transition-all
                "
              >
                <span>
                  {form.date ? `Day ${form.date}` : "Select day"}
                </span>
                <span className="text-muted-foreground">▾</span>
              </button>

              {/* Dropdown */}
              {dateOpen && (
                <div className="
                  absolute z-50 mt-2 w-full p-3
                  bg-card border border-border rounded-xl shadow-lg
                ">
                  <div className="grid grid-cols-7 gap-2">
                    {[...Array(daysInMonth)].map((_, i) => {
                      const day = i + 1;

                      return (
                        <button
                          key={day}
                          type="button"
                          onClick={() => {
                            setForm({ ...form, date: String(day) });
                            setDateOpen(false);
                          }}
                          className={`
                            aspect-square rounded-lg text-sm border transition-all
                            ${
                              form.date === String(day)
                                ? "bg-primary text-white border-primary shadow"
                                : "bg-secondary hover:border-primary/40"
                            }
                          `}
                        >
                          {day}
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
              {/* Gender */}
              <div >
                <label className="block text-xs font-medium uppercase tracking-widest text-muted-foreground mb-2">
                  Gender
                </label>

              <select
                className={inputClass}
                required
                value={form.gender}
                disabled={isAnniversary}
                onChange={(e) => setForm({ ...form, gender: e.target.value })}
              >
                <option value="">Choose</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
              </select>
              </div>

              </div>
            {/* Event */}
            <div>
              <label className="block text-xs font-medium uppercase tracking-widest text-muted-foreground mb-2">
                Event
              </label>

              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setForm({ ...form, event: "birthday" });
                    setisAnniversary(false);
                  }
                }
                  className={
                    form.event === "birthday"
                      ? "bg-primary text-white px-3 py-2 rounded-lg text-sm"
                      : "bg-secondary px-3 py-2 rounded-lg text-sm"
                  }
                >
                  Birthday
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setForm({ ...form, event: "anniversary"
                   });
                   setisAnniversary(true)
                  }
                }
                  className={
                    form.event === "anniversary"
                      ? "bg-primary text-white px-3 py-2 rounded-lg text-sm"
                      : "bg-secondary px-3 py-2 rounded-lg text-sm"
                  }
                >
                  Anniversary
                </button>
              </div>
            </div>

          </div>
        );
      })()}

      <GenerationFields
        generation={generation}
        parentName={parentName}
        grandparentName={grandparentName}
        greatGrandparentName={greatGrandparentName}
        onGenerationChange={setGeneration}
        onParentNameChange={setParentName}
        onGrandparentNameChange={setGrandparentName}
        onGreatGrandparentNameChange={setGreatGrandparentName}
      />

      {/* Drop zone */}
      <div
        onClick={() => fileInputRef.current?.click()}
        className="mt-6 border-2 border-dashed border-border rounded-xl min-h-[200px] flex items-center justify-center cursor-pointer hover:border-primary/50 hover:bg-secondary/50 transition-all duration-300 group"
      >
        {imagePreview ? (
          <img
            src={imagePreview}
            alt="Preview"
            className="w-full max-h-[280px] object-cover rounded-lg"
          />
        ) : (
          <div className="flex flex-col items-center gap-3 p-8 text-center">
            <div className="w-14 h-14 rounded-2xl bg-secondary flex items-center justify-center group-hover:bg-primary/10 transition-colors">
              <Camera className="w-7 h-7 text-muted-foreground group-hover:text-primary transition-colors" />
            </div>
            <p className="text-sm text-muted-foreground">
              Click to select an image
            </p>
            <p className="text-xs text-muted-foreground/60">
              JPG, PNG — max 10MB
            </p>
          </div>
        )}
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (!file) return;

            setImage(file);
            setForm({ ...form, image: file });

            setImagePreview(URL.createObjectURL(file));
            setShowCrop(true);
          }}
        />
      </div>

      {/* Upload button */}
      <button
        onClick={handleUpload}
        disabled={!isValid || uploading }
        className="mt-6 w-full py-4 bg-primary text-primary-foreground rounded-xl font-display font-semibold text-sm uppercase tracking-widest hover:brightness-110 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center gap-2"
      >
        {uploading  ? (
          <span className="spinner text-lg">◌</span>
        ) : (
          <>
            <Upload className="w-4 h-4" />
            Upload Image
          </>
        )}
      </button>

      <StatusBox status={uploadStatus} />
    </div>
  </div>
)}
        {/* Gallery Tab */}
        {activeTab === "gallery" && (
          <div className="panel-enter">
            <div className="card-shine bg-card border border-border rounded-2xl p-6 sm:p-8">
              <h2 className="text-2xl font-display font-bold mb-1">Gallery</h2>
              <p className="text-muted-foreground text-sm mb-6">
                Browse all uploaded celebration photos
              </p>
              <ImageGallery images={galleryImages} />
            </div>
          </div>
        )}
        {/* Generate Tab */}
        {activeTab === "generate" && (
          <div className="panel-enter">
            <div className="card-shine bg-card border border-border rounded-2xl p-6 sm:p-8 overflow-visible">
              <h2 className="text-2xl font-display font-bold mb-1">Generate Video</h2>
              <p className="text-muted-foreground text-sm mb-8">
                Compile all uploaded images for a month into a stunning video
              </p>

              <div className="mb-6 relative z-50">
                <label className="block text-xs font-medium uppercase tracking-widest text-muted-foreground mb-2">
                  Select Month
                </label>
                <MonthSelector
                  value={videoMonth}
                  onChange={setVideoMonth}
                  placeholder="Choose a month for compilation"
                />
              </div>

              {/* Month display card */}
              {videoMonth && (
                <div className="flex items-center gap-4 p-5 bg-secondary rounded-xl border border-border mb-6">
                  <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                    <Sparkles className="w-6 h-6 text-primary" />
                  </div>
                  <div>
                    <p className="text-2xl font-display font-bold text-foreground">{videoMonth}</p>
                    <p className="text-xs text-muted-foreground">Compilation target</p>
                  </div>
                </div>
              )}

              {/* Progress indicator while generating */}
              {generating && (
                <VideoProgress steps={progressSteps} />
              )}

              <button
                onClick={handleGenerateVideo}
                disabled={generating || !videoMonth}
                className="w-full py-4 bg-primary text-primary-foreground rounded-xl font-display font-semibold text-sm uppercase tracking-widest hover:brightness-110 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center gap-2"
              >
                {generating ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Generate Video
                  </>
                )}
              </button>

              <StatusBox status={videoStatus} />
            </div>
          </div>
        )}
        {/* Preview Tab */}
        {activeTab === "preview" && (
          <div className="panel-enter">
            <div className="card-shine bg-card border border-border rounded-2xl p-6 sm:p-8">
              <h2 className="text-2xl font-display font-bold mb-1">Video Preview</h2>
              <p className="text-muted-foreground text-sm mb-6">
                Watch your generated celebration video
              </p>
              <VideoPreview videoUrl={videoUrl} videoMonth={videoMonth} />
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="relative z-10 text-center py-6 text-xs text-muted-foreground tracking-widest font-body">
        AutoVid © {new Date().getFullYear()}
      </footer>
    </div>
  );
}
