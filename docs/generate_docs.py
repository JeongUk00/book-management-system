import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib import font_manager
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Windows 한글 폰트 설정
_korean_fonts = ['Malgun Gothic', 'NanumGothic', 'AppleGothic', 'DejaVu Sans']
for _f in _korean_fonts:
    if any(_f.lower() in fm.name.lower() for fm in font_manager.fontManager.ttflist):
        matplotlib.rcParams['font.family'] = _f
        break
matplotlib.rcParams['axes.unicode_minus'] = False

# ────────────────────────────────────────────────────────────
# 1. ERD
# ────────────────────────────────────────────────────────────
def draw_erd():
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis('off')
    fig.patch.set_facecolor('#F8F9FA')

    # Entity box
    box_x, box_y, box_w, box_h = 2.5, 0.8, 5, 5.4
    header_h = 0.7

    # Shadow
    shadow = FancyBboxPatch((box_x + 0.08, box_y - 0.08), box_w, box_h,
                             boxstyle="round,pad=0.05", linewidth=0,
                             facecolor='#CED4DA', zorder=1)
    ax.add_patch(shadow)

    # Body
    body = FancyBboxPatch((box_x, box_y), box_w, box_h,
                           boxstyle="round,pad=0.05", linewidth=1.5,
                           edgecolor='#495057', facecolor='white', zorder=2)
    ax.add_patch(body)

    # Header
    header = FancyBboxPatch((box_x, box_y + box_h - header_h), box_w, header_h,
                             boxstyle="round,pad=0.05", linewidth=0,
                             facecolor='#4263EB', zorder=3)
    ax.add_patch(header)

    ax.text(box_x + box_w / 2, box_y + box_h - header_h / 2, 'BOOK',
            ha='center', va='center', fontsize=16, fontweight='bold',
            color='white', zorder=4)

    # Fields
    fields = [
        ('PK', 'id',             'BIGINT',        'AUTO_INCREMENT'),
        ('',   'title',          'VARCHAR(255)',   'NOT NULL'),
        ('',   'author',         'VARCHAR(255)',   'NOT NULL'),
        ('',   'content',        'TEXT',           'nullable'),
        ('',   'cover_image_url','TEXT',           'nullable'),
        ('',   'created_at',     'TIMESTAMP',      'auto @CreationTimestamp'),
        ('',   'updated_at',     'TIMESTAMP',      'auto @UpdateTimestamp'),
    ]

    col_x = [box_x + 0.15, box_x + 0.65, box_x + 2.2, box_x + 3.8]
    row_start_y = box_y + box_h - header_h - 0.1
    row_h = 0.62

    # Column headers
    for cx, label in zip(col_x, ['Key', 'Field', 'Type', 'Constraint']):
        ax.text(cx, row_start_y - 0.3, label,
                fontsize=7.5, color='#868E96', fontweight='bold', zorder=4)

    # Divider under column headers
    ax.plot([box_x + 0.1, box_x + box_w - 0.1],
            [row_start_y - 0.48, row_start_y - 0.48],
            color='#DEE2E6', linewidth=0.8, zorder=4)

    for i, (key, name, dtype, constraint) in enumerate(fields):
        y = row_start_y - 0.62 - i * row_h

        # Alternate row shading
        if i % 2 == 0:
            ax.add_patch(plt.Rectangle((box_x + 0.05, y - 0.22), box_w - 0.1, row_h - 0.05,
                                        facecolor='#F1F3F5', linewidth=0, zorder=2))

        # PK badge
        if key == 'PK':
            badge = FancyBboxPatch((col_x[0] - 0.02, y - 0.16), 0.42, 0.32,
                                   boxstyle="round,pad=0.03", linewidth=0,
                                   facecolor='#FFD43B', zorder=4)
            ax.add_patch(badge)
            ax.text(col_x[0] + 0.19, y, 'PK',
                    ha='center', va='center', fontsize=7, fontweight='bold',
                    color='#664D03', zorder=5)

        ax.text(col_x[1], y, name, fontsize=9, va='center',
                color='#212529', fontweight='bold' if key == 'PK' else 'normal', zorder=4)
        ax.text(col_x[2], y, dtype, fontsize=8.5, va='center', color='#1971C2', zorder=4)
        ax.text(col_x[3], y, constraint, fontsize=7.5, va='center', color='#868E96', zorder=4)

    ax.set_title('Book Entity — ERD', fontsize=14, fontweight='bold',
                 color='#212529', pad=12)

    out = os.path.join(OUTPUT_DIR, 'erd.png')
    plt.tight_layout()
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print(f'Saved: {out}')


