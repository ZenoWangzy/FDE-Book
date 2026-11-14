# FDE 教材：企业 AI 智能体落地（12 周）

一本写给大一学生的中文教材，讲 FDE（Forward Deployed Engineer）怎样把 AI 智能体带进客户的日常工作。目标是：没有老师讲，自己看也能学会。

**从这里开始读：[book/00-前言.md](book/00-前言.md)**

## 书里有什么

- 12 章，每周一章。每章五段：先弄明白、看例子、跟着练、自己做、本周实训。
- 每章一张配图、两道例题、两道带提示的练习、四道独立习题。答案在 [book/98-参考答案.md](book/98-参考答案.md)。
- 三个期末任务和评分表：[book/99-表现性任务.md](book/99-表现性任务.md)。
- 术语表、dsh 安装说明、借鉴说明在 `book/` 里。

## 现在的状态

- 文字和配图已完成。
- 每章「本周实训」的操作步骤是按平台资料写的，还没有在课堂环境逐步实测。
- 第 7–12 章的业务数据是课堂合成数据，不是任何真实客户的记录。

## 借鉴与许可

- 书中借鉴的资料集中放在书末：[book/参考文献.md](book/参考文献.md) 和 [book/附录B-借鉴说明.md](book/附录B-借鉴说明.md)。正文里不逐处标注。
- 本书文字和配图采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hans)：可以免费阅读、分享和改编，须署名、不得商用、改编后用相同许可。详见 [LICENSE.md](LICENSE.md)。
- `.claude/skills/textbook*` 是开源的教材写作流程（cabbage2000-lab/textbook-writer-skills，MIT 许可），不属于本书内容。

## 这本书是怎么写的

由一个 AI supervisor 会话带一组 AI 写手和审稿人，按 UbD 逆向设计流程写成，作者把关方向。设计文档见 [book/00-教材设计.md](book/00-教材设计.md)，决定记录见 `docs/adr/`，检查脚本在 `tools/`。

发现错误或看不懂的地方，欢迎提 issue。
