from __future__ import annotations

import csv
import json
import re
import zipfile
from pathlib import Path

from lxml import etree
from tableauhyperapi import Connection, CreateMode, HyperProcess, Inserter, Nullability, SqlType, TableDefinition, TableName, Telemetry
from cwtwb import TWBEditor

ROOT = Path(__file__).resolve().parent
DATA_ROOT = ROOT / "data_latest" / "extracted" / "shanghai_house_dataset"
COMMUNITY_CSV = DATA_ROOT / "tableau_ready" / "08_D3小区级_打分用.csv"
LISTING_CSV = DATA_ROOT / "v3" / "01_房源子集_旧表小区.csv"
REFERENCE_HTML = ROOT / "reference_dashboard" / "Dashboard3_加权推荐_reference.html"
OUT = ROOT / "tableau_output"
HYPER = OUT / "D3_加权推荐_v3.hyper"
TWBX = OUT / "D3_加权推荐_v3.twbx"

HOUSING_COLUMNS = [
    ("房源ID", SqlType.text()), ("记录类型", SqlType.text()), ("区", SqlType.text()), ("街道", SqlType.text()),
    ("小区", SqlType.text()), ("区域", SqlType.text()), ("价格", SqlType.double()),
    ("面积", SqlType.double()), ("单价", SqlType.double()), ("朝向", SqlType.text()),
    ("装修", SqlType.text()), ("楼层位置", SqlType.text()), ("建造年份", SqlType.double()),
    ("经度", SqlType.double()), ("纬度", SqlType.double()), ("最近地铁站", SqlType.text()),
    ("步行时间_分钟", SqlType.double()), ("学校_500米", SqlType.double()),
    ("医院_500米", SqlType.double()), ("挂牌数", SqlType.big_int()), ("中位单价", SqlType.double()),
    ("教育基础分", SqlType.double()), ("医疗基础分", SqlType.double()), ("交通基础分", SqlType.double()),
]


def clean_text(value: str | None) -> str | None:
    value = (value or "").strip()
    return value or None


def number(value: str | None) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    value = clean_text(value)
    return float(value) if value is not None else None


def integer(value: str | None) -> int | None:
    if isinstance(value, (int, float)):
        return int(value)
    value = clean_text(value)
    return int(float(value)) if value is not None else None


def read_community_metrics() -> dict[tuple[str, str], dict[str, str]]:
    records: list[dict[str, str]] = []
    with COMMUNITY_CSV.open("r", encoding="utf-8-sig", newline="") as source:
        records = list(csv.DictReader(source))
    extrema: dict[str, dict[str, tuple[float, float]]] = {}
    for district in {record["区"].strip() for record in records}:
        district_rows = [record for record in records if record["区"].strip() == district]
        extrema[district] = {}
        for field in ("学校_500米", "医院_500米", "步行时间_分钟"):
            values = [float(record[field]) for record in district_rows if clean_text(record.get(field)) is not None]
            extrema[district][field] = (min(values), max(values))
    metrics: dict[tuple[str, str], dict[str, str]] = {}
    for record in records:
        district = record["区"].strip()
        for source_field, score_field, reverse in (
            ("学校_500米", "教育基础分", False),
            ("医院_500米", "医疗基础分", False),
            ("步行时间_分钟", "交通基础分", True),
        ):
            value = float(record[source_field])
            minimum, maximum = extrema[district][source_field]
            score = 50.0 if maximum == minimum else 100.0 * ((maximum - value) if reverse else (value - minimum)) / (maximum - minimum)
            record[score_field] = str(score)
        metrics[(district, record["小区"].strip())] = record
    return metrics


def housing_rows() -> list[list[object]]:
    metrics = read_community_metrics()
    rows: list[list[object]] = []
    with LISTING_CSV.open("r", encoding="utf-8-sig", newline="") as source:
        for listing_id, record in enumerate(csv.DictReader(source), start=1):
            key = ((record.get("区") or "").strip(), (record.get("小区") or "").strip())
            merged = dict(record)
            merged["记录类型"] = "房源"
            metric = metrics.get(key, {})
            for field in ("经度", "纬度", "学校_500米", "医院_500米", "挂牌数", "中位单价", "教育基础分", "医疗基础分", "交通基础分"):
                if metric.get(field) not in (None, ""):
                    merged[field] = metric[field]
            row: list[object] = []
            for name, sql_type in HOUSING_COLUMNS:
                if name == "房源ID":
                    row.append(str(listing_id))
                elif sql_type == SqlType.text():
                    row.append(clean_text(merged.get(name)))
                elif sql_type == SqlType.big_int():
                    row.append(integer(merged.get(name)))
                else:
                    row.append(number(merged.get(name)))
            rows.append(row)
    for point_id, (district, longitude, latitude) in enumerate(boundary_points(), start=1):
        boundary = {
            "房源ID": f"B{point_id}", "记录类型": "区界", "区": district,
            "小区": "行政区边界", "经度": longitude, "纬度": latitude,
        }
        row = []
        for name, sql_type in HOUSING_COLUMNS:
            value = boundary.get(name)
            if sql_type == SqlType.text():
                row.append(clean_text(value))
            elif sql_type == SqlType.big_int():
                row.append(integer(value))
            else:
                row.append(number(value))
        rows.append(row)
    return rows


