---
name: port-orchestrator
description: 交互式复刻编排 Skill。先通过 question UI 问 3–4 轮（基线支持本地路径、远程 Git URL、APK），绝不先扫描电脑；再分析行为/规则/平台差异，给出可编辑的 1.0.0 / 1.1.0 划分；确认后生成开发规范，用 git worktree + 多 agent 并行/串行完成 1.0.0；完成后等待用户说“开始 1.1.0”，再根据 1.0.0 证据生成计划并继续执行；最终输出需要用户手动填写的 appId/key 清单与填写位置。Use when replicating/porting a codebase to another stack, framework, or version, especially multi-phase 1.0.0/1.1.0 delivery. 触发词：`port start`、`port adopt`、`port resume`、`开始复刻`、`接管已有 1.0.0`、`1.0.0 完整吗`.
version: 1.0.0
user-invocable: true
argument-hint: "[source-project-path] [target-project-path]"
---

# Port Orchestrator

> **STOP：`port start` = 先提问。**
> 不要 `ls`，不要 `find`，不要 `git`，不要“先看看目录”，不要扫描 Desktop/家目录。
> 加载后第一个 tool call 必须是 question；本地路径、远程 Git URL、APK 都可以。

## 0.0 启动协议（`port start` 必须先读）

> **加载本 Skill 后的第一个 tool call 必须是 question/ask 工具。**  
> 在用户回答第一轮之前，禁止运行任何 Shell、文件搜索或 git 命令，包括 `pwd`、`ls`、`find`、`mdfind`、`rg --files`、`git ls-remote`。  
> 不要扫描 `/Users`、`~/Desktop`、`~/Documents`、`~/Downloads`、家目录或 `/`；当前目录为空也不扫描。  
> 基线可以是**本地路径**、**远程 Git URL** 或 **APK/产物**；先问用户，不要从目录名猜。

如果你已经运行了扫描命令，说明违反了启动协议：停止扫描，下一条消息改为提问，不要继续把扫描结果当候选。

唯一例外：用户明确说“扫描某个目录/帮我找”，才只扫描该目录；先说范围，不扩大到父目录/家目录。

## 0. 这个 Skill 做什么

把一个**基线项目**复刻成**目标项目**，并按 1.0.0 / 1.1.0 两阶段交付。

它不是“直接写代码”的 Skill，而是交互式编排：

```text
Intake → Analyze → Scope Split（用户可编辑）→ Standards → G1
→ Build 1.0.0（worktree + 多 agent）→ Verify 1.0.0
→ 等待“开始 1.1.0”
→ 基于 1.0.0 证据生成 1.1.0 计划 → Build 1.1.0 → Verify
→ 手动配置清单
```

核心原则：

> **先契约、后代码；先 1.0.0、后 1.1.0；先分析、后 worktree；未过门禁不合并。**

---

## 1. 交互契约

### 1.1 必须交互的节点

| 节点 | 必须问/确认 |
|---|---|
| Intake | 基线来源（本地/远程/APK）、路径或 URL、版本、目标项目、技术栈、后端、平台、范围 |
| Analyze | 是否允许启动并行 recon；是否已有设计/接口/埋点文档 |
| Scope Split | **必须展示 1.0.0 / 1.1.0 建议表，允许用户增删改，确认后冻结** |
| Standards | 架构/状态/埋点/验证规范是否接受 |
| Build 1.0.0 | 每个 slice 是否继续；高风险 spike 是否通过 |
| 1.1.0 | 必须等用户明确说“开始 1.1.0”或等价指令 |
| Manual Config | 输出填写清单；**不要让用户在聊天里贴密钥** |

### 1.2 提问方式（强制）

**如果宿主有 question/ask 工具，必须用它，不得打印 10 行 Markdown 表格。**  
本环境是 OpenCode 的 `question` 工具；其他宿主用等价的问答/表单工具。

规则：

