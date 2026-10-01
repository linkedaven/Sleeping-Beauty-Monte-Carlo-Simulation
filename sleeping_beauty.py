import numpy as np
import matplotlib.pyplot as plt

plt.style.use('dark_background')

BG_COLOR = '#1e1e1e'
PANEL_COLOR = '#2b2b2b'
TEXT_COLOR = '#e0e0e0'
GRID_COLOR = '#444444'
ACCENT1 = '#ff9f43'
ACCENT2 = '#54a0ff'
ACCENT3 = '#1dd1a1'

N_TRIALS = 1_000_000

# ----------------------------------------------------------------------
# Simulation
# ----------------------------------------------------------------------
rng = np.random.default_rng()
is_heads = rng.random(N_TRIALS) < 0.5           # True = Heads
n_awakenings_per_trial = np.where(is_heads, 1, 2)

heads_trials = int(is_heads.sum())
tails_trials = N_TRIALS - heads_trials

total_awakenings = int(n_awakenings_per_trial.sum())
heads_awakenings = heads_trials
tails_awakenings = tails_trials * 2

always_heads_correct = heads_awakenings
always_tails_correct = tails_awakenings

# ----------------------------------------------------------------------
# Convergence history: P(Heads | awakened) sampled at log-spaced checkpoints
# ----------------------------------------------------------------------
is_heads_awake = np.repeat(is_heads, n_awakenings_per_trial)  # one entry per awakening
cum_heads = np.cumsum(is_heads_awake)
awake_idx = np.arange(1, total_awakenings + 1)

checkpoints = np.unique(np.round(np.logspace(1, np.log10(total_awakenings), 150)).astype(int))
checkpoints = checkpoints[checkpoints <= total_awakenings]
if checkpoints[-1] != total_awakenings:
    checkpoints = np.append(checkpoints, total_awakenings)

history_x = checkpoints
history_y = cum_heads[checkpoints - 1] / awake_idx[checkpoints - 1]

fig = plt.figure(figsize=(7, 7))
fig.patch.set_facecolor(BG_COLOR)

ax_bar = fig.add_axes([0.07, 0.56, 0.38, 0.36])
ax_conv = fig.add_axes([0.55, 0.56, 0.40, 0.36])
ax_panel = fig.add_axes([0.07, 0.06, 0.88, 0.40])

def style_axis(ax, title):
    ax.set_facecolor(BG_COLOR)
    ax.grid(True, color=GRID_COLOR, alpha=0.4)
    ax.tick_params(colors=TEXT_COLOR, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)
    ax.xaxis.label.set_color(TEXT_COLOR)
    ax.yaxis.label.set_color(TEXT_COLOR)
    ax.title.set_color(TEXT_COLOR)
    ax.set_title(title, fontsize=12)

style_axis(ax_bar, 'Awakenings by Coin Result')
bars = ax_bar.bar(['Heads', 'Tails'], [heads_awakenings, tails_awakenings],
                   color=[ACCENT1, ACCENT2], width=0.5)
for rect, val in zip(bars, [heads_awakenings, tails_awakenings]):
    pct = 100 * val / total_awakenings
    ax_bar.text(rect.get_x() + rect.get_width() / 2, rect.get_height() * 1.02,
                f'{val:,}', ha='center', va='bottom', color=TEXT_COLOR, fontsize=11, fontweight='bold')
    ax_bar.text(rect.get_x() + rect.get_width() / 2, rect.get_height() * 0.5,
                f'{pct:.1f}%', ha='center', va='center', color=BG_COLOR, fontsize=11, fontweight='bold')
ax_bar.set_ylabel('Count of individual awakenings')
ax_bar.set_ylim(0, max(heads_awakenings, tails_awakenings) * 1.15)

style_axis(ax_conv, 'Convergence of P(Heads | awakened)')
ax_conv.set_xscale('log')
ax_conv.plot(history_x, history_y, color=ACCENT1, lw=2)
ax_conv.scatter([history_x[-1]], [history_y[-1]], color=ACCENT1, zorder=5, s=25)
ax_conv.axhline(0.5, color='#888888', lw=1.5, linestyle='--')
ax_conv.axhline(1 / 3, color=ACCENT3, lw=1.5, linestyle='--')
ax_conv.text(total_awakenings, 0.5, 'halfer: 1/2  ', color='#888888', fontsize=9, va='center', ha='right',
             bbox=dict(facecolor=BG_COLOR, edgecolor='none', pad=1))
ax_conv.text(total_awakenings, 1 / 3, 'thirder: 1/3  ', color=ACCENT3, fontsize=9, va='center', ha='right',
             bbox=dict(facecolor=BG_COLOR, edgecolor='none', pad=1))
