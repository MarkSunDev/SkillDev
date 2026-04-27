---
name: android-analyzer-engineer
version: 3.3.0
description: |
  Full Android app investigation: fetch Google Play store metadata, download APK,
  parse manifest, detect ad SDKs / keep-alive strategies / permissions, generate a
  fixed-format Markdown report, and optionally publish to Feishu Docs.
  Use when asked to "分析竞品", "analyze this app", "reverse engineer this Android app",
  "find API endpoints", "全面分析", or any task requiring manifest inspection,
  ad SDK detection, background strategy analysis, or deep source-level analysis.
triggers:
  - 分析竞品
  - 竞品报告
  - 分析这个app
  - 分析 apk
  - analyze competitor
  - reverse engineer
  - find API endpoints
  - android package analysis
  - 反编译
  - 提取接口
allowed-tools:
  - Bash
  - Read
  - Write
---

# Android Analyzer & Engineer

**版本：3.3.0**

## 版本历史

| 版本 | 变更内容 |
|---|---|
| 3.3.0 | 飞书文档创建改为调用 `/feishu_create_doc` skill（slash command），不再直接使用 `feishu_doc` MCP tool |
| 3.2.0 | 新增版本历史追踪：每次分析后自动归档报告到 `history/`，更新 `versions.json` 索引；新增 `compare.py` 支持跨版本 diff（权限/SDK/保活策略/组件变化） |
| 3.1.0 | 修复工作区路径：默认缓存改为 `~/.cache/android-app-analyzer/`，不再依赖脚本所在目录，任意 CWD 调用结果一致；store_fetcher.js 自动安装 google-play-scraper（对齐 dependency_bootstrap.py 模式，无需预提交 node_modules）；修复 google-play-scraper 新版 ESM default export 兼容问题；SKILL.md 路径引用全部从硬编码 `SKILL_DIR` 改为 harness 注入的 `BASE_DIR` |
| 3.0.0 | 重构商店数据获取：移除 diandian/opencli/gstack/WebFetch 爬虫方案，改用 google-play-scraper（Node.js）；输入仅支持包名；报告格式固定为八节结构；新增飞书文档创建步骤；报告新增评分分布、IAP、数据安全声明、权限 Play Store 对比 |
| 2.0.0 | 合并 android-app-analyzer：Phase 1 新增 diandian URL 提取包名、fetch_google_play.py |
| 1.2.0 | SyncAdapter / ContactDirectory 策略描述修正 |
| 1.1.0 | 报告改为中文格式；敏感权限标注【敏感】|
| 1.0.0 | 初始版本 |

## 功能概述

整合完整 Android 应用调查工作流：

- **Phase 1（竞品分析）** — 用户提供包名；通过 `google-play-scraper` 获取商店详情（评分、下载量、IAP、数据安全声明、权限声明等）；通过 `apkeep` 下载 APK/XAPK；`androguard` 解析 Manifest 的权限、保活策略、广告 SDK；输出**固定八节格式**的中文报告；分析完成后调用 `/feishu_create_doc` skill 创建飞书文档。
- **Phase 2（逆向工程）** — 用 jadx 或 Fernflower/Vineflower 反编译 APK；追踪 UI → 网络调用链；提取并文档化 HTTP API 接口。

## 使用时机

| 用户意图 | 建议路径 |
|---|---|
| "这个 app 有什么权限 / SDK？" | Phase 1 |
| "帮我分析竞品" + 包名 | Phase 1 |
| "反编译这个 APK" / "找 API 接口" | Phase 2 |
| "全面分析" / "能找到什么就找什么" | Phase 1 + Phase 2 |

---

## Phase 1 — 竞品分析（`analyzer/`）

### 1.1 前置依赖

**Node.js + google-play-scraper**（获取商店信息）：

```bash
# 在 analyzer/ 目录安装
cd ${BASE_DIR}/analyzer
npm install google-play-scraper
```

> 若 Node.js 未安装，商店数据获取步骤自动跳过，报告仍输出 APK 分析部分。

**apkeep**（下载 APK）：

```bash
brew install apkeep          # macOS / Linux (Homebrew)
cargo install apkeep         # 任意平台（需要 Rust）
# 或从 https://github.com/EFForg/apkeep/releases/latest 下载二进制
```

**Python 依赖**（首次运行自动安装）：

```bash
python3 -m pip install -r ${BASE_DIR}/analyzer/requirements.txt
```

### 1.2 输入规范

**只接受包名**，格式：`com.example.app`

```
✅ com.whatsapp
✅ kjv.bible.kingjamesbible
❌ URL、文件路径、点点链接（不再支持）
```

