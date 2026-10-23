# Port Orchestrator Skill

交互式复刻编排 Skill：把一个基线项目复刻成目标项目，按 1.0.0 / 1.1.0 两阶段交付。

## 它能做什么

1. **Intake**：问清基线项目、目标项目、版本、技术栈、后端、平台、范围。
2. **Analyze**：并行 recon，产出 active/dead/native 映射、规则矩阵、状态机、API/copy/analytics/platform 清单。
3. **Scope Split**：给出 **可编辑的 1.0.0 / 1.1.0 划分**，用户确认后冻结。
4. **Standards**：生成架构、状态所有权、埋点、测试、worktree/agent 规范。
5. **Build 1.0.0**：git worktree + 多 agent 并行/串行，按切片实现并过门禁。
6. **Wait 1.1.0**：1.0.0 完成后停止；用户说“开始 1.1.0”再继续。
7. **Manual Config**：输出 appId/key/证书的填写位置与验证方式，不在聊天里收集真实密钥。

## 安装

### 项目级

```bash
mkdir -p .opencode/skills
cp -R port-orchestrator .opencode/skills/
```

### 全局（OpenCode）

```bash
mkdir -p ~/.config/opencode/skills
cp -R port-orchestrator ~/.config/opencode/skills/
```

## 使用

默认是 `guided` 模式：在 Intake、Scope 确认、Standards、G1、1.0.0 完成、1.1.0 启动这些节点停下。  
需要更细就加“用 step 模式”；需要更自动就加“用 auto 模式”。

Intake 默认用宿主 question/ask 工具分 3–4 轮问（每轮 3–4 题），不是打印 10 行表格；用户可点选，也可自由输入。

**`port start` 的第一动作是提问，不是扫描电脑。** 基线支持本地路径、远程 Git URL、APK/产物；只读用户给出的位置，不扫描桌面/家目录/下载。

最小输入：

```text
用 port-orchestrator skill，port start。
```

然后按 question UI 回答即可。也可以一次给全：

```text
用 port-orchestrator skill，port start。
基线：/path/to/source 或 https://github.com/org/repo.git
基线版本：v1.0.5 @ 9a327821
目标：/path/to/target
目标栈：Flutter / Android
1.0.0：核心闭环可运行
1.1.0：全量 parity
```

常用指令：

| 指令 | 行为 |
|---|---|
| `port start` | 开始 Intake（第一动作是 question，不扫描电脑） |
| `port analyze` | 只做分析 |
| `port adopt` | 接管已有 1.0.0，只读扫描目标项目并回填 state/evidence |
| `port audit` | 跑构建/测试/lint/config 检查 |
| `port completeness` | 对照基线生成 1.0.0 完整性矩阵 |
| `port plan` | 生成/修改 1.0.0/1.1.0 划分 |
| `port standards` | 生成开发规范 |
| `port build 1.0.0` | 执行 1.0.0 |
| `port status` | 查看 phase/gates/worktrees；无 state 时提示先 adopt |
| `port config` | 输出手动配置清单 |
| `开始 1.1.0` | 1.0.0 过 G5 后继续 |
| `port resume` | 从 state.yaml 继续 |

> 已有 1.0.0 但没有 `docs/port/state.yaml`：先 `port adopt`，不要直接 `port status`。  
> 最小输入：`port adopt` + 基线路径或 Git URL（可选），目标默认当前目录；只读扫描目标项目，只问 3 个问题，不扫描电脑。

## 文件结构

```text
port-orchestrator/
├── SKILL.md
├── README.md
├── references/
│   ├── 01-interaction.md
│   ├── 02-analysis.md
│   ├── 03-scope-split.md
│   ├── 04-standards.md
│   ├── 05-worktree-agents.md
│   ├── 06-manual-config.md
│   ├── 07-1.1.0.md
│   └── 08-adopt-existing-1.0.0.md
└── templates/
    ├── state.yaml
    ├── scope-split.md
    ├── agent-handoff.md
    ├── manual-config.md
    └── completeness-report.md
```

## 要求

- 目标项目最好是 git 仓库（worktree 需要）。
- 支持 OpenCode skill 的宿主。
- 需要能创建/合并 git worktree。
- 真实密钥不要写进仓库/聊天；用 `.env.example`、CI secret、服务端签发。

## 注意

- G1 前不写业务代码。
- 1.0.0 未过 G5 不进入 1.1.0。
- 默认只接基础 SDK，不接 UI SDK。
- 不机械套用上一个项目的跨入口不变量；必须从基线项目重新推导。
