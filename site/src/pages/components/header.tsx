import { Geist, Geist_Mono } from "next/font/google";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const fontClass = `${geistSans.className} ${geistMono.className} font-[family-name:var(--font-geist-sans)] text-3xl text-white font-bold`

export default function Header() {
  return (
    <div 
      className={
        `${fontClass} flex w-screen justify-center py-3 bg-[var(--color-three)]`
        }>
      Anom
    </div>
  );
}
