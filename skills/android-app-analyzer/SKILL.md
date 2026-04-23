---
name: android-app-analyzer
version: 2.1.0
description: |
  Analyze Android apps by package name, local APK/XAPK, or diandian.com URL.
  Inspects manifest metadata, permissions, background keep-alive strategies,
  push integrations, ad SDK usage, and third-party services.
  Also supports full competitor analysis with store info fetched from Google Play.
triggers:
  - 分析竞品
  - analyze competitor
  - 竞品报告
  - diandian.com
  - android package analysis
  - 分析 apk
  - 分析这个app
allowed-tools:
  - Bash
  - Read
  - Write
  - WebFetch
---

# Android App Analyzer

**版本：2.1.0**

## 版本历史

| 版本 | 变更内容 |
|---|---|
| 2.1.0 | 商店数据源改为 Google Play（公开无需登录）；新增 fetch_google_play.py；移除 fetch_diandian.py；图标改用 Google Play CDN URL |
| 2.0.0 | 合并竞品分析功能：支持 diandian.com URL 输入；正文改为中文 |
| 1.2.0 | SyncAdapter / ContactDirectory 策略描述修正为保活滥用语义 |
| 1.1.0 | 报告改为中文格式；敏感权限标注改为【敏感】|
| 1.0.0 | 用 apkeep 替换 APKCombo 下载器；移除 apkcombo_download.py |

## 升级

如果已安装旧版本，升级步骤：

```bash
# 1. 进入 skill 所在目录
cd ~/.claude/skills/android-app-analyzer   # 全局安装
# 或
cd .claude/skills/android-app-analyzer     # 项目级安装

# 2. 如果是 git clone 方式安装，直接 pull
git pull

# 3. 如果是手动复制安装，重新复制新版本文件
cp /path/to/new/android_analyzer.py .
cp /path/to/new/SKILL.md .
cp /path/to/new/workspace_manager.py .
cp /path/to/new/dependency_bootstrap.py .
cp /path/to/new/fetch_google_play.py .   # 2.1.0 新增（替换 fetch_diandian.py）
rm fetch_diandian.py                     # 2.1.0 移除
```

Python 依赖无需重新安装（`androguard`、`lxml` 版本要求未变）。

---

## 功能概述

分析 Android 应用包，从 `AndroidManifest.xml` 生成结构化中文 Markdown 报告。支持三种输入模式：

| 模式 | 输入示例 | 说明 |
|---|---|---|
| **竞品分析模式** | `https://app.diandian.com/app/.../googleplay?...&id=com.xxx` | 从 URL 正则提取包名 → 抓取 Google Play 商店信息 + APK 静态分析 |
| **包名模式** | `com.example.app` | 直接抓取 Google Play 商店信息 + APK 静态分析 |
| **本地文件模式** | `/path/to/app.apk` 或 `/path/to/app.xapk` | 直接分析本地文件，无商店信息 |

---

## 前置要求

**apkeep**（包名模式必须安装，本地文件模式可跳过）：

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
python3 -m pip install -r requirements.txt
```

---

## 工作空间规则

技能使用统一的缓存工作空间：

- 默认根目录：`.cache/android-app-analyzer/`
- 每个包一个子目录：`.cache/android-app-analyzer/<包名>/`
- 子目录结构：
  - `downloads/` — 下载的 APK/XAPK
  - `extracted/` — 解压的 XAPK 内容
  - `reports/` — 生成的报告和 Manifest XML
  - `temp/` — 临时文件

缓存限制：
- 超过 5 个包工作区：打印警告并继续
- 超过 20 个包工作区：停止运行，需手动清理后再执行

---

## 竞品分析模式

### Step 1：识别输入类型，提取包名

```bash
INPUT="<用户输入的内容>"

if echo "$INPUT" | grep -q "diandian.com"; then
    # 点点链接：用正则从 id= 参数提取包名，不访问点点页面
    PACKAGE=$(echo "$INPUT" | grep -oP '(?<=id=)[^&]+' | \
        python3 -c "import sys,urllib.parse; print(urllib.parse.unquote(sys.stdin.read().strip()))")
elif echo "$INPUT" | grep -qP '^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*){1,}$'; then
    # 纯包名
    PACKAGE="$INPUT"
else
    # 本地文件路径，跳过商店信息抓取
    PACKAGE=""
fi

echo "PACKAGE: $PACKAGE"
```

### Step 2：抓取 Google Play 商店信息

Google Play 是公开页面，无需登录，构造 URL：
```
https://play.google.com/store/apps/details?id=<PACKAGE>&hl=en-us&gl=us
```

**优先级 1：`opencli browser`**（JS 完整渲染，推荐）

```bash
SKILL_DIR="$HOME/.claude/skills/android-app-analyzer"
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

