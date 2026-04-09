# `design.json` Schema

`card-creator` 的 Step 1 产物必须写成这个结构。字段可以扩展，但下面这些字段不能缺。

```json
{
  "meta": {
    "version": "1",
    "style_id": "glass-news-report",
    "style_name": "玻璃质感新闻风",
    "source": "preset",
    "reason": "适合专业信息报告与新闻摘要"
  },
  "colors": {
    "page_background": "#0f172a",
    "page_gradient": "linear-gradient(...)",
    "surface": "rgba(255,255,255,0.06)",
    "surface_border": "rgba(255,255,255,0.12)",
    "primary": "#f8fafc",
    "secondary": "#60a5fa",
    "accent": "#f59e0b",
    "accent_soft": "rgba(245,158,11,0.15)",
    "text_primary": "#ffffff",
    "text_secondary": "#cbd5e1",
    "text_muted": "#94a3b8"
  },
  "fonts": {
    "title_family": "'Noto Sans SC', sans-serif",
    "body_family": "'Noto Sans SC', sans-serif",
    "mono_family": "'JetBrains Mono', monospace",
    "title_size": "56px",
    "heading_size": "36px",
    "body_size": "30px",
    "label_size": "24px",
    "title_weight": 800,
    "body_weight": 400
  },
  "layout": {
    "canvas_width": "1080px",
    "min_height": "100vh",
    "page_padding": "40px",
    "container_width": "1000px",
    "section_gap": "28px",
    "card_padding": "36px",
    "card_radius": "28px"
  },
  "effects": {
    "shadow": "0 18px 48px rgba(15, 23, 42, 0.28)",
    "glow": "0 0 0 rgba(0,0,0,0)",
    "noise": false
  }
}
```

## 约束

- 所有尺寸字段都用字符串，带单位
- `layout.canvas_width` 固定为 `1080px`
- `layout.min_height` 固定为 `100vh`
- `fonts.title_size` 不低于 `48px`
- `fonts.body_size` 不低于 `28px`
- `meta.source` 只能是 `preset` 或 `generated`

## 为什么要固定 schema

这个 skill 之前不稳定，核心原因之一就是预设和生成结果的结构不一致，导致 Step 2 只能临场猜字段。现在统一 schema，就是为了让 Step 2 和校验脚本可以稳定消费。