def boundary_points() -> list[tuple[str, float, float]]:
    html = REFERENCE_HTML.read_text(encoding="utf-8")
    match = re.search(r"\bGEO\s*=\s*(\{.*?\})\s*;\s*echarts\.registerMap\('sh',\s*GEO\)", html, re.S)
    if not match:
        raise ValueError("Shanghai GeoJSON was not found in the reference HTML")
    geojson = json.loads(match.group(1))
    points: list[tuple[str, float, float]] = []
    for feature in geojson["features"]:
        district = feature.get("properties", {}).get("区")
        geometry = feature.get("geometry", {})
        polygons = geometry.get("coordinates", [])
        if geometry.get("type") == "Polygon":
            polygons = [polygons]
        for polygon in polygons:
            for ring in polygon:
                for coordinate in ring:
                    points.append((district, float(coordinate[0]), float(coordinate[1])))
    return points


def build_hyper() -> None:
    housing = TableDefinition(TableName("Extract", "HousingData"), [TableDefinition.Column(n, t, Nullability.NULLABLE) for n, t in HOUSING_COLUMNS])
    with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as process:
        with Connection(process.endpoint, HYPER, CreateMode.CREATE_AND_REPLACE) as connection:
            connection.catalog.create_schema("Extract")
            connection.catalog.create_table(housing)
            with Inserter(connection, housing) as inserter:
                inserter.add_rows(housing_rows())
                inserter.execute()


def add_fields(editor: TWBEditor) -> None:
    for name, default in (("教育权重", "33.0"), ("医疗权重", "33.0"), ("交通权重", "34.0")):
        editor.add_parameter(name, datatype="real", default_value=default, domain_type="range", min_value="0.0", max_value="100.0", granularity="1.0")
    editor.add_calculated_field("教育分", "FLOAT([教育基础分])", default_format="n0")
    editor.add_calculated_field("医疗分", "FLOAT([医疗基础分])", default_format="n0")
    editor.add_calculated_field("交通分", "FLOAT([交通基础分])", default_format="n0")
    editor.add_calculated_field(
        "综合推荐分",
        "IF [教育权重] + [医疗权重] + [交通权重] = 0 THEN 0.0 ELSE ("
        + "FLOAT([教育基础分]) * FLOAT([教育权重]) + "
        + "FLOAT([医疗基础分]) * FLOAT([医疗权重]) + "
        + "FLOAT([交通基础分]) * FLOAT([交通权重])) / FLOAT([教育权重] + [医疗权重] + [交通权重]) END",
        default_format="n0",
    )
    editor.add_calculated_field("总分", "[综合推荐分]", default_format="n0")
    editor.add_calculated_field("房源编号", "STR([房源ID])", datatype="string", role="dimension", field_type="nominal")
    editor.add_calculated_field("地图标识", "IF [记录类型] = '区界' THEN [房源编号] ELSE [小区] END", datatype="string", role="dimension", field_type="nominal")
    editor.add_calculated_field("地图颜色分", "IF [记录类型] = '区界' THEN 0 ELSE [总分] END", default_format="n1")
    editor.add_calculated_field("地图大小", "IF [记录类型] = '区界' THEN 1 ELSE [挂牌数] END", default_format="n0")
    editor.add_calculated_field("位置", "MAKEPOINT([纬度], [经度])", datatype="spatial", role="dimension", field_type="nominal")


