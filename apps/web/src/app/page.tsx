"use client";

import { useEffect, useState } from "react";
import { api, Story } from "@/lib/api";
import { useAppContext } from "@/components/AppProvider";
import WorldDashboard from "@/components/WorldDashboard";
import { UploadCloud, FolderOpen, Loader2 } from "lucide-react";

export default function Home() {
  const { storyId, setStoryId, setBranchId, setCurrentSequence, setWorldSummary } = useAppContext();
  
  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [file, setFile] = useState<File | null>(null);

  useEffect(() => {
    loadStories();
  }, []);

  const loadStories = async () => {
    try {
      setLoading(true);
      const data = await api.getStories();
      setStories(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const selectStory = async (id: string) => {
    try {
      const summary = await api.getWorldSummary(id, "canon");
      setStoryId(id);
      setBranchId("canon");
      setCurrentSequence(summary.current_sequence);
      setWorldSummary(summary);
    } catch (err) {
      console.error("Failed to load world summary", err);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    try {
      setUploading(true);
      const res = await api.uploadStory(file, file.name.replace(/\.[^/.]+$/, ""));
      await loadStories();
      await selectStory(res.story_id);
    } catch (err) {
      console.error("Upload failed", err);
    } finally {
      setUploading(false);
    }
  };

  if (storyId) {
    return <WorldDashboard />;
  }

  return (
    <div className="flex-1 flex items-center justify-center p-8 relative overflow-hidden">
      {/* Background cinematic elements */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-canon/5 rounded-full blur-[100px] pointer-events-none" />
      
      <div className="max-w-4xl w-full grid grid-cols-1 md:grid-cols-2 gap-8 z-10">
        
        {/* Upload Panel */}
        <div className="bg-panel border border-panel-border p-8 rounded-lg flex flex-col items-center justify-center text-center">
          <div className="w-16 h-16 rounded-full bg-border flex items-center justify-center mb-6 text-primary">
            <UploadCloud size={32} />
          </div>
          <h2 className="text-xl font-serif mb-2">Ingest Source Material</h2>
          <p className="text-primary-muted text-sm mb-8 font-mono">TXT, PDF, DOCX supported</p>
          
          <form onSubmit={handleUpload} className="w-full flex flex-col gap-4">
            <label className="border-2 border-dashed border-border rounded-lg p-8 cursor-pointer hover:border-primary-muted transition-colors">
              <span className="text-sm font-mono text-primary-muted">
                {file ? file.name : "Select or drop file"}
              </span>
              <input 
                type="file" 
                className="hidden" 
                onChange={e => setFile(e.target.files?.[0] || null)}
                accept=".txt,.pdf,.docx"
              />
            </label>
            <button 
              type="submit" 
              disabled={!file || uploading}
              className="bg-primary text-background font-mono uppercase text-sm py-3 px-4 rounded hover:bg-white disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {uploading ? (
                <><Loader2 className="animate-spin" size={16} /> Ingesting...</>
              ) : "Begin Reconstruction"}
            </button>
          </form>
        </div>

        {/* Existing Worlds */}
        <div className="bg-panel border border-panel-border p-8 rounded-lg flex flex-col">
          <div className="flex items-center gap-3 mb-6 text-primary">
            <FolderOpen size={24} />
            <h2 className="text-xl font-serif">Archived Worlds</h2>
          </div>
          
          <div className="flex-1 overflow-y-auto pr-2 flex flex-col gap-3">
            {loading ? (
              <div className="animate-pulse flex flex-col gap-3">
                {[1, 2, 3].map(i => (
                  <div key={i} className="h-20 bg-border rounded" />
                ))}
              </div>
            ) : stories.length === 0 ? (
              <div className="flex-1 flex items-center justify-center text-primary-muted font-mono text-sm text-center">
                No archived worlds found.<br/>Ingest a new source to begin.
              </div>
            ) : (
              stories.map(story => (
                <button
                  key={story.id}
                  onClick={() => selectStory(story.id)}
                  className="text-left p-4 border border-border rounded hover:border-canon/50 hover:bg-canon/5 transition-all group"
                >
                  <h3 className="font-serif text-lg text-primary group-hover:text-canon transition-colors">{story.title}</h3>
                  <p className="text-primary-muted text-xs font-mono mt-1">{story.description}</p>
                </button>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
