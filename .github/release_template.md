## 更新日志

{{ CHANGELOG }}

## 文件下载

| 平台    | 文件名                                                                                                                                    |
| ------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Windows | [TingJu-${{ VERSION }}-windows.zip](https://github.com/Pi3-l22/TingJu/releases/download/${{ VERSION }}/TingJu-${{ VERSION }}-windows.zip) |
| Linux   | [TingJu-${{ VERSION }}-linux.zip](https://github.com/Pi3-l22/TingJu/releases/download/${{ VERSION }}/TingJu-${{ VERSION }}-linux.zip)     |
| macOS   | [TingJu-${{ VERSION }}-macos.dmg](https://github.com/Pi3-l22/TingJu/releases/download/${{ VERSION }}/TingJu-${{ VERSION }}-macos.dmg)     |

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

### 启动时出现 NLTK 词库下载失败

```shell
ERROR:   punkt 或 punkt_tab 下载失败
```

可能是因为国外网络问题导致无法下载词库。首次使用工具时，请使用科学上网，词库下载成功后，则后续无需再使用。

punkt 和 punkt_tab 手动下载地址为 👉 [蓝奏云 - nltk_data.zip](https://wwrs.lanzouo.com/ie7x932top2b)

下载 `nltk_data.zip` 并解压到工具运行根目录下即可。如: 

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