def build_workbook() -> None:
    editor = TWBEditor("")
    editor.set_hyper_connection(
        str(HYPER),
        tables=[{"name": "HousingData", "table": "HousingData"}],
    )
    add_fields(editor)
    for worksheet in ("小区综合得分地图", "推荐排名表", "房源明细"):
        editor.add_worksheet(worksheet)
    district_filter = [{"column": "区", "type": "categorical", "values": ["黄浦"], "ui_domain": "relevant"}]
    editor.configure_chart(
        "小区综合得分地图", mark_type="Map", geographic_field="位置", color="AVG(地图颜色分)", size="AVG(地图大小)", detail="地图标识",
        tooltip=["小区", "区", "记录类型", "AVG(总分)", "AVG(教育分)", "AVG(医疗分)", "AVG(交通分)", "AVG(中位单价)", "AVG(挂牌数)"], filters=district_filter,
    )
    editor.configure_worksheet_style(
        "小区综合得分地图", background_color="#eaf0f4", hide_gridlines=True, hide_zeroline=True, hide_borders=True,
        map_style={"map_style": "light", "washout": 55},
        color_style={"field": "AVG(地图颜色分)", "colors": ["#6f8796", "#f18f5b", "#df4e3f", "#9e1b32"], "min": 0, "max": 100},
    )

    editor.configure_chart(
        "推荐排名表", mark_type="Text", rows=["小区"],
        measure_values=["AVG(总分)", "AVG(中位单价)", "AVG(挂牌数)"],
        detail="区",
        tooltip=["小区", "街道", "最近地铁站", "AVG(步行时间_分钟)", "AVG(中位单价)", "AVG(挂牌数)"],
        filters=district_filter + [{"column": "记录类型", "type": "categorical", "values": ["房源"]}],
    )
    editor.configure_worksheet_style("推荐排名表", background_color="#ffffff", hide_gridlines=True, hide_zeroline=True, hide_borders=False)

    editor.configure_chart(
        "房源明细", mark_type="Text", rows=["小区", "房源编号"],
        measure_values=["AVG(单价)", "AVG(价格)", "AVG(面积)", "AVG(步行时间_分钟)"], detail="街道",
        tooltip=["小区", "街道", "价格", "面积", "单价", "朝向", "装修", "楼层位置", "最近地铁站", "步行时间_分钟"],
        filters=district_filter + [{"column": "记录类型", "type": "categorical", "values": ["房源"]}],
    )
    editor.configure_worksheet_style("房源明细", background_color="#ffffff", hide_gridlines=True, hide_zeroline=True, hide_borders=False)
    editor.link_worksheet_filters("区", ["小区综合得分地图", "推荐排名表", "房源明细"])

    layout = {
        "type": "container", "direction": "vertical", "style": {"background-color": "#eef3f6"}, "children": [
            {"type": "text", "fixed_size": 66, "style": {"background-color": "#09263a"}, "runs": [
                {"text": "Dashboard 3 · 小区加权推荐", "bold": True, "font_size": 22, "font_color": "#ffffff"},
                {"text": "\n上海二手房 V3 · 区内标准化评分 · 选择区后地图高亮并更新排名与房源", "font_size": 10, "font_color": "#a9c7d8"},
            ]},
            {"type": "container", "direction": "horizontal", "fixed_size": 62, "style": {"background-color": "#dce8ef"}, "children": [
                {"type": "filter", "worksheet": "推荐排名表", "field": "区", "caption": "选择区", "show_title": True, "mode": "dropdown", "values": "relevant", "show_all": False, "style": {"background-color": "#dce8ef"}},
                {"type": "paramctrl", "parameter": "教育权重", "caption": "教育权重", "show_title": True, "style": {"background-color": "#dce8ef"}},
                {"type": "paramctrl", "parameter": "医疗权重", "caption": "医疗权重", "show_title": True, "style": {"background-color": "#dce8ef"}},
                {"type": "paramctrl", "parameter": "交通权重", "caption": "交通权重", "show_title": True, "style": {"background-color": "#dce8ef"}},
            ]},
            {"type": "container", "direction": "horizontal", "fixed_size": 465, "style": {"background-color": "#eef3f6"}, "children": [
                {"type": "container", "direction": "vertical", "fixed_size": 900, "style": {"background-color": "#ffffff"}, "children": [
                    {"type": "text", "fixed_size": 46, "style": {"background-color": "#ffffff"}, "runs": [
                        {"text": "① 所选区与小区得分", "bold": True, "font_size": 14, "font_color": "#16374b"},
                        {"text": "\n灰蓝点=行政区边界；暖色点=小区得分，大小=挂牌数", "font_size": 9, "font_color": "#607d8b"},
                    ]},
                    {"type": "worksheet", "name": "小区综合得分地图", "show_title": False, "fit": "entire", "style": {"background-color": "#ffffff"}},
                ]},
                {"type": "container", "direction": "vertical", "weight": 7, "style": {"background-color": "#ffffff"}, "children": [
                    {"type": "text", "fixed_size": 46, "style": {"background-color": "#ffffff"}, "runs": [
                        {"text": "② 推荐排名", "bold": True, "font_size": 14, "font_color": "#16374b"},
                        {"text": "\n点击总分列头可降序 · 点击任一小区联动房源明细", "font_size": 9, "font_color": "#607d8b"},
                    ]},
                    {"type": "worksheet", "name": "推荐排名表", "show_title": False, "fit": "width", "style": {"background-color": "#ffffff"}},
                ]},
            ]},
            {"type": "container", "direction": "vertical", "fixed_size": 245, "style": {"background-color": "#ffffff"}, "children": [
                {"type": "text", "fixed_size": 42, "style": {"background-color": "#ffffff"}, "runs": [
                    {"text": "③ 房源明细", "bold": True, "font_size": 14, "font_color": "#16374b"},
                    {"text": " · 默认显示所选区房源；点击地图或排名后缩小到对应小区", "font_size": 9, "font_color": "#607d8b"},
                ]},
                {"type": "worksheet", "name": "房源明细", "show_title": False, "fit": "width", "style": {"background-color": "#ffffff"}},
            ]},
            {"type": "text", "fixed_size": 62, "style": {"background-color": "#09263a"}, "runs": [
                {"text": "评分方法：所选区内 min-max 归一化；教育、医疗越多分越高，交通按到最近地铁站步行时间反向计分。权重按总和归一化。", "font_size": 9, "font_color": "#b9d0dd"},
                {"text": "\n口径：学校与医院为 500m 内设施数量，仅代表设施密度，不代表教育/医疗质量或学区资格。", "font_size": 9, "font_color": "#f1b48b"},
            ]},
        ],
    }
    dashboard = "Dashboard 3 · 小区加权推荐"
    editor.add_dashboard(dashboard, width=1600, height=900, layout=layout, worksheet_names=["小区综合得分地图", "推荐排名表", "房源明细"])
    for source in ("小区综合得分地图", "推荐排名表"):
        editor.add_dashboard_action(dashboard, "filter", source_sheet=source, target_sheet="房源明细", field_mappings={"区": "区", "小区": "小区"}, caption=f"{source} → 房源明细", clear_behavior="show-all")
    editor.set_active_dashboard(dashboard)
    for worksheet in ("小区综合得分地图", "推荐排名表", "房源明细"):
        editor.set_worksheet_hidden(worksheet, hidden=True)
    editor.save(TWBX, validate=True)
    repair_unicode_field_metadata()


