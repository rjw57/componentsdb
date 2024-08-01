import { defineConfig } from "astro/config";
import react from "@astrojs/react";

import tailwind from "@astrojs/tailwind";

// https://astro.build/config
export default defineConfig({
  integrations: [react(), tailwind()],
  vite: {
    define: {
      // HACK: work around next.js Link component trying to examine process.env.
      "process.env": {},
    },
    ssr: {
      noExternal: ["@apollo/client"],
    },
  },
});
