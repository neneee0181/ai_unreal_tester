// main.jsx — React 앱의 시작점.
// 역할: <div id="root"> 를 찾아 그 안에 <App/> 을 그린다(mount). 딱 이것만.

import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";

// index.html 의 <div id="root"> 를 React 가 접수
const root = createRoot(document.getElementById("root"));
root.render(<App />);