- **加载后第一个 tool call 必须是 question**；不要先跑 Shell 再问。
- 每轮最多 **4 个问题**；Intake 分 3–4 轮，不要一次甩 10 项。
- 每个问题给 3–5 个选项 + 说明；允许用户自由输入。
- 第一轮只问**基线**：来源（本地/远程/APK）、路径或 URL、版本、交互级别。
- 每轮结束等用户回答，再问下一轮。
- 用户答“不确定/默认”就按默认，并记录。
- 用户首条消息已给全字段时，仍用 question 做一次确认，只问缺失/冲突项，不重复问已知项。
- 只有宿主明确没有 question 工具时，才用编号列表；即使如此也每轮最多 4 项。
- **禁止**用 `ls/find/mdfind/git` 扫描电脑来“发现”基线；只读用户给出的路径/URL。
- 所有回答写进 `docs/port/state.yaml` 和 `docs/port/01-decisions.md`。

推荐的 4 轮：

| 轮次 | 问题 |
|---|---|
| 1 | 基线来源；基线路径或 Git URL；基线版本；交互级别 |
| 2 | 目标目录；目标技术栈/平台；业务关系/后端；1.0.0 目标 |
| 3 | 1.1.0 目标；必须真实接入的基础 SDK；不接的 SDK/UI SDK；已有资产 |
| 4 | 手动配置现状；并发 agent 上限；目标日期 |

**反例**：一上来输出 10 行“基线/目标/业务关系/…”表格，让用户自己填。  
**正例**：第一轮用 question 工具问 4 个问题，用户选完再问下一轮。

### 1.3 状态文件

每个项目必须有：

```text
docs/port/state.yaml
```

记录：phase、gates、scope、decisions、worktrees、agents、manual_config。

**每次继续对话先读它。** 用户说“继续”“status”“开始 1.1.0”都从它恢复。

模板：`templates/state.yaml`。

**没有 state.yaml 的已有项目**：先 `port adopt` 接管/回填，不要直接 `status` 或假装已完成。

### 1.4 禁止

- `port start` 第一动作不是提问，而是先扫描电脑/家目录/桌面。
- G1 前写业务代码。
- 用户未确认 1.0.0/1.1.0 划分就开工。
- 未经确认启动 1.1.0。
- 在聊天/仓库里收集真实密钥。
- 两个 agent 改同一文件。
- 未过门禁合并。

### 1.5 交互级别

默认 `guided`：

| 模式 | 行为 |
|---|---|
| `guided`（默认） | 在 Intake、Scope 确认、Standards、G1、1.0.0 完成、1.1.0 启动这些节点停下 |
| `step` | 每个 phase / slice 完成都停下汇报 |
| `auto` | Scope/Standards 确认后连续执行，只在 blocker、门禁失败、1.1.0 启动时停 |

用户可以说“用 step 模式”或“auto 模式”。  
无论哪种模式：**1.0.0 完成必须停；1.1.0 必须等用户明确说“开始 1.1.0”。**

---

## 2. 命令 / 模式

用户可直接说，也可用命令式短语：

| 指令 | 行为 |
|---|---|
| `port start` / “开始复刻” | Intake + 分析 |
| `port analyze` | 只做 recon/分析 |
| `port adopt` / “接管已有 1.0.0” | 扫描已有项目，回填 state/evidence；gates 标 claimed/verified |
| `port audit` | 跑构建/测试/lint/config 检查，更新 evidence（不替代业务验收） |
| `port completeness` / “1.0.0 完整吗” | 对照基线生成完整性矩阵：verified/implemented/missing/unknown |
| `port plan` | 生成/修改 1.0.0/1.1.0 划分 |
| `port standards` | 生成开发规范 |
| `port build 1.0.0` | 执行 1.0.0 |
| `port status` | 汇报 phase/gates/worktrees/next；无 state 时提示先 adopt |
| `port config` | 输出/更新手动配置清单 |
| `开始 1.1.0` | 进入 1.1.0（前提：1.0.0 过 G5） |
| `port build 1.1.0` | 执行 1.1.0 |
| `port resume` | 从 state 继续当前 phase |

---

## 3. Phase 0：Intake

### 3.1 启动协议：先问，后看

**`port start` 加载后第一个 tool call 必须是 question。**  
在用户回答第一轮之前，禁止运行任何 Shell、文件搜索或 git 命令；不要用 `pwd/ls/find/mdfind/rg --files/git ls-remote` 去找基线。

