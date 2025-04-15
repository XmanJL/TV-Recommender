import type { Metadata } from "next";
import "./globals.css";
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';
import { Container } from "@mui/material";

export const metadata: Metadata = {
  title: "GDG Content Recommender",
  description: "By Jasper Li and Bryan Bergo",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`antialiased`}
      >
        <Container>
          {children}
        </Container>
      </body>
    </html>
  );
}
