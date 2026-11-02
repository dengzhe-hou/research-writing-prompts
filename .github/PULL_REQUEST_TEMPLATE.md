## Prompt contribution / Prompt 贡献

### Scenario / 场景

Which scenario does this add or change? Why is the current prompt insufficient?
要新增或修改哪个场景？现有 prompt 的具体不足是什么？

### Change / 改动

- [ ] New scenario
- [ ] New alternative for an existing scenario
- [ ] Rewrite of a primary candidate
- [ ] Example or evaluation case
- [ ] Documentation / build / site

### Source and license / 来源与许可

- Upstream repository or author / 原始仓库或作者：
- Link / 链接：
- License or terms / License 或使用条款：
- Verbatim, adapted (name the section), or written for this catalog / 原文、改编（注明章节）还是本仓库编写：

If the upstream has no license, write “not declared”. Do not guess.
如果上游没有许可证，写“未声明”，不要推测。

### Prompt text / Prompt 原文

Paste the complete prompt. It must include the input schema and the output
contract. If it touches numbers, citations or reviewer responses, include an
anti-fabrication rule.
粘贴完整 prompt，必须包含输入位置和输出格式；涉及数字、引用或审稿回复时，必须写明不许编造。

### Example / 示例

Provide one synthetic input and the output before/after. Every number in the
output must be traceable to the input.
提供一组合成输入和修改前后的输出。输出里的每个数字都必须能从输入复现。

**Input / 输入**：

**Current output / 当前输出**：

**Proposed output / 建议输出**：

### Checks / 检查

- [ ] Edited `data/prompts.yaml`, not the generated README/CATALOG files.
- [ ] Ran `python tools/build.py`.
- [ ] Ran `python tools/check.py`.
- [ ] Added or updated an `eval/cases.yaml` case if this fixes a failure mode.
- [ ] The source line is accurate and the license is not guessed.
- [ ] No private text, unpublished results or personal data in the example.