# ────────────────────────────────────────────────────────────
# 2. API 명세서
# ────────────────────────────────────────────────────────────
def draw_api_spec():
    rows = [
        ('#', 'Method', 'Endpoint',          'Request Body',                      'Response',          'Description'),
        ('1', 'GET',    '/books',             '—',                                 '200 + Book[]',      '도서 목록 조회'),
        ('2', 'GET',    '/books/{id}',        '—',                                 '200 + Book',        '도서 상세 조회'),
        ('3', 'POST',   '/books',             'title*, author*, content',          '201 + Book',        '도서 등록'),
        ('4', 'PATCH',  '/books/{id}',        'title?, author?, content?',         '200 + Book',        '도서 부분 수정'),
        ('5', 'DELETE', '/books/{id}',        '—',                                 '204 No Content',    '도서 삭제'),
        ('6', 'PATCH',  '/books/{id}/cover',  'coverImageUrl',                     '200 + Book',        'AI 표지 URL 저장'),
    ]

    method_colors = {
        'GET':    '#2F9E44',
        'POST':   '#1971C2',
        'PATCH':  '#E67700',
        'DELETE': '#C92A2A',
    }

    col_w   = [0.4, 0.7, 2.0, 2.6, 1.5, 2.1]
    col_x   = [0]
    for w in col_w[:-1]:
        col_x.append(col_x[-1] + w)
    total_w = sum(col_w)

    row_h   = 0.52
    fig_w   = total_w + 1.2
    fig_h   = len(rows) * row_h + 2.0

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, total_w)
    ax.set_ylim(0, len(rows) * row_h)
    ax.axis('off')
    fig.patch.set_facecolor('#F8F9FA')

    for r_idx, row in enumerate(rows):
        y_bottom = (len(rows) - r_idx - 1) * row_h
        is_header = r_idx == 0

        bg = '#4263EB' if is_header else ('#FFFFFF' if r_idx % 2 == 1 else '#F1F3F5')
        ax.add_patch(plt.Rectangle((0, y_bottom), total_w, row_h,
                                    facecolor=bg, linewidth=0, zorder=1))

        for c_idx, (cell, cx, cw) in enumerate(zip(row, col_x, col_w)):
            text_x = cx + 0.08
            text_y = y_bottom + row_h / 2

            if is_header:
                ax.text(text_x, text_y, cell, fontsize=9, fontweight='bold',
                        color='white', va='center', zorder=3)
            elif c_idx == 1 and cell in method_colors:
                badge = FancyBboxPatch((cx + 0.05, y_bottom + 0.1), cw - 0.1, row_h - 0.2,
                                       boxstyle="round,pad=0.04", linewidth=0,
                                       facecolor=method_colors[cell], zorder=2)
                ax.add_patch(badge)
                ax.text(cx + cw / 2, text_y, cell, fontsize=8, fontweight='bold',
                        color='white', ha='center', va='center', zorder=3)
            else:
                color = '#495057' if c_idx != 2 else '#1971C2'
                ax.text(text_x, text_y, cell, fontsize=8,
                        color=color, va='center', zorder=3)

        # Row border
        ax.plot([0, total_w], [y_bottom, y_bottom], color='#DEE2E6', linewidth=0.5, zorder=2)

    # Outer border
    ax.add_patch(plt.Rectangle((0, 0), total_w, len(rows) * row_h,
                                 fill=False, edgecolor='#ADB5BD', linewidth=1.5, zorder=4))

    # Column separators
    for cx in col_x[1:]:
        ax.plot([cx, cx], [0, len(rows) * row_h], color='#DEE2E6', linewidth=0.5, zorder=3)

    # Error responses note
    note = '* 필수 필드   ? 선택 필드   |   오류 응답: 404 (도서 없음) · 400 (검증 실패)'
    fig.text(0.5, 0.02, note, ha='center', fontsize=8, color='#868E96')

    ax.set_title('API 명세서 — Book Manager REST API', fontsize=13,
                 fontweight='bold', color='#212529', pad=10)

    out = os.path.join(OUTPUT_DIR, 'api_spec.png')
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print(f'Saved: {out}')


if __name__ == '__main__':
    draw_erd()
    draw_api_spec()
    print('Done.')
