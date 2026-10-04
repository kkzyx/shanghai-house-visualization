# COMP7507 往届 Tableau 案例分析：high-01（香港教育数据分析）

## 1. 文档说明

- **案例名称**：`high-01`
- **视频时长**：约 3 分 03 秒
- **视频地址**：[Panopto 案例页面](https://hku.ap.panopto.com/Panopto/Pages/Viewer.aspx?id=63d1d5ab-6edf-4c3a-b913-b07b007126d1)
- **画面中的项目标题**：`COMP7507 Visualization and Visual Analytics – Group C Project: Analysis of the data related to education situation in Hong Kong`
- **项目主题**：香港学校地理分布、学校属性、学额与入学人数分析
- **限制**：视频没有可用字幕。本报告依据实际画面和交互状态完成。`Secondary Section` 页面入口可见，但视频中没有清楚展示该页面的完整内容，因此不对其具体图表作推测。

本报告用于提炼可复用方法，不代表课程官方评分，也不建议复制往届项目的题目或设计。

---

## 2. 时间点与观察证据

| 时间点 | 画面内容 |
|---|---|
| 0:00 | `School Information` 页面：香港地图、地区列表、学校层级、财务类型、宗教、学校列表、学额与入学人数图。 |
| 约 0:36 | 选择 Central & Western District 后，地图、学校数量、Finance Type、Religion、School List 和柱状图联动更新。 |
| 约 1:12 | 地图放大至已选地区，学校点位和地区边界更清晰，学校数量由选择条件决定。 |
| 约 1:48 | 同时选择多个地区，并切换到 Secondary；年份变为 2016，学校数量、地图、饼图、列表和学额图同步更新。 |
| 约 2:24 | `Primary Section` 页面：小学趋势、地区与年级、宗教、年级趋势、超额收生和低使用率地区分析。 |
| 约 3:00 | 在小学页面选择地区后，Finance Type 饼图得到更新，其他图表保留联动状态。 |

### 信息可信度分类

- **画面确认**：页面名称、学校地区、Primary/Secondary 层级、Finance Type、Religion、Accommodation、Enrolment、Grade、年份和交互状态。
- **合理推断**：目标用户可能包括教育管理人员、学校规划人员、研究人员和希望比较地区教育资源的公众。
- **无法确认**：数据来源、学校年份覆盖范围的完整定义、Accommodation 的官方口径、作者最终政策建议和 Secondary Section 的完整图表内容。

---

## 3. 项目问题与分析框架

该项目把香港教育数据组织成两个分析层次：

1. **学校查找与地区概览**：学校在哪里、属于什么类型、由谁资助、是否具有宗教背景，以及各区的学额与入学人数；
2. **教育容量与趋势分析**：小学学额和入学人数如何随年份和年级变化，哪些地区可能过度拥挤或资源使用不足。

潜在分析逻辑为：

> 地区选择 → 学校分布 → 学校属性 → 学额与入学人数 → 年级趋势 → 容量利用率异常地区

这一案例不仅提供“学校目录”，还进一步支持教育资源配置分析，是目录型 Dashboard 与政策分析 Dashboard 的结合。

---

## 4. 数据结构分析

### 4.1 可观察的数据维度

- School Name；
- District：香港 18 区；
- School Level：Primary、Secondary；
- Finance Type：Aided、Government、Direct Subsidy Scheme、International、Private 等；
- Religion：Catholicism、Christianity、Buddhism、Islam、No Religion 等；
- Grade：P1–P6；
- Year：画面可见 2006–2016；
- 地理位置：学校点位及地区边界。

### 4.2 可观察的指标

- No. of School Selected；
- Accommodation；
- Enrolment；
- Accommodation 与 Enrolment 的差值；
- Occupied rate 或容量使用率；
- 按地区、资助类型、宗教和年级汇总的数量；
- Top Five Over Crowded District；
- Lowest Five Occupied District。

### 4.3 适合的数据模型

类似项目可能需要至少三类数据：

1. **学校主表**：School ID、School Name、District、Level、Finance Type、Religion、地址和经纬度；
2. **年度容量表**：School ID、Year、Grade、Accommodation、Enrolment；
3. **地区空间数据**：District Name 和地理边界。

Proposal 中应写清：

- 学校名称变化和学校合并如何处理；
- District 命名如何统一；
- 地址如何转成经纬度；
- Accommodation 和 Enrolment 的统计口径；
- 缺失年份、重复学校和异常占用率如何处理。

---

## 5. `School Information` 页面分析

### 5.1 页面结构

该页面采用左侧控制、中央地图、右侧属性与容量分析、底部学校详情的布局。

主要模块包括：

- 页面导航：School Information、Primary Section、Secondary Section；
- `No. of School Selected` KPI；
- Hong Kong 18 Districts 列表；
- School Level：Primary / Secondary；
- `Reset All Marking`；
- 香港地图与学校点位；
- Finance Type 饼图；
- Religion 饼图；
- School List；
- `Accommodation and Enrolment Analysis by District and Sector in Year`；
- 年份选择器；
- School Detail 区域。

### 5.2 地图与地区筛选

地图是该页面的核心导航控件。视频中选择 Central & Western District 后：

- 地区边界被突出显示；
- 学校点位显示在地图上；
- KPI 更新为所选学校数量；
- Finance Type 和 Religion 饼图更新；
- School List 更新；
- Accommodation / Enrolment 柱状图更新。

视频还展示了多地区选择，说明项目支持比较多个地区，而不只查看单一区域。

### 5.3 学校属性分析

Finance Type 和 Religion 两个饼图展示地区内学校的组成。它们可以回答：

- 某地区以哪种资助类型的学校为主？
- 不同地区的宗教背景结构是否不同？
- Primary 与 Secondary 的学校结构是否不同？

但饼图类别较多，颜色和标签拥挤。若类别超过五个，排序条形图通常更容易比较。

### 5.4 学额与入学人数

页面使用分组柱状图比较不同 Finance Type 下的 Accommodation 与 Enrolment。该图可以用于判断：

- 哪种学校类型承担最多学额；
- 实际入学人数是否接近或超过学额；
- 不同年份的容量压力是否变化；
- 哪些地区或资助类型可能存在资源不足或闲置。

这一模块具有明确政策价值，但需要在 Dashboard 中解释 Accommodation 的定义，并提醒用户容量差值不等于教育质量。

### 5.5 School List 与 School Detail

右侧学校列表提供从地区汇总到学校级别明细的入口。底部 `School Detail` 区域在未选中学校时显示空状态。

优点是支持 Overview → District → School 的下钻。问题是空状态只显示“无学校详情”，缺少“请从右侧选择学校”的操作提示。

---

## 6. `Primary Section` 页面分析

### 6.1 `Primary School Trend`

该图展示约 2006–2016 年小学 Accommodation 和 Enrolment 的总体趋势。画面显示两项指标总体先下降，后期略有回升。

适合回答：

- 小学整体学额和入学人数是否长期下降？
- 两者之间的差距是否扩大？
- 哪些年份发生趋势转折？

当前标签几乎覆盖所有年份，造成视觉拥挤。更好的方式是保留端点、极值和转折点标签，其余通过 Tooltip 查看。

### 6.2 `Primary School Analysis by District and Grade`

该区域使用 Treemap 展示不同地区或年级规模。Treemap 适合快速识别规模较大的地区，但不适合精确比较相近数值。

可改进为：

- 排序条形图；
- 地区 × 年级热力图；
- 地图和年级筛选联动。

### 6.3 `Primary School Analysis by Religions`

画面使用柱形与折线组合图比较不同宗教类别。组合图能同时展示规模和另一项指标，但必须清楚标注双轴含义，否则容易误读。

### 6.4 `Primary School Trend by Grade`

该区域使用多条折线比较 P1–P6 的变化，并配有年级复选框和年份范围控件。

优点：

- 支持用户选择关注的年级；
- 可以比较不同年级的趋势和交叉；
- 适合观察人口或招生周期带来的变化。

问题：

- 六条以上折线容易拥挤；
- Accommodation 和 Enrolment 如果同时展示，线条数量可能翻倍；
- 应允许用户在指标之间切换，而不是一次显示所有组合。

### 6.5 容量使用率异常地区

右下区域包含：

- `Analysis between Accommodation and Enrolment in Year 2016`；
- `The Top FIVE Over Crowded District in Year 2016`；
- `The Lowest FIVE Occupied District in Year 2016`。

这是全项目最具有决策价值的模块。它把原始容量与入学人数转化为需要关注的异常地区：

- 超额收生地区可能面临学位压力；
- 低使用率地区可能存在资源闲置；
- 用户可以通过年份参数查看变化。

Proposal 如果采用类似排名，必须明确公式，例如：

> Occupancy Rate = Enrolment / Accommodation

并说明 Accommodation 为零、数据缺失和极小样本如何处理。

---

## 7. 交互设计分析

### 视频中确认的交互

- 地区列表单选和多选；
- 地图选择与缩放；
- Primary / Secondary 切换；
- 年份下拉选择；
- 年级复选框；
- 年份范围滑块；
- Reset All Marking；
- 地区、地图、学校数量、饼图、学校列表和容量图联动；
- 选择地区后显示对应 Finance Type 结构。

### 优点

- 地图不仅是展示，也是分析入口；
- 支持总体、地区和学校多个层级；
- 同一选择同时更新多个视图；
- 年份和年级筛选允许纵向比较；
- Reset 功能降低用户迷失风险。

### 风险

- 控件数量较多，初次使用者学习成本高；
- 多地区选择后标题非常长；
- 不同控件的影响范围未明确标注；
- 空白区域缺少操作提示；
- 选择状态主要依赖颜色，对色觉障碍用户不够友好。

---

## 8. 视觉与信息设计评价

### 优点

1. 页面结构稳定，左侧导航、中央主视图和右侧细节区分明确；
2. 采用多页面组织学校信息和学校层级分析；
3. 深色背景与彩色图表形成较高对比；
4. KPI、地图、属性、列表和趋势形成 Overview-to-Detail 结构；
5. 标题通常会反映当前地区、年份和学校层级。

### 不足

1. 深色背景中部分字体和坐标较小；
2. 饼图类别较多，标签拥挤；
3. 页面信息密度高，用户很难快速识别首要结论；
4. 多折线和密集数据标签增加视觉噪声；
5. 黄色侧栏、深色画布和多种图表颜色缺少统一语义；
6. 空白状态和选择说明不够清楚；
7. 缺少关键结论、数据来源和指标定义说明。

---

## 9. 数据故事与用户价值

该项目的叙事顺序可以概括为：

1. 选择香港地区；
2. 查看学校数量和空间分布；
3. 了解学校资助类型和宗教结构；
4. 比较学额与入学人数；
5. 观察小学多年趋势和年级变化；
6. 识别超额收生和低使用率地区。

潜在用户价值包括：

- 教育管理者识别容量压力；
- 规划人员判断地区资源配置；
- 研究人员比较长期趋势；
- 家长或公众了解某区学校分布与类型。

但一个 Dashboard 同时服务政策管理者和公众可能导致需求冲突。Proposal 应选择主要用户，而不是笼统声称“所有人都可以使用”。

---

## 10. 综合评价

以下为非官方项目规划评价：

| 维度 | 评价 | 说明 |
|---|---:|---|
| 选题公共价值 | 4.5/5 | 教育资源与学校容量具有明确社会和政策意义。 |
| 数据维度丰富度 | 4.5/5 | 地区、学校、层级、资助、宗教、年份、年级和容量较完整。 |
| 信息架构 | 4/5 | 学校信息与分层分析采用多页面组织。 |
| 地理分析 | 4.5/5 | 地图选择与多个视图联动，具有实际分析作用。 |
| 交互设计 | 4/5 | 多选、年份、年级、层级和 Reset 功能丰富。 |
| 图表选择 | 3.5/5 | 地图、趋势和排名合理，但饼图、Treemap 和多折线存在可读性问题。 |
| 可读性 | 3/5 | 页面信息密度高、文字小、颜色较多。 |
| 数据故事 | 3.5/5 | 分析路径完整，但缺少摘要和关键发现。 |

总体评价：

> 这是一个数据维度丰富、交互层级清楚的香港教育 Dashboard。其最大优势是将地图、学校属性、长期趋势和容量压力连接起来；主要不足是页面拥挤、图表标签过多，以及缺少指标解释和关键结论。

---

## 11. 对新 Proposal 的启示

### 11.1 先确定主要用户

可以选择其中一类：

- 教育政策或资源规划人员；
- 学校管理人员；
- 教育研究人员；
- 学生家长或公众。

不同用户需要的内容不同。例如，家长可能关注学校位置和类型，政策人员更关注容量、趋势和异常地区。

### 11.2 定义核心分析问题

| 分析问题 | 数据 | 推荐图表 | 用户价值 |
|---|---|---|---|
| 学校分布是否均衡？ | 学校位置、地区、层级 | 点位地图或密度图 | 发现服务空白区 |
| 各区学校结构有何差异？ | Finance Type、Religion、District | 排序条形图 | 比较教育供给结构 |
| 学额与入学人数如何变化？ | Year、Accommodation、Enrolment | 折线图 | 判断长期容量趋势 |
| 哪些地区过度拥挤？ | Accommodation、Enrolment | 排名条形图或地图 | 识别资源压力 |
| 哪些地区使用率较低？ | Occupancy Rate、District | 排名和地图 | 识别闲置资源 |
| 不同年级是否存在周期变化？ | Grade、Year、Enrolment | Small multiples 或热力图 | 支持招生规划 |

### 11.3 Proposal 中必须解释的指标

- Accommodation 的官方含义；
- Enrolment 的统计时点；
- Occupancy Rate 的计算；
- Over Crowded 的阈值；
- 多校区学校如何计数；
- 学校合并或停办如何处理；
- 地理编码精度；
- 年份之间口径是否一致。

### 11.4 推荐页面结构

1. **Education Overview**：学校总数、学生人数、总体容量使用率和时间趋势；
2. **School Explorer**：地区地图、学校列表和学校详情；
3. **District Comparison**：地区、资助类型和学校层级比较；
4. **Capacity Analysis**：学额、入学人数、超额和低使用率；
5. **Grade Trend**：按年级分析招生变化。

### 11.5 数据伦理与表达

教育数据涉及公共资源和学校评价。新 Proposal 应避免：

- 将容量使用率直接解释为学校质量；
- 根据宗教或资助类型作价值判断；
- 在样本很小时进行不稳定排名；
- 暴露不必要的个人信息；
- 忽略不同地区人口结构和年龄分布。

---

## 12. 值得学习与不应照搬

### 值得学习

- 使用地图作为地区筛选与下钻入口；
- 将学校目录和教育资源分析结合；
- 支持地区、年份、年级和学校层级多维筛选；
- 将原始学额数据转化为过度拥挤和低使用率指标；
- 提供 Reset，帮助用户恢复默认状态；
- 使用多页面避免所有分析集中在一个画布。

### 不应照搬

- 直接复制香港教育主题或页面结构；
- 使用过多饼图和拥挤的数据标签；
- 在一个页面中同时服务所有潜在用户；
- 使用容量排名却不解释计算口径；
- 用深色背景和多种颜色但没有统一颜色语义；
- 让空白图表出现，却不提供操作指引；
- 把学校容量或宗教结构解释为学校质量。

---

## 13. 最终结论

`high-01` 的核心价值是把香港学校的空间信息、属性信息和容量信息连接成一个可交互系统。用户可以从全港概览进入地区，再进入学校列表和学校详情，同时通过年份、层级和年级分析长期变化及容量压力。

对新 Proposal 最重要的启示是：

> 一个公共数据可视化项目应从“在哪里、是什么、如何变化、哪里异常”逐层展开，并明确指标定义和目标用户，避免把复杂 Dashboard 变成难以阅读的数据堆叠。

