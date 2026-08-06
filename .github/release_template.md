## 更新日志

{{ CHANGELOG }}

## 文件下载

| 平台    | 文件名                                                                                                                                    |
| ------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
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

### 使用某些语言时出现 NLTK 词库错误

```shell
ERROR:   punkt 或 punkt_tab 下载失败
```

新版本发布包会预置 `punkt` 和 `punkt_tab`，且不会在启动阶段阻塞浏览器。如果使用旧版本或手动构建包，请确认以下目录存在；否则程序会尝试在首次分句时下载。

punkt 和 punkt_tab 手动下载地址为 👉 [蓝奏云 - nltk_data.zip](https://wwrs.lanzouo.com/ie7x932top2b)

下载 `nltk_data.zip` 并解压到工具运行根目录下即可。例如:

```shell
TingJu/
├── TingJu.exe
├── _internal/
├── nltk_data/           # 👈
│   └─── tokenizers/     # 👈
│       ├───punkt/       # 👈
│       └── punkt_tab/   # 👈
├── static/
└── templates/
```