如果用户提供的是 URL 或其他格式，直接告知需要提供 Android 包名，不做任何自动提取或转换。

### 1.3 执行流程

```
Step 0: 获取商店信息（google-play-scraper）
  └── node store_fetcher.js <package>
      ├── app()         → 基本信息、评分、下载量、IAP、版本、近期更新
      ├── permissions() → Play Store 声明权限列表
      └── datasafety()  → 数据安全声明

Step 1: 下载 APK（apkeep）
  └── apkeep -a <package> -d apk-pure <downloads_dir>

Step 2: 解析 Manifest（androguard）
  └── python3 analyzer/android_analyzer.py <package>

Step 3: 生成固定格式报告
  └── <workspace>/reports/<package>_report.md

Step 4: 调用 /feishu_create_doc skill → 创建飞书文档
```

### 1.4 调用方式

```bash
# BASE_DIR is injected by the Claude Code harness as the skill's own directory.
# Do NOT hardcode ~/.claude/skills/... — the skill may live anywhere.

# 标准分析（获取商店信息 + 下载 + 分析）
python3 "${BASE_DIR}/analyzer/android_analyzer.py" com.example.app

# 跳过下载（使用缓存 APK）
python3 "${BASE_DIR}/analyzer/android_analyzer.py" com.example.app --skip-download

# 跳过商店信息（仅 APK 分析）
python3 "${BASE_DIR}/analyzer/android_analyzer.py" com.example.app --skip-store
```

**工作空间结构**（`.cache/android-app-analyzer/<包名>/`）：

```
downloads/   — 原始 APK / XAPK 文件
extracted/   — 从 XAPK 中提取的基础 APK
reports/     — <package>_report.md、<package>_manifest.xml（当前最新）
history/     — 按版本归档：<日期>_v<版本名>_<版本号>_report.md / _manifest.xml
               版本 diff 报告：<日期>_diff_<vA>_to_<vB>.md
temp/        — 临时文件
run.json     — 最近一次运行元数据（路径、版本、时间）
versions.json — 所有历史版本索引（版本名、版本号、分析时间、归档报告文件名）
```

缓存限制：超过 5 个包工作区发出警告；超过 20 个停止运行，需手动清理。

### 1.5 版本历史与对比

每次分析完成后，报告和 Manifest 自动归档到 `history/`，`versions.json` 记录所有历史版本索引。

**查看历史版本列表：**

```bash
python3 "${BASE_DIR}/analyzer/compare.py" com.example.app --list
```

**对比最近两次分析（默认行为）：**

```bash
python3 "${BASE_DIR}/analyzer/compare.py" com.example.app
```

**对比指定版本名：**

```bash
python3 "${BASE_DIR}/analyzer/compare.py" com.example.app -a 2.24.9 -b 2.25.1
```

**对比指定索引（0-based）：**

```bash
python3 "${BASE_DIR}/analyzer/compare.py" com.example.app -i 0 -j 2
```

**保存 diff 报告到 history/：**

```bash
python3 "${BASE_DIR}/analyzer/compare.py" com.example.app --save
```

**diff 报告涵盖：**

| 维度 | 内容 |
|---|---|
| APK 基本信息 | 版本名/号、SDK 版本变化 |
| 后台保活策略 | 各项策略状态变化（✅/➖）|
| 广告 SDK | 新增/移除的广告 SDK |
| 第三方服务 | 新增/移除的第三方服务 |
| 权限 | 新增/移除的权限（含敏感权限）|
| 组件统计 | Activity / Service / Receiver / Provider 数量变化 |

**当用户说以下内容时触发版本对比：**
- "对比上次分析" / "和上个版本比较" → `compare.py <pkg>`
- "查看历史版本" / "分析过几次" → `compare.py <pkg> --list`
- "对比 v2.24 和 v2.25" → `compare.py <pkg> -a 2.24 -b 2.25`

### 1.6 固定报告格式

生成的 `<package>_report.md` **严格遵循以下八节结构**，内容由分析结果填充，节标题和顺序不可更改：

