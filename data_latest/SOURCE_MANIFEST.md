# 最新数据源下载与校验记录

## 来源

- 仓库：`https://github.com/kkzyx/shanghai-house-visualization`
- README 指向的 Release：`https://github.com/kkzyx/shanghai-house-visualization/releases/tag/data-v2-v3`
- Release 更新时间：2026-10-12 16:34:40 UTC（北京时间 2026-10-13 00:34:40）
- 下载资产：`shanghai_house_dataset_v2_v3.zip`
- 下载地址：`https://github.com/kkzyx/shanghai-house-visualization/releases/download/data-v2-v3/shanghai_house_dataset_v2_v3.zip`
- 下载时间：2026-10-13（Asia/Shanghai）

检查 GitHub Releases 订阅时，该仓库只有 `data-v2-v3` 这一项 Release，因此它是下载时可获得的最新发布数据源。

## 原始资产校验

- 文件：`archives/shanghai_house_dataset_v2_v3.zip`
- 字节数：18,557,058
- SHA-256：`FB2DAC62C244BEBD9116216CC2F8B098576635168F312F8AFEF86E84BFB07DCE`
- ZIP 条目数：19
- ZIP CRC 检查：通过，无损坏条目

原压缩包保持不变。内容解压到 `extracted/shanghai_house_dataset/`；未向 CSV 补列、补行、拼接外部数据或重算指标。

## CSV 结构校验

| 相对路径 | 数据行 | 列数 | 异常行 |
|---|---:|---:|---:|
| `tableau_ready/04_相关系数表.csv` | 8 | 7 | 0 |
| `tableau_ready/05_网格热力.csv` | 1,055 | 5 | 0 |
| `tableau_ready/06_箱形图分位.csv` | 16 | 13 | 0 |
| `tableau_ready/07_区内分化.csv` | 16 | 7 | 0 |
| `tableau_ready/08_D3小区级_打分用.csv` | 1,467 | 21 | 0 |
| `v2/01_房源级.csv` | 171,344 | 48 | 0 |
| `v2/02_小区级.csv` | 13,543 | 55 | 0 |
| `v2/03_区级.csv` | 16 | 50 | 0 |
| `v3/01_房源子集_旧表小区.csv` | 35,569 | 54 | 0 |
| `v3/02小区总表_安居客重算.csv` | 1,467 | 39 | 0 |
| `v3/03_区表_年鉴口径_district.csv` | 16 | 41 | 0 |

这里的“数据行”不含表头，并使用 CSV 解析器计数，因此正确处理了字段中的嵌入换行。

## D3 使用入口

- 首选打分表：`extracted/shanghai_house_dataset/tableau_ready/08_D3小区级_打分用.csv`
- 房源明细：`extracted/shanghai_house_dataset/v3/01_房源子集_旧表小区.csv`
- 小区总表：`extracted/shanghai_house_dataset/v3/02小区总表_安居客重算.csv`
- 区级表：`extracted/shanghai_house_dataset/v3/03_区表_年鉴口径_district.csv`
- 构建说明：`extracted/shanghai_house_dataset/Tableau构建指引.md`

`verify_sources.py` 是只读校验脚本，会输出压缩包与各 CSV 的 SHA-256、行列数、异常行数和表头；它不会写入或改动数据文件。
