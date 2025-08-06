## 下载

| 平台    | 文件名                                                                                                                                    |
| ------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Windows | [TingJu-${{ VERSION }}-windows.zip](https://github.com/Pi3-l22/TingJu/releases/download/${{ VERSION }}/TingJu-${{ VERSION }}-windows.zip) |
| Linux   | [TingJu-${{ VERSION }}-linux.zip](https://github.com/Pi3-l22/TingJu/releases/download/${{ VERSION }}/TingJu-${{ VERSION }}-linux.zip)     |
| macOS   | [TingJu-${{ VERSION }}-macos.zip](https://github.com/Pi3-l22/TingJu/releases/download/${{ VERSION }}/TingJu-${{ VERSION }}-macos.zip)     |

## 问题

如果启动工具时出现以下错误

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