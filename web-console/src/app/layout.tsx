import "./globals.css";
import React from "react";

export const metadata = {
  title: "TigerGraph Agentic Fraud Console | HHGOA",
  description: "Next-generation fraud investigation, uncertainty assessment, and next-best action platform.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#090d16] text-slate-100 min-h-screen flex flex-col font-sans">
        {children}
      </body>
    </html>
  );
}
