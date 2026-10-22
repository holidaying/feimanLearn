# 费曼实验课

> **讲不明白，就是没搞懂。**
>
> 每天 10 个话题，随机抽一个，**不查资料裸讲一遍**，让千问当那个「听不懂的外行」给你打分 —— 圈出卡点、只给方向不给答案，改到及格为止。

一个**输出倒逼输入的理解力训练器**。不是知识学习 App，不给你上课、不推送文章、不划重点。你以为你懂了，那就讲一遍；讲不明白的地方，就是你没真懂的地方。

| | |
|---|---|
| Web 端（线上） | http://58.87.96.207:83/ |
| 移动端 H5（线上） | http://58.87.96.207:84/ |
| 权威文档 | [产品手册 v1.0](./费曼实验课-产品手册-v1.0.md) · [PRD v1.1](./费曼实验课-PRD-v1.1.md) |
| 状态 | Web 端已上线；移动端 H5 已上线，Android 包待 HBuilderX 云打包 |

---

## 目录

- [核心闭环](#核心闭环)
- [特性](#特性)
- [快速开始](#快速开始)
- [目录结构](#目录结构)
- [API 一览](#api-一览)
- [评价体系](#评价体系)
- [分层提示机制（L1–L4）](#分层提示机制l1l4)
- [技术栈](#技术栈)
- [配置项](#配置项)
- [线上部署](#线上部署)
- [开发约定与踩坑](#开发约定与踩坑)
- [文档索引](#文档索引)

---

## 核心闭环

```
选课题 → ① 裸讲（打字 / 语音）
            ↓
        ② 千问评价（四维打分 + 卡点 + 等级）
            ↓
        ③ 依据卡点修正重讲  ←──────────┐
            ↓                          │
        ≤5 轮迭代 ────────────────────┘
            ↓
        等级 ≥ 良（70 分）→ 结业
            ↓
        生成 300 字小科普 · 导出 / 分享
```

理论依据是费曼学习法四步（选定目标 → 讲给小孩 → 定位卡点 → 简化打磨），底层规律是**合意困难 + 生成效应**。所以本项目最核心的一条铁律是：**AI 只给卡点和方向，绝不给现成答案**（精确含义见[分层提示机制](#分层提示机制l1l4)）。

---

## 特性

- **今日课题**：每天 10 条 = 6 条常青底库 + 4 条热榜（当前热榜为占位，M3 接真实爬取），点击「开始随机实验」抽 1 条
- **裸讲输入**：键盘打字，或语音输入（Web Speech API，Chrome / Edge；转写结果可编辑后再提交）
- **千问四维评价**：简洁性 / 完整性 / 逻辑性 / 比喻力，各 25 分，满分 100，输出结构化 JSON（雷达图 + 卡点 + 建议 + 与上轮对比）
- **多轮修正**：单次实验最多 5 轮，历次版本可对比回看
- **结业产出**：300 字小科普 → 纯文字 / Markdown 文件 / 图片卡片（1080×1440）三种形态 + 系统分享
- **题库与收藏**：全量课题分类浏览（6 大类）、我的收藏
- **分层提示**：L1 改进方向 → L2 结构提示 → L3 一句起头 → L4 标准示范（仅结业后），逐级递进，绝不剧透
- **双端同构**：Web（Vue3 + Vite）与移动端（uni-app Vue3）共用同一套 REST API，业务逻辑逐行一致

---

## 快速开始

### 环境要求

| 依赖 | 版本 | 说明 |
|---|---|---|
| Python | 3.8+ | 后端**零第三方依赖**，只用标准库 |
| Node.js | 18+ | 仅前端构建需要 |
| 有效端口 | 8000 | 后端默认端口，可用 `PORT` 环境变量覆盖 |
| 千问 API Key | — | 从 [阿里云百炼](https://bailian.console.aliyun.com/) 获取，**只放后端** |

### 1. 拉起后端

**方式一：一键启动（推荐）**

```powershell
.\start.ps1
# 提示输入千问 API Key（仅存在于当前会话，不落盘）
# 打开 http://localhost:8000
```

**方式二：手动**

```bash
cd server
export DASHSCOPE_API_KEY="sk-..."      # Windows: $env:DASHSCOPE_API_KEY = "sk-..."
python app.py
```

后端**单进程同时提供 API 与前端静态资源**（托管 `web/dist`），所以只需访问 `8000` 一个端口。

### 2. 构建前端

```bash
cd web
npm install
npm run build        # 产物输出到 web/dist，后端自动托管
```

### 3. 前端联调（可选，开发期用）

```bash
cd web
npm run dev          # http://localhost:5173，/api 反代到 localhost:8000
```

### 4. 移动端 H5

```bash
cd app
npm install
npm run build:h5     # 产物 -> app/dist/build/h5
npm run dev:h5       # 开发调试，端口 5174
```

Android 安装包必须由 HBuilderX 云打包，详见 [`app/APP_PACKAGING.md`](./app/APP_PACKAGING.md)。

### 5. 冒烟自检

```bash
curl http://localhost:8000/api/health
# {"status": "ok", "topics": 120}
```

---

## 目录结构

```
费曼实验法/
├─ 费曼实验课-PRD-v1.1.md        # 产品需求文档（基线版）
├─ 费曼实验课-产品手册-v1.0.md    # 使用 / 运营 / 运维三合一手册
├─ start.ps1                     # 一键启动脚本
├─ docs/archive/                 # 历史草稿（v0.1 / v0.2 / v1.0）
│
├─ server/                       # 后端：Python 标准库 http.server，零依赖
│  ├─ app.py                     #   路由 + 静态托管 + Markdown 导出
│  ├─ evaluator.py               #   千问评价代理（服务端持 Key，边界复评）
│  ├─ generate_topics.py         #   底库批量生成器
│  └─ topics_base.json           #   题库数据（6 类 × 20 条 = 120 条）
│
├─ evaluation/                   # 评价 Prompt 工程（离线验证用）
│  ├─ rubric.md                  #   四维评分锚定
│  ├─ system_prompt.md           #   System Prompt 全文
│  ├─ evaluate.py                #   独立验证脚本
│  └─ VALIDATION.md              #   梯度实测报告
│
├─ web/                          # Web 端：Vue 3 + Vite，零 UI 框架
│  ├─ src/api.js                 #   统一 API 层（相对路径 /api）
│  ├─ src/store.js               #   会话状态（localStorage）
│  ├─ src/components/            #   GradeBadge / RadarChart
│  └─ src/views/                 #   LabBench / Narration / Report /
│                                 #   Graduation / TopicBank / Favorites
│
├─ app/                          # 移动端：uni-app 3.0（Vue 3 + JS）
│  ├─ src/config.js              #   API_BASE（必须是字面量，不能用 import.meta.env）
│  ├─ src/utils/speech.js        #   语音识别适配（plus.speech / Web Speech）
│  └─ src/pages/                 #   bench / narration / report /
│                                 #   graduation / bank / favorites
│
└─ deploy/                       # 打包与发布脚本（pack.mjs / pack-app.mjs）
```

**当前题库规模**：120 条常青底库（科学常识 / 经济金融 / 技术概念 / 人文社科 / 生活经验 / 职场方法 各 20 条），PRD 目标为扩到 1000 条 —— 重跑 `server/generate_topics.py` 即可继续扩充。

---

## API 一览

| 方法 | 路径 | 用途 |
|---|---|---|
| GET | `/api/health` | 健康检查（含底库条数） |
| GET | `/api/topics/daily` | 每日 10 条（6 底库 + 4 热榜） |
| GET | `/api/topics/all` | 全量底库 + 分类统计 |
| POST | `/api/topics/random` | 随机抽 1 条 |
| POST | `/api/evaluate` | 千问四维评价（payload: `topic` / `background` / `text` / `prev_grade`） |
| POST | `/api/export/markdown` | 生成结业 Markdown 文本 |
| POST | `/api/demonstrate` | 结业标准示范（**服务端二次校验 grade**，非良/优返回 `forbidden`） |

---

## 评价体系

### 四维评分（各 25 分，满分 100）

| 维度 | 判定要点 |
|---|---|
| **简洁性** | 有无未解释术语 / 行话；句子是否直白，外行能否不卡壳读完 |
| **完整性** | 是否覆盖「是什么 / 为什么 / 怎么用（含举例）」三要素 |
| **逻辑性** | 有无自相矛盾、循环论证、因果倒置；因果链是否可追 |
| **比喻力** | 有无生活化原创类比；贴切加分，不当类比扣分 |

行为锚定按 `0 / 5 / 10 / 15 / 20 / 25` 六档给分。

### 等级映射

| 等级 | 分数 | 及格 | 处理 |
|---|---|---|---|
| 优 | 85–100 | ✅ | 直接结业 |
| 良 | 70–84 | ✅ | 结业；70–74 提示「再修一轮可冲优」 |
| 中 | 50–69 | ❌ | 继续修正 |
| 差 | 0–49 | ❌ | 建议先补课再来 |

### 一致性保障

- 固定 rubric 写进 System Prompt，`temperature = 0.2`
- **边界分（68–72）自动触发二次评价取中**（主评 `qwen3.7-plus` → 复评 `qwen3.7-max`），避免一次评差就劝退
- 每次评价记录 prompt 版本号（`fe-rubric@1.1` / `fe-demo@1.0`），便于回归对比
- JSON 解析失败自动降级提示，**用户讲述内容绝不丢**

实测结论见 [`evaluation/VALIDATION.md`](./evaluation/VALIDATION.md)。

---

## 分层提示机制（L1–L4）

「要不要给答案」被拆成「**什么时候给、给到哪一层**」，用四级闸门替代一刀切。

| 层级 | 触发时机 | 给什么 | 绝不给什么 |
|---|---|---|---|
| **L1** 改进方向 | 每轮评价都有 | 去哪找、补什么方向 | 定义、机制、结论 |
| **L2** 结构提示 | 每轮评价都有 | 「及格的重讲至少要说清哪几点」，仅骨架（2–3 条） | 具体内容、数据、例子 |
| **L3** 一句起头 | 第 3 轮起，用户主动点开 | 一句话开头（≤ 40 字） | 第二句、完整解释 |
| **L4** 标准示范 | **仅结业（良/优）后**，产出页主动点开 | 250–350 字完整示范 + 类比 + 避坑 | —— |

硬性约束：L1–L3 在 System Prompt 中被明确禁止写出正确定义；L4 由**服务端二次校验 grade**，非良/优直接返回 `forbidden`，前端无法绕过；L4 默认不自动加载，必须用户点击才请求。

---

## 技术栈

| 层 | 选型 | 理由 |
|---|---|---|
| Web 前端 | Vue 3 + Vite，零 UI 框架 | 体积小（产物约 99 KB JS / 26 KB CSS），加载快 |
| 移动端 | uni-app 3.0（Vue 3 + JS） | 与 Web 端复用业务逻辑与 API 层，一套代码可延伸小程序 |
| 后端 | Python 标准库 `http.server` | **零依赖**，免 pip 安装，部署到任何有 Python 的机器即可 |
| 并发 | `ThreadingHTTPServer` | 评价请求最长 40–120 s，不阻塞静态资源与其他 API |
| AI | 通义千问 MaaS 私有网关（OpenAI 兼容模式） | 主评 `qwen3.7-plus`，边界复评 `qwen3.7-max` |
| 语音 | Web Speech API / `plus.speech` | 浏览器与 App 原生能力，零额外成本；转写结果可编辑 |
| 持久化 | localStorage / uni storage | MVP 无账号，本机会话足够 |

---

## 配置项

| 变量 | 默认值 | 说明 |
|---|---|---|
| `DASHSCOPE_API_KEY` | 无（**必填**） | 千问 API Key。**仅后端持有，绝不进前端、不入库明文** |
| `DASHSCOPE_BASE_URL` | `https://token-plan.maas.qianwenaiapi.com/compatible-mode/v1` | 千问网关地址，换模型只改配置 |
| `PORT` | `8000` | 后端监听端口 |

移动端后端地址改 `app/src/config.js` 中的 `API_BASE`（**必须是字面量**）。

---

## 线上部署

| 项 | 值 |
|---|---|
| 实例 | `lhins-gpai56uk`（腾讯云轻量，ap-beijing，58.87.96.207） |
| Web 访问 | http://58.87.96.207:83/ |
| 移动 H5 访问 | http://58.87.96.207:84/ |
| 代码目录 | `/opt/feynman/`（server + web/dist） |
| 密钥文件 | `/etc/feynman.env`，权限 600 |
| 服务 | systemd `feynman.service`（:83）/ `feynman-h5.service`（:84），`Restart=always`，开机自启 |
| 防火墙 | 本项目新增 TCP 83、84，其余原有规则未动 |

**常用运维命令：**

```bash
systemctl restart feynman      # 重启 Web 服务
systemctl status feynman       # 查看状态
journalctl -u feynman -f       # 实时日志
ss -lntp | grep :83            # 确认端口监听
```

**发布流程：** 本地 `npm run build` → 生成 tar.gz → 传输到服务器 → sha256 校验 → 解包覆盖 `/opt/feynman` → `systemctl restart feynman`。全程不影响 80/81/82/8848 上的既有服务。打包脚本见 `deploy/pack.mjs`（Web）、`deploy/pack-app.mjs`（移动 H5）。

---

## 开发约定与踩坑

- **API Key 绝不入代码库**：只走环境变量；`server/evaluator.py` 里的默认网关地址是公开的，Key 不是
- **双端逻辑逐行同步**：`api.js` / `store.js` 接口形状保持一致；只有请求（`fetch` vs `uni.request`）、持久化（`localStorage` vs `uni storage`）、剪贴板分享（`navigator.*` vs `uni.*`）三处差异
- **App 端禁用 `import.meta.env`**：原生层 polyfill 会抛错，配置一律走 `src/config.js` 字面量
- **App 端不用 SVG 画雷达图**：改用 `canvas` + `uni.createCanvasContext`
- **`<style>` 内不要写 `#ifdef` / `@media`**：uni-app esbuild 不识别，直接报 css-syntax-error
- **中文路径**：打包与临时目录一律用 ASCII 路径（如 `D:\tmp\fh5`），规避 Windows Unicode 归一化问题
- **递归拷贝用 robocopy**：`fs.cpSync` 在 Windows 上会崩 Node
- **Android 云打包**：必须在 `manifest.json` 显式声明 `Speech`、`Share` 原生模块并填入 DCloud AppID，否则 `plus.speech` 为 undefined

---

## 文档索引

| 文档 | 用途 |
|---|---|
| [费曼实验课-产品手册-v1.0.md](./费曼实验课-产品手册-v1.0.md) | 使用者 / 产品运营 / 部署运维 三合一手册 |
| [费曼实验课-PRD-v1.1.md](./费曼实验课-PRD-v1.1.md) | 产品需求文档（基线版，决策已锁定） |
| [app/APP_PACKAGING.md](./app/APP_PACKAGING.md) | 移动端出包说明与踩坑清单 |
| [evaluation/VALIDATION.md](./evaluation/VALIDATION.md) | 评价 Prompt 梯度实测报告 |
| [evaluation/rubric.md](./evaluation/rubric.md) | 四维评分锚定细则 |
| [evaluation/system_prompt.md](./evaluation/system_prompt.md) | 评价 System Prompt 全文 |
| `docs/archive/` | 历史草稿（v0.1 / v0.2 / v1.0），保留不删 |

---

*由「费曼实验课」生成 · 讲不明白，就是没搞懂*
