import { useState, useRef } from "react";
import {
  Upload,
  Sparkles,
  Images,
  Play,
  Camera,
  Calendar,
  User,
  Type,
} from "lucide-react";
import GenerationFields from "@/components/GenerationFields";
import ImageGallery from "@/components/ImageGallery";
import VideoPreview from "@/components/VideoPreview";
import StatusBox from "@/components/StatusBox";

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

type TabId = (typeof TABS)[number]["id"];

export default function Index() {
  const [activeTab, setActiveTab] = useState<TabId>("upload");

  // Upload state
  const [form, setForm] = useState({
    name: "",
    month: "January",
    date: "",
    type: "",
  });
  const [generation, setGeneration] = useState(1);
  const [parentName, setParentName] = useState("");
  const [grandparentName, setGrandparentName] = useState("");
  const [greatGrandparentName, setGreatGrandparentName] = useState("");
  const [image, setImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [uploadStatus, setUploadStatus] = useState<any>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  // Gallery state (demo data — replace with real API)
  const [galleryImages] = useState<any[]>([]);

  // Generate state
  const [videoMonth, setVideoMonth] = useState("January");
  const [videoStatus, setVideoStatus] = useState<any>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);

  const [loading, setLoading] = useState(false);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setImage(file);
    setImagePreview(URL.createObjectURL(file));
  };

  const handleUpload = async () => {
    if (!image) return setUploadStatus({ error: "Please select an image." });
    setLoading(true);
    setUploadStatus(null);
    try {
      const fd = new FormData();
      fd.append("name", form.name);
      fd.append("month", form.month);
      fd.append("date", form.date);
      fd.append("generation", String(generation));
      fd.append("type", form.type);
      if (generation >= 3) fd.append("parent_name", parentName);
      if (generation >= 4) fd.append("grandparent_name", grandparentName);
      if (generation >= 5) fd.append("great_grandparent_name", greatGrandparentName);
      fd.append("image", image);
      const res = await fetch(`${BASE_URL}/upload`, { method: "POST", body: fd });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");
      setUploadStatus({ success: true, data });
    } catch (e: any) {
      setUploadStatus({ error: e.message });
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateVideo = async () => {
    setLoading(true);
    setVideoStatus(null);
    try {
      const res = await fetch(`${BASE_URL}/generate-video/${videoMonth}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Video generation failed");
      setVideoStatus({ success: true, data });
      if (data.video_url) setVideoUrl(data.video_url);
    } catch (e: any) {
      setVideoStatus({ error: e.message });
    } finally {
      setLoading(false);
    }
  };

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

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="block text-xs font-medium uppercase tracking-widest text-muted-foreground mb-2">
                    <User className="w-3 h-3 inline mr-1" />
                    Celebrant's Name
                  </label>
                  <input
                    className={inputClass}
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                    placeholder="e.g. James Okafor"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium uppercase tracking-widest text-muted-foreground mb-2">
                    <Calendar className="w-3 h-3 inline mr-1" />
                    Month
                  </label>
                  <select
                    className={inputClass}
                    value={form.month}
                    onChange={(e) => setForm({ ...form, month: e.target.value })}
                  >
                    {MONTHS.map((m) => (
                      <option key={m}>{m}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium uppercase tracking-widest text-muted-foreground mb-2">
                    Date
                  </label>
                  <input
                    className={inputClass}
                    value={form.date}
                    onChange={(e) => setForm({ ...form, date: e.target.value })}
                    placeholder="e.g. 15th"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium uppercase tracking-widest text-muted-foreground mb-2">
                    <Type className="w-3 h-3 inline mr-1" />
                    Type
                  </label>
                  <input
                    className={inputClass}
                    value={form.type}
                    onChange={(e) => setForm({ ...form, type: e.target.value })}
                    placeholder="e.g. Birthday"
                  />
                </div>
              </div>

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
                onClick={() => fileRef.current?.click()}
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
                  ref={fileRef}
                  type="file"
                  accept="image/*"
                  hidden
                  onChange={handleImageChange}
                />
              </div>

              <button
                onClick={handleUpload}
                disabled={loading}
                className="mt-6 w-full py-4 bg-primary text-primary-foreground rounded-xl font-display font-semibold text-sm uppercase tracking-widest hover:brightness-110 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center gap-2"
              >
                {loading ? (
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
            <div className="card-shine bg-card border border-border rounded-2xl p-6 sm:p-8">
              <h2 className="text-2xl font-display font-bold mb-1">Generate Video</h2>
              <p className="text-muted-foreground text-sm mb-8">
                Compile all uploaded images for a month into a stunning video
              </p>

              <div className="mb-6">
                <label className="block text-xs font-medium uppercase tracking-widest text-muted-foreground mb-2">
                  Select Month
                </label>
                <select
                  className={inputClass}
                  value={videoMonth}
                  onChange={(e) => setVideoMonth(e.target.value)}
                >
                  {MONTHS.map((m) => (
                    <option key={m}>{m}</option>
                  ))}
                </select>
              </div>

              {/* Month display card */}
              <div className="flex items-center gap-4 p-5 bg-secondary rounded-xl border border-border mb-6">
                <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                  <Sparkles className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <p className="text-2xl font-display font-bold text-foreground">{videoMonth}</p>
                  <p className="text-xs text-muted-foreground">Compilation target</p>
                </div>
              </div>

              <button
                onClick={handleGenerateVideo}
                disabled={loading}
                className="w-full py-4 bg-primary text-primary-foreground rounded-xl font-display font-semibold text-sm uppercase tracking-widest hover:brightness-110 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center gap-2"
              >
                {loading ? (
                  <span className="spinner text-lg">◌</span>
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
