# 费曼实验课 · 移动端出包说明

> 技术栈：uni-app 3.0（`3.0.0-5020420260813001`，Compiler 5.24 / vue3）+ Vite 5 + Vue 3 + JS
> 工程目录：`D:\AI小项目\费曼学习法\app`

---

## 1. 目录结构

```
app/
├─ package.json          # 依赖版本与 uni 脚本
├─ vite.config.js        # @ -> src 别名
├─ index.html
└─ src/
   ├─ main.js            # createSSRApp
   ├─ App.vue            # 全局设计系统（CSS 变量 + 通用类）
   ├─ manifest.json      # App 配置：模块声明 / 权限 / 打包参数
   ├─ pages.json         # 6 个页面注册
   ├─ config.js          # API_BASE（必须是字面量）
   ├─ api.js             # 统一 uni.request
   ├─ store.js           # 会话状态 + uni storage 持久化
   ├─ utils/speech.js    # 语音识别适配（plus.speech / Web Speech）
   ├─ components/
   │  ├─ GradeBadge.vue
   │  └─ RadarChart.vue  # canvas 绘制四维雷达
   └─ pages/
      ├─ bench/bench.vue           # 实验台
      ├─ narration/narration.vue   # 裸讲（打字 + 语音）
      ├─ report/report.vue         # 实验报告（L2 结构提示 + L3 起头）
      ├─ graduation/graduation.vue # 实验产出（四种导出 + L4 标准示范）
      ├─ bank/bank.vue             # 全部课题
      └─ favorites/favorites.vue   # 我的收藏
```

## 2. 与 Web 端的关系

数据层同构：`api.js` / `store.js` 与 `web/src` 下的同名文件接口形状完全一致，只有三处差异：

| 点 | Web 端 | App 端 |
|---|---|---|
| 请求 | `fetch` | `uni.request` |
| 持久化 | `localStorage` | `uni.getStorageSync/setStorageSync` |
| 剪贴板/分享 | `navigator.clipboard` / `navigator.share` | `uni.setClipboardData` / `uni.shareWithSystem` |

业务逻辑（分层提示 L1–L4、评分换算、练习记录取最好成绩）逐行保持一致，改一处记得改另一处。

## 3. 常用命令

```bash
npm run dev:h5     # H5 开发（端口 5174）
npm run build:h5   # H5 构建 -> dist/build/h5
npm run dev:app    # App 开发（需 HBuilderX 运行基座）
npm run build:app  # App 资源构建 -> dist/build/app
```

## 4. 已验证

- `npm run build:h5` 通过，6 个页面全部产出 chunk
- H5 版本已部署至 **http://58.87.96.207:84/** （systemd `feynman-h5.service`，防火墙 TCP 84）
- headless Chrome 校验：`uni-page data-page="pages/bench/bench"` 挂载成功，「今日课题 · 10 条」数据加载正常

## 5. 打 Android 安装包

`build:app` 只产出**前端资源**，`.apk` 必须由 HBuilderX 打包：

1. 用 HBuilderX 打开 `app/` 目录（不是整个项目根目录）
2. `manifest.json` → **App 模块配置** 勾选：`Speech(语音识别)`、`Share(分享)`；**App 权限配置** 勾选录音、存储、网络
3. `manifest.json` → **基础配置** 填入 DCloud **AppID**（替换占位的 `__UNI__FYNMAN1`）
4. 顶部菜单 **发行 → 原生App-云打包**
   - 勾选 Android，选择「使用 DCloud 公用证书」或自有证书
   - 渠道包可先不选
5. 等待云端队列（通常 3–10 分钟），下载 apk

> 自有证书更推荐：公用证书换包名会导致无法覆盖安装。
> 离线打包（Android Studio）见 DCloud 官方 SDK 文档，本项目未接入原生插件，可直接用官方 App 离线 SDK。

## 6. 踩坑清单（已规避，勿回退）

| 坑 | 处理 |
|---|---|
| `fs.cpSync` 递归在 Windows 崩 Node | 用 robocopy 或手写递归拷贝 |
| 中文路径被 Windows Unicode 归一化搞坏 | 打包/临时目录一律用 ASCII 路径（如 `D:\tmp\fh5`） |
| `<style>` 内写 `#ifdef` / `@media` | esbuild 不识别，直接报 css-syntax-error —— 本项目未使用 |
| `import.meta.env.VITE_XXX` | App 原生层 polyfill 抛错，配置全部走 `src/config.js` 字面量 |
| `manifest` 未声明原生模块 | 云打包后 `plus.speech` 为 undefined |
| 雷达图用 SVG | App 端不支持，改用 `canvas` + `uni.createCanvasContext` |
| App 端 canvas 层级最高 | 分享卡 canvas 放 `position:fixed; left:-99999rpx` 离屏 |

## 7. 后端地址

`src/config.js`：

```js
export const API_BASE = 'http://58.87.96.207:83/api'
```

换环境直接改这一行。**不要**改成相对路径 `/api` —— App 端没有同源概念。
若要保留 H5 部署到同源，可另加一个 `API_BASE_H5` 常量按条件取，但当前 H5 与 App 都用绝对地址，CORS 已放开 `*`，开箱即用。
