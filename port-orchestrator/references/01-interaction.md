# 01 交互模板

## 1.0 启动协议（不可跳过）

- **加载 Skill 后第一个 tool call 必须是 question/ask 工具。**
- 在用户回答第一轮前，不运行 `pwd/ls/find/mdfind/rg --files/git ls-remote`。
- 不扫描 `/Users`、桌面、文档、下载、家目录或 `/`；当前目录为空也不扫描。
- 基线支持：本地路径、远程 Git URL、APK/产物。**先问，不要从目录名猜。**
- 第一轮 4 题；每轮最多 4 题；Intake 共 3–4 轮。

## 1. 第 1 轮（4 题）

1. **基线来源**：本地仓库 / 远程 Git 仓库 / 仅 APK/产物 / 不确定。
2. **基线位置**：当前目录 / 稍后提供 / 自由输入本地路径或 Git URL。
3. **基线版本**：默认分支 / 最新 tag / 指定 tag/commit/分支 / 不确定。
4. **交互级别**：`guided`（默认）/ `step` / `auto`。

示例：

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

### 第 1 轮回答后取源

- **本地**：只读给定路径；`ls`、`git -C <path> status`、`git -C <path> log -1`、`git -C <path> rev-parse HEAD`。不扫描父目录。
- **远程**：验证 `https://` / `ssh://` / `git@` / `file://`；默认 clone 到 `./.port/source`；已存在且非空先问，不 `rm -rf`；私有仓库用现有 SSH/credential helper，不要在聊天里要 token。
- **APK**：`file`、`unzip -l`、`apkanalyzer`（若有）；明确只能做黑盒/资源级分析。
- 记录 `source.type/location/url/version/commit/cloned_to`；目标 `git init` 时把 `.port/` 加进 `.gitignore`。

## 1.1 第 2–4 轮

### 第 2 轮（目标）

5. 目标目录：当前目录 / 指定路径。
6. 目标技术栈/平台：Flutter Android / Flutter iOS / Android Kotlin / React Native / 其他。
7. 业务关系/后端：同一后端新客户端 / 同一产品重写 / 新品牌独立后端 / 不确定。
8. 1.0.0 目标：核心闭环 / 可发布 / 内测。

### 第 3 轮（范围）

9. 1.1.0 目标：全量 parity / 增量 SDK / 新功能 / 不确定。
10. 必须真实接入的基础 SDK：按基线分析后列出；可先选“按基线自动确定”。
11. UI SDK 边界：所有 UI SDK 不接、UI 自绘（推荐）/ 允许指定 / 我指定。
12. 已有资产（多选）：设计稿 / 接口文档 / 埋点文档 / 测试账号 / 历史 bug / 无。

### 第 4 轮（交付）

13. 手动配置现状：全部缺失 / 部分有 / 完整 / 不确定。
14. 并发 agent 上限：2–4 / 5–8 / 其他。
15. 目标日期：无硬 deadline / 指定日期。

### 文本框备用

只有宿主没有 question 工具时，才用编号列表；每轮最多 4 项，不要一次给 10 项。

## 1.2 接管已有 1.0.0 的最小输入

```text
port adopt
基线：/path/to/source 或 git URL（可选）
目标：默认当前目录
```

不要要求用户填 8 项。**只读扫描目标项目**（不扫描电脑），再只问：

1. 推断的 1.0.0 范围对不对？
2. 哪些是真机/发布验证过的？
3. 1.1.0 目标是什么？

## 2. Scope 确认

```text
下面是建议的 1.0.0 / 1.1.0 划分：

<表格>

请直接修改/删除/补充条目；
回复“确认”后冻结，后续变更走 ADR。
```

## 3. 状态汇报

```text
## Port Status
- Phase:
- Gates: G0 / G1 / G2 / G3 / G4 / G5
- Completeness: verified / implemented / missing / unknown
- 1.0.0 slices: done / in-progress / blocked
- Worktrees:
- Open questions:
- Next:
```

## 4. 1.0.0 完成

```text
1.0.0 已完成并通过 G4/G5。
- 证据：docs/port/1.0.0/...
- 未完成/延后：...
- 手动配置：docs/port/manual-config.md
下一步：等你说“开始 1.1.0”。
```

## 5. 1.1.0 启动

```text
收到“开始 1.1.0”。
我会先读 1.0.0 的 ports/deferred/parity/risk，
生成 1.1.0 计划和 worktree/agent 分配，
再开始执行。
```

## 6. 手动配置

```text
以下需要你手动填写（不要在聊天里贴真实值）：
| Key | 填写位置 | 用途 | 状态 |
...
填完后告诉我“配置完成”，我会跑 config check + 真机验证。
```

## 7. 用户修改 scope

- 记录到 `state.yaml` 的 `scope`。
- 变更写 ADR：改了什么、为什么、影响哪个 gate/工期。
- 如果影响已开始的 slice，停下来重新评估，不静默继续。

## 8. 用户说“继续”

- 先读 `state.yaml`。
- 找当前 phase / gate / blocked 项。
- 汇报下一步，然后继续。
- 不从头重复分析。
