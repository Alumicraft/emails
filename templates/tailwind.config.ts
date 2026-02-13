import type { Config } from "tailwindcss";

const config: Config = {
  theme: {
    extend: {
      colors: {
        brand: {
          primary: "var(--primary-color)",
          text: "var(--text-color)",
          background: "var(--background-color)",
        },
      },
    },
  },
};

export default config;
