import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import {
  isReAstryxVendorCss,
  scopeReAstryxVendorCss,
} from './scripts/scope-re-astryx-css.mjs'

function reAstryxCssContainmentPlugin() {
  return {
    name: 'cenvalue-re-astryx-css-containment',
    enforce: 'pre',
    transform(code, id) {
      if (!isReAstryxVendorCss(id)) return null
      return {
        code: scopeReAstryxVendorCss(code, id),
        map: null,
      }
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [reAstryxCssContainmentPlugin(), react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      }
    },
    hmr: {
      overlay: true,
    }
  }
})
