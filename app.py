import streamlit as st
import io

# 💡 修正ポイント：必要なクラスを boxes.py のサブモジュールから直接インポートします
from boxes.box_maker import BoxMaker
from boxes.finger_joint import FingerJoint
from boxes.plain import Plain
from boxes.dxf import Dxf
from boxes.svg import Svg

# ... ページ設定やタイトルの部分はそのまま ...
st.set_page_config(
    page_title="レーザーカット箱ジェネレーター",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("📦 レーザーカット箱ジェネレーター")
st.markdown("寸法と素材の厚さを入力し、指接ぎ箱のSVG図面を生成します。")

# ... (サイドバーの入力部分は省略) ...

# --- 2. Boxes.pyでの図面生成ロジック ---
# 💡 修正ポイント：関数内では、インポートしたクラス名（BoxMaker, FingerJointなど）を直接使用します
def generate_box_svg(w, d, h, t, j_s, k, lid):
    """Boxes.pyを使って箱の図面を生成し、バイトデータとして返す"""
    try:
        # Boxes.pyのBoxMakerインスタンスを作成（修正済みのインポートを使用）
        box = BoxMaker()
        
        # 寸法を設定
        box.size = size_mode.lower()
        box.width = w
        box.depth = d
        box.height = h
        box.thickness = t
        
        # ジョイントを設定
        box.joint = FingerJoint(size=j_s) # 修正済みのインポートを使用
        
        # カーフを設定
        box.kerf = k
        
        # 蓋の設定
        if lid:
            box.top = FingerJoint(size=j_s) # 修正済みのインポートを使用
        else:
            box.top = Plain() # 修正済みのインポートを使用

        # Boxインスタンスを描画
        dxf_d = Dxf(box) # 修正済みのインポートを使用

        # SVGフォーマットに出力
        svg_buffer = io.BytesIO()
        Svg(dxf_d).write(svg_buffer) # 修正済みのインポートを使用
        
        return svg_buffer.getvalue()

    except Exception as e:
        # Streamlitでの表示に配慮してエラーメッセージを調整
        st.error(f"図面生成中に内部エラーが発生しました。入力値を確認してください: {e}")
        return None

# ... (メイン画面の処理と注意書きは省略) ...