def repair_unicode_field_metadata() -> None:
    numeric_fields = {
        "价格", "面积", "单价", "建造年份", "经度", "纬度", "步行时间_分钟",
        "学校_500米", "医院_500米", "挂牌数", "中位单价",
        "教育基础分", "医疗基础分", "交通基础分",
    }
    with zipfile.ZipFile(TWBX, "r") as source:
        members = {name: source.read(name) for name in source.namelist()}
    twb_name = next(name for name in members if name.lower().endswith(".twb"))
    root = etree.fromstring(members[twb_name])
    for shelf_sorts in root.findall(".//shelf-sorts"):
        parent = shelf_sorts.getparent()
        if parent is not None:
            parent.remove(shelf_sorts)
    for column in root.findall(".//column"):
        field_name = (column.get("name") or "").strip("[]")
        if field_name in numeric_fields:
            column.set("datatype", "real")
            column.set("role", "measure")
            column.set("type", "quantitative")
        elif field_name == "房源ID":
            column.set("datatype", "string")
            column.set("role", "dimension")
            column.set("type", "nominal")
    members[twb_name] = etree.tostring(root, encoding="utf-8", xml_declaration=True)
    temporary = TWBX.with_suffix(".repairing.twbx")
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as target:
        for name, data in members.items():
            target.writestr(name, data)
    temporary.replace(TWBX)


def main() -> None:
    for required in (COMMUNITY_CSV, LISTING_CSV, REFERENCE_HTML):
        if not required.exists():
            raise FileNotFoundError(f"Required source is missing: {required}")
    OUT.mkdir(exist_ok=True)
    if TWBX.exists() or HYPER.exists():
        raise FileExistsError("Refusing to overwrite an existing Tableau v3 output")
    build_hyper()
    build_workbook()
    print(TWBX)


if __name__ == "__main__":
    main()
