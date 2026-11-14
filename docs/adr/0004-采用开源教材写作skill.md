# ADR-0004 采用开源教材写作 skill：textbook-writer-skills

日期：2026-11-13　状态：已定（作者要求「不要自己创新，用前人的智慧」）

## 决定

教材的写作流程改用开源的 [cabbage2000-lab/textbook-writer-skills](https://github.com/cabbage2000-lab/textbook-writer-skills)（MIT 许可，v0.7.0，commit e2b8250），不再自己设计流程。

- 5 个 skill 已装进项目的 `.claude/skills/`：`textbook`、`textbook-outline`、`textbook-chapter`、`textbook-exercises`、`textbook-init`。
- 流程分五个阶段：
  1. 教学定位确认；
  2. UbD 五件套，作者确认后才能往下走（第一道 gate）；
  3. 章节树和评估设计，作者确认后才能往下走（第二道 gate）；
  4. 逐章写正文和习题；
  5. 审核定稿。
- 教材项目目录用 `book/`，里面的文件布局按这套 skill 的规定（`00-教材设计.md`、`NN-章.md`、`98-参考答案.md`、`99-表现性任务.md`、`术语表.md`、`.progress.json`）。
- 已经起草的 `docs/目录.md`（12 周目录草案）和 ADR-0001～0003 不作废，作为阶段 1–3 的输入素材。

## 为什么选这一套

在 GitHub 上搜「教材写作」「instructional design」「textbook」类 skill，比较了以下几套：

| 仓库 | 星标 | 许可 | 结论 |
|---|---|---|---|
| cabbage2000-lab/textbook-writer-skills | 47 | MIT | 采用：中文；方法是成熟的 UbD 逆向设计和 Bloom 认知层级；关键决策要经作者确认；验证不了的内容一律标注「需作者确认」；进度可以中断续写；三份学科档案中有人文社科和经济学 |
| savvides/idstack | 28 | MIT | 一起用（作者 2026-11-13 要求把相关 skill 结合起来）：作为项目级插件安装，在两道 gate 和定稿时做检查，见 `docs/写作流程.md` |
| dmccreary/ibook-skills（原名 claude-skills） | 111 | 未声明 | 不采用：面向 MkDocs 英文「智能教材」，许可证没有声明 |
| hcming2026/textbook-writing-skills、International-tax/…Writing-Skill 等 | 0–2 | 未声明 | 不采用：人用得太少，许可证也没有声明 |

textbook-writer-skills 和 ibook-skills 快照在 `references/skills/`，idstack 的源码在 `tools/plugins/idstack/`，版本都记在 `references/skills-manifest.tsv`。

## 影响

- 问题单 05（12 周目录草案）改为「按 textbook skill 跑阶段 1–3」；问题单 07（考核与评分方案）并入阶段 3 的评估设计；问题单 06（样章）改为阶段 4 的第一章。
- 这套 skill 不单独产出「实训指导书」。实训内容放在哪里（章内一节，还是单独成文件），在阶段 1–3 里和作者确认。
- 引用规则仍按 `references/README.md`：skill 要求核对来源，和本书的引用要求一致。
