import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Seleen Customer Portal",
  description: "Manage your Seleen licenses, users, and billing",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
