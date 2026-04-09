# Step 1：生成 `design.json`

Step 1 的唯一目标，是把视觉决策收敛成结构化文件 `design.json`。

## 硬规则

允许输出：

- `design.json`
- 简短说明为什么选这个风格

禁止输出：

- HTML
- CSS
- SVG
- “我接下来会这样设计”的口头描述代替文件

Step 1 完成的标准不是“想好了”，而是：

1. `design.json` 已写入磁盘
2. `python scripts/validate_design_json.py design.json` 返回成功

## 先查预设

优先查看 `styles/` 目录里的预设文件。

如果用户内容明显符合某个预设，就直接复用该预设的设计语言，再补齐 `meta.reason`。不要为了“创意”强行绕过预设。

适配原则：

- 风险、警示、负面舆情、异常监测：优先 `dark-alert-report.json`
- 专业资讯、编辑感、新闻摘要、信息报告：优先 `glass-news-report.json`

如果两个都不合适，再新建一份 `design.json`。

## `design.json` schema

结构必须与 `references/design-schema.md` 一致，至少包含：

- `meta`
- `colors`
- `fonts`
- `layout`
- `effects`

### 最低要求

`meta` 至少包含：

- `version`
- `style_id`
- `style_name`
- `source`
- `reason`

`colors` 至少包含：

- `page_background`
- `surface`
- `primary`
- `accent`
- `text_primary`
- `text_secondary`

`fonts` 至少包含：

- `title_family`
- `body_family`
- `title_size`
- `body_size`

`layout` 至少包含：

- `canvas_width`
- `min_height`
- `page_padding`
- `container_width`
- `section_gap`
- `card_padding`
- `card_radius`

## 设计约束

- `layout.canvas_width` 必须是 `1080px`
- `layout.min_height` 必须是 `100vh`
- 正文字号不要低于 `28px`
- 标题字号不要低于 `48px`
- 设计必须面向手机单列分享卡片，不要面向桌面多栏页面

## 推荐做法

先把风格决定说清楚，再落字段：

1. 这张卡片的语气是什么
2. 为什么选这个配色和层次
3. 如何保证手机端可读性

然后再写 `design.json`，不要反过来先写一堆 HTML。

## 校验

运行：

```powershell
python scripts/validate_design_json.py design.json
```

如果失败，先修 `design.json`，不要进入 Step 2。
