# 05 Worktree / 多 Agent

## 1. 前置

- 目标项目必须是 git 仓库。
- 主工作区只做集成/文档/门禁。
- 一个 worktree 一个 agent。
- 一个文件一个 writer。

## 2. Worktree

```bash
git worktree add ../wt-1.0.0-<slice> -b port/1.0.0/<slice>
git worktree add ../wt-1.1.0-<slice> -b port/1.1.0/<slice>
```

规则：

- 分支：`port/1.0.0/<slice>`、`port/1.1.0/<slice>`。
- 合并前 rebase 到 `port/1.0.0` / `port/1.1.0`。
- 合并 `--no-ff`。
- 合并后删 worktree，`git worktree prune`。
- 长任务每天 rebase。
- 冲突 > 30 分钟：停下来抽接口。

## 3. Agent 角色

| 角色 | 写域 |
|---|---|
| `recon-*` | docs/port/handoffs |
| `contract-*` | docs/port/contracts |
| `domain-*` | domain + unit tests |
| `data-*` | data/repository/DTO/fixture |
| `ui-*` | features/UI + widget/golden |
| `platform-*` | SDK adapter/平台通道 |
| `verify-*` | integration/parity/device |
| `integrator` | 合并/门禁/冲突 |

## 4. 并行/串行

| 工作 | 并行？ |
|---|---|
| recon | 是（按模块） |
| 契约 | 是（按 feature；签收串行） |
| 独立 feature | 是 |
| 共享 domain（额度/计费/会话/状态） | 否，一个 owner |
| 独立 SDK adapter | 是 |
| 共享 wiring | 否 |
| 集成/合并/发布 | 否 |

并发建议：2–4 个 writer + 1 个 integrator；不要一次开 10 个。

## 5. 子 Agent Prompt

```text
Role: <role>
Slice: <slice>
Read:
- docs/port/PORT-BRIEF.md
- docs/port/11-scope-1.0.0.md
- docs/port/04-rule-matrix.md
- docs/port/contracts/<contract>.md
Write only:
- <paths>
Do not touch:
- <paths>
Deliver:
- code/tests/docs
Acceptance:
- <gates>
Run:
- <commands>
Handoff:
- docs/port/handoffs/<task>.md
Rules:
- No business logic in UI.
- No SDK/UI-kit imports outside adapters.
- No scope expansion.
- If blocked, stop and write blocker.
```

## 6. Handoff

必须含：

- status
- files changed
- tests/gates + results
- evidence
- open questions/blockers
- risks
- next step

没有 handoff = 未完成。

## 7. 合并顺序

```text
domain → data → features/UI → tests/docs
```

跨 slice 按依赖，不按“谁先写完”。

## 8. 停止条件

- 契约缺失/冲突
- 需要改别人写域
- 服务端语义无法确认
- 测试无法稳定复现
- 需要新 SDK/新依赖
- active/dead 分类错误

停下来写 handoff，不扩大范围。

## 9. 状态更新

每个 slice 完成/阻塞：

- 更新 `state.yaml` 的 `worktrees`/`agents`/`gates`。
- 更新 `docs/port/status.md`。
- 汇报给用户。
