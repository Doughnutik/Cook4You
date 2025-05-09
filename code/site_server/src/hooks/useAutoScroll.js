import { useEffect } from "react";

export function useAutoScroll(ref, dependency) {
  useEffect(() => {
    ref.current?.scrollIntoView({ behavior: "smooth" });
  }, [dependency]);
}