#### 第 1 轮（4 题，必须用 question 工具）

1. **基线来源**
   - 本地仓库（已有源码）
   - 远程 Git 仓库（URL）
   - 仅 APK/AAB/产物
   - 不确定（我描述产品，你帮我判断）
2. **基线位置**
   - 当前目录
   - 稍后提供
   - 自由输入：本地路径或 Git URL
3. **基线版本**
   - 默认分支
   - 最新 tag
   - 指定 tag / commit / 分支
   - 不确定，先看默认分支
4. **交互级别**
   - `guided`（默认）
   - `step`
   - `auto`

选“不确定”时：让用户用一句话描述产品/给 URL/给大致路径；**仍然不要扫描磁盘**。

示例（OpenCode）：

```text
question({
  questions: [
    { header: "基线来源", question: "这次复刻的基线是什么？", options: [
      { label: "本地仓库", description: "已有源码，下一步填路径" },
      { label: "远程 Git 仓库", description: "下一步填 URL 和分支/tag" },
      { label: "仅 APK/产物", description: "只能做黑盒/资源级分析" },
      { label: "不确定", description: "先描述产品，我帮你判断" }
    ]},
    { header: "基线位置", question: "本地路径或 Git URL 是什么？", options: [
      { label: "当前目录", description: "使用当前工作目录" },
      { label: "稍后提供", description: "先继续，之后再补" }
    ]},
    { header: "基线版本", question: "锁定哪个版本？", options: [
      { label: "默认分支", description: "跟随当前默认分支" },
      { label: "最新 tag", description: "取最新发布版本" },
      { label: "指定 tag/commit", description: "在自由输入里填写" }
    ]},
    { header: "交互级别", question: "希望我在哪里停下来？", options: [
      { label: "guided（默认）", description: "关键节点停" },
      { label: "step", description: "每个 slice 停" },
      { label: "auto", description: "只在 blocker/门禁失败停" }
    ]}
  ]
})
```

#### 第 2 轮（目标，4 题）

5. **目标目录**：当前目录 / 指定路径（自由输入）。
6. **目标技术栈/平台**：Flutter（Android）/ Flutter（iOS）/ Android Kotlin / React Native / 其他。
7. **业务关系/后端**：同一后端新客户端 / 同一产品重写 / 新品牌独立后端 / 不确定。
8. **1.0.0 目标**：核心闭环可运行 / 可发布 / 内测。

#### 第 3 轮（范围，4 题）

9. **1.1.0 目标**：全量 parity / 增量 SDK 接入 / 新功能 / 不确定。
10. **必须真实接入的基础 SDK**：按基线分析后列出；现在可先选“按基线自动确定”。
11. **UI SDK 边界**：所有 UI SDK 不接、UI 自绘（推荐）/ 允许指定 UI SDK / 我指定。
12. **已有资产**（多选）：设计稿 / 接口文档 / 埋点文档 / 测试账号 / 历史 bug / 无。

#### 第 4 轮（交付，3 题）

13. **手动配置现状**：全部缺失 / 部分有 / 完整 / 不确定。
14. **并发 agent 上限**：2–4 / 5–8 / 其他。
15. **目标日期**：无硬 deadline / 指定日期。

#### 用户回答后怎么取源

- **本地仓库**：只读用户给的路径，执行 `ls`、`git -C <path> status`、`git -C <path> log -1`、`git -C <path> rev-parse HEAD`。不要扫描父目录或家目录。
- **远程 Git**：验证 URL（`https://`、`ssh://`、`git@`、`file://`），默认 clone 到 `./.port/source`；已存在且非空时先问，不要 `rm -rf`。用现有 SSH/credential helper；私有仓库拉取失败就让用户给本地路径，**不要在聊天里要 token**。
- **APK/产物**：`file`、`unzip -l`、`apkanalyzer`（若有）；明确只能做黑盒/资源级分析，不能假装有源码 parity。
- **记录**：`source.type`、`source.location`、`source.url`、`source.version`、`source.commit`、`source.cloned_to` 写入 `state.yaml`；目标 git init 时把 `.port/` 加进 `.gitignore`。

### 3.2 产出

