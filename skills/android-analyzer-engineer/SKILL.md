---
name: android-analyzer-engineer
version: 2.0.0
description: |
  Full Android app investigation combining manifest analysis and reverse engineering.
  Use when asked to "分析竞品", "analyze this APK", "reverse engineer this Android app",
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
  - WebFetch
---

# Android Analyzer & Engineer

**版本：2.0.0**

## 版本历史

| 版本 | 变更内容 |
|---|---|
| 2.0.0 | 合并 android-app-analyzer（已废弃）：Phase 1 新增竞品分析模式（diandian URL 提取包名 → Google Play 商店信息抓取）、fetch_google_play.py；正文改为中文 |
| 1.2.0 | SyncAdapter / ContactDirectory 策略描述修正为保活滥用语义 |
| 1.1.0 | 报告改为中文格式；敏感权限标注改为【敏感】|
| 1.0.0 | 初始版本：整合 android-app-analyzer 与 android-reverse-engineering-re |

## 功能概述

整合两个能力的完整 Android 应用调查工作流：

- **Phase 1（Manifest 分析）** — 通过包名下载或分析本地 APK/XAPK；支持 diandian.com URL 输入自动提取包名并从 Google Play 抓取商店信息；解析 `AndroidManifest.xml` 的权限、后台保活策略、广告 SDK；生成结构化中文报告。
- **Phase 2（逆向工程）** — 用 jadx 或 Fernflower/Vineflower 反编译 APK；追踪从 UI 到网络的调用链；提取并文档化 HTTP API 接口。

## 使用时机决策

| 用户意图 | 建议路径 |
|---|---|
| "这个 app 有什么权限 / SDK？" | 仅 Phase 1（Manifest 分析） |
| "帮我分析竞品" / 给了点点链接或包名 | 仅 Phase 1（含 Google Play 商店信息） |
| "反编译这个 APK" / "找 API 接口" | 仅 Phase 2（逆向工程） |
| "全面分析" / "能找到什么就找什么" | Phase 1 + Phase 2 |

---

## Phase 1 — Manifest 分析与竞品报告（`analyzer/`）

### 1.1 前置要求

**apkeep**（通过包名下载 APK 时必须安装，分析本地文件可跳过）：

```bash
# macOS / Linux
brew install apkeep

# 任意平台（需要 Rust）
cargo install apkeep

# Windows：从 GitHub Releases 下载预编译二进制
# https://github.com/EFForg/apkeep/releases/latest
```

**Python 依赖**（首次运行时自动安装，也可提前安装）：

```bash
python3 -m pip install -r ${SKILL_DIR}/analyzer/requirements.txt
```

### 1.2 输入识别与包名提取

支持三种输入方式：

| 输入类型 | 示例 | 处理方式 |
|---|---|---|
| **点点数据链接** | `https://app.diandian.com/app/.../googleplay?...&id=com.xxx` | 正则提取 `id=` 参数作为包名，不访问点点页面 |
| **包名** | `com.example.app` | 直接使用 |
| **本地文件** | `/path/to/app.apk` 或 `.xapk` | 跳过商店信息，直接分析 |

```bash
INPUT="<用户输入的内容>"

if echo "$INPUT" | grep -q "diandian.com"; then
    # 从点点 URL 提取包名
    PACKAGE=$(echo "$INPUT" | grep -oP '(?<=id=)[^&]+' | \
        python3 -c "import sys,urllib.parse; print(urllib.parse.unquote(sys.stdin.read().strip()))")
elif echo "$INPUT" | grep -qP '^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*){1,}$'; then
    PACKAGE="$INPUT"
else
    # 本地文件，跳过商店信息
    PACKAGE=""
fi
```

### 1.3 抓取 Google Play 商店信息

有包名时，从 Google Play 获取商店信息（公开页面，无需登录）。

构造 URL：`https://play.google.com/store/apps/details?id=<PACKAGE>&hl=en-us&gl=us`

**抓取工具优先���：**

**优先级 1：`opencli browser`**（JS 完整渲染，推荐）

```bash
SKILL_DIR="$HOME/.claude/skills/android-analyzer-engineer"
CACHE_DIR="$SKILL_DIR/.cache/$PACKAGE"
mkdir -p "$CACHE_DIR/web-articles"

GPLAY_URL="https://play.google.com/store/apps/details?id=${PACKAGE}&hl=en-us&gl=us"
opencli browser open "$GPLAY_URL"
opencli browser wait time 2
opencli browser extract > "$CACHE_DIR/web-articles/google_play.md"

# 单独获取图标 URL（extract 输出不含图标）
ICON_URL=$(opencli browser eval "
  const imgs = Array.from(document.querySelectorAll('img'));
  const icon = imgs.find(img => img.src && img.src.includes('play-lh') && img.width > 60 && !img.src.includes('w526'));
  icon ? icon.src.replace(/=w\d+-h\d+-rw/, '=s256-rw') : ''
" 2>/dev/null | tr -d '"')
```

**优先级 2：gstack browse**（无头浏览器，opencli 不可用时）

