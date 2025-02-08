import { Toaster } from "@/components/ui/toaster";
import AuthProvider from "@/context/AuthProvider";
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "advista",
  description: "AI-powered research. Human-centered insights",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <AuthProvider>
        {/* <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange> */}
        <body className="">
          {children}
          <Toaster />
        </body>
        {/* </ThemeProvider> */}
      </AuthProvider>
    </html>
  );
}