```markdown
# 竞品分析报告：<app_name>

> **分析时间：** YYYY-MM-DD HH:MM:SS
> **包名：** `<package>`
> **数据来源：** Google Play + APK 静态分析

---

## 一、商店信息

| 字段 | 值 |
|---|---|
| **图标** | ![icon](<icon_url>) |
| **应用名称** | ... |
| **包名** | `...` |
| **开发者** | ... |
| **开发者邮箱** | ... |
| **开发者网站** | ... |
| **评分** | ★ X.XX（N 条评价）|
| **下载量** | ... |
| **价格** | 免费（含内购）/ ¥XX |
| **分类** | ... |
| **内容分级** | ... |
| **适配 Android** | X.X 及以上 |
| **最近更新** | YYYY-MM-DD |
| **当前版本** | ... |
| **Google Play** | [查看页面](...) |

**评分分布：**
| 星级 | 数量 |
|---|---|
| ★★★★★ | N |
...

**近期更新说明：**
> ...

**隐私政策：** [链接](...)

---

## 二、APK 基本信息

| 字段 | 值 |
|---|---|
| **包名** | `...` |
| **版本名** | ... |
| **版本号** | ... |
| **compileSdk** | ... |
| **targetSdk** | ... |
| **minSdk** | ... |
| **Application 类** | `...` |

---

## 三、后台保活与推送策略

共检测到 N 项策略（共 9 项）：

| 策略 | 状态 | 说明 |
|---|---|---|
| 滥用同步适配器保活（SyncAdapter） | ✅ 已检测 / ➖ 未发现 | ... |
| 滥用联系人目录提供者保活（ContactDirectory） | ... | ... |
| 开机自启广播接收器 | ... | ... |
| Firebase 云消息推送（FCM） | ... | ... |
| 全屏意图（Full-screen Intent） | ... | ... |
| 悬浮窗（System Alert Window） | ... | ... |
| 前台服务（Foreground Service） | ... | ... |
| 精确闹钟（Exact Alarm） | ... | ... |
| WorkManager / JobScheduler | ... | ... |

### 已检测策略详情
（每个已检测策略的详细说明和相关组件）

---

## 四、广告 SDK

共检测到 N 个广告 SDK：

| SDK | 备注 |
|---|---|
| ... | App ID: `...` / — |

---

## 五、第三方服务与 SDK

共检测到 N 个第三方服务：
- ...

---

## 六、权限列表

共 N 个权限（系统 N，自定义/第三方 N）

⚠️ 敏感权限（N 个）：
- `android.permission.XXX` 【敏感】

⚠️ 以下敏感权限存在于 APK 中，但未在 Google Play 商店页面声明：
（若存在差异时显示）

### 系统权限（N 个）
- `android.permission.XXX`
- `android.permission.YYY` 【敏感】

### 自定义 / 第三方权限（N 个）
- `com.xxx.permission.YYY`

---

## 七、组件统计

| 组件类型 | 数量 |
|---|---|
| Activity（界面）| N |
| Service（服务）| N |
| Receiver（广播接收器）| N |
| Provider（内容提供者）| N |

---

## 八、数据安全声明（Google Play）

（来自 google-play-scraper datasafety()，列出收集的数据类型和用途）

---

*报告由 android-analyzer-engineer v3.3.0 自动生成 · YYYY-MM-DD HH:MM:SS*
```

### 1.7 飞书文档创建

报告文件生成并经 Claude 确认内容无误后，**调用 `/feishu_create_doc` skill** 创建飞书文档：

```
调用 /feishu_create_doc skill，传入：
    title:    竞品分析：<app_name>（<package>）
    markdown: 完整报告 Markdown 内容（读取 <workspace>/reports/<package>_report.md）

创建完成后输出文档链接。
若 /feishu_create_doc skill 不可用，提示用户报告已保存到本地路径，并显示完整报告内容。
```

> ⚠️ 注意：此处必须使用 `/feishu_create_doc` **skill**（slash command），而非 MCP tool。

---

## Phase 2 — 逆向工程（`re/`）

### 2.1 检查并安装依赖

```bash
bash ${BASE_DIR}/re/scripts/check-deps.sh
```

必须安装：**Java 17+**、**jadx**
推荐安装：**Vineflower/Fernflower**、**dex2jar**

```bash
bash ${BASE_DIR}/re/scripts/install-dep.sh jadx
bash ${BASE_DIR}/re/scripts/install-dep.sh vineflower
bash ${BASE_DIR}/re/scripts/install-dep.sh dex2jar
```

### 2.2 反编译

```bash
# 默认：jadx
bash ${BASE_DIR}/re/scripts/decompile.sh <apk_file>

# 混淆代码
bash ${BASE_DIR}/re/scripts/decompile.sh --deobf <apk_file>

# JAR/AAR 推荐 Fernflower
bash ${BASE_DIR}/re/scripts/decompile.sh --engine fernflower <file>

# 双引擎对比
bash ${BASE_DIR}/re/scripts/decompile.sh --engine both --deobf <file>
```