使用 `/browse` skill 导航至 Google Play 页面，提取 Markdown 内容保存至 `$CACHE_DIR/web-articles/google_play.md`，图标 URL 同理通过 eval 获取。

**优先级 3：WebFetch**（最后兜底，Google Play JS 渲染可能拿到残缺内容）

> ⚠️ 商店信息抓取失败时，自动降级：跳过商店信息，继续输出 APK 分析部分。

**解析 Google Play 数据：**

```bash
GPLAY_JSON=$(python3 "$SKILL_DIR/analyzer/fetch_google_play.py" \
    "$CACHE_DIR/web-articles/google_play.md" "$PACKAGE")
```

输出字段：`app_name`、`developer`、`rating`、`rating_count`、`downloads`、`last_update`（YYYY-MM-DD）、`category`（中文）、`google_play_url`。

### 1.4 APK 静态分析

```bash
SKILL_DIR="$HOME/.claude/skills/android-analyzer-engineer"

# 通过包名下载并分析
python3 "$SKILL_DIR/analyzer/android_analyzer.py" "$PACKAGE"

# 本地文件
python3 "$SKILL_DIR/analyzer/android_analyzer.py" /path/to/app.apk

# 已有缓存，跳过下载
python3 "$SKILL_DIR/analyzer/android_analyzer.py" "$PACKAGE" --skip-download
```

**工作空间**（`.cache/android-app-analyzer/<包名>/`）：

```
downloads/   — APK / XAPK 文件
extracted/   — 从 XAPK 解压的基础 APK
reports/     — *_manifest.xml、*_analysis.md
run.json     — 运行元数据
```

缓存限制：超过 5 个包工作区警告；超过 20 个停止运行，需手动清理。

### 1.5 报告内容

生成的 `*_analysis.md` 包含：

1. **基本信息** — 包名、版本、compileSdk、targetSdk、minSdk
2. **后台保活与推送策略** — 开机自启、FCM、前台服务、精确闹钟、WorkManager、同步适配器、悬浮窗
3. **广告 SDK** — AdMob（含 App ID）、AppLovin、IronSource、Unity Ads、Meta、Mintegral、ByteDance/Pangle 等 20+ 个
4. **第三方服务** — Firebase Analytics/Crashlytics、Adjust、AppsFlyer、Branch、Sentry、ExoPlayer 等
5. **权限列表** — 系统权限（标注【敏感】）和自定义权限
6. **组件统计** — Activity、Service、Receiver、Provider 数量

### 1.6 竞品分析报告模板

**完整竞品报告（有商店信息）：**

```markdown
# 竞品分析：<app_name>

> 分析时间：<当前日期>
> 包名：`<package>`
> 数据来源：Google Play + APK 静态分析

---

## 一、商店信息

| 字段 | 值 |
|---|---|
| **图标** | ![](<icon_url>) |
| **应用名称** | <app_name> |
| **包名** | `<package>` |
| **开发者** | <developer> |
| **评分** | ⭐ <rating>（<rating_count>） |
| **下载量** | <downloads> |
| **最近更新** | <last_update> |
| **分类** | <category> |
| **Google Play** | [点击查看](<google_play_url>) |

---

## 二、APK 基本信息

（粘贴 APK 分析报告的「基本信息」章节）

---

## 三、后台保活与推送策略

（粘贴 APK 分析报告的「后台保活与消息推送策略」章节）

---

## 四、广告 SDK

（粘贴 APK 分析报告的「广告 SDK」章节）

---

## 五、第三方服务

（粘贴 APK 分析报告的「第三方服务」章节）

---

## 六、权限列表

（粘贴 APK 分析报告的「权限列表」章节）

---

## 七、组件统计

（粘贴 APK 分析报告的「组件数量统计」章节）
```

**无商店信息模式（本地文件 / 抓取失败降级）：**

```markdown
# APK 分析：<package_or_filename>

> 分析时间：<当前日期>
> 数据来源：APK 静态分析
> ⚠️ 商店信息不可用

（从二开始，结构同上）
```

---

## Phase 2 — 逆向工程（`re/`）

### 2.1 检查并安装依赖

```bash
bash ${SKILL_DIR}/re/scripts/check-deps.sh
```

必须安装：**Java 17+**、**jadx**
推荐安装：**Vineflower/Fernflower**、**dex2jar**

安装缺失依赖：

```bash
bash ${SKILL_DIR}/re/scripts/install-dep.sh jadx
bash ${SKILL_DIR}/re/scripts/install-dep.sh vineflower
bash ${SKILL_DIR}/re/scripts/install-dep.sh dex2jar
```

安装脚本自动检测 OS，尽量不需要 sudo。如需 sudo 且用户拒绝，脚本会打印手动安装说明（退出码 2）。

### 2.2 反编译

使用 Phase 1 下载的 APK 或单独提供的文件：

```bash
# 默认：jadx（适合 APK/XAPK/JAR/AAR）
bash ${SKILL_DIR}/re/scripts/decompile.sh <file>

# 混淆代码时加 --deobf
bash ${SKILL_DIR}/re/scripts/decompile.sh --deobf <file>

# JAR/AAR 推荐 Fernflower（Java 还原质量更好）
bash ${SKILL_DIR}/re/scripts/decompile.sh --engine fernflower <file>

# jadx 有警告时，双引擎对比
bash ${SKILL_DIR}/re/scripts/decompile.sh --engine both --deobf <file>
```

