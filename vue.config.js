import { defineConfig } from '@vue/cli-service'
export default defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: 'http://localhost:5000'
  }
})
