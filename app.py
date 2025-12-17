import streamlit as st
import io
import sys
import os

st.set_page_config(page_title="レーザーカット箱ジェネレーター", layout="centered")
st.title("📦 レーザーカット箱ジェネレーター")

# --- デバッグ情報表示 ---
with st.expander("🛠️ システム診断情報 (エラー時に確認)"):
    st.write(f"Python バージョン: {sys.version}")
    try:
        import boxes
        st.write(f"boxes ライブラリの場所: {boxes.__file__}")
    except Exception as e:
        st.write(f"boxes インポートエラー: {e}")

# --- ライブラリの読み込み試行 ---
try:
    # 💡 内部構造を直接指定してインポート
    import boxes.box_maker
    import boxes.finger_joint
    import boxes.plain
    import boxes.dxf
    import boxes.svg
    
    BoxMaker = boxes.box_maker.BoxMaker
    FingerJoint = boxes.finger_joint.FingerJoint
    Plain = boxes.plain.Plain
    Dxf = boxes.dxf.Dxf
    Svg = boxes.svg.Svg
    LIB_AVAILABLE = True
except Exception as e:
    LIB_AVAILABLE = False
    ERROR_DETAIL = str(e)

if not LIB_AVAILABLE:
    st.error(f"❌ ライブラリの読み込みに失敗しました。")
    st.info(f"詳細エラー: {ERROR_DETAIL}")
    st.warning("【解決策】Streamlit Cloud の 'Manage App' から 'Delete App' を行い、再度デプロイしてください。")
    st.stop()

# --- メイン UI ---
st.markdown("寸法を入力してSVGを生成します。")

with st.sidebar:
    st.header("📐 設定")
    width = st.number_input("幅 (mm)", value=100)
    depth = st.number_input("奥行 (mm)", value=100)
    height = st.number_input("高さ (mm)", value=50)
    thickness = st.number_input("板厚 (mm)", value=3.0)
    kerf = st.number_input("カーフ (mm)", value=0.1)

# --- 生成ロジック ---
if st.button("✨ 図面を生成"):
    try:
        box = BoxMaker()
        box.width, box.depth, box.height = width, depth, height
        box.thickness = thickness
        box.kerf = kerf
        
        # 指接ぎ設定
        fj = FingerJoint(size=8.0)
        box.joint = fj
        box.top = Plain()

        # 描画
        dxf_obj = Dxf(box)
        svg_buffer = io.BytesIO()
        Svg(dxf_obj).write(svg_buffer)
        
        st.success("図面が生成されました！")
        st.download_button(
            label="⬇️ SVGをダウンロード",
            data=svg_buffer.getvalue(),
            file_name="box_design.svg",
            mime="image/svg+xml"
        )
    except Exception as e:
        st.error(f"生成エラー: {e}")