**引擎选择指南：**

| 输入类型 | 推荐策略 |
|---|---|
| APK / XAPK | jadx 优先；混淆时加 `--deobf` |
| JAR / AAR | fernflower（Java 还原质量更好） |
| jadx 输出有警告 | `--engine both` 逐类对比 |

### 2.3 分析结构

反编译完成后：

1. 读取 `<output>/resources/AndroidManifest.xml` — 找 launcher Activity、Application 类、权限声明
2. 浏览 `<output>/sources/` — 找 `api`、`network`、`data`、`repository` 等包
3. 识别架构模式（MVP / MVVM / Clean Architecture）

详细追踪技术参考：`${SKILL_DIR}/re/references/call-flow-analysis.md`

### 2.4 追踪调用链

从 UI 到网络的典型路径：

```
Activity.onCreate() → 点击事件 → ViewModel → Repository → ApiService → HTTP 请求
```

混淆代码时的策略：
- **字符串不会被混淆**：从 URL、错误信息、常量入手
- **Android 框架类保留原名**：`Activity`、`Fragment`、`Intent`
- **库的公开 API 保留**：Retrofit 注解、OkHttp builder 可直接识别
- 使用 `--deobf` 让 jadx 生成可读替换名

### 2.5 提取并文档化 API

```bash
# 全量扫描
bash ${SKILL_DIR}/re/scripts/find-api-calls.sh <output>/sources/

# 精准扫描
bash ${SKILL_DIR}/re/scripts/find-api-calls.sh <output>/sources/ --retrofit
bash ${SKILL_DIR}/re/scripts/find-api-calls.sh <output>/sources/ --urls
bash ${SKILL_DIR}/re/scripts/find-api-calls.sh <output>/sources/ --auth
```

每个接口按以下格式文档化：

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

API 提取模式参考：`${SKILL_DIR}/re/references/api-extraction-patterns.md`

---

## 完整分析输出

完整分析（Phase 1 + Phase 2）最终交付：

1. **竞品报告**（`*_analysis.md`）— 商店信息、权限、SDK、后台策略
2. **反编译源码** — 输出目录
3. **架构摘要** — 主要包结构、架构模式
4. **API 文档** — 所有发现的接口（按上述格式）
5. **调用链图** — 关键路径（重点：认证流程、核心功能）
6. **交叉验证发现** — 例：「Manifest 声明 AdMob → 源码确认 `MobileAds.initialize()` 在 `Application.onCreate()` 调用」

---

## 常见问题

| 问题 | 解决方法 |
|---|---|
| `apkeep` 未安装 | Homebrew、cargo，或从 GitHub Releases 下载二进制 |
| `python` 指向 Python 2 | 明确使用 `python3` |
| 工作区包数量超限 | 手动删除 `.cache/android-app-analyzer/` 下的旧目录 |
| XAPK 无法提取基础 APK | 上游包问题，手动从 APKCombo 下载后指定本地路径 |
| APK 下载失败 | 手动下载放到 `.cache/android-app-analyzer/<package>/downloads/`，用本地路径重新分析 |
| opencli 不可用 | 降级为 gstack browse，再降级为 WebFetch |
| Google Play 解析失败 | 自动降级，仅输出 APK 分析（无商店信息） |
| Phase 2 先于 Phase 1 运行 | Manifest 报告很快，通常已能回答问题，不必反编译 |
| `--engine fernflower` 用于 APK 但无 dex2jar | 先安装 dex2jar：`install-dep.sh dex2jar` |
| 将混淆类名作为发现点报告 | 用 `--deobf` 或通过字符串字面量和库调用导航 |
| 文档化接口时缺少调用链 | 必须追溯到 Activity/Fragment 入口点 |

---

## 完整执行示例

```
用户: 帮我分析这个竞品
      https://app.diandian.com/app/oy1qiouqq8r5s1n/googleplay?market=11&country=24&id=kjv.bible.kingjamesbible

执行流程（Phase 1）：
1. 从点点 URL 正则提取包名 → kjv.bible.kingjamesbible（不访问点点页面）
2. opencli browser 抓取 Google Play 页面 + eval 获取图标 URL
3. fetch_google_play.py 解析 → 开发者: Ozion, 评分: 4.80, 更新: 2026-04-17
4. android_analyzer.py 分析 APK → 生成 *_analysis.md
5. 合并输出完整竞品报告
```

```
用户: 全面分析 com.example.app，找出所有 API 接口

执行流程（Phase 1 + Phase 2）：
1. 从 Google Play 获取商店信息
2. android_analyzer.py 分析 Manifest → 生成权限/SDK 报告
3. check-deps.sh 检查逆向工具
4. decompile.sh 反编译 APK（jadx）
5. find-api-calls.sh 提取所有 HTTP 接口
6. 追踪关键调用链，交叉验证 Manifest 声明
7. 输出完整报告
```
