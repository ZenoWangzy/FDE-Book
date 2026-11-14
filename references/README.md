# 参考资料库（references/）

本目录存放编写教材时借鉴的外部资料，都不是本教材的原创内容。教材正文引用其中任何观点、案例、数据或结构，都要按下面的「引用规则」注明出处。

## 1. ChatGPT 资料搜集对话

| 文件 | 内容 |
|---|---|
| `chatgpt-fde-research/conversation.md` | ChatGPT 对话「搜集FDE培训材料」全文（https://chatgpt.com/c/6af6c6c8-4c6c-83e9-92a3-ffceac0e5468），2026-11-13 经 CDP 导出 |
| `chatgpt-fde-research/deep-research-report.md` | 同一对话中 Deep Research 插件生成的报告 |
| `chatgpt-fde-research/sources.md` | 对话和报告引用的全部网页，编号 S001 起（S068–S091 来自报告） |
| `own-vecta/` | 作者本人的 VectA FDE 课件讲稿（作者原创，不属于借鉴资料） |

这是 AI 检索整理的二手资料，只能当线索用。教材不引用这段对话本身，要引用 `sources.md` 里的原始网页，并在引用前打开核对原文。

重新导出：在 Chrome 中打开该对话，用页面内的 `/backend-api/conversation/<id>` 取回 JSON，再运行：

```
python3 tools/chatgpt_to_md.py <conv.json> references/chatgpt-fde-research
```

## 2. 来源网页快照（`web/`）

`sources.md` 里每个网页的本地副本：网页存为 md，PDF 存原文件，索引见 `web/README.md`。2026-11-13 用作者本机的 Chrome 抓取。重新抓取：`node tools/fetch_sources.mjs [S001 ...]`（不带编号时只抓还没有本地文件的来源）。

有 4 个网页没有抓到正文（S011、S049 已抓到公开的课程介绍，课程内容本身要登录 Databricks 才能看）：
- S042：ServiceNow 文档页，等待时间内页面没有加载出来。
- S050：Intuit 招聘页，岗位已下线（"Job Not Found"）。
- S069：OpenAI Playground 链接，要登录，正文不是公开文档。
- S072：ServiceNow 社区附件，抓取失败（见 `web/README.md` 备注）。

## 3. GitHub 仓库（`repos/`）

快照版本见 `repos-manifest.tsv`（仓库地址、commit、日期）。已删除各仓库的 `.git` 目录，内容停留在该 commit。

| 目录 | 作者 | 许可 | 教材可以怎么用 |
|---|---|---|---|
| `xdash__FDE-the-Guidance-Book-of-Forward-Deployed-Engineer` | 范冰（XDash）《前线部署工程师》 | 作者保留著作权；只许免费阅读和非商业分享，必须注明出处与作者；商业用途须事先取得书面许可 | 只可借鉴观点并注明出处，不得大段转载。教材如果商业出版，引用前要取得作者书面许可 |
| `goday-org__FDE-Handbook` | Nicole Li 等 | 正文 CC BY-NC-SA 4.0，代码 MIT | 不得商用；改编内容须用相同许可发布 |
| `global-fde__awesome-fde-resources` | global-fde | 原创内容 CC BY 4.0；`scripts/` 为 Apache-2.0；所链接的项目仍归各自作者 | 注明出处即可使用 |
| `libaice__Awesome-FDE` | awesome-fde contributors | MIT | 注明出处即可使用 |
| `lunar-arun__Forward-Deployed-Engineer` | lunar-arun | MIT（见 README） | 注明出处即可使用 |
| `aifde__fde-practice-cases` | aifde | 仓库里没有 LICENSE 文件 | 默认保留所有权利，只能借鉴观点并注明出处 |

## 引用规则

1. 教材中凡是借鉴的观点、案例、数据、框架或章节结构，都在出现处注明来源，书末列出参考文献。
2. 优先引用原始出处（公司官网、论文、原文章），不引用转述者。只有资料库里的作者自己提出的观点，才引用该资料库。
3. 直接引用原文要加引号；改写也要注明来源。
4. 不使用来源不明的数据。
