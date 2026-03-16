# AI Shorts Factory — 操作手册 (Manual SOP)

## 你（主人）每天只需做 4 件事

### Step 1: 查看任务列表
打开文件夹：`Z:\shorts_system\manual_generation_queue\pending\`

每个 `TASK_XXXX` 文件夹就是一个视频任务。优先处理 CH_A（前缀 A），然后 CH_B、CH_C。

### Step 2: 复制 Prompt 到小云雀
1. 打开任务文件夹中的 `prompt.txt`
2. 全选复制（Ctrl+A → Ctrl+C）
3. 打开小云雀网页端
4. 粘贴到提示词输入框
5. 点击生成（约15分钟）

> 💡 **提速技巧**：可以同时打开多个小云雀网页标签，并行生成多个视频

### Step 3: 检查视频质量
生成完成后，快速检查：
- ✅ 画面清晰，无变形
- ✅ 动作流畅，无闪烁
- ✅ 内容与 prompt 一致
- ✅ 时长约 15 秒
- ❌ 如果质量差 → 重新生成

### Step 4: 下载并放入 inbox
1. 下载视频（MP4格式）
2. 查看 `operator_note.txt` 中指示的目标频道
3. 在对应频道的 inbox 创建文件夹，放入视频：

```
Z:\shorts_system\nas_shorts\inbox\ch_a\V_A001\video.mp4
Z:\shorts_system\nas_shorts\inbox\ch_b\V_B001\video.mp4  
Z:\shorts_system\nas_shorts\inbox\ch_c\V_C001\video.mp4
```

4. 将 `publish_prep.json` 从任务文件夹复制到同一目录

```
Z:\shorts_system\nas_shorts\inbox\ch_a\V_A001\publish_prep.json
```

5. 将任务文件夹从 `pending/` 移动到 `completed/`

**搞定！** NAS Docker 会在预定时间自动上传到 YouTube。

---

## 命名规则速查

| 频道 | 文件夹前缀 | 示例 |
|------|-----------|------|
| CH_A 动物剧情 | V_A | `V_A001`, `V_A002` |
| CH_B 奇幻世界 | V_B | `V_B001`, `V_B002` |
| CH_C 微知识 | V_C | `V_C001`, `V_C002` |

## 上传时间（US Eastern）

| 时段 | 时间 (ET) | 北京时间（冬令时） |
|------|----------|-------------------|
| 午间 | 11:30 AM | 次日 00:30 |
| 傍晚 | 7:30 PM | 次日 08:30 |
| 夜间 | 9:30 PM | 次日 10:30 |

## 常见问题

**Q: 某个时间窗口inbox没有视频怎么办？**
A: 系统会自动跳过，等下个时间窗口再检查。

**Q: 视频放错了频道文件夹怎么办？**
A: 赶紧移到正确的文件夹。如果已经上传了，在 YouTube Studio 删除后重新走流程。

**Q: 一天没生成够 3 条怎么办？**
A: 没关系，系统按实际数量上传，不会强制。
