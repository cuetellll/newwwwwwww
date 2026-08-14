import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "ربات دانلود ویدیو تلگرام",
  description: "ویدیو به ربات فوروارد کنید، لینک دانلود مستقیم دریافت کنید",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="fa" dir="rtl">
      <body className="bg-slate-900 text-white antialiased">{children}</body>
    </html>
  );
}
