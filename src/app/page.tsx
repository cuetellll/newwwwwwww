"use client";

import { useState, useEffect, useCallback } from "react";

interface VideoInfo {
  id: number;
  fileName: string;
  fileSize: number;
  duration: number;
  username: string;
  createdAt: string;
}

interface Stats {
  totalVideos: number;
  totalSize: number;
  recentVideos: VideoInfo[];
}

function formatFileSize(bytes: number | null | undefined): string {
  if (!bytes) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDuration(seconds: number | null | undefined): string {
  if (!seconds) return "—";
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

export default function Home() {
  const [webhookUrl, setWebhookUrl] = useState("");
  const [webhookStatus, setWebhookStatus] = useState<string>("");
  const [webhookInfo, setWebhookInfo] = useState<string>("");
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"setup" | "stats">("setup");

  const fetchWebhookInfo = useCallback(async () => {
    try {
      const res = await fetch("/api/telegram/setup");
      const data = await res.json();
      if (data.result) {
        setWebhookInfo(
          data.result.url
            ? `✅ Webhook فعال: ${data.result.url}`
            : "❌ Webhook تنظیم نشده"
        );
      }
    } catch {
      setWebhookInfo("خطا در دریافت اطلاعات");
    }
  }, []);

  const fetchStats = useCallback(async () => {
    try {
      const res = await fetch("/api/telegram/stats");
      const data = await res.json();
      if (!data.error) {
        setStats(data);
      }
    } catch {
      // ignore
    }
  }, []);

  useEffect(() => {
    fetchWebhookInfo();
    fetchStats();
  }, [fetchWebhookInfo, fetchStats]);

  const handleSetWebhook = async () => {
    if (!webhookUrl) return;
    setLoading(true);
    try {
      const res = await fetch("/api/telegram/setup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "set", webhookUrl }),
      });
      const data = await res.json();
      setWebhookStatus(data.ok ? "✅ Webhook با موفقیت تنظیم شد!" : `❌ خطا: ${data.description}`);
      fetchWebhookInfo();
    } catch {
      setWebhookStatus("❌ خطا در ارتباط با سرور");
    }
    setLoading(false);
  };

  const handleDeleteWebhook = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/telegram/setup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "delete" }),
      });
      const data = await res.json();
      setWebhookStatus(data.ok ? "✅ Webhook حذف شد!" : `❌ خطا: ${data.description}`);
      fetchWebhookInfo();
    } catch {
      setWebhookStatus("❌ خطا در ارتباط با سرور");
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900" dir="rtl">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-sm bg-white/5">
        <div className="max-w-5xl mx-auto px-4 py-6">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-blue-500 rounded-2xl flex items-center justify-center text-3xl shadow-lg shadow-blue-500/30">
              🤖
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">ربات دانلود ویدیو تلگرام</h1>
              <p className="text-blue-300/80 text-sm mt-1">
                ویدیو فوروارد کنید، لینک دانلود مستقیم دریافت کنید
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8 space-y-6">
        {/* Tab Navigation */}
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab("setup")}
            className={`px-6 py-3 rounded-xl font-medium transition-all ${
              activeTab === "setup"
                ? "bg-blue-500 text-white shadow-lg shadow-blue-500/30"
                : "bg-white/10 text-white/70 hover:bg-white/20"
            }`}
          >
            ⚙️ تنظیمات
          </button>
          <button
            onClick={() => {
              setActiveTab("stats");
              fetchStats();
            }}
            className={`px-6 py-3 rounded-xl font-medium transition-all ${
              activeTab === "stats"
                ? "bg-blue-500 text-white shadow-lg shadow-blue-500/30"
                : "bg-white/10 text-white/70 hover:bg-white/20"
            }`}
          >
            📊 آمار و ویدیوها
          </button>
        </div>

        {/* Setup Tab */}
        {activeTab === "setup" && (
          <div className="space-y-6">
            {/* Webhook Status */}
            <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/10">
              <h2 className="text-lg font-semibold text-white mb-3">📡 وضعیت Webhook</h2>
              <p className="text-blue-200/80 text-sm font-mono bg-black/20 rounded-lg px-4 py-3">
                {webhookInfo || "در حال بررسی..."}
              </p>
            </div>

            {/* Setup Webhook */}
            <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/10">
              <h2 className="text-lg font-semibold text-white mb-4">🔧 تنظیم Webhook</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-blue-200/80 text-sm mb-2">آدرس Webhook:</label>
                  <input
                    type="url"
                    value={webhookUrl}
                    onChange={(e) => setWebhookUrl(e.target.value)}
                    placeholder="https://your-domain.railway.app/api/telegram/webhook"
                    className="w-full bg-black/30 border border-white/20 rounded-xl px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500 text-left"
                    dir="ltr"
                  />
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={handleSetWebhook}
                    disabled={loading || !webhookUrl}
                    className="px-6 py-3 bg-green-500 hover:bg-green-600 disabled:opacity-50 text-white rounded-xl font-medium transition-all shadow-lg shadow-green-500/20"
                  >
                    {loading ? "⏳ صبر کنید..." : "✅ فعال‌سازی"}
                  </button>
                  <button
                    onClick={handleDeleteWebhook}
                    disabled={loading}
                    className="px-6 py-3 bg-red-500 hover:bg-red-600 disabled:opacity-50 text-white rounded-xl font-medium transition-all shadow-lg shadow-red-500/20"
                  >
                    🗑 حذف Webhook
                  </button>
                </div>
                {webhookStatus && (
                  <div className="bg-black/20 rounded-lg px-4 py-3 text-sm text-blue-200/80">
                    {webhookStatus}
                  </div>
                )}
              </div>
            </div>

            {/* Instructions */}
            <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/10">
              <h2 className="text-lg font-semibold text-white mb-4">📖 راهنمای راه‌اندازی</h2>
              <div className="space-y-4 text-blue-200/80 text-sm">
                <div className="flex gap-3">
                  <span className="bg-blue-500/20 text-blue-300 rounded-full w-7 h-7 flex items-center justify-center flex-shrink-0 text-xs font-bold">1</span>
                  <div>
                    <p className="font-medium text-white">ساخت ربات در تلگرام</p>
                    <p className="mt-1">به <span dir="ltr">@BotFather</span> در تلگرام پیام بدید و <span dir="ltr">/newbot</span> بزنید. توکن دریافتی رو کپی کنید.</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <span className="bg-blue-500/20 text-blue-300 rounded-full w-7 h-7 flex items-center justify-center flex-shrink-0 text-xs font-bold">2</span>
                  <div>
                    <p className="font-medium text-white">تنظیم متغیرهای محیطی</p>
                    <p className="mt-1">در Railway متغیر <code className="bg-black/30 px-2 py-1 rounded" dir="ltr">TELEGRAM_BOT_TOKEN</code> و <code className="bg-black/30 px-2 py-1 rounded" dir="ltr">BASE_URL</code> رو تنظیم کنید.</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <span className="bg-blue-500/20 text-blue-300 rounded-full w-7 h-7 flex items-center justify-center flex-shrink-0 text-xs font-bold">3</span>
                  <div>
                    <p className="font-medium text-white">فعال‌سازی Webhook</p>
                    <p className="mt-1">آدرس webhook رو در فرم بالا وارد کنید: <code className="bg-black/30 px-2 py-1 rounded" dir="ltr">https://your-app.railway.app/api/telegram/webhook</code></p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <span className="bg-blue-500/20 text-blue-300 rounded-full w-7 h-7 flex items-center justify-center flex-shrink-0 text-xs font-bold">4</span>
                  <div>
                    <p className="font-medium text-white">استفاده از ربات</p>
                    <p className="mt-1">حالا ویدیو به ربات فوروارد کنید و لینک دانلود مستقیم دریافت کنید!</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Environment Variables */}
            <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/10">
              <h2 className="text-lg font-semibold text-white mb-4">🔐 متغیرهای محیطی مورد نیاز</h2>
              <div className="bg-black/30 rounded-xl p-4 font-mono text-sm text-green-300 space-y-2" dir="ltr">
                <p><span className="text-blue-300">DATABASE_URL</span>=postgresql://user:pass@host:5432/dbname</p>
                <p><span className="text-blue-300">TELEGRAM_BOT_TOKEN</span>=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz</p>
                <p><span className="text-blue-300">BASE_URL</span>=https://your-app.railway.app</p>
              </div>
            </div>
          </div>
        )}

        {/* Stats Tab */}
        {activeTab === "stats" && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/10">
                <div className="text-3xl mb-2">🎬</div>
                <div className="text-3xl font-bold text-white">{stats?.totalVideos ?? 0}</div>
                <div className="text-blue-300/70 text-sm mt-1">تعداد ویدیوها</div>
              </div>
              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/10">
                <div className="text-3xl mb-2">💾</div>
                <div className="text-3xl font-bold text-white">
                  {formatFileSize(stats?.totalSize)}
                </div>
                <div className="text-blue-300/70 text-sm mt-1">حجم کل</div>
              </div>
              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/10">
                <div className="text-3xl mb-2">📡</div>
                <div className="text-3xl font-bold text-white">فعال</div>
                <div className="text-blue-300/70 text-sm mt-1">وضعیت ربات</div>
              </div>
            </div>

            {/* Recent Videos */}
            <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/10">
              <h2 className="text-lg font-semibold text-white mb-4">🕐 آخرین ویدیوها</h2>
              {stats?.recentVideos && stats.recentVideos.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-white/10">
                        <th className="text-right text-blue-300/70 pb-3 font-medium">#</th>
                        <th className="text-right text-blue-300/70 pb-3 font-medium">نام فایل</th>
                        <th className="text-right text-blue-300/70 pb-3 font-medium">حجم</th>
                        <th className="text-right text-blue-300/70 pb-3 font-medium">مدت</th>
                        <th className="text-right text-blue-300/70 pb-3 font-medium">کاربر</th>
                        <th className="text-right text-blue-300/70 pb-3 font-medium">تاریخ</th>
                      </tr>
                    </thead>
                    <tbody>
                      {stats.recentVideos.map((video, index) => (
                        <tr key={video.id} className="border-b border-white/5">
                          <td className="py-3 text-white/60">{index + 1}</td>
                          <td className="py-3 text-white font-mono text-xs max-w-[200px] truncate">
                            {video.fileName || "—"}
                          </td>
                          <td className="py-3 text-white/80">{formatFileSize(video.fileSize)}</td>
                          <td className="py-3 text-white/80">{formatDuration(video.duration)}</td>
                          <td className="py-3 text-blue-300">@{video.username || "ناشناس"}</td>
                          <td className="py-3 text-white/60 text-xs" dir="ltr">
                            {new Date(video.createdAt).toLocaleDateString("fa-IR")}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-12 text-white/40">
                  <div className="text-5xl mb-4">📭</div>
                  <p>هنوز ویدیویی ثبت نشده</p>
                  <p className="text-sm mt-2">اولین ویدیو رو به ربات بفرستید!</p>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 mt-12">
        <div className="max-w-5xl mx-auto px-4 py-6 text-center text-white/30 text-sm">
          ربات دانلود ویدیو تلگرام | ساخته شده با Next.js و PostgreSQL
        </div>
      </footer>
    </div>
  );
}
