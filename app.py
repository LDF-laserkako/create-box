import streamlit as st
import io
import sys

# 依存関係が正しくロードされるよう強制的にインポート
try:
    import boxes
    from boxes.box_maker import BoxMaker
    from boxes.finger_joint import FingerJoint
    from boxes.plain import Plain
    from boxes.dxf import Dxf
    from boxes.svg import Svg
except ImportError:
    st.error("ライブラリ 'boxes' の読み込みに失敗しました。requirements.txt が正しく設定されているか確認してください。")

# --- ページ設定 ---
st.set_page_config(
    page_title="レーザーカット箱ジェネレーター",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("📦 レーザーカット箱ジェネレーター")
st.markdown("寸法と素材の厚さを入力し、指接ぎ箱のSVG図面を生成します。")
# 

# --- 1. 入力パラメーターのサイドバー ---
st.sidebar.header("📐 箱の寸法と設定")

# 寸法の入力（内寸または外寸）
size_mode = st.sidebar.radio(
    "寸法の計算基準:",
    ("外寸 (Outer)", "内寸 (Inner)"),
    index=0
)

# ユーザー入力
width = st.sidebar.number_input("幅 (X軸) [mm]", min_value=10, value=100, step=10)
depth = st.sidebar.number_input("奥行き (Y軸) [mm]", min_value=10, value=100, step=10)
height = st.sidebar.number_input("高さ (Z軸) [mm]", min_value=10, value=50, step=10)

# 素材の厚さ
thickness = st.sidebar.number_input("素材の厚さ [mm]", min_value=0.5, max_value=20.0, value=3.0, step=0.1)

# 指接ぎの設定
st.sidebar.subheader("🔗 ジョイント設定")
joint_size = st.sidebar.number_input("指接ぎの長さ [mm]", min_value=2.0, value=8.0, step=1.0)
kerf = st.sidebar.number_input("カーフ補正 [mm]", min_value=0.0, max_value=0.5, value=0.15, step=0.01, help="レーザーの焼き幅による誤差を補正します。通常0.1～0.2mm程度です。")
lid_mode = st.sidebar.checkbox("蓋（フタ）を含める", value=False)


# --- 2. Boxes.pyでの図面生成ロジック ---
def generate_box_svg(w, d, h, t, j_s, k, lid):
    """Boxes.pyを使って箱の図面を生成し、バイトデータとして返す"""
    try:
        # 💡 修正ポイント 2: boxesモジュールから属性としてクラスを直接取得 (boxes.box_maker.BoxMaker() のように)
        
        # Boxes.pyのBoxインスタンスを作成
        BoxMaker = boxes.box_maker.BoxMaker
        box = BoxMaker()
        
        # 寸法を設定
        box.size = size_mode.lower()
        box.width = w
        box.depth = d
        box.height = h
        box.thickness = t
        
        # ジョイントを設定
        FingerJoint = boxes.finger_joint.FingerJoint
        box.joint = FingerJoint(size=j_s)
        
        # カーフを設定
        box.kerf = k
        
        # 蓋の設定
        Plain = boxes.plain.Plain
        if lid:
            box.top = FingerJoint(size=j_s) # 蓋も指接ぎで作成
        else:
            box.top = Plain() # 蓋なし

        # Boxインスタンスを描画
        Dxf = boxes.dxf.Dxf
        dxf_d = Dxf(box)

        # SVGフォーマットに出力
        Svg = boxes.svg.Svg
        svg_buffer = io.BytesIO()
        Svg(dxf_d).write(svg_buffer)
        
        return svg_buffer.getvalue()

    except Exception as e:
        # Streamlitでの表示に配慮
        st.error(f"図面生成中にエラーが発生しました: {e}")
        return None

# --- 3. メイン画面の処理とダウンロードボタン ---
if st.button("✨ 図面を生成"):
    st.subheader("✅ 生成結果")
    
    # ユーザー入力を基にSVGを生成
    svg_data = generate_box_svg(
        w=width, 
        d=depth, 
        h=height, 
        t=thickness, 
        j_s=joint_size, 
        k=kerf, 
        lid=lid_mode
    )
    
    if svg_data:
        # ダウンロードボタンの表示
        filename = f"box_{width}x{depth}x{height}t{thickness}.svg"
        st.download_button(
            label=f"⬇️ {filename} をダウンロード (SVG)",
            data=svg_data,
            file_name=filename,
            mime="image/svg+xml"
        )

        st.success("SVGファイルの生成に成功しました。ダウンロードしてお使いください！")
        
        st.info("生成された図面は、Inkscapeなどのベクターグラフィックソフトで開いて内容を確認してください。")

# --- 4. 注意書きと情報 ---
st.markdown("---")
st.markdown(
    """
    #### ⚠️ 注意事項
    * このアプリはオープンソースライブラリ **Boxes.py** を利用しています。
    * **カーフ補正**は、レーザー機種や素材によって最適な値が異なります。試し切りで確認してください。
    * 生成されたSVGファイルは、レーザーカッターのソフトウェアで読み込み、加工設定を行ってください。
    """
)