ax_conv.set_xlabel('Number of awakenings (log scale)')
ax_conv.set_ylabel('P(Heads | awakened)')
ax_conv.set_ylim(0, 1)

ax_panel.set_facecolor(PANEL_COLOR)
ax_panel.set_xticks([]); ax_panel.set_yticks([])
for spine in ax_panel.spines.values():
    spine.set_color(GRID_COLOR)
ax_panel.set_title('Numeric Report', color=TEXT_COLOR, fontsize=13, pad=12)

p_heads_given_awake = heads_awakenings / total_awakenings

left_text = (
    f"Trials (coin flips):  {N_TRIALS:,}\n"
    f"  Heads trials: {heads_trials:,}  ({100*heads_trials/N_TRIALS:.2f}%)\n"
    f"  Tails trials: {tails_trials:,}  ({100*tails_trials/N_TRIALS:.2f}%)\n\n"
    f"Total awakenings:  {total_awakenings:,}\n"
    f"  on Heads-trial: {heads_awakenings:,}  ({100*heads_awakenings/total_awakenings:.2f}%)\n"
    f"  on Tails-trial: {tails_awakenings:,}  ({100*tails_awakenings/total_awakenings:.2f}%)\n\n"
    f"P(Heads | awakened) ~ {p_heads_given_awake:.4f}\n"
    f"  thirder predicts 1/3 = 0.3333\n"
    f"  halfer predicts 1/2 = 0.5"
)

right_text = (
    f"Guessing scorecard (every awakening)\n"
    f"  Always 'Heads': {always_heads_correct:,} / {total_awakenings:,}\n"
    f"    correct ({100*always_heads_correct/total_awakenings:.2f}%)\n"
    f"  Always 'Tails': {always_tails_correct:,} / {total_awakenings:,}\n"
    f"    correct ({100*always_tails_correct/total_awakenings:.2f}%)\n\n"
    f"-> 'Always Tails' wins ~2/3 of awakenings,\n"
    f"   even though the coin is fair."
)

txt_left = ax_panel.text(0.02, 0.92, left_text, transform=ax_panel.transAxes, color=TEXT_COLOR,
                         fontsize=10, va='top', family='monospace', linespacing=1.6)
txt_right = ax_panel.text(0.52, 0.92, right_text, transform=ax_panel.transAxes, color=TEXT_COLOR,
                          fontsize=10, va='top', family='monospace', linespacing=1.6)

def shrink_to_fit(txt, right_edge_axes_frac, min_size=6.0):
    renderer = fig.canvas.get_renderer()
    panel_bb = ax_panel.get_window_extent(renderer)
    limit_x = ax_panel.transAxes.transform((right_edge_axes_frac, 0))[0]
    while txt.get_fontsize() > min_size:
        bb = txt.get_window_extent(renderer)
        if bb.x1 <= limit_x and bb.y0 >= panel_bb.y0 and bb.y1 <= panel_bb.y1:
            break
        txt.set_fontsize(txt.get_fontsize() - 0.25)

fig.canvas.draw()
shrink_to_fit(txt_left, 0.50)
shrink_to_fit(txt_right, 0.98)
common = min(txt_left.get_fontsize(), txt_right.get_fontsize())
txt_left.set_fontsize(common)
txt_right.set_fontsize(common)

fig.suptitle('Sleeping Beauty Simulation', color=TEXT_COLOR, fontsize=18, y=0.985)

def center_window(fig):
    try:
        manager = fig.canvas.manager
        backend = plt.get_backend().lower()
        window = manager.window

        if 'tk' in backend:
            window.update_idletasks()
            width = window.winfo_width()
            height = window.winfo_height()
            if width <= 1 or height <= 1:
                width = window.winfo_reqwidth()
                height = window.winfo_reqheight()
            screen_w = window.winfo_screenwidth()
            screen_h = window.winfo_screenheight()
            x = max(0, (screen_w - width) // 2)
            y = max(0, (screen_h - height) // 2 - 20)   # -20: allow for title bar
            window.geometry(f"{width}x{height}+{x}+{y}")

        elif 'qt' in backend:
            screen = window.screen() if hasattr(window, 'screen') else None
            if screen is None:
                from matplotlib.backends.qt_compat import QtWidgets
                screen = QtWidgets.QApplication.primaryScreen()
            screen_geo = screen.availableGeometry()
            frame_geo = window.frameGeometry()
            frame_geo.moveCenter(screen_geo.center())
            window.move(frame_geo.topLeft())

        elif 'wx' in backend:
            window.CentreOnScreen()

    except Exception:
        pass

_state = {'done': False}

def _center_once(event):
    if _state['done']:
        return
    _state['done'] = True
    fig.canvas.mpl_disconnect(_cid)
    center_window(fig)

_cid = fig.canvas.mpl_connect('draw_event', _center_once)
plt.show()