```text
docs/port/
  00-intake.md
  PORT-BRIEF.md
  state.yaml
  01-decisions.md
```

`PORT-BRIEF.md` 写清：

- 基线/目标/版本/后端
- 1.0.0 包含/不包含
- 1.1.0 包含
- 核心闭环、高风险能力
- 明确“冻结基线、不追新版本”

**G0**：上述信息有书面记录；没有“待定”的核心范围。

### 3.3 已有 1.0.0 接管（port adopt）

如果用户已经自己做了一个 1.0.0，不需要从头重跑；先接管。

**最小输入**（不要要求用户填长模板）：

```text
port adopt
基线：/path/to/source 或 git URL（可选）
目标：默认当前目录；不在当前目录才给 /path/to/target
```

1. **只读扫描目标项目**（用户给的路径）：README/docs/tags/package/build/CI/tests/config/TODO/git。不要扫描电脑/家目录/桌面。
2. 自动推断：技术栈、版本、as-built 范围、已实现入口、测试/构建/配置现状、1.1.0 候选。
3. **只问 3 个无法推断的问题**：
   - 推断出的 1.0.0 范围对不对？
   - 哪些是你**真机/发布验证过**的（不是“代码写了”）？
   - 1.1.0 目标是什么（或按基线自动推断）？
4. 产出：
   - `docs/port/state.yaml`（`adopted: true`，phase `ADOPTED_1_0`）
   - `docs/port/adopt/00-as-built.md`
   - `docs/port/adopt/01-evidence.md`
   - `docs/port/adopt/02-gaps.md`
   - `docs/port/adopt/03-1.1.0-plan.md`
   - `docs/port/adopt/04-completeness.md`（完整性矩阵）
   - `docs/port/manual-config.md`
5. 完整性矩阵状态：
   - `verified`：有测试/真机/差分证据。
   - `implemented`：代码存在，未验证。
   - `missing`：基线有，目标没有。
   - `unknown`：无法判断（缺基线/缺证据/缺入口）。
   - `not-in-scope`：明确不在 1.0.0。
   - **不允许把 unknown 写成 verified。**
6. Gate 语义：
   - `claimed`：用户说做了，代码/文档有迹象；**未验证**。
   - `verified`：有构建/测试/真机/差分证据。
   - `partial`：部分完成/部分验证。
   - 不要把 adopted 的 G4/G5 直接写 `passed`。
7. 然后 `port audit` / `port completeness` 跑可自动检查的部分；业务正确性仍需人工/差分验收。
8. 用户确认后，`port status` / `port plan 1.1.0` 才可靠。

> 不要一上来让用户写“1.0.0 已做/已验证/已知缺口”长模板。先只读扫描**目标项目**，再让用户纠正；不要扫描磁盘找项目。

详细：`references/08-adopt-existing-1.0.0.md`。

---

## 4. Phase 1：Analyze

### 4.1 并行 recon

按源工程类型/模块拆：

| Agent | 范围 |
|---|---|
| `recon-shell` | 入口、导航、DI、主题、构建、权限、深链、推送、后台 |
| `recon-feature-*` | 每个 feature：页面、状态、use case、API、存储、埋点、文案 |
| `recon-data` | API/proto、DTO、错误码、存储 key、迁移、缓存 |
| `recon-platform` | SDK、原生通道、FCM/推送、支付、IM/通话、图片、定位 |
| `recon-risk` | 历史 bug、平台限制、审核约束、已知坑 |

规则：

- 按模块/目录切，不按“业务 vs 基建”切。
- 每个 agent 只写自己的 handoff。
- 先分类 **active / active-native / dead**；dead 不进入契约。

### 4.2 产出

```text
docs/port/
  02-source-surface-map.md
  03-behavior-inventory.md
  04-rule-matrix.md
  05-state-machines.md
  06-api-contract.md
  07-copy-deck.md
  08-analytics-contract.md
  09-platform-capabilities.md
  10-risk-register.md
  analysis-report.md
  handoffs/recon-*.md
```

### 4.3 分析报告必须回答

