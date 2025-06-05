import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navigation from "@/components/Navigation";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "HopeForJob - Automated Job Applications",
  description: "Automate your job search with intelligent applications to LinkedIn and other platforms. Save time, increase applications, and land your dream job faster.",
  keywords: "job search, automated applications, linkedin, job hunting, career",
  authors: [{ name: "HopeForJob Team" }],
  viewport: "width=device-width, initial-scale=1",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="font-sans antialiased">
        <Navigation />
        <main className="lg:pl-72">
          <div className="lg:px-8">
            {children}
          </div>
        </main>
      </body>
    </html>
  );
}
