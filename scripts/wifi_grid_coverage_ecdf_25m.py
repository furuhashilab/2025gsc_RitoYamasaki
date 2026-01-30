exec(r"""
import os, csv
import processing
from qgis.core import (
    QgsProject, QgsCoordinateReferenceSystem, QgsProcessingFeedback,
    QgsVectorLayer, QgsWkbTypes
)

# =========================
# CONFIG
# =========================
AP_NAME    = "ap_gt_points_6677"
ROADS_NAME = "roads_10m_seg_src"
AOI_NAME   = "aoi"

# プロジェクト(.qgz)ファイルの場所からリポジトリルートを推定
# 例: .../2025gsc_ZemiReport_clean/data/2025_shibuya_wifi_25m_ecdf.qgz
# → PROJ_ROOT = .../2025gsc_ZemiReport_clean
proj_path = QgsProject.instance().fileName()
PROJ_ROOT = os.path.dirname(os.path.dirname(proj_path))

# このリポジトリ内の outputs/ フォルダに出力
OUT_DIR = os.path.join(PROJ_ROOT, "outputs")

CELL_SIZE_M = 25  # ★まずは25m
R_LIST = [5, 10, 15, 20, 25, 35, 45, 50]  # ECDF作りたいr全部

TARGET_CRS = QgsCoordinateReferenceSystem("EPSG:6677")  # meters想定

# =========================
def get_layer(name: str) -> QgsVectorLayer:
    ls = QgsProject.instance().mapLayersByName(name)
    if not ls:
        raise RuntimeError(f"Layer not found: {name}")
    return ls[0]

feedback = QgsProcessingFeedback()

def reproject_if_needed(layer: QgsVectorLayer, target: QgsCoordinateReferenceSystem) -> QgsVectorLayer:
    if layer.crs().authid() == target.authid():
        return layer
    res = processing.run("native:reprojectlayer", {
        "INPUT": layer,
        "TARGET_CRS": target,
        "OUTPUT": "TEMPORARY_OUTPUT"
    }, feedback=feedback)
    return res["OUTPUT"]

def create_grid_clipped(aoi_layer: QgsVectorLayer, cell_m: float) -> QgsVectorLayer:
    # extent = aoiの外接矩形
    ext = aoi_layer.extent()
    grid = processing.run("native:creategrid", {
        "TYPE": 2,  # rectangle (polygon)
        "EXTENT": ext,
        "HSPACING": cell_m,
        "VSPACING": cell_m,
        "HOVERLAY": 0,
        "VOVERLAY": 0,
        "CRS": TARGET_CRS,
        "OUTPUT": "TEMPORARY_OUTPUT"
    }, feedback=feedback)["OUTPUT"]

    # AOIでクリップ（必要なら切り出し）
    clipped = processing.run("native:clip", {
        "INPUT": grid,
        "OVERLAY": aoi_layer,
        "OUTPUT": "TEMPORARY_OUTPUT"
    }, feedback=feedback)["OUTPUT"]

    # grid_id を作る（intersectionで持ち回る用）
    with_id = processing.run("native:fieldcalculator", {
        "INPUT": clipped,
        "FIELD_NAME": "grid_id",
        "FIELD_TYPE": 1,  # Integer
        "FIELD_LENGTH": 10,
        "FIELD_PRECISION": 0,
        "FORMULA": "$id",
        "OUTPUT": "TEMPORARY_OUTPUT"
    }, feedback=feedback)["OUTPUT"]

    return with_id

def buffer_dissolve(ap_layer: QgsVectorLayer, r_m: float) -> QgsVectorLayer:
    # DISSOLVE=True で一つの面に溶かす（高速化）
    return processing.run("native:buffer", {
        "INPUT": ap_layer,
        "DISTANCE": r_m,
        "SEGMENTS": 8,
        "END_CAP_STYLE": 0,
        "JOIN_STYLE": 0,
        "MITER_LIMIT": 2,
        "DISSOLVE": True,
        "OUTPUT": "TEMPORARY_OUTPUT"
    }, feedback=feedback)["OUTPUT"]

def clip_lines_by_poly(lines: QgsVectorLayer, poly: QgsVectorLayer) -> QgsVectorLayer:
    return processing.run("native:clip", {
        "INPUT": lines,
        "OVERLAY": poly,
        "OUTPUT": "TEMPORARY_OUTPUT"
    }, feedback=feedback)["OUTPUT"]

def intersect_lines_with_grid(lines: QgsVectorLayer, grid: QgsVectorLayer) -> QgsVectorLayer:
    # 出力にgrid_idが残るように、OVERLAY_FIELDSにgrid_idを含める
    return processing.run("native:intersection", {
        "INPUT": lines,
        "OVERLAY": grid,
        "INPUT_FIELDS": [],
        "OVERLAY_FIELDS": ["grid_id"],
        "OVERLAY_FIELDS_PREFIX": "",
        "OUTPUT": "TEMPORARY_OUTPUT"
    }, feedback=feedback)["OUTPUT"]

def sum_length_by_gridid(line_layer: QgsVectorLayer) -> dict:
    out = {}
    for f in line_layer.getFeatures():
        gid = f["grid_id"]
        if gid is None:
            continue
        g = f.geometry()
        if g is None or g.isEmpty():
            continue
        # CRSがメートル系なら length()はメートル
        out[gid] = out.get(gid, 0.0) + g.length()
    return out

def write_csv(path, rows, fieldnames):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def ecdf_from_values(values):
    # values: list[float]
    v = sorted(values)
    n = len(v)
    rows = []
    for i, x in enumerate(v, start=1):
        rows.append({"x": x, "ecdf": i / n})
    return rows

# =========================
# MAIN
# =========================
os.makedirs(OUT_DIR, exist_ok=True)

ap   = reproject_if_needed(get_layer(AP_NAME), TARGET_CRS)
roads= reproject_if_needed(get_layer(ROADS_NAME), TARGET_CRS)
aoi  = reproject_if_needed(get_layer(AOI_NAME), TARGET_CRS)

print("Using layers:")
print("  AP   :", ap.name(), "features=", ap.featureCount())
print("  Roads:", roads.name(), "features=", roads.featureCount())
print("  AOI  :", aoi.name(), "features=", aoi.featureCount())
print("Output :", OUT_DIR)

# 1) Grid作成（25m）
grid = create_grid_clipped(aoi, CELL_SIZE_M)

# プロジェクトに追加（確認したいなら）
QgsProject.instance().addMapLayer(grid)

# 2) total road length per cell（道路×グリッド交差）
roads_x_grid = intersect_lines_with_grid(roads, grid)
total_len = sum_length_by_gridid(roads_x_grid)

cells_with_roads = [gid for gid, L in total_len.items() if L > 0]
print("cells with roads =", len(cells_with_roads))

# 3) rごとに covered length と ratio を作る
ratio_rows = []         # grid_coverage_ratio_by_r.csv 用
ecdf_rows  = []         # ecdf_grid_coverage_ratio.csv 用

for r_m in R_LIST:
    print(f"--- r={r_m}m ---")

    buf = buffer_dissolve(ap, r_m)
    covered_roads = clip_lines_by_poly(roads, buf)
    cov_x_grid = intersect_lines_with_grid(covered_roads, grid)
    covered_len = sum_length_by_gridid(cov_x_grid)

    # ratio rows
    vals = []
    for gid in cells_with_roads:
        Ltot = total_len.get(gid, 0.0)
        Lcov = covered_len.get(gid, 0.0)
        if Ltot <= 0:
            continue
        ratio = Lcov / Ltot
        ratio_rows.append({
            "r": r_m,
            "grid_id": gid,
            "total_len_m": Ltot,
            "covered_len_m": Lcov,
            "coverage_ratio": ratio
        })
        vals.append(ratio)

    # ECDF rows（rごと）
    ec = ecdf_from_values(vals)
    for row in ec:
        ecdf_rows.append({
            "r": r_m,
            "coverage_ratio": row["x"],
            "ecdf": row["ecdf"]
        })

# 4) 書き出し
ratio_csv = os.path.join(OUT_DIR, "grid_coverage_ratio_by_r.csv")
ecdf_csv  = os.path.join(OUT_DIR, "ecdf_grid_coverage_ratio.csv")

write_csv(ratio_csv, ratio_rows, ["r","grid_id","total_len_m","covered_len_m","coverage_ratio"])
write_csv(ecdf_csv,  ecdf_rows,  ["r","coverage_ratio","ecdf"])

print("✅ Done")
print("ratio:", ratio_csv)
print("ecdf :", ecdf_csv)
""")

