# Step 3：生成 `card.png`

Step 3 的职责很单一：把 `card.html` 稳定转成完整截图 `card.png`。

## 硬规则

进入 Step 3 之前，必须已经有通过校验的 `card.html`。

禁止事项：

- 不经截图直接声称图片已生成
- 不设置视口宽度就截图
- 不用 `--full` 就截长页面
- 截图失败后仍然汇报完成

## 推荐流程

优先直接打开本地文件：

```powershell
agent-browser open "file:///ABSOLUTE/PATH/TO/card.html"
agent-browser wait --load networkidle
agent-browser set viewport 1080 1200 2
agent-browser screenshot --full card.png
```

说明：

- 视口宽度固定为 `1080`
- 初始高度推荐 `1200`，避免短内容页面因为 `min-height: 100vh` 留下过多底部空白
- 用 `2` 倍 DPR 可以提升清晰度

如果本地文件模式下字体或资源加载异常，再退回本地 HTTP 服务，但要使用当前环境原生的后台进程方式，不要照搬别的 shell 示例。

## 截图后校验

运行：

```powershell
python scripts/validate_png.py card.png --expected-width 1080 --min-height 1200 --min-ratio 1.1 --reject-blank
```

如果是长内容卡片，建议把 `--min-height` 提高到 `1600` 或更高。

如果校验失败且怀疑是白屏、空白图、浏览器瞬时异常，优先原样重截一次。只有连续失败，才回退到 Step 2 查 HTML。

## 失败处理

如果截图失败，按下面顺序排查：

1. `card.html` 是否真实存在
2. 视口是否已设置为 `1080`
3. 是否使用了 `--full`
4. 是否出现白屏或近空白截图
5. HTML 是否存在固定高度导致内容被裁

定位到问题后，回退到对应步骤修复，不要在 Step 3 硬补救。