GPLAY_MD="$CACHE_DIR/web-articles/google_play.md"
```

**优先级 2：gstack browse**（无头浏览器，opencli 不可用时）

使用 `/browse` skill 导航至 Google Play 页面，提取 Markdown 内容，保存到：
`$CACHE_DIR/web-articles/google_play.md`
（图标 URL 通过 gstack eval 同理获取）

**优先级 3：WebFetch**（最后兜底，Google Play JS 渲染可能拿到残缺内容）

使用 `WebFetch` 工具抓取 Google Play URL，将结果保存到：
`$CACHE_DIR/web-articles/google_play.md`

> ⚠️ 如果 Google Play 页面抓取内容为空或解析失败，自动降级为无商店信息模式，继续输出 APK 分析部分。

### Step 3：解析 Google Play 数据

```bash
SKILL_DIR="$HOME/.claude/skills/android-app-analyzer"
GPLAY_JSON=$(python3 "$SKILL_DIR/fetch_google_play.py" "$GPLAY_MD" "$PACKAGE")
echo "$GPLAY_JSON"
```

从 JSON 读取以下字段：

| 字段 | 说明 |
|---|---|
| `app_name` | 应用名称 |
| `developer` | 开发者 |
| `rating` | 评分 |
| `rating_count` | 评分数量（如 "22.2K reviews"） |
| `downloads` | 下载量（如 "5M+"） |
| `last_update` | 最近更新日期（格式：YYYY-MM-DD） |
| `category` | 分类（中文） |
| `google_play_url` | Google Play 链接 |

图标 URL 通过 Step 2 的 `$ICON_URL` 变量获取（`=s256-rw` 为 256px 正方形）。

### Step 4：APK 静态分析

```bash
SKILL_DIR="$HOME/.claude/skills/android-app-analyzer"
python3 "$SKILL_DIR/android_analyzer.py" "$PACKAGE"

# 找到生成的分析报告
REPORT_MD=$(find "$SKILL_DIR/.cache/android-app-analyzer" \
    -path "*$PACKAGE*" -name "*_analysis.md" 2>/dev/null | head -1)
echo "APK Report: $REPORT_MD"
```

如果 APK 已下载过，加 `--skip-download` 跳过重新下载：

```bash
python3 "$SKILL_DIR/android_analyzer.py" "$PACKAGE" --skip-download
```

### Step 5：生成综合竞品报告

将 Google Play 商店数据 + APK 静态分析合并，输出完整报告，保存到：
`$SKILL_DIR/.cache/$PACKAGE/report.md`

---

## 报告模板

### 完整竞品报告（有商店信息）

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

### 无商店信息模式（本地文件 / 抓取失败降级）

```markdown
# APK 分析：<package_or_filename>

> 分析时间：<当前日期>
> 数据来源：APK 静态分析
> ⚠️ 商店信息不可用

---

（从二开始，结构同上）
```

---

## 本地文件模式（快速启动）

```bash
# 包名分析
python3 android_analyzer.py com.example.app

# 跳过下载（已有缓存）
python3 android_analyzer.py com.example.app --skip-download

# 本地 APK/XAPK
python3 android_analyzer.py path/to/app.apk
python3 android_analyzer.py path/to/app.xapk
```

---

## 输出文件

每个包工作区可能包含：

- `downloads/*.apk` 或 `downloads/*.xapk`
- `extracted/<xapk-name>/...`
- `reports/*_manifest.xml`
- `reports/*_analysis.md`
- `run.json`

---

## 常见问题

| 问题 | 解决方法 |
|---|---|
| `apkeep` 未安装 | 通过 Homebrew、cargo 安装，或从 GitHub Releases 下载二进制 |
| `python` 指向 Python 2 | 明确使用 `python3` |
| 工作区包数量超限 | 手动删除 `.cache/android-app-analyzer/` 下的旧目录 |
| XAPK 无法提取基础 APK | 通常是上游包问题，可尝试手动从 APKCombo 下载并指定本地路径 |
| APK 下载失败 | 手动从 APKCombo 下载，放到 `.cache/android-app-analyzer/<package>/downloads/`，然后用本地路径重新分析 |
| opencli 不可用 | 降级为 gstack browse，再降级为 WebFetch |
| Google Play 解析失败 | 自动降级，仅输出 APK 分析部分（无商店信息） |

---

## 完整执行示例

```
用户: 帮我分析这个竞品
      https://app.diandian.com/app/oy1qiouqq8r5s1n/googleplay?market=11&country=24&id=kjv.bible.kingjamesbible&n=King%2520James%2520Bible

执行流程：
1. 从点点 URL 正则提取包名 → kjv.bible.kingjamesbible（不访问点点页面）
2. 构造 Google Play URL，opencli browser 抓取页面
3. opencli browser eval 获取图标 URL → https://play-lh.googleusercontent.com/...=s256-rw
4. fetch_google_play.py 解析 → 开发者: Ozion, 评分: 4.80, 更新: 2026-04-17
5. android_analyzer.py kjv.bible.kingjamesbible → 生成 APK 报告
6. 合并输出最终竞品报告
```

```
用户: 帮我分析 com.example.biblereader

执行流程：
1. 识别为包名模式
2. 构造 Google Play URL，抓取商店信息
3. android_analyzer.py com.example.biblereader → 生成 APK 报告
4. 合并输出最终竞品报告
```
