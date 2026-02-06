import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Seleen Founder Portal",
  description: "Super admin portal for managing Seleen platform and customers",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
