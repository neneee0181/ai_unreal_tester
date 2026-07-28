// vite.config.js — Vite(화면 빌드 도구) 설정.
//
// Vite 역할: JSX/React 를 브라우저가 이해하는 JS 로 변환 + 개발 중 실시간 갱신(HMR).
// 우리 화면 파일은 전부 renderer/ 아래 있으니 root 를 renderer 로 잡는다.

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";   // JSX 를 처리해주는 플러그인

export default defineConfig({
  root: "renderer",              // index.html 이 있는 폴더
  plugins: [react()],
  base: "./",                    // 배포 시 file:// 로 열려도 경로가 깨지지 않게 상대경로
  server: { port: 5173 },        // 개발서버 포트 (main.js 가 이 주소를 로드)
  build: {
    outDir: "dist",              // renderer/dist 로 빌드 (main.js 배포 로드 경로와 일치)
    emptyOutDir: true,
  },
});
