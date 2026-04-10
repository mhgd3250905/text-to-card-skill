---
name: card-creator
description: 制作精美分享卡片图片。当用户提到卡片、海报、图文、小红书图片、朋友圈分享图、宣传图、数据报告可视化、信息图、手机分享页、分享卡片、分享图片、做图片、做卡片等，即使没有明确说“卡片”，也应触发此技能。
---

# Card Creator

把一段内容稳定地制作成分享卡片图片。

这个 skill 的重点不是“自由发挥”，而是按固定产物链执行。只要任一步的产物缺失或校验失败，就不能进入下一步。视觉目标也必须明确：做出来的不是“桌面网页缩成手机比例”，而是便于手机社交媒体分享的一页内容。

## 执行契约

唯一允许的执行顺序：

1. 生成 `design.json`
2. 生成 `card.html`
3. 生成 `card.png`

禁止事项：

- 不要把 Step 1 和 Step 2 合并
- 不要在没有 `design.json` 的情况下直接写 HTML
- 不要在没有 `card.html` 的情况下直接截图
- 不要把“脑内设计稿”当作已完成的 Step 1
- 不要跳过脚本校验
- 不要把内容压成桌面看板式的拥挤布局

## 产物约定

在当前任务目录中固定写出以下文件：

- `design.json`
- `card.html`
- `card.png`

如果用户已经给了目标目录，就写到该目录；否则写到当前工作目录。文件名保持不变，避免后续步骤找不到输入。

## Step 1：生成设计参数

目标：只产出结构化设计参数，不写 HTML/CSS。

执行方式：

1. 先检查 `styles/` 里的预设风格
2. 如果某个预设明显匹配用户场景，直接复用该预设，并把它整理成 `design.json`
3. 如果没有合适预设，就直接根据用户内容生成新的 `design.json`

不要把 `frontend-design` 当作 Step 1 的默认依赖。这个 skill 自己负责把设计收敛成 schema；如果你真的需要额外审美灵感，也只能把结果整理回 `design.json` 后再继续。

Step 1 要始终围绕“手机社交媒体分享的一页内容”来设计，不要做成信息密度很高的桌面可视化布局。

`design.json` 必须符合 `references/design-schema.md` 中的字段要求，然后运行：

```powershell
python scripts/validate_design_json.py design.json
```

只有校验通过，Step 1 才算完成。

详细规则见 [`references/step-1-design.md`](references/step-1-design.md)

## Step 2：生成 HTML

目标：根据 `design.json` 和用户内容生成完整 HTML。

要求：

- 固定输出文件名 `card.html`
- 宽度必须是 `1080px`
- 高度必须自适应，不允许把页面主容器写成固定高度
- 布局必须是手机社交媒体页面式的分享卡片，默认单列，不做桌面站多列排版
- 文字和间距要优先保证手机可读性，不要为了塞信息缩小字号

写完后运行：

```powershell
python scripts/validate_html.py card.html
```

只有校验通过，Step 2 才算完成。

详细规则见 [`references/step-2-html.md`](references/step-2-html.md)

## Step 3：截图导出

目标：把 `card.html` 产出为 `card.png`。

优先使用 `agent-browser` 直接打开本地文件：

```powershell
agent-browser open "file:///ABSOLUTE/PATH/TO/card.html"
agent-browser wait --load networkidle
agent-browser set viewport 1080 1200 2
agent-browser screenshot --full card.png
```

截图后运行：

```powershell
python scripts/validate_png.py card.png --expected-width 1080 --min-height 1200 --min-ratio 1.1 --reject-blank
```

如果用户内容很多，`card.png` 高度通常应该明显超过最小值。若校验失败，先重截一次；如果仍失败，再回到 Step 2 调整 HTML，不要强行结束。

详细规则见 [`references/step-3-screenshot.md`](references/step-3-screenshot.md)

## 最终回复

完成后只汇报高信号结果：

- 使用了哪个预设或说明是新建设计
- 生成文件路径：`design.json`、`card.html`、`card.png`
- 是否通过了三个校验脚本
- 若存在未验证项，明确写出

## 回归验证

这个 skill 自带两组人工样例，放在 `manual-runs/`。

只验证现有产物是否仍符合规范：

```powershell
python scripts/run_regression.py
```

如果你修改了 HTML 并想重新截图再验证：

```powershell
python scripts/run_regression.py --recapture
```

## 资源

- [`references/design-schema.md`](references/design-schema.md)
- [`references/step-1-design.md`](references/step-1-design.md)
- [`references/step-2-html.md`](references/step-2-html.md)
- [`references/step-3-screenshot.md`](references/step-3-screenshot.md)
- [`styles/`](styles)
- [`manual-runs/manifest.json`](manual-runs/manifest.json)
- [`scripts/validate_design_json.py`](scripts/validate_design_json.py)
- [`scripts/validate_html.py`](scripts/validate_html.py)
- [`scripts/validate_png.py`](scripts/validate_png.py)
- [`scripts/run_regression.py`](scripts/run_regression.py)
