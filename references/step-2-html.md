# Step 2：生成 `card.html`

Step 2 的输入只有两个：

- `design.json`
- 用户内容

Step 2 的输出只有一个：

- `card.html`

## 硬规则

进入 Step 2 之前，必须已经有通过校验的 `design.json`。

禁止事项：

- 没有读 `design.json` 就直接写固定模板
- 用固定高度页面硬塞内容
- 做横向多列桌面布局
- 输出别的 HTML 文件名导致 Step 3 找不到

## 页面结构要求

建议结构：

- `body`
- `.page`
- `.hero`
- 一个或多个 `.card`

类名可以扩展，但必须保证页面是单列向下生长的。

## 核心 CSS 约束

至少满足这些约束：

```css
body {
  width: 1080px;
  min-height: 100vh;
}

.page {
  width: 1000px;
  margin: 0 auto;
}
```

同时满足：

- `body` 不要写固定 `height`
- 主容器必须水平居中
- 区块之间要有明显的纵向间距
- 字号必须来自 `design.json`

## 从 `design.json` 映射到 HTML

最低映射要求：

- `colors.page_background` -> 页面背景
- `colors.surface` -> 卡片背景
- `colors.primary` / `colors.accent` -> 标题、标签、强调元素
- `fonts.title_family` / `fonts.body_family` -> 字体族
- `fonts.title_size` / `fonts.body_size` -> 基础字号
- `layout.page_padding` / `layout.container_width` / `layout.card_padding` / `layout.card_radius` -> 布局尺寸
- `effects.shadow` / `effects.glow` -> 可选视觉效果

## 长内容规则

如果用户内容明显偏长：

- 用多段卡片拆分信息
- 用时间线、列表、标签、摘要框分层
- 允许页面自然变高

不要为了控制图片高度删信息，也不要硬压缩成超小字号。

## 校验

写完后运行：

```powershell
python scripts/validate_html.py card.html
```

只有校验通过，才能进入 Step 3。
