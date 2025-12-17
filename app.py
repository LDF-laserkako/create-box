import streamlit as st

# --- ページ設定 ---
st.set_page_config(page_title="レーザーカット箱ジェネレーター", layout="wide")

st.title("📦 レーザーカット箱ジェネレーター (Standalone)")
st.write("外部ライブラリ不要で、確実に動作する指接ぎ箱ジェネレーターです。")

# --- サイドバー：設定 ---
with st.sidebar:
    st.header("📐 寸法設定 (mm)")
    W = st.number_input("幅 (Width)", value=100.0, step=1.0)
    D = st.number_input("奥行 (Depth)", value=100.0, step=1.0)
    H = st.number_input("高さ (Height)", value=50.0, step=1.0)
    T = st.number_input("板厚 (Thickness)", value=3.0, step=0.1)
    
    st.header("🔗 ジョイント設定")
    tab_size = st.number_input("指のサイズ (おおよそ)", value=10.0, step=1.0)
    kerf = st.number_input("カーフ補正 (焼き幅)", value=0.1, step=0.01, format="%.2f")

# --- ロジック：指接ぎのパス生成 ---
def get_finger_path(length, thickness, approx_tab_size, is_tab_start, is_inverted=False):
    """指接ぎのギザギザなラインを生成する"""
    num_tabs = max(1, int(length / (approx_tab_size * 2)))
    actual_tab_size = length / (num_tabs * 2 + 1)
    
    points = [(0, 0)]
    current_x = 0
    
    for i in range(num_tabs * 2 + 1):
        is_tab = (i % 2 == 0) if is_tab_start else (i % 2 != 0)
        h = -thickness if (is_tab ^ is_inverted) else 0
        
        # 垂直に移動
        points.append((current_x, h))
        # 水平に移動
        current_x += actual_tab_size
        points.append((current_x, h))
        
    # 最後を0に戻す
    points.append((current_x, 0))
    return points

def make_panel_svg(w, h, t, tabs_config):
    """1つのパネルを生成する (tabs_config: [top, right, bottom, left] の指接ぎ設定)"""
    # 簡易化のため、ポリラインで描画
    paths = []
    # 各辺の指接ぎを取得 (0:凹, 1:凸)
    # top
    p_top = get_finger_path(w, t, tab_size, tabs_config[0] == 1)
    # right
    p_right = get_finger_path(h, t, tab_size, tabs_config[1] == 1)
    # bottom
    p_bottom = get_finger_path(w, t, tab_size, tabs_config[2] == 1)
    # left
    p_left = get_finger_path(h, t, tab_size, tabs_config[3] == 1)

    svg = f'<g transform="translate(10, 10)">'
    
    # 辺を組み立てる
    # Top
    d = f"M 0,0 " + " ".join([f"L {p[0]},{p[1]}" for p in p_top])
    # Right (回転して接続)
    d += f" M {w},0 " + " ".join([f"L {w-p[1]},{p[0]}" for p in p_right])
    # Bottom
    d += f" M {w},{h} " + " ".join([f"L {w-p[0]},{h+p[1]}" for p in p_bottom])
    # Left
    d += f" M 0,{h} " + " ".join([f"L {p[1]},{h-p[0]}" for p in p_left])
    
    svg += f'<path d="{d}" fill="none" stroke="red" stroke-width="0.5" />'
    svg += f'</g>'
    return svg, w + 20, h + 20

# --- メイン処理 ---
# パネル構成 (0=凹, 1=凸)
# Bottom: [凹, 凹, 凹, 凹]
# Front:  [凹, 凹, 凸, 凹]
# Back:   [凹, 凹, 凸, 凹]
# Left:   [凹, 凸, 凸, 凸]
# Right:  [凹, 凸, 凸, 凸]
# Top:    [凸, 凸, 凸, 凸]

panels = [
    ("Bottom", W, D, [0, 0, 0, 0]),
    ("Front",  W, H, [0, 0, 1, 0]),
    ("Back",   W, H, [0, 0, 1, 0]),
    ("Left",   D, H, [0, 1, 1, 1]),
    ("Right",  D, H, [0, 1, 1, 1]),
    ("Top",    W, D, [1, 1, 1, 1])
]

st.subheader("🛠️ パネルプレビュー")
cols = st.columns(3)

full_svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800" viewBox="0 0 800 800">'
offset_y = 0

for i, (name, pw, ph, cfg) in enumerate(panels):
    panel_svg, view_w, view_h = make_panel_svg(pw, ph, T, cfg)
    with cols[i % 3]:
        st.write(f"**{name}** ({pw}x{ph})")
        st.components.v1.html(f'<svg width="{view_w}" height="{view_h}">{panel_svg}</svg>', height=view_h+20)
    
    full_svg += f'<g transform="translate(50, {offset_y + 50})">{panel_svg}</g>'
    offset_y += ph + 40

full_svg += "</svg>"

st.divider()

# --- ダウンロード ---
st.download_button(
    label="⬇️ SVGファイルをダウンロード",
    data=full_svg,
    file_name=f"box_{W}x{D}x{H}.svg",
    mime="image/svg+xml"
)

st.info("💡 ヒント: この図面はそのままレーザーカッターで読み込めます。赤線がカットラインです。")