1. 源项目真实形态（active/dead/native）。
2. 业务动作有哪些？每个动作几个入口？
3. 每个动作的规则/状态/额度/计费/持久化。
4. 服务端语义（limit、matched、isFree、leftFreeMsgCount、entitlement）。
5. 平台差异（源 vs 目标）。
6. 埋点/文案/一次性卡片。
7. 哪些规则源项目本身有 bug/不一致（不要盲目复刻）。
8. 1.0.0/1.1.0 的候选划分与风险。

**G1**：核心 flow 有 behavior contract + rule matrix + state machine；API/copy/analytics 有清单；历史 bug 已转回归用例。

---

## 5. Phase 2：Scope Split（用户可编辑）

### 5.1 推荐划分

必须给表格，不是散文：

```text
| 能力 | 1.0.0 | 1.1.0 | 理由 | 风险 |
```

划分原则：

1. 1.0.0 = 可运行的核心闭环 + 必须真实接入的核心 SDK。
2. 1.1.0 = 增量能力 + 增长/观测/风控 SDK + 完整 parity。
3. 不在 1.0.0 做“半成品，1.1.0 重写”的功能。
4. UI SDK 不进生产；只允许基础 SDK + 自绘 UI（除非用户明确同意）。
5. 核心计费/额度/免费权益必须在 1.0.0，不能留到 1.1.0。
6. 每个 deferred 项必须有 owner/风险/依赖。

### 5.2 交互

展示表格后问：

```text
请直接修改/删除/补充 1.0.0 或 1.1.0 的条目；
回复“确认”后冻结，后续变更走 ADR。
```

用户确认后：

- 写 `docs/port/11-scope-1.0.0.md`
- 写 `docs/port/12-scope-1.1.0.md`
- 更新 `state.yaml` 的 `scope`
- 写 ADR

---

## 6. Phase 3：Standards

生成：

```text
docs/port/
  13-architecture.md
  14-state-ownership.md
  15-analytics-contract.md
  16-validation-gates.md
  17-worktree-plan.md
  18-subagent-plan.md
  standards.md
```

规范必须包含：

- 分层/依赖规则
- 一个动作一个 service
- 状态所有权/reset
- 业务逻辑不进 UI
- 埋点契约/生成/对账
- 文案契约
- SDK 边界（基础 SDK / UI SDK）
- 测试/门禁
- worktree/agent 规则
- 手动配置规则

**G2**：规范落盘；用户确认；骨架/工具链可执行。

---

## 7. Phase 4：Build 1.0.0

### 7.1 Worktree

```bash
git worktree add ../wt-1.0.0-<slice> -b port/1.0.0/<slice>
```

规则：

- 主工作区只做集成/文档。
- 一个 slice 一个 worktree。
- 一个文件一个 writer。
- 合并前 rebase 到 `port/1.0.0`。
- 合并 `--no-ff`；合并后删 worktree。

### 7.2 Agent 角色

| 角色 | 写域 |
|---|---|
| `contract-*` | docs/port |
| `domain-*` | domain 层 + 单测 |
| `data-*` | repository/DTO/fixture |
| `ui-*` | feature UI |
| `platform-*` | SDK adapter/平台通道 |
| `verify-*` | 集成/差分/golden |
| `integrator` | 合并/门禁/冲突 |

### 7.3 并行/串行

- 并行：独立 feature、独立 recon、独立 SDK adapter。
- 串行：共享 domain、集成、合并、发布。
- 同一文件永远只有一个 writer。
- 冲突 > 30 分钟：停下来抽接口，不硬解。

### 7.4 每个 slice

```text
契约 → domain/状态机 → 单测
→ data/fixture → 契约测试
→ UI → widget/golden
→ 集成 → 差分 → G3
```

**G3**：规则/状态/跨入口/契约/widget/golden/集成通过；无核心 TODO。

### 7.5 高风险 spike 先行

- 通话/实时音视频
- 支付/验单/恢复/重复回调
- Push 冷启动/杀进程
- IM 自定义消息
- 平台通道/浮窗/深链
- 图片方向/裁剪

spike 不通过，不进入对应 slice。

---

## 8. Phase 5：Verify 1.0.0

产出：

```text
docs/port/1.0.0/
  parity-report.md
  ports-inventory.md
  deferred.md
  coverage.md
  bug-root-causes.md
  device-matrix.md
  manual-config.md
```

