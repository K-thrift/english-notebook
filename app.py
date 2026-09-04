import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(
    page_title="My English Notebook",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# CSS giả lập trang vở học tập
st.markdown(
    """
    <style>
    .notebook-sheet {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 6px solid #e53e3e;
        border-radius: 8px;
        padding: 24px 28px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .page-header {
        font-size: 22px;
        font-weight: 700;
        color: #1a202c;
        margin-bottom: 4px;
    }
    .source-link {
        font-size: 13px;
        color: #718096;
        margin-bottom: 16px;
    }
    .section-title {
        font-size: 15px;
        font-weight: 600;
        color: #2b6cb0;
        margin-top: 14px;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .content-box {
        background: #f7fafc;
        border: 1px solid #edf2f7;
        border-radius: 6px;
        padding: 12px;
        font-family: inherit;
        white-space: pre-wrap;
        line-height: 1.6;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Kết nối Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)


def load_data():
  data = conn.read(ttl=0)
  if data.empty or "page_id" not in data.columns:
    data = pd.DataFrame(
        columns=[
            "page_id",
            "title",
            "source_url",
            "vocab_phonetics",
            "examples",
            "sample_passage",
        ]
    )
  else:
    data["page_id"] = pd.to_numeric(
        data["page_id"], errors="coerce"
    ).fillna(1)
    data = data.sort_values(by="page_id").reset_index(drop=True)
  return data


df = load_data()

# Quản lý số trang hiện tại
max_page = int(df["page_id"].max()) if not df.empty else 1
if "curr_page" not in st.session_state:
  st.session_state.curr_page = 1

# Thanh điều hướng chuyển trang
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
  if st.button("◀ Trang trước") and st.session_state.curr_page > 1:
    st.session_state.curr_page -= 1
    st.rerun()

with col2:
  st.markdown(
      f"<div style='text-align:center; font-weight:600; font-size:16px;'>Trang"
      f" {st.session_state.curr_page} / {max(max_page, st.session_state.curr_page)}</div>",
      unsafe_allow_html=True,
  )

with col3:
  if st.button("Trang sau ▶"):
    st.session_state.curr_page += 1
    st.rerun()

st.divider()

# Tìm dữ liệu trang hiện tại
current_row = df[df["page_id"] == st.session_state.curr_page]
row = current_row.iloc[0] if not current_row.empty else None

tab_read, tab_write = st.tabs(
    ["📖 Đọc bài học", "✏️ Soạn / Sửa bài trang này"]
)

with tab_read:
  if row is not None and pd.notna(row.get("title")):
    st.markdown(
        f"""
        <div class="notebook-sheet">
            <div class="page-header">{row.get('title', '')}</div>
            <div class="source-link">Nguồn trích: <a href="{row.get('source_url', '#')}" target="_blank">{row.get('source_url', 'Không có link')}</a></div>
            
            <div class="section-title">1 & 2. Từ vựng & Phát âm (IPA)</div>
            <div class="content-box">{row.get('vocab_phonetics', '')}</div>
            
            <div class="section-title">3. Câu ví dụ</div>
            <div class="content-box">{row.get('examples', '')}</div>
            
            <div class="section-title">4. Đoạn mẫu từ bài báo</div>
            <div class="content-box" style="background:#fffaf0; border-color:#feebc8;">{row.get('sample_passage', '')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
  else:
    st.info(
        f"Trang {st.session_state.curr_page} hiện đang trống. Hãy qua tab"
        " 'Soạn / Sửa bài' để nhập bài học."
    )

with tab_write:
  with st.form(key=f"edit_form_{st.session_state.curr_page}"):
    title_in = st.text_input(
        "Tiêu đề bài báo", value=row["title"] if row is not None else ""
    )
    url_in = st.text_input(
        "Link nguồn bài báo",
        value=row["source_url"] if row is not None else "",
    )
    vocab_in = st.text_area(
        "1 & 2. Từ vựng và phiên âm",
        value=row["vocab_phonetics"] if row is not None else "",
        height=130,
        placeholder="- resilient /rɪˈzɪl.jənt/ (adj): kiên cường, phục hồi nhanh\n- mitigate /ˈmɪt.ɪ.ɡeɪt/ (v): giảm nhẹ",
    )
    examples_in = st.text_area(
        "3. Các câu ví dụ rút ra",
        value=row["examples"] if row is not None else "",
        height=130,
        placeholder="1. The local community showed resilient spirit.\n2. Steps have been taken to mitigate the risks.",
    )
    passage_in = st.text_area(
        "4. Đoạn văn mẫu nguyên bản",
        value=row["sample_passage"] if row is not None else "",
        height=150,
        placeholder="Dán 2-3 câu hoàn chỉnh chứa ngữ cảnh của bài báo vào đây...",
    )

    btn_save = st.form_submit_button("💾 Lưu trang này vào sổ")

    if btn_save:
      new_data = {
          "page_id": int(st.session_state.curr_page),
          "title": str(title_in),
          "source_url": str(url_in),
          "vocab_phonetics": str(vocab_in),
          "examples": str(examples_in),
          "sample_passage": str(passage_in),
      }

      if row is not None:
        idx = df[df["page_id"] == st.session_state.curr_page].index[0]
        for col, val in new_data.items():
          df.at[idx, col] = val
      else:
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)

      # Cập nhật ngược lại Google Sheets
      conn.update(data=df)
      st.success("Đã lưu trang thành công!")
      st.rerun()
