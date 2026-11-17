import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./app/App";
import "@tinkerbells/xenon-ui/styles.css";
import { ThemeProvider } from "@tinkerbells/xenon-ui";
import { Toaster } from "sonner";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider>
      <App />
      <Toaster />
    </ThemeProvider>
  </StrictMode>
);
