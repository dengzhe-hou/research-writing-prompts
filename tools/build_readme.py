"""Copy the primary prompts of every scenario from CATALOG.md into README.md and README_EN.md.

Run after editing a primary prompt in CATALOG.md:

    python tools/build_readme.py

It rewrites only the text between <!-- prompts:start --> and <!-- prompts:end -->.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (scenario id, Chinese summary, English summary). Groups follow CATALOG.md.
GROUPS = [
    ('翻译', 'Translation', [
        ('1.1', '中译英：贴中文草稿，得到能放进 LaTeX 的英文段落，附中文回译供核对',
                'Chinese → English: paste a Chinese draft, get a LaTeX-ready English paragraph plus a Chinese back-translation'),
    ]),
    ('润色', 'Polishing', [
        ('2.1', '英文润色：贴英文 LaTeX，得到润色稿、中文直译和修改日志',
                'English polish: paste English LaTeX, get the polished text plus a Chinese translation and a Chinese change log'),
        ('2.2', '中文润色：贴中文段落，只改该改的地方，原文没问题就原样返回；草稿还很零散的，用完整目录里的替代那条',
                'Chinese polish: paste a Chinese paragraph; it only fixes real problems and returns good text unchanged (for rough notes, use the alternative in the full catalog)'),
        ('2.3', '英文去 AI 味：贴英文 LaTeX，换掉 delve、leverage 这类词；本来自然的段落原样通过',
                'De-AI English: paste English LaTeX; replaces words like delve and leverage, leaves natural text alone (adds a Chinese translation and change log)'),
        ('2.4', '中文去 AI 味：贴中文段落，去掉空话大词和翻译腔，附修改日志',
                'De-AI Chinese: paste Chinese text; removes empty buzzwords and translationese, with a change log'),
    ]),
    ('缩写、扩写、逻辑检查', 'Shorten, expand, check logic', [
        ('3.1', '缩写：贴英文 LaTeX，只删 5 到 15 个词，参数一个不丢',
                'Shorten: paste English LaTeX; removes only 5 to 15 words and keeps every parameter (adds a Chinese translation and change log)'),
        ('3.2', '扩写：贴英文 LaTeX，只加 5 到 15 个词，把隐含的因果写明',
                'Expand: paste English LaTeX; adds only 5 to 15 words that spell out implied reasoning (adds a Chinese translation and change log)'),
        ('3.3', '逻辑检查：贴英文 LaTeX，只报致命问题；没问题就回“检测通过”',
                'Logic check: paste English LaTeX; reports only serious problems, otherwise says it passed (replies in Chinese)'),
    ]),
    ('论文各部分', 'Paper sections', [
        ('4.1', '选题：填研究领域，得到研究题目、文献空白、研究问题或新应用（四条任选）',
                'Brainstorming: fill in a field; get topics, literature gaps, research questions or new applications (pick one of four)'),
        ('4.2', '摘要：贴论文要点，得到一段摘要',
                'Abstract: paste the key content, get an abstract'),
        ('4.3', '文献综述：填主题或贴文字，得到综述、总结或两个理论的对比（模型给的文献要逐条核实）',
                'Literature review: give a topic or text; get a review, a summary or a comparison of two theories (check every reference)'),
        ('4.4', '方法：填研究主题得到方法草稿，或贴方法段落得到优缺点分析',
                'Methodology: give a topic for a draft method, or paste a method to get its strengths and weaknesses'),
        ('4.5', '结果与讨论：贴结果，得到第三人称的 Results 段落或一段讨论',
                'Results and discussion: paste results, get a third-person Results paragraph or a discussion'),
        ('4.6', '结论：贴正文或摘要，得到结论（可附建议）',
                'Conclusion: paste the paper or abstract, get a conclusion (optionally with recommendations)'),
        ('4.7', '未来工作：贴研究概要，得到 3 个未来研究方向',
                'Future work: paste a summary of the study, get 3 directions for future research'),
        ('4.8', '标题：贴摘要或主要贡献，填目标期刊，得到 3 到 5 个标题候选和各自的理由',
                'Title: paste the abstract or key contributions and name the venue; get 3 to 5 title options, each with a short rationale (rationales in Chinese)'),
        ('4.9', '相关工作：贴方法概要和读过的文献清单（cite key 加一句备注），得到按主题分组、写明本文区别的 Related Work，只引用你给的文献',
                'Related work: paste your method summary and the papers you have read (cite key plus a one-line note), get a Related Work section grouped by theme that states how your paper differs, citing only your list'),
    ]),
    ('实验与图表', 'Experiments and figures', [
        ('5.1', '实验分析：贴实验数据表，得到 LaTeX 分析段落和中文直译，不许编数据',
                'Experiment analysis: paste a results table, get LaTeX analysis paragraphs plus a Chinese translation, no invented numbers'),
        ('5.2', '绘图推荐：贴数据表和想强调的结论，得到 1 到 2 种推荐图表和画法规范',
                'Figure choice: paste the data and the point to make, get 1 or 2 chart types with drawing guidelines (replies in Chinese)'),
        ('5.3', '图标题：写一句中文图片描述，得到规范的英文图标题（按 LaTeX 转义 % _ &，用 Word 的删掉 prompt 里转义那一行）',
                'Figure caption: write a Chinese description, get an English caption (LaTeX-escaped; for Word, delete the escaping line)'),
        ('5.4', '表标题：写一句中文表格描述，得到规范的英文表标题（按 LaTeX 转义 % _ &，用 Word 的删掉 prompt 里转义那一行）',
                'Table caption: write a Chinese description, get an English caption (LaTeX-escaped; for Word, delete the escaping line)'),
        ('5.5', '架构图：贴摘要和方法，得到一张方法架构图（要用能生成图片的模型）',
                'Architecture diagram: paste the abstract and method, get a diagram (needs an image-generating model)'),
    ]),
    ('审稿与投稿', 'Review and submission', [
        ('6.1', '投稿前自审：贴整篇论文，得到审稿报告、评分，以及每个弱点怎么修',
                'Self-review before submission: paste the paper, get a review, a score and how to fix each weakness (replies in Chinese)'),
        ('6.2', '回复审稿人：贴审稿意见和你实际做的修改，得到完整回复信和修改对照表',
                'Response to reviewers: paste the comments and what you actually changed, get a full response letter and change log'),
        ('6.3', '投稿信：贴目标期刊、标题、摘要和主要贡献，得到一页给编辑的投稿信，没提供的审稿人和声明留 [待补]',
                'Cover letter: paste the journal, title, abstract and main contributions, get a one-page letter to the editor with [待补] placeholders for reviewers and declarations you did not supply'),
    ]),
]


def primary_prompts(catalog_text):
    """Return {scenario id: [every code block under its primary candidate]}.

    Some primaries (4.1, 4.3-4.6) are several one-line prompts to pick from.
    """
    found = {}
    for block in re.split(r'^## (?=\d+\.\d+)', catalog_text, flags=re.M)[1:]:
        sid = block.split()[0]
        primary = re.split(r'^### (?:替代候选|Alternative Candidate)', block, flags=re.M)[0]
        codes = re.findall(r'^```[^\n]*\n(.*?)^```', primary, flags=re.S | re.M)
        assert codes, f'no prompt block under the primary candidate of {sid}'
        found[sid] = [c.rstrip('\n') for c in codes]
    return found


def render(prompts, zh):
    out = []
    for zh_title, en_title, items in GROUPS:
        out.append(f'### {zh_title if zh else en_title}\n')
        for sid, zh_sum, en_sum in items:
            out += ['<details>',
                    f'<summary><b>{sid}</b> {zh_sum if zh else en_sum}</summary>',
                    '']
            for prompt in prompts[sid]:
                out += ['```text', prompt, '```', '']
            if sid == '2.3':
                label, target = (
                    ('可选参考词表', 'CATALOG.md#23-去-ai-味英文-de-ai-english') if zh else
                    ('Optional word-list reference', 'CATALOG_EN.md#23-de-ai-english')
                )
                out += [f'[{label}]({target})', '']
            out += ['</details>', '']
    return '\n'.join(out)


def main():
    prompts = primary_prompts((ROOT / 'CATALOG.md').read_text(encoding='utf-8'))
    wanted = [sid for _, _, items in GROUPS for sid, _, _ in items]
    assert sorted(prompts) == sorted(wanted), (sorted(prompts), sorted(wanted))
    for name, zh in (('README.md', True), ('README_EN.md', False)):
        path = ROOT / name
        text = path.read_text(encoding='utf-8')
        new, n = re.subn(r'(<!-- prompts:start -->\n).*?(<!-- prompts:end -->)',
                         lambda m: m.group(1) + '\n' + render(prompts, zh) + m.group(2),
                         text, flags=re.S)
        assert n == 1, f'{name}: expected one prompts:start/end marker pair'
        path.write_text(new, encoding='utf-8', newline='\n')
        print(f'{name}: {len(wanted)} prompts written')


if __name__ == '__main__':
    main()
