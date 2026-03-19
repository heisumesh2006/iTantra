
import { createContext, useState, type ReactNode } from "react";
import type { Media } from "./types";
const Context = createContext<{
  media: Media | null;
  setMedia: (media: Media | null) => void;
}>({ media: null, setMedia: () => {} });
export function AudioContext({ children }: { children: ReactNode }) {
  const [media, setMedia] = useState<Media | null>(null);
  return (
    <Context.Provider value={{ media, setMedia }}>{children}</Context.Provider>
  );
}