**G4**：1.0.0 功能完整。
**G5**：差分/golden/E2E/设备/支付/通话/埋点通过；已知偏差签字。

完成后：

- 汇报 1.0.0 状态。
- 输出手动配置清单。
- **停止，等待用户说“开始 1.1.0”。**

---

## 9. Phase 6：1.1.0（用户触发）

用户说“开始 1.1.0”后：

1. 读 `state.yaml` + `1.0.0/` 证据。
2. 生成：

```text
docs/port/1.1.0/
  00-plan.md
  SKILL.md
  sdk-matrix.md
  adapter-contracts.md
  e2e-matrix.md
  rollout.md
```

3. 从 `ports-inventory.md` / `deferred.md` / `risk-register.md` / `coverage.md` / `bug-root-causes.md` 生成任务。
4. 重复 Phase 4/5 的 worktree/agent/gate 流程。
5. **G7**：1.1.0 功能完整。
6. **G8**：发布/上架/回滚/手动配置完成。

1.1.0 不是“只接 SDK”：如果 1.0.0 deferred 了业务能力，1.1.0 要按垂直切片补齐。

---

## 10. 手动配置

最终必须输出：

```text
docs/port/manual-config.md
```

每条包含：

| 字段 | 内容 |
|---|---|
| Key | 环境变量/配置名 |
| 用途 | 支付/推送/IM/埋点/崩溃/归因 |
| 填写位置 | 精确文件/控制台页面 |
| 格式 | 字符串/JSON/文件 |
| 何时需要 | 1.0.0 / 1.1.0 |
| 当前状态 | missing / placeholder / filled |
| 验证方式 | 启动/构建/真机 |

规则：

- 不让用户在聊天里贴真实密钥。
- 仓库只放 `.env.example` / 占位符。
- `.env`、`local.properties`、keystore、`google-services.json` 等按项目规则 gitignore。
- CI 用 secret manager。
- key 缺失时功能降级或 fail-fast，不能静默。
- 用户填写后，运行配置检查 + 真机验证。

---

## 11. 硬规则

1. 先分析，后写代码。
2. 先 1.0.0，后 1.1.0。
3. 用户确认 scope 后才开工。
4. 一个动作一个 service。
5. UI 不写业务规则。
6. 不接 UI SDK（除非用户明确同意）。
7. 不搬死代码。
8. 不猜服务端语义。
9. 一个文件一个 writer。
10. 未过门禁不合并。
11. 不收集真实密钥。
12. 不把“测试通过”当“业务正确”。
13. 接管已有 1.0.0 时，`claimed` 不等于 `verified`；没有证据不得写 `passed`。

---

## 12. 参考

- 交互模板：`references/01-interaction.md`
- 分析模板：`references/02-analysis.md`
- 范围划分：`references/03-scope-split.md`
- 开发规范：`references/04-standards.md`
- Worktree/Agent：`references/05-worktree-agents.md`
- 手动配置：`references/06-manual-config.md`
- 1.1.0：`references/07-1.1.0.md`
- 接管已有 1.0.0：`references/08-adopt-existing-1.0.0.md`
- 完整性矩阵：`templates/completeness-report.md`
- 状态模板：`templates/state.yaml`
- Scope 模板：`templates/scope-split.md`
- Handoff 模板：`templates/agent-handoff.md`
- 配置模板：`templates/manual-config.md`

---

## 13. 快速开始

用户说“开始复刻/port start”时：

1. 读本 Skill。
2. **第一个动作：用 question 工具问第 1 轮 4 题**（基线来源/路径或 URL/版本、交互级别）；不要先扫描电脑。
3. 用户回答后，只读给定路径或 clone 给定 Git URL；再问第 2–4 轮。
4. 创建 `docs/port/state.yaml`、`PORT-BRIEF.md`。
5. 启动并行 recon。
6. 产出分析报告。
7. 展示 1.0.0/1.1.0 建议表，等待用户编辑/确认。
8. 生成规范；过 G2。
9. 建 worktree、派 agent、执行 1.0.0。
10. 过 G4/G5；输出手动配置；停止。
11. 用户说“开始 1.1.0”后继续。
