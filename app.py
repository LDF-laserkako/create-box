import streamlit as st
import io
import sys

# --- 1. ページ設定 ---
st.set_page_config(page_title="レーザーカット箱ジェネレーター", layout="centered")

st.title("📦 レーザーカット箱ジェネレーター")

# --- 2. ライブラリの動的インポートと検証 ---
@st.cache_resource
def load_boxes_engine():
    try:
        import boxes
        # Boxes.pyのメインクラスとジェネレーターを読み込む
        from boxes.generators.box import Box as BoxGenerator
        return True, BoxGenerator, None
    except Exception as e:
        return False, None, str(e)

success, BoxGenerator, error_msg = load_boxes_engine()

if not success:
    st.error(f"❌ ライブラリの構造解析に失敗しました。")
    st.code(f"Error: {error_msg}")
    st.info("requirements.txt を修正して Push し、アプリを再起動してください。")
    st.stop()

# --- 3. UI（サイドバー） ---
st.sidebar.header("📐 箱の寸法と設定")
u_width = st.sidebar.number_input("幅 (x) [mm]", value=100.0)
u_depth = st.sidebar.number_input("奥行 (y) [mm]", value=100.0)
u_height = st.sidebar.number_input("高さ (h) [mm]", value=50.0)
u_thick = st.sidebar.number_input("素材の厚さ [mm]", value=3.0)

st.sidebar.subheader("🔗 詳細設定")
u_kerf = st.sidebar.number_input("カーフ (焼き幅) [mm]", value=0.1, format="%.2f")
u_joint = st.sidebar.number_input("指接ぎの幅 [mm]", value=5.0)

# --- 4. 図面生成ロジック ---
def generate_svg():
    try:
        # Boxes.py のジェネレーターをインスタンス化
        gen = BoxGenerator()
        
        # パラメータを辞書形式で設定
        # Boxes.py の内部変数名に合わせて値を渡します
        params = {
            "x": u_width,
            "y": u_depth,
            "h": u_height,
            "thickness": u_thick,
            "kerf": u_kerf,
            "finger": u_joint,
            "format": "svg"
        }
        
        # 描画用のバッファ
        out = io.BytesIO()
        
        # Boxes.py は標準出力を書き換えてファイル生成することが多いため、
        # 内部メソッドを安全に呼び出します
        gen.render(params, out)
        
        return out.getvalue()
    except Exception as e:
        st.error(f"生成エラー: {e}")
        return None

# --- 5. メイン表示 ---
st.markdown("MakerCaseと同じように、指接ぎ箱のSVG図面を作成します。")

if st.button("✨ 図面を生成"):
    with st.spinner("計算中..."):
        svg_data = generate_svg()
        
        if svg_data:
            st.subheader("✅ 生成完了")
            st.download_button(
                label="⬇️ SVGファイルをダウンロード",
                data=svg_data,
                file_name=f"box_{u_width}x{u_depth}x{u_height}.svg",
                mime="image/svg+xml"
            )
            st.success("ダウンロードしてレーザーカッターでご利用ください！")

st.divider()
st.caption("Powered by Boxes.py & Streamlit")