| 输入类型 | 推荐策略 |
|---|---|
| APK / XAPK | jadx 优先；混淆时加 `--deobf` |
| JAR / AAR | fernflower（Java 还原质量更好）|
| jadx 输出有警告 | `--engine both` 逐类对比 |

### 2.3 分析结构

1. 读取 `<output>/resources/AndroidManifest.xml` — 找 launcher Activity、Application 类
2. 浏览 `<output>/sources/` — 找 `api`、`network`、`data`、`repository` 包
3. 识别架构模式（MVP / MVVM / Clean Architecture）

参考：`${BASE_DIR}/re/references/call-flow-analysis.md`

### 2.4 追踪调用链

```
Activity.onCreate() → 点击事件 → ViewModel → Repository → ApiService → HTTP 请求
```

混淆代码策略：
- **字符串不被混淆**：从 URL、错误信息、常量入手
- **Android 框架类保留原名**：`Activity`、`Fragment`、`Intent`
- **库公开 API 保留**：Retrofit 注解、OkHttp builder 可直接识别
- 用 `--deobf` 让 jadx 生成可读替换名

### 2.5 提取并文档化 API

```bash
bash ${BASE_DIR}/re/scripts/find-api-calls.sh <output>/sources/
bash ${BASE_DIR}/re/scripts/find-api-calls.sh <output>/sources/ --retrofit
bash ${BASE_DIR}/re/scripts/find-api-calls.sh <output>/sources/ --urls
bash ${BASE_DIR}/re/scripts/find-api-calls.sh <output>/sources/ --auth
```

每个接口格式：

```markdown
### `METHOD /path`

- **来源**：`com.example.api.ApiService`（文件:行号）
- **Base URL**：`https://api.example.com/v1`
- **Path 参数**：`id`（String）
- **Query 参数**：`page`（int）、`limit`（int）
- **Headers**：`Authorization: Bearer <token>`
- **Request Body**：`{ "email": "string", "password": "string" }`
- **Response**：`ApiResponse<User>`
- **调用链**：`LoginActivity → LoginViewModel → UserRepository → ApiService`
```

---

## 完整分析输出

Phase 1 + Phase 2 交付：

1. **竞品报告**（固定八节格式 Markdown）
2. **飞书文档**（通过 `/feishu_create_doc` skill 创建）
3. **反编译源码**（输出目录）
4. **架构摘要**（主要包结构、架构模式）
5. **API 文档**（所有发现的接口）
6. **调用链图**（认证流程、核心功能关键路径）
7. **交叉验证发现**（Manifest 声明 vs 源码实现）

---

## 常见问题

| 问题 | 解决方法 |
|---|---|
| `node` 不在 PATH | 安装 Node.js；或用 `--skip-store` 跳过商店数据 |
| `google-play-scraper` 未安装 | `cd analyzer && npm install google-play-scraper` |
| 商店数据获取失败（网络/限流）| 重试；或用 `--skip-store` 仅做 APK 分析 |
| `apkeep` 未安装 | `brew install apkeep` 或从 GitHub Releases 下载 |
| APK 下载失败 | 手动放至 `.cache/android-app-analyzer/<pkg>/downloads/`，加 `--skip-download` |
| XAPK 无法提取基础 APK | 手动从 APKCombo 下载，用本地路径重新分析 |
| 工作区包数量超限 | 删除 `.cache/android-app-analyzer/` 下旧目录 |
| `--engine fernflower` 用于 APK 但无 dex2jar | `install-dep.sh dex2jar` |

---

## 完整执行示例

```
用户: 帮我全面分析竞品 com.whatsapp

执行流程（Phase 1）：
Step 0: node store_fetcher.js com.whatsapp
        → app_name: WhatsApp, developer: WhatsApp LLC
        → rating: 4.00, installs: 5,000,000,000+
        → permissions: [...], data_safety: [...]
Step 1: apkeep -a com.whatsapp -d apk-pure downloads/
        → downloads/com.whatsapp.xapk
Step 2: python3 android_analyzer.py com.whatsapp
        → 解析 Manifest：权限 N 个，FCM ✅，前台服务 ✅
Step 3: 生成 com.whatsapp_report.md（固定八节格式）
Step 4: 调用 /feishu_create_doc skill → 创建飞书文档
        → 文档链接：https://...

执行流程（Phase 2，如用户需要）：
5. check-deps.sh → jadx OK
6. decompile.sh --deobf com.whatsapp.apk
7. find-api-calls.sh sources/ --all
8. 追踪关键调用链，交叉验证 Manifest 声明
9. 输出 API 文档
```

