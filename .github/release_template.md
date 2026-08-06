## 更新日志

{{ CHANGELOG }}

## 文件下载

| 平台    | 文件                                                                                                                             |
| ------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Windows | [TingJu-__VERSION__-windows.zip](https://github.com/Pi3-l22/TingJu/releases/download/__VERSION__/TingJu-__VERSION__-windows.zip) |
| Linux   | [TingJu-__VERSION__-linux.zip](https://github.com/Pi3-l22/TingJu/releases/download/__VERSION__/TingJu-__VERSION__-linux.zip)     |
| macOS   | [TingJu-__VERSION__-macos.dmg](https://github.com/Pi3-l22/TingJu/releases/download/__VERSION__/TingJu-__VERSION__-macos.dmg)     |

👉 国内下载地址: [蓝奏云 - TingJu-v1](https://pi3.lanzouo.com/b0kob9yze) | 密码:51122

## 常见问题

### macOS 用户如何打开应用

由于 TingJu 未使用 Apple Developer ID 签名（需付费 $99/年），首次打开时 macOS Gatekeeper 会阻止运行。

**解决方法（任选其一）：**

**方法一：右键打开（推荐）**
1. 下载并打开 `.dmg` 文件，将 `TingJu` 文件夹拖入 `应用程序` 或桌面
2. 在 `TingJu` 文件夹中找到 `TingJu` 可执行文件
3. **右键点击** → 选择 **"打开"**
4. 在弹出的对话框中点击 **"仍要打开"**
5. 之后即可正常双击运行

**方法二：终端清除隔离标记**
```bash
# 进入 TingJu 文件夹所在目录，执行：
xattr -cr TingJu/
```
之后再双击 `TingJu` 可执行文件即可正常运行。

> 💡 提示：方法一只需操作一次，之后无需重复。

### 分句功能

新版本 TingJu (v1.2.0+) 的分句功能使用本地 sentencex，不需要下载 NLTK、Punkt 或其他分句词库。完整引语块默认作为一个学习单元，即使引号内部包含多个句末标点。
