import streamlit as st
import io
import sys

# --- 1. ライブラリのインポートチェック ---
try:
    import boxes
    from boxes.box_maker import BoxMaker
    from boxes.finger_joint import FingerJoint
    from boxes.plain import Plain
    from boxes.dxf import Dxf
    from boxes.svg import Svg
    LIB_AVAILABLE = True
except ImportError as e:
    LIB_AVAILABLE = False
    IMPORT_ERROR_MSG = str(e)

# --- 2. ページ設定 ---
st.set_page_config(
    page_title="レーザーカット箱ジェネレーター",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("📦 レーザーカット箱ジェネレーター")

if not LIB_AVAILABLE:
    st.error(f"❌ ライブラリ 'boxes' の読み込みに失敗しました: {IMPORT_ERROR_MSG}")
    st.info("requirements.txt に 'git+https://github.com/florianfesti/boxes.git' が含まれているか確認してください。")
    st.stop()

st.markdown("寸法と素材の厚さを入力し、指接ぎ箱のSVG図面を生成します。")

# --- 3. 入力パラメーターのサイドバー ---
st.sidebar.header("📐 箱の寸法と設定")

size_mode = st.sidebar.radio(
    "寸法の計算基準:",
    ("外寸 (Outer)", "内寸 (Inner)"),
    index=0
)

width = st.sidebar.number_input("幅 (X軸) [mm]", min_value=10, value=100, step=10)
depth = st.sidebar.number_input("奥行き (Y軸) [mm]", min_value=10, value=100, step=10)
height = st.sidebar.number_input("高さ (Z軸) [mm]", min_value=10, value=50, step=10)
thickness = st.sidebar.number_input("素材の厚さ [mm]", min_value=0.5, max_value=20.0, value=3.0, step=0.1)

st.sidebar.subheader("🔗 ジョイント設定")
joint_size = st.sidebar.number_input("指接ぎの長さ [mm]", min_value=2.0, value=8.0, step=1.0)
kerf = st.sidebar.number_input("カーフ補正 [mm]", min_value=0.0, max_value=0.5, value=0.15, step=0.01)
lid_mode = st.sidebar.checkbox("蓋（フタ）を含める", value=False)

# --- 4. 図面生成関数 ---
def generate_box_svg(w, d, h, t, j_s, k, lid):
    try:
        # Boxes.pyのメインクラスを初期化
        box = BoxMaker()
        
        # 基本設定
        box.size = size_mode.lower()
        box.width = w
        box.depth = d
        box.height = h
        box.thickness = t
        box.kerf = k
        
        # 指接ぎの設定
        finger_joint = FingerJoint(size=j_s)
        box.joint = finger_joint
        
        # 蓋の設定
        if lid:
            box.top = finger_joint
        else:
            box.top = Plain()

        # DXFオブジェクトを介してSVGを生成
        dxf_obj = Dxf(box)
        svg_buffer = io.BytesIO()
        Svg(dxf_obj).write(svg_buffer)
        
        return svg_buffer.getvalue()

    except Exception as e:
        st.error(f"図面生成中にエラーが発生しました: {e}")
        return None

# --- 5. メイン画面の実行 ---
if st.button("✨ 図面を生成"):
    with st.spinner('図面を計算中...'):
        svg_data = generate_box_svg(
            w=width, d=depth, h=height, t=thickness, 
            j_s=joint_size, k=kerf, lid=lid_mode
        )
    
    if svg_data:
        st.subheader("✅ 生成結果")
        filename = f"box_{width}x{depth}x{height}mm.svg"
        st.download_button(
            label="⬇️ SVGファイルをダウンロード",
            data=svg_data,
            file_name=filename,
            mime="image/svg+xml"
        )
        st.success("図面が完成しました！")

st.markdown("---")
st.markdown("#### ⚠️ 注意事項")
st.markdown("* カーフ補正（焼き幅）はレーザーの種類や板材に合わせて調整してください。")
st.markdown("* 生成されたSVGは、InkscapeやIllustratorで微調整が可能です。")
