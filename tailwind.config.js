/** @type {import('tailwindcss').Config} */
export default {
  "content": [
    "./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}"
  ],
  "theme": {
    "extend": {
      "colors": {
        "primary": "#003366",
        "secondary": "#4472C4",
        "accent": "#FFC000",
        "background": "#F3F3F3",
        "text": "#333333",
        "success": "#548235",
        "warning": "#FF0000"
      },
      "fontFamily": {
        "sans": [
          "Inter",
          "system-ui",
          "sans-serif"
        ]
      }
    }
  },
  "plugins": [
    "@tailwindcss/typography"
  ]
}