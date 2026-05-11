import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


CELL = 72
MAX_GRID = 14

PALETTE = {
    "bg": "#eef1f4",
    "panel": "#ffffff",
    "panel_border": "#c8d0da",
    "text": "#1f2933",
    "muted": "#64748b",
    "accent": "#2f80ed",
    "accent_soft": "#d9ebff",
    "tile": "#f8fafc",
    "tile_selected": "#dbeafe",
    "tile_border": "#9fb3c8",
    "tile_selected_border": "#2563eb",
    "board_bg": "#d8dee7",
    "text_area": "#f8fafc",
    "empty": "#f7f7f7",
    "grid": "#777777",
    "solution_text": "#111111",
    "piece_fill": "#ffbd5a",
    "piece_outline": "#4a2b00",
    "danger": "#b91c1c",
}

THEMES = {
    "light": PALETTE,
    "dark": {
        "bg": "#151a21",
        "panel": "#1f2933",
        "panel_border": "#05070a",
        "text": "#e5edf5",
        "muted": "#9aa8b7",
        "accent": "#60a5fa",
        "accent_soft": "#1d3b5f",
        "tile": "#202a35",
        "tile_selected": "#17375e",
        "tile_border": "#05070a",
        "tile_selected_border": "#60a5fa",
        "board_bg": "#111827",
        "text_area": "#0f1720",
        "empty": "#d6dce3",
        "grid": "#05070a",
        "solution_text": "#0b1220",
        "piece_fill": "#f6b352",
        "piece_outline": "#2a1a00",
        "danger": "#f87171",
    },
}

REST_4_TYPE_QUICK_SELECT_IDS = {"4-1", "4-13", "4-14", "4-16"}

COLORS = {
    "empty": "#f7f7f7",
    "blocked": "#151515",
    "A": "#d63b3b",
    "B": "#3b72d6",
    "C": "#35a853",
    "D": "#c253d6",
}

FIXED_COLORS = [
    "#d63b3b",
    "#3b72d6",
    "#35a853",
    "#c253d6",
    "#c2410c",
    "#0f766e",
    "#7c3aed",
    "#be123c",
    "#4d7c0f",
    "#0369a1",
]

SOLUTION_COLORS = [
    "#f4a340",
    "#8e44ad",
    "#2f80ed",
    "#27ae60",
    "#d35400",
    "#16a085",
    "#c0392b",
    "#7f8c8d",
    "#f1c40f",
    "#6c5ce7",
]

# Fill fixed_shape_ids with shape IDs such as ["2-1", "3-4", "4-12"].
# The order maps to 固定1, 固定2, 固定3...
PRESET_FIXED_PIECES = [
    {"id": "lost_radiance", "name": "失落光芒", "en": "Lost Radiance", "fixed_shape_ids": ["2-1", "3-4", "3-3", "4-13"]},
    {"id": "diabolos", "name": "迪亞波羅斯", "en": "Diabolos", "fixed_shape_ids": ["2-2", "3-2", "3-6", "4-1"]},
    {"id": "devils_blood_curse", "name": "惡魔之血詛咒", "en": "Devil's Blood: Curse", "fixed_shape_ids": ["2-2", "3-5", "3-2", "4-16"]},
    {"id": "street_boxer", "name": "街頭拳王", "en": "Street Boxer", "fixed_shape_ids": ["2-1", "3-1", "3-3", "4-14"]},
    {"id": "fireflies_and_the_forest", "name": "森林螢火之心", "en": "Fireflies and the Forest", "fixed_shape_ids": ["2-1", "3-5", "3-4", "4-16"]},
    {"id": "crimson_twin_butterflies", "name": "真紅雙生蝶", "en": "Crimson: Twin Butterflies", "fixed_shape_ids": ["2-2", "3-1", "3-6", "4-14"]},
    {"id": "theas_night_tavern", "name": "緹雅的夜間酒館", "en": "Thea's Night Tavern", "fixed_shape_ids": ["3-1", "3-5", "3-4", "3-2"]},
    {"id": "kingdoms_guard", "name": "守衛王國", "en": "Kingdom's Guard", "fixed_shape_ids": ["3-1", "3-5", "3-3", "3-6"]},
    {"id": "speedy_hedgehog", "name": "音速藍刺蝟", "en": "Speedy Hedgehog", "fixed_shape_ids": ["3-4", "3-2", "3-3", "3-6"]},
    {"id": "quiet_manor", "name": "靜謐山莊", "en": "Quiet Manor", "fixed_shape_ids": ["2-1", "2-2", "4-13", "4-16"]},
    {"id": "shadow_creed", "name": "影之信條", "en": "Shadow Creed", "fixed_shape_ids": ["2-1", "2-2", "4-1", "4-16"]},
    {"id": "tiny_big_adventure", "name": "小小大冒險", "en": "Tiny Big Adventure", "fixed_shape_ids": ["2-1", "2-2", "4-1", "4-14"]},
]


def normalize(cells):
    min_r = min(r for r, _ in cells)
    min_c = min(c for _, c in cells)
    return tuple(sorted((r - min_r, c - min_c) for r, c in cells))


def rotate(cells):
    return normalize((c, -r) for r, c in cells)


def reflect(cells):
    return normalize((r, -c) for r, c in cells)


def variants(cells, allow_rotation=True, allow_reflection=False):
    shapes = {normalize(cells)}
    if allow_reflection:
        shapes.add(reflect(cells))
    if allow_rotation:
        seeds = list(shapes)
        for seed in seeds:
            cur = seed
            for _ in range(3):
                cur = rotate(cur)
                shapes.add(cur)
    return sorted(shapes)


def dims(cells):
    return max(r for r, _ in cells) + 1, max(c for _, c in cells) + 1


def generate_fixed_polyominoes(size):
    shapes = {((0, 0),)}
    for _ in range(1, size):
        next_shapes = set()
        for shape in shapes:
            occupied = set(shape)
            for r, c in shape:
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    n = (r + dr, c + dc)
                    if n not in occupied:
                        next_shapes.add(normalize((*shape, n)))
        shapes = next_shapes
    return sorted(shapes)


class TilingSolver:
    def __init__(
        self,
        rows,
        cols,
        board,
        enabled_shapes,
        required_shapes,
        fixed_placed_shapes,
        allow_rotation,
        allow_reflection,
        max_solutions,
        max_empty_cells=0,
        rest_size_limits=None,
        dedupe_by_piece_set=True,
    ):
        self.rows = rows
        self.cols = cols
        self.board = board
        self.enabled_shapes = enabled_shapes
        self.required_shapes = required_shapes
        self.fixed_placed_shapes = fixed_placed_shapes
        self.allow_rotation = allow_rotation
        self.allow_reflection = allow_reflection
        self.max_solutions = max_solutions
        self.max_empty_cells = max_empty_cells
        self.rest_size_limits = rest_size_limits
        self.dedupe_by_piece_set = dedupe_by_piece_set
        self.solutions = []
        self.solution_keys = set()
        self.candidates_by_cell = {}
        self.required_ids = {piece_id for piece_id, _, _ in required_shapes}

    def shape_group(self, cells):
        return tuple(min(variants(cells, self.allow_rotation, self.allow_reflection)))

    def solve(self):
        open_cells = {
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if self.board[r][c] == "empty"
        }
        required_area = sum(len(shape) for _, _, shape in self.required_shapes)
        if required_area > len(open_cells):
            return self.solutions
        if not open_cells and not self.required_shapes:
            self.solutions.append([])
            return self.solutions

        piece_variants = []
        for shape_id, cells in self.enabled_shapes:
            for variant in variants(cells, self.allow_rotation, self.allow_reflection):
                piece_variants.append(("rest", shape_id, variant))
        for piece_id, shape_id, cells in self.required_shapes:
            for variant in variants(cells, self.allow_rotation, self.allow_reflection):
                piece_variants.append(("required", f"{piece_id}:{shape_id}", variant))

        if not piece_variants and self.max_empty_cells == 0:
            return self.solutions

        candidate_keys = set()
        candidates = []
        for kind, shape_id, shape in piece_variants:
            height, width = dims(shape)
            for r0 in range(self.rows - height + 1):
                for c0 in range(self.cols - width + 1):
                    placed = frozenset((r0 + r, c0 + c) for r, c in shape)
                    key = (kind, shape_id if kind == "required" else "", placed)
                    if placed <= open_cells and key not in candidate_keys:
                        candidate_keys.add(key)
                        candidates.append((kind, shape_id, placed))

        by_cell = {cell: [] for cell in open_cells}
        for candidate in candidates:
            for cell in candidate[2]:
                by_cell[cell].append(candidate)
        self.candidates_by_cell = by_cell

        self._search(open_cells, set(self.required_ids), [], set(), {})
        return self.solutions

    def _search(self, remaining, required_left, placed, empty_cells, rest_size_counts):
        if len(self.solutions) >= self.max_solutions:
            return
        if not remaining:
            if not required_left:
                key = self.solution_key(placed, empty_cells)
                if key not in self.solution_keys:
                    self.solution_keys.add(key)
                    solution = list(placed)
                    for cell in sorted(empty_cells):
                        solution.append(("empty", "空格", frozenset({cell})))
                    self.solutions.append(solution)
            return

        if required_left:
            min_required_cells = 0
            for piece_id, _, shape in self.required_shapes:
                if piece_id in required_left:
                    min_required_cells += len(shape)
            if min_required_cells > len(remaining):
                return

        def usable_options(cell):
            out = []
            for kind, shape_id, cells in self.candidates_by_cell[cell]:
                if not cells <= remaining:
                    continue
                if kind == "required":
                    piece_id = shape_id.split(":", 1)[0]
                    if piece_id not in required_left:
                        continue
                elif self.rest_size_limits is not None:
                    size = len(cells)
                    if rest_size_counts.get(size, 0) >= self.rest_size_limits.get(size, 0):
                        continue
                out.append((kind, shape_id, cells))
            return out

        target = min(remaining, key=lambda cell: len(usable_options(cell)))
        options = usable_options(target)
        if not options and len(empty_cells) >= self.max_empty_cells:
            return

        if len(empty_cells) < self.max_empty_cells:
            required_cells = 0
            for piece_id, _, shape in self.required_shapes:
                if piece_id in required_left:
                    required_cells += len(shape)
            if required_cells <= len(remaining) - 1:
                self._search(remaining - {target}, required_left, placed, empty_cells | {target}, rest_size_counts)

        for kind, shape_id, cells in options:
            next_required = required_left
            next_counts = rest_size_counts
            if kind == "required":
                piece_id = shape_id.split(":", 1)[0]
                next_required = required_left - {piece_id}
            else:
                size = len(cells)
                next_counts = dict(rest_size_counts)
                next_counts[size] = next_counts.get(size, 0) + 1
            placed.append((kind, shape_id, cells))
            self._search(remaining - cells, next_required, placed, empty_cells, next_counts)
            placed.pop()
            if len(self.solutions) >= self.max_solutions:
                return

    def solution_key(self, placed, empty_cells):
        if self.dedupe_by_piece_set:
            parts = [self.normalized_solution_shape_id(shape_id) for shape_id, _ in self.fixed_placed_shapes]
            parts.extend(self.normalized_solution_shape_id(shape_id) for _, shape_id, _ in placed)
            parts.extend("空格" for _ in empty_cells)
            return tuple(sorted(parts))

        parts = [(len(cells), tuple(sorted(cells))) for _, cells in self.fixed_placed_shapes]
        for _, _, cells in placed:
            parts.append((len(cells), tuple(sorted(cells))))
        for cell in empty_cells:
            parts.append((0, (cell,)))
        return tuple(sorted(parts))

    def normalized_solution_shape_id(self, shape_id):
        return shape_id.split(":", 1)[1] if ":" in shape_id else shape_id


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("異環方塊盤面求解器")
        self.resizable(True, True)

        self.rows = tk.IntVar(value=4)
        self.cols = tk.IntVar(value=5)
        self.mode = tk.StringVar(value="blocked")
        self.fixed_slot = tk.IntVar(value=0)
        self.selected_fixed_shape = tk.StringVar(value="")
        self.allow_rotation = tk.BooleanVar(value=False)
        self.allow_reflection = tk.BooleanVar(value=False)
        self.fill_mode = tk.StringVar(value="full")
        self.dedupe_by_piece_set = tk.BooleanVar(value=True)
        self.theme_name = tk.StringVar(value="light")
        self.max_solutions = tk.IntVar(value=500)
        self.solution_index = tk.IntVar(value=0)
        self.active_preset_id = tk.StringVar(value="")

        self.shape_cells = []
        self.shape_by_id = {}
        self.size_by_shape_id = {}
        self.rest_shape_vars = {}
        self.fixed_slots = []
        self.board = []
        self.solutions = []
        self.drag_last_cell = None
        self.dragging_fixed_from_library = False
        self.preset_buttons = {}
        self.suppress_preset_clear = False
        self.palette = THEMES["light"]

        self._build_shapes()
        self.fixed_slots = [self.make_fixed_slot(i) for i in range(4)]
        self._build_ui()
        self.reset_board()

    def make_fixed_slot(self, index):
        mark = chr(ord("A") + index) if index < 26 else f"F{index + 1}"
        return {"label": f"固定{index + 1}", "mark": mark, "shape_id": "", "shape": None, "cells": set()}

    def fixed_marks(self):
        return {slot["mark"] for slot in self.fixed_slots}

    def is_fixed_mark(self, value):
        return value in self.fixed_marks()

    def color_for_mark(self, mark):
        for index, slot in enumerate(self.fixed_slots):
            if slot["mark"] == mark:
                return FIXED_COLORS[index % len(FIXED_COLORS)]
        return COLORS.get(mark, "#dddddd")

    def _build_shapes(self):
        self.shape_cells = []
        for size in (2, 3, 4):
            for idx, shape in enumerate(generate_fixed_polyominoes(size), start=1):
                shape_id = f"{size}-{idx}"
                self.shape_cells.append((size, shape_id, shape))
                self.shape_by_id[shape_id] = (size, shape)
                self.size_by_shape_id[shape_id] = size

    def _build_ui(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        self.style = style
        self.apply_theme(redraw=False)

        root = ttk.Frame(self, padding=10)
        root.grid(row=0, column=0)

        title = ttk.Label(root, text="異環方塊盤面求解器", font=("Microsoft JhengHei UI", 16, "bold"))
        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        ttk.Button(root, text="日/夜模式", command=self.toggle_theme).grid(row=0, column=1, sticky="e", pady=(0, 10))

        left = ttk.Frame(root)
        left.grid(row=1, column=0, sticky="n")
        right = ttk.Frame(root)
        right.grid(row=1, column=1, padx=(12, 0), sticky="n")

        board_bar = ttk.LabelFrame(left, text="盤面")
        board_bar.grid(row=0, column=0, sticky="ew")
        ttk.Label(board_bar, text="列").grid(row=0, column=0)
        self.rows_spinbox = ttk.Spinbox(board_bar, from_=1, to=MAX_GRID, width=4, textvariable=self.rows)
        self.rows_spinbox.grid(row=0, column=1)
        ttk.Label(board_bar, text="欄").grid(row=0, column=2)
        self.cols_spinbox = ttk.Spinbox(board_bar, from_=1, to=MAX_GRID, width=4, textvariable=self.cols)
        self.cols_spinbox.grid(row=0, column=3)
        ttk.Button(board_bar, text="套用尺寸", command=self.reset_board).grid(row=0, column=4, padx=6)
        ttk.Button(board_bar, text="清空", command=self.clear_board).grid(row=0, column=5)
        ttk.Button(board_bar, text="匯入完整設定", command=self.import_config).grid(row=0, column=6, padx=(6, 0))
        ttk.Button(board_bar, text="匯出完整設定", command=self.export_config).grid(row=0, column=7, padx=(6, 0))

        board_view = ttk.Frame(left)
        board_view.grid(row=1, column=0, sticky="nsew", pady=14)
        board_view.grid_columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(board_view, width=self.cols.get() * CELL, height=self.rows.get() * CELL, bg=self.palette["board_bg"], highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="n", pady=(8, 10))
        self.canvas.bind("<Button-1>", self.start_canvas_drag)
        self.canvas.bind("<B1-Motion>", self.drag_on_canvas)
        self.canvas.bind("<ButtonRelease-1>", self.end_canvas_drag)

        mode_box = ttk.LabelFrame(left, text="繪製模式")
        mode_box.grid(row=2, column=0, sticky="ew")
        for i, (label, value) in enumerate(
            (("空格", "empty"), ("黑色不可放", "blocked"), ("放置目前固定方塊", "fixed"))
        ):
            ttk.Radiobutton(mode_box, text=label, value=value, variable=self.mode).grid(row=0, column=i, padx=3)

        preset_box = ttk.LabelFrame(left, text="預設固定方塊")
        preset_box.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        self.preset_frame = ttk.Frame(preset_box)
        self.preset_frame.grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        self.redraw_preset_buttons()

        fixed_box = ttk.LabelFrame(right, text="1. 選固定方塊，點盤面放置")
        fixed_box.grid(row=0, column=0, sticky="nw")
        self.slot_bar = ttk.Frame(fixed_box)
        self.slot_bar.grid(row=0, column=0, sticky="ew")
        self.fixed_slot_buttons = []
        self.plus_fixed_button = None
        self.minus_fixed_button = None
        self.redraw_fixed_slot_buttons()
        self.fixed_status = ttk.Label(fixed_box, text="")
        self.fixed_status.grid(row=1, column=0, sticky="w", pady=(4, 4))

        self.fixed_shape_frame = ttk.Frame(fixed_box)
        self.fixed_shape_frame.grid(row=2, column=0, sticky="w")
        self._draw_fixed_shape_library()

        rest_box = ttk.LabelFrame(right, text="2. 選剩餘可重複使用的方塊")
        rest_box.grid(row=0, column=1, sticky="nw", padx=(10, 0))
        rest_header = ttk.Frame(rest_box)
        rest_header.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        ttk.Label(rest_header, text="方塊方向固定：不旋轉、不鏡像").grid(row=0, column=0, columnspan=3, sticky="w")
        ttk.Radiobutton(rest_header, text="填滿，自動補 2/3/4", value="full", variable=self.fill_mode).grid(row=0, column=3, columnspan=2, sticky="w", padx=(12, 0))
        ttk.Radiobutton(rest_header, text="可空 1 格，只用勾選型", value="allow_one_empty", variable=self.fill_mode).grid(row=0, column=5, columnspan=3, sticky="w", padx=(12, 0))
        for i, size in enumerate((2, 3, 4)):
            text = "4 型全選（4 種）" if size == 4 else f"{size} 型全選"
            ttk.Button(rest_header, text=text, command=lambda s=size: self.select_rest_size(s)).grid(row=1, column=i, padx=(0, 6), pady=(4, 0))
        ttk.Button(rest_header, text="清空", command=self.clear_rest_shapes).grid(row=1, column=3, padx=(0, 6), pady=(4, 0))
        ttk.Button(rest_header, text="全選全部", command=self.select_all_rest_shapes).grid(row=1, column=4, pady=(4, 0))
        self.rest_selection_note = ttk.Label(rest_header, text="")
        self.rest_selection_note.grid(row=2, column=0, columnspan=7, sticky="w", pady=(4, 0))

        self.rest_shape_frame = ttk.Frame(rest_box)
        self.rest_shape_frame.grid(row=1, column=0, sticky="w")
        self._draw_rest_shape_selectors()
        self.update_rest_selection_note()

        action_box = ttk.LabelFrame(right, text="求解")
        action_box.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Label(action_box, text="最多輸出").grid(row=0, column=0)
        self.max_solutions_spinbox = ttk.Spinbox(action_box, from_=1, to=100000, width=8, textvariable=self.max_solutions)
        self.max_solutions_spinbox.grid(row=0, column=1)
        ttk.Button(action_box, text="尋找所有可能", command=self.run_solver).grid(row=0, column=2, padx=6)
        ttk.Button(action_box, text="匯出解答 JSON", command=self.export_json).grid(row=0, column=3)
        ttk.Checkbutton(
            action_box,
            text="只看使用方塊去重",
            variable=self.dedupe_by_piece_set,
        ).grid(row=0, column=4, padx=(10, 0), sticky="w")

        result_bar = ttk.Frame(action_box)
        result_bar.grid(row=1, column=0, columnspan=5, sticky="ew", pady=(8, 0))
        ttk.Button(result_bar, text="上一個", command=lambda: self.move_solution(-1)).grid(row=0, column=0)
        ttk.Button(result_bar, text="下一個", command=lambda: self.move_solution(1)).grid(row=0, column=1)
        self.status = ttk.Label(result_bar, text="尚未求解")
        self.status.grid(row=0, column=2, padx=10)

        self.result_text = tk.Text(
            right,
            width=112,
            height=12,
            wrap="none",
            bg=self.palette["text_area"],
            fg=self.palette["text"],
            insertbackground=self.palette["text"],
            relief="solid",
            bd=1,
        )
        self.result_text.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self.update_fixed_status()

    def toggle_theme(self):
        self.theme_name.set("dark" if self.theme_name.get() == "light" else "light")
        self.apply_theme(redraw=True)

    def apply_theme(self, redraw=True):
        self.palette = THEMES.get(self.theme_name.get(), THEMES["light"])
        self.configure(bg=self.palette["bg"])
        if hasattr(self, "style"):
            self.style.configure(".", font=("Microsoft JhengHei UI", 10), background=self.palette["bg"], foreground=self.palette["text"])
            self.style.configure("TFrame", background=self.palette["bg"])
            self.style.configure("TLabelframe", background=self.palette["bg"], bordercolor=self.palette["panel_border"])
            self.style.configure(
                "TLabelframe.Label",
                background=self.palette["bg"],
                foreground=self.palette["text"],
                font=("Microsoft JhengHei UI", 10, "bold"),
            )
            self.style.configure("TLabel", background=self.palette["bg"], foreground=self.palette["text"])
            self.style.configure("TButton", padding=(10, 5), background=self.palette["tile"], foreground=self.palette["text"])
            self.style.map("TButton", background=[("active", self.palette["tile_selected"])])
            self.style.configure("TRadiobutton", background=self.palette["bg"], foreground=self.palette["text"])
            self.style.configure("TCheckbutton", background=self.palette["bg"], foreground=self.palette["text"])
            self.style.configure(
                "TSpinbox",
                fieldbackground=self.palette["text_area"],
                background=self.palette["tile"],
                foreground=self.palette["text"],
                arrowcolor=self.palette["text"],
                bordercolor=self.palette["panel_border"],
                lightcolor=self.palette["panel_border"],
                darkcolor=self.palette["panel_border"],
                insertcolor=self.palette["text"],
            )
            self.style.map(
                "TSpinbox",
                fieldbackground=[("readonly", self.palette["text_area"]), ("focus", self.palette["text_area"]), ("!disabled", self.palette["text_area"])],
                foreground=[("readonly", self.palette["text"]), ("focus", self.palette["text"]), ("!disabled", self.palette["text"])],
                background=[("readonly", self.palette["tile"]), ("focus", self.palette["tile"]), ("!disabled", self.palette["tile"])],
                arrowcolor=[("readonly", self.palette["text"]), ("focus", self.palette["text"]), ("!disabled", self.palette["text"])],
            )
        if hasattr(self, "canvas"):
            self.canvas.config(bg=self.palette["board_bg"])
        if hasattr(self, "result_text"):
            self.result_text.config(bg=self.palette["text_area"], fg=self.palette["text"], insertbackground=self.palette["text"])
        for spinbox_name in ("rows_spinbox", "cols_spinbox", "max_solutions_spinbox"):
            if hasattr(self, spinbox_name):
                spinbox = getattr(self, spinbox_name)
                spinbox.configure(foreground=self.palette["text"])
                try:
                    spinbox.configure(background=self.palette["text_area"])
                except tk.TclError:
                    pass
        if redraw:
            self.redraw_fixed_slot_buttons()
            self.redraw_preset_buttons()
            self._draw_fixed_shape_library()
            self._draw_rest_shape_selectors()
            self.draw_board()
            self.update_fixed_status()

    def redraw_preset_buttons(self):
        for child in self.preset_frame.winfo_children():
            child.destroy()
        self.preset_buttons = {}
        for index, preset in enumerate(PRESET_FIXED_PIECES):
            row = index // 2
            col = index % 2
            selected = self.active_preset_id.get() == preset["id"]
            text = f"{index + 1}. {preset['name']}\n{preset['en']}"
            bg = self.palette["tile_selected"] if selected else self.palette["tile"]
            border = self.palette["tile_selected_border"] if selected else self.palette["tile_border"]
            btn = tk.Label(
                self.preset_frame,
                text=text,
                justify="left",
                anchor="w",
                padx=10,
                pady=7,
                width=28,
                cursor="hand2",
                bg=bg,
                fg=self.palette["text"],
                relief="solid",
                bd=2 if selected else 1,
                highlightthickness=1,
                highlightbackground=border,
                font=("Microsoft JhengHei UI", 9, "bold" if selected else "normal"),
            )
            btn.grid(row=row, column=col, sticky="ew", padx=4, pady=4)
            btn.bind("<Button-1>", lambda _event, preset_id=preset["id"]: self.apply_fixed_preset(preset_id))
            self.preset_buttons[preset["id"]] = btn

    def apply_fixed_preset(self, preset_id):
        preset = next((item for item in PRESET_FIXED_PIECES if item["id"] == preset_id), None)
        if not preset:
            return
        shape_ids = [shape_id for shape_id in preset["fixed_shape_ids"] if shape_id in self.shape_by_id]
        if not shape_ids:
            self.set_status(f"{preset['name']} 尚未設定 fixed_shape_ids")
            return
        self.suppress_preset_clear = True
        try:
            for slot in self.fixed_slots:
                for r, c in slot["cells"]:
                    if 0 <= r < self.rows.get() and 0 <= c < self.cols.get() and self.board[r][c] == slot["mark"]:
                        self.board[r][c] = "empty"
            self.fixed_slots = [self.make_fixed_slot(i) for i in range(max(4, len(shape_ids)))]
            for i, shape_id in enumerate(shape_ids):
                self.fixed_slots[i]["shape_id"] = shape_id
                self.fixed_slots[i]["shape"] = self.shape_by_id[shape_id][1]
            self.fixed_slot.set(0)
            self.selected_fixed_shape.set(self.fixed_slots[0]["shape_id"])
            self.active_preset_id.set(preset_id)
            self.solutions = []
            self.redraw_fixed_slot_buttons()
            self._draw_fixed_shape_library()
            self.draw_board()
            self.update_fixed_status()
            self.redraw_preset_buttons()
            self.set_status(f"已套用預設：{preset['name']}")
        finally:
            self.suppress_preset_clear = False

    def clear_active_preset(self):
        if self.suppress_preset_clear or not self.active_preset_id.get():
            return
        self.active_preset_id.set("")
        self.redraw_preset_buttons()

    def redraw_fixed_slot_buttons(self):
        for child in self.slot_bar.winfo_children():
            child.destroy()
        self.fixed_slot_buttons = []
        for i, slot in enumerate(self.fixed_slots):
            btn = tk.Label(self.slot_bar, text=slot["label"], padx=10, pady=6, cursor="hand2", font=("Microsoft JhengHei UI", 9, "bold"))
            btn.grid(row=0, column=i, padx=(0, 6), sticky="w")
            btn.bind("<Button-1>", lambda _event, index=i: self.select_fixed_slot(index))
            self.fixed_slot_buttons.append(btn)
        plus = tk.Label(self.slot_bar, text="+", padx=12, pady=6, cursor="hand2", font=("Microsoft JhengHei UI", 12, "bold"))
        plus.grid(row=0, column=len(self.fixed_slots), padx=(2, 0), sticky="w")
        plus.bind("<Button-1>", lambda _event: self.add_fixed_slot())
        self.plus_fixed_button = plus
        minus = tk.Label(self.slot_bar, text="-", padx=13, pady=6, cursor="hand2", font=("Microsoft JhengHei UI", 12, "bold"))
        minus.grid(row=0, column=len(self.fixed_slots) + 1, padx=(6, 0), sticky="w")
        minus.bind("<Button-1>", lambda _event: self.remove_last_fixed_slot())
        self.minus_fixed_button = minus

    def add_fixed_slot(self):
        self.clear_active_preset()
        self.fixed_slots.append(self.make_fixed_slot(len(self.fixed_slots)))
        self.fixed_slot.set(len(self.fixed_slots) - 1)
        self.selected_fixed_shape.set("")
        self.redraw_fixed_slot_buttons()
        self._draw_fixed_shape_library()
        self.update_fixed_status()

    def remove_last_fixed_slot(self):
        self.clear_active_preset()
        if len(self.fixed_slots) <= 1:
            self.clear_current_fixed_shape()
            return
        index = len(self.fixed_slots) - 1
        slot = self.fixed_slots.pop(index)
        for r, c in slot["cells"]:
            if 0 <= r < self.rows.get() and 0 <= c < self.cols.get() and self.board[r][c] == slot["mark"]:
                self.board[r][c] = "empty"
        self.fixed_slot.set(min(self.fixed_slot.get(), len(self.fixed_slots) - 1))
        self.selected_fixed_shape.set(self.fixed_slots[self.fixed_slot.get()]["shape_id"])
        self.solutions = []
        self.redraw_fixed_slot_buttons()
        self._draw_fixed_shape_library()
        self.draw_board()
        self.update_fixed_status()

    def _draw_fixed_shape_library(self):
        for child in self.fixed_shape_frame.winfo_children():
            child.destroy()
        col = 0
        row = 0
        none_tile = self.create_text_tile(
            self.fixed_shape_frame,
            "未選",
            selected=self.selected_fixed_shape.get() == "",
            width=76,
            height=88,
        )
        none_tile.grid(row=row, column=col, padx=4, pady=4)
        none_tile.bind("<Button-1>", lambda _event: self.clear_current_fixed_shape())
        col += 1
        row += 1
        col = 0
        last_size = None
        for size, shape_id, shape in self.shape_cells:
            if last_size != size:
                if last_size is not None and col != 0:
                    row += 1
                ttk.Label(self.fixed_shape_frame, text=f"{size} 型").grid(row=row, column=0, columnspan=6, sticky="w", pady=(6, 2))
                row += 1
                col = 0
                last_size = size
            mini = self.create_shape_tile(
                self.fixed_shape_frame,
                shape_id,
                shape,
                selected=self.selected_fixed_shape.get() == shape_id,
                width=76,
                height=88,
            )
            mini.grid(row=row, column=col, padx=4, pady=4)
            mini.bind("<Button-1>", lambda event, sid=shape_id: self.start_fixed_library_drag(event, sid))
            mini.bind("<B1-Motion>", self.drag_fixed_library)
            mini.bind("<ButtonRelease-1>", self.end_fixed_library_drag)
            col += 1
            if col >= 7:
                col = 0
                row += 1

    def _draw_rest_shape_selectors(self):
        for child in self.rest_shape_frame.winfo_children():
            child.destroy()
        old_values = {shape_id: var.get() for shape_id, var in self.rest_shape_vars.items()}
        self.rest_shape_vars = {}
        col = 0
        row = 0
        last_size = None
        for size, shape_id, shape in self.shape_cells:
            if last_size != size:
                if last_size is not None and col != 0:
                    row += 1
                ttk.Label(self.rest_shape_frame, text=f"{size} 型").grid(row=row, column=0, columnspan=6, sticky="w", pady=(6, 2))
                row += 1
                col = 0
                last_size = size
            var = tk.BooleanVar(value=old_values.get(shape_id, size == 2))
            self.rest_shape_vars[shape_id] = var
            mini = self.create_shape_tile(self.rest_shape_frame, shape_id, shape, selected=var.get(), width=66, height=78)
            mini.grid(row=row, column=col, padx=4, pady=4)
            mini.bind("<Button-1>", lambda _event, sid=shape_id: self.toggle_rest_shape(sid))
            col += 1
            if col >= 7:
                col = 0
                row += 1
        self.update_rest_selection_note()

    def create_shape_tile(self, parent, shape_id, shape, selected=False, width=72, height=84):
        bg = self.palette["tile_selected"] if selected else self.palette["tile"]
        border = self.palette["tile_selected_border"] if selected else self.palette["tile_border"]
        canvas = tk.Canvas(parent, width=width, height=height, bg=bg, highlightthickness=0, cursor="hand2")
        canvas.create_rectangle(2, 2, width - 2, height - 2, fill=bg, outline=border, width=3 if selected else 1)
        canvas.create_text(width / 2, 14, text=shape_id, fill=self.palette["text"], font=("Microsoft JhengHei UI", 9, "bold"))
        self._draw_mini_shape(canvas, shape, top=24)
        if selected:
            canvas.create_rectangle(7, height - 10, width - 7, height - 5, fill=self.palette["accent"], outline="")
        return canvas

    def create_text_tile(self, parent, text, selected=False, width=72, height=84):
        bg = self.palette["tile_selected"] if selected else self.palette["tile"]
        border = self.palette["tile_selected_border"] if selected else self.palette["tile_border"]
        canvas = tk.Canvas(parent, width=width, height=height, bg=bg, highlightthickness=0, cursor="hand2")
        canvas.create_rectangle(2, 2, width - 2, height - 2, fill=bg, outline=border, width=3 if selected else 1)
        canvas.create_text(width / 2, height / 2, text=text, fill=self.palette["muted"], font=("Microsoft JhengHei UI", 11, "bold"))
        if selected:
            canvas.create_rectangle(7, height - 10, width - 7, height - 5, fill=self.palette["accent"], outline="")
        return canvas

    def _draw_mini_shape(self, canvas, shape, top=6):
        h, w = dims(shape)
        canvas_width = int(canvas["width"])
        canvas_height = int(canvas["height"])
        available_height = max(20, canvas_height - top - 14)
        size = min(18, (canvas_width - 18) // max(1, w), available_height // max(1, h))
        ox = (canvas_width - w * size) // 2
        oy = top + (available_height - h * size) // 2
        for r, c in shape:
            canvas.create_rectangle(
                ox + c * size,
                oy + r * size,
                ox + (c + 1) * size,
                oy + (r + 1) * size,
                fill=self.palette["piece_fill"],
                outline=self.palette["piece_outline"],
                width=2,
            )

    def pick_fixed_shape(self, shape_id):
        self.selected_fixed_shape.set(shape_id)
        self.assign_shape_to_current_slot()

    def clear_current_fixed_shape(self):
        self.clear_active_preset()
        slot = self.fixed_slots[self.fixed_slot.get()]
        for r, c in slot["cells"]:
            if self.board[r][c] == slot["mark"]:
                self.board[r][c] = "empty"
        slot["shape_id"] = ""
        slot["shape"] = None
        slot["cells"] = set()
        self.selected_fixed_shape.set("")
        self.solutions = []
        self.draw_board()
        self._draw_fixed_shape_library()
        self.update_fixed_status()

    def select_fixed_slot(self, index):
        if not 0 <= index < len(self.fixed_slots):
            return
        self.fixed_slot.set(index)
        shape_id = self.fixed_slots[index]["shape_id"]
        self.selected_fixed_shape.set(shape_id)
        self._draw_fixed_shape_library()
        self.update_fixed_status()

    def toggle_rest_shape(self, shape_id):
        if shape_id not in self.rest_shape_vars:
            return
        self.rest_shape_vars[shape_id].set(not self.rest_shape_vars[shape_id].get())
        self._draw_rest_shape_selectors()

    def start_fixed_library_drag(self, event, shape_id):
        self.pick_fixed_shape(shape_id)
        self.mode.set("fixed")
        self.dragging_fixed_from_library = True
        self.set_status("拖到盤面後放開即可放置固定方塊")

    def drag_fixed_library(self, event):
        if self.dragging_fixed_from_library:
            self.set_status("拖到盤面後放開即可放置固定方塊")

    def end_fixed_library_drag(self, event):
        if not self.dragging_fixed_from_library:
            return
        self.dragging_fixed_from_library = False
        cell = self.cell_from_root(event.x_root, event.y_root)
        if cell:
            self.place_fixed_shape(*cell)
        else:
            self.set_status("未放到盤面")

    def assign_shape_to_current_slot(self):
        self.clear_active_preset()
        shape_id = self.selected_fixed_shape.get()
        if shape_id == "":
            self.clear_current_fixed_shape()
            return
        if shape_id not in self.shape_by_id:
            return
        _, shape = self.shape_by_id[shape_id]
        slot = self.fixed_slots[self.fixed_slot.get()]
        if slot["cells"] and slot["shape_id"] != shape_id:
            for r, c in slot["cells"]:
                if self.board[r][c] == slot["mark"]:
                    self.board[r][c] = "empty"
            slot["cells"] = set()
            self.solutions = []
        slot["shape_id"] = shape_id
        slot["shape"] = shape
        self.draw_board()
        self._draw_fixed_shape_library()
        self.update_fixed_status()

    def update_fixed_status(self):
        slot = self.fixed_slots[self.fixed_slot.get()]
        selected = slot["shape_id"] or "尚未選擇"
        if not slot["shape_id"]:
            placed = "尚未選固定形狀"
        else:
            placed = "已指定位置" if slot["cells"] else "未指定位置，求解時必須使用"
        self.fixed_status.config(text=f"目前槽位：{slot['label']}，形狀：{selected}，狀態：{placed}")
        for i, item in enumerate(self.fixed_slots):
            shape_text = item["shape_id"] or "未選"
            if not item["shape_id"]:
                place_text = "待選"
            else:
                place_text = "定位" if item["cells"] else "必用"
            selected = i == self.fixed_slot.get()
            self.fixed_slot_buttons[i].config(
                text=f"{item['label']} {shape_text} {place_text}",
                bg=self.palette["accent_soft"] if selected else self.palette["tile"],
                fg=self.palette["text"],
                relief="solid",
                bd=2 if selected else 1,
                highlightthickness=1,
                highlightbackground=self.palette["tile_selected_border"] if selected else self.palette["tile_border"],
            )
        if self.plus_fixed_button:
            self.plus_fixed_button.config(
                bg=self.palette["tile"],
                fg=self.palette["accent"],
                relief="solid",
                bd=1,
                highlightthickness=1,
                highlightbackground=self.palette["tile_border"],
            )
        if self.minus_fixed_button:
            self.minus_fixed_button.config(
                bg=self.palette["tile"],
                fg=self.palette["danger"],
                relief="solid",
                bd=1,
                highlightthickness=1,
                highlightbackground=self.palette["tile_border"],
            )

    def select_rest_size(self, size):
        for shape_size, shape_id, _ in self.shape_cells:
            if shape_size != size:
                continue
            if not self.is_allowed_supplement_shape(shape_size, shape_id):
                continue
            if size == 4:
                self.rest_shape_vars[shape_id].set(shape_id in REST_4_TYPE_QUICK_SELECT_IDS)
            else:
                self.rest_shape_vars[shape_id].set(True)
        self._draw_rest_shape_selectors()

    def select_all_rest_shapes(self):
        for var in self.rest_shape_vars.values():
            var.set(True)
        self._draw_rest_shape_selectors()

    def clear_rest_shapes(self):
        for var in self.rest_shape_vars.values():
            var.set(False)
        self._draw_rest_shape_selectors()

    def update_rest_selection_note(self):
        if not hasattr(self, "rest_selection_note"):
            return
        selected_4 = sorted(
            shape_id
            for shape_id, var in self.rest_shape_vars.items()
            if shape_id.startswith("4-") and var.get()
        )
        quick_4 = sorted(REST_4_TYPE_QUICK_SELECT_IDS)
        if selected_4 == quick_4:
            text = "4 型全選只包含：4-1、4-13、4-14、4-16"
        elif selected_4:
            text = "目前已選 4 型：" + "、".join(selected_4)
        else:
            text = "目前未選 4 型"
        self.rest_selection_note.config(text=text)

    def is_allowed_supplement_shape(self, shape_size, shape_id):
        return shape_size != 4 or shape_id in REST_4_TYPE_QUICK_SELECT_IDS

    def reset_board(self):
        self.rows.set(max(1, min(MAX_GRID, int(self.rows.get()))))
        self.cols.set(max(1, min(MAX_GRID, int(self.cols.get()))))
        self.board = [["empty" for _ in range(self.cols.get())] for _ in range(self.rows.get())]
        for slot in self.fixed_slots:
            slot["cells"] = set()
        self.solutions = []
        self.solution_index.set(0)
        self.draw_board()
        self.update_fixed_status()
        self.set_status("尚未求解")

    def clear_board(self):
        for r in range(self.rows.get()):
            for c in range(self.cols.get()):
                self.board[r][c] = "empty"
        for slot in self.fixed_slots:
            slot["cells"] = set()
        self.solutions = []
        self.draw_board()
        self.update_fixed_status()
        self.set_status("已清空")

    def start_canvas_drag(self, event):
        self.drag_last_cell = None
        self.apply_canvas_action(event)

    def drag_on_canvas(self, event):
        self.apply_canvas_action(event)

    def end_canvas_drag(self, event):
        self.drag_last_cell = None

    def cell_from_root(self, x_root, y_root):
        x = x_root - self.canvas.winfo_rootx()
        y = y_root - self.canvas.winfo_rooty()
        c = x // CELL
        r = y // CELL
        if 0 <= r < self.rows.get() and 0 <= c < self.cols.get():
            return int(r), int(c)
        return None

    def apply_canvas_action(self, event):
        c = event.x // CELL
        r = event.y // CELL
        if 0 <= r < self.rows.get() and 0 <= c < self.cols.get():
            current_cell = (int(r), int(c))
            if self.mode.get() == "fixed" and current_cell == self.drag_last_cell:
                return
            self.drag_last_cell = current_cell
            if self.mode.get() == "fixed":
                self.place_fixed_shape(r, c)
            else:
                if self.is_fixed_mark(self.board[r][c]):
                    self.clear_fixed_slot_by_mark(self.board[r][c])
                self.board[r][c] = self.mode.get()
                self.solutions = []
                self.draw_board()

    def clear_fixed_slot_by_mark(self, mark):
        for slot in self.fixed_slots:
            if slot["mark"] == mark:
                for rr, cc in slot["cells"]:
                    if self.board[rr][cc] == mark:
                        self.board[rr][cc] = "empty"
                slot["cells"] = set()
        self.update_fixed_status()

    def place_fixed_shape(self, anchor_r, anchor_c):
        slot = self.fixed_slots[self.fixed_slot.get()]
        if not slot["shape"]:
            self.assign_shape_to_current_slot()
        if not slot["shape"]:
            messagebox.showerror("尚未選固定形狀", "請先在右側固定方塊形狀庫選一個形狀。")
            return

        new_cells = {(anchor_r + r, anchor_c + c) for r, c in slot["shape"]}
        if any(r < 0 or c < 0 or r >= self.rows.get() or c >= self.cols.get() for r, c in new_cells):
            self.set_status("固定方塊超出盤面")
            return

        old_cells = set(slot["cells"])
        for r, c in old_cells:
            if self.board[r][c] == slot["mark"]:
                self.board[r][c] = "empty"

        blocked = []
        for r, c in new_cells:
            if self.board[r][c] != "empty":
                blocked.append((r, c))
        if blocked:
            for r, c in old_cells:
                self.board[r][c] = slot["mark"]
            self.set_status("固定方塊位置重疊或碰到黑格")
            return

        slot["cells"] = new_cells
        for r, c in new_cells:
            self.board[r][c] = slot["mark"]
        self.solutions = []
        self.draw_board()
        self.update_fixed_status()

    def draw_board(self):
        self.canvas.delete("all")
        rows = self.rows.get()
        cols = self.cols.get()
        for r in range(rows):
            for c in range(cols):
                state = self.board[r][c]
                color = self.color_for_mark(state) if self.is_fixed_mark(state) else self.palette["empty"] if state == "empty" else COLORS.get(state, "#ffffff")
                self.canvas.create_rectangle(c * CELL, r * CELL, (c + 1) * CELL, (r + 1) * CELL, fill=color, outline=self.palette["grid"])
                if self.is_fixed_mark(state):
                    self.canvas.create_text(c * CELL + CELL / 2, r * CELL + CELL / 2, text=state, fill="white", font=("Arial", 16, "bold"))

        if self.solutions:
            for i, (kind, shape_id, cells) in enumerate(self.solutions[self.solution_index.get()]):
                if kind == "required":
                    mark = shape_id.split(":", 1)[0]
                    color = self.color_for_mark(self.fixed_mark_for_label(mark))
                    text = mark.replace("固定", "固")
                    text_color = "white"
                elif kind == "empty":
                    color = self.palette["empty"]
                    text = "空"
                    text_color = self.palette["muted"]
                else:
                    color = SOLUTION_COLORS[i % len(SOLUTION_COLORS)]
                    text = str(i + 1)
                    text_color = self.palette["solution_text"]
                for r, c in cells:
                    options = {"fill": color, "outline": self.palette["piece_outline"], "width": 2}
                    if kind == "empty":
                        options["dash"] = (4, 3)
                    self.canvas.create_rectangle(c * CELL + 3, r * CELL + 3, (c + 1) * CELL - 3, (r + 1) * CELL - 3, **options)
                    self.canvas.create_text(c * CELL + CELL / 2, r * CELL + CELL / 2, text=text, fill=text_color, font=("Arial", 15, "bold"))

        self.canvas.config(width=cols * CELL, height=rows * CELL)

    def fixed_mark_for_label(self, label):
        for slot in self.fixed_slots:
            if slot["label"] == label:
                return slot["mark"]
        return ""

    def selected_shapes(self):
        return [
            (shape_id, shape)
            for shape_size, shape_id, shape in self.shape_cells
            if self.rest_shape_vars.get(shape_id) and self.rest_shape_vars[shape_id].get()
        ]

    def enabled_shapes_for_fill_mode(self):
        selected = self.selected_shapes()
        if not selected:
            return selected

        plan_sizes = self.fill_size_plan_sizes()
        selected_sizes = {len(shape) for _, shape in selected}
        enabled = list(selected)
        selected_ids = {shape_id for shape_id, _ in enabled}
        for shape_size, shape_id, shape in self.shape_cells:
            if shape_size not in plan_sizes or shape_size in selected_sizes:
                continue
            if not self.is_allowed_supplement_shape(shape_size, shape_id):
                continue
            if shape_id not in selected_ids:
                enabled.append((shape_id, shape))
                selected_ids.add(shape_id)
        return enabled

    def shapes_for_sizes(self, sizes):
        return [
            (shape_id, shape)
            for shape_size, shape_id, shape in self.shape_cells
            if shape_size in sizes
        ]

    def selected_sizes(self):
        return {len(shape) for _, shape in self.selected_shapes()}

    def fill_size_plan_sizes(self):
        sizes = self.selected_sizes()
        if not sizes:
            return set()
        if len(sizes) != 1:
            return sizes
        size = next(iter(sizes))
        fill_area = self.current_fill_area()
        if fill_area <= 0:
            return {size}
        if self.fill_mode.get() == "allow_one_empty" and fill_area % size == 1:
            return {size}
        limits = self.full_fill_size_limits(fill_area, size) if self.fill_mode.get() == "full" else self.single_supplement_size_limits(fill_area, size)
        return set(limits) if limits else {size}

    def fill_size_limits(self):
        sizes = self.selected_sizes()
        if len(sizes) != 1:
            return None
        size = next(iter(sizes))
        fill_area = self.current_fill_area()
        if fill_area < 0:
            return None
        if self.fill_mode.get() == "allow_one_empty" and fill_area % size == 1:
            return {size: fill_area // size}
        if self.fill_mode.get() == "full":
            return self.full_fill_size_limits(fill_area, size)
        return self.single_supplement_size_limits(fill_area, size)

    def single_supplement_size_limits(self, fill_area, primary_size):
        if fill_area % primary_size == 0:
            return {primary_size: fill_area // primary_size}
        for supplement in (2, 3, 4):
            if supplement == primary_size:
                continue
            if fill_area >= supplement and (fill_area - supplement) % primary_size == 0:
                return {primary_size: (fill_area - supplement) // primary_size, supplement: 1}
        return None

    def full_fill_size_limits(self, fill_area, primary_size):
        best = None
        best_key = None
        max_primary_count = fill_area // primary_size
        for primary_count in range(max_primary_count, -1, -1):
            remaining = fill_area - primary_count * primary_size
            supplement_counts = self.minimum_supplement_counts(remaining, primary_size)
            if supplement_counts is None:
                continue
            counts = dict(supplement_counts)
            if primary_count:
                counts[primary_size] = counts.get(primary_size, 0) + primary_count
            supplement_total = sum(count for size, count in counts.items() if size != primary_size)
            key = (-primary_count, supplement_total, sum(counts.values()))
            if best_key is None or key < best_key:
                best = counts
                best_key = key
        return best

    def minimum_supplement_counts(self, area, primary_size):
        if area == 0:
            return {}
        best = None
        best_key = None
        choices = [size for size in (2, 3, 4) if size != primary_size]
        for a in range(area // 2 + 1):
            for b in range(area // 3 + 1):
                for c in range(area // 4 + 1):
                    counts = {2: a, 3: b, 4: c}
                    if counts.get(primary_size):
                        continue
                    total = 2 * a + 3 * b + 4 * c
                    if total != area:
                        continue
                    clean = {size: count for size, count in counts.items() if count}
                    key = (sum(clean.values()), tuple(clean.get(size, 0) for size in (2, 3, 4)))
                    if best_key is None or key < best_key:
                        best = clean
                        best_key = key
        return best

    def current_fill_area(self):
        open_cells = sum(1 for row in self.board for cell in row if cell == "empty")
        required_area = sum(len(slot["shape"]) for slot in self.fixed_slots if slot["shape_id"] and not slot["cells"])
        return open_cells - required_area

    def can_cover_area(self, area, sizes):
        if area < 0:
            return False
        reachable = [False] * (area + 1)
        reachable[0] = True
        for total in range(area + 1):
            if not reachable[total]:
                continue
            for size in sizes:
                if total + size <= area:
                    reachable[total + size] = True
        return reachable[area]

    def run_solver(self):
        required_shapes = [
            (slot["label"], slot["shape_id"], slot["shape"])
            for slot in self.fixed_slots
            if slot["shape_id"] and not slot["cells"]
        ]
        fixed_placed_shapes = [
            (slot["shape_id"], frozenset(slot["cells"]))
            for slot in self.fixed_slots
            if slot["shape_id"] and slot["cells"]
        ]
        open_cells = sum(1 for row in self.board for cell in row if cell == "empty")
        required_area = sum(len(shape) for _, _, shape in required_shapes)
        fill_area = open_cells - required_area
        if fill_area < 0:
            messagebox.showerror("面積不相容", "未指定位置的固定方塊面積已超過剩餘空格。")
            return
        enabled = self.enabled_shapes_for_fill_mode()
        if not enabled and fill_area > 0:
            messagebox.showerror("無可用方塊", "請至少勾選一種剩餘可重複使用的方塊。")
            return
        selected_sizes = self.selected_sizes()
        max_empty_cells = 0
        if self.fill_mode.get() == "allow_one_empty" and len(selected_sizes) == 1:
            size = next(iter(selected_sizes))
            if fill_area % size == 1:
                max_empty_cells = 1
        rest_size_limits = self.fill_size_limits()

        solver = TilingSolver(
            self.rows.get(),
            self.cols.get(),
            [row[:] for row in self.board],
            enabled,
            required_shapes,
            fixed_placed_shapes,
            False,
            False,
            int(self.max_solutions.get()),
            max_empty_cells,
            rest_size_limits,
            self.dedupe_by_piece_set.get(),
        )
        self.solutions = solver.solve()
        self.solution_index.set(0)
        self.draw_board()
        self.update_result_text()
        if self.solutions:
            capped = "以上" if len(self.solutions) >= int(self.max_solutions.get()) else ""
            self.set_status(f"找到 {len(self.solutions)} 種{capped}")
        else:
            self.set_status("找不到解")

    def move_solution(self, delta):
        if not self.solutions:
            return
        self.solution_index.set((self.solution_index.get() + delta) % len(self.solutions))
        self.draw_board()
        self.update_result_text()

    def update_result_text(self):
        self.result_text.delete("1.0", "end")
        if not self.solutions:
            self.result_text.insert("end", "沒有可顯示的解。\n")
            return
        idx = self.solution_index.get()
        self.result_text.insert("end", f"解 {idx + 1} / {len(self.solutions)}\n")
        self.result_text.insert("end", "格式：方塊編號 shape_id [(列,欄)...]\n\n")
        for i, (kind, shape_id, cells) in enumerate(self.solutions[idx], start=1):
            coords = sorted((r + 1, c + 1) for r, c in cells)
            if kind == "required":
                label = shape_id
            elif kind == "empty":
                label = "保留空格"
            else:
                label = f"剩餘:{shape_id}"
            self.result_text.insert("end", f"{i:02d}. {label} {coords}\n")

    def config_data(self):
        return {
            "version": 1,
            "rows": self.rows.get(),
            "cols": self.cols.get(),
            "board": self.board,
            "fixed_pieces": [
                {
                    "label": slot["label"],
                    "mark": slot["mark"],
                    "shape_id": slot["shape_id"],
                    "cells": sorted((r + 1, c + 1) for r, c in slot["cells"]),
                }
                for slot in self.fixed_slots
            ],
            "rest_shape_ids": [shape_id for shape_id, var in self.rest_shape_vars.items() if var.get()],
            "active_preset_id": self.active_preset_id.get(),
            "fill_mode": self.fill_mode.get(),
            "auto_fill_supplement_types": True,
            "max_solutions": self.max_solutions.get(),
            "allow_rotation": False,
            "allow_reflection": False,
        }

    def export_config(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=(("JSON", "*.json"), ("All files", "*.*")),
            initialfile="yihuan_board_config.json",
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.config_data(), f, ensure_ascii=False, indent=2)
        self.set_status(f"已匯出盤面 {path}")

    def import_config(self):
        path = filedialog.askopenfilename(filetypes=(("JSON", "*.json"), ("All files", "*.*")))
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.apply_config(data)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            messagebox.showerror("匯入失敗", str(exc))
            return
        self.set_status(f"已匯入盤面 {path}")

    def apply_config(self, data):
        rows = int(data.get("rows", 5))
        cols = int(data.get("cols", 6))
        rows = max(1, min(MAX_GRID, rows))
        cols = max(1, min(MAX_GRID, cols))
        self.rows.set(rows)
        self.cols.set(cols)

        fixed_data = data.get("fixed_pieces", [])
        if not fixed_data:
            fixed_data = [self.make_fixed_slot(i) for i in range(4)]

        self.fixed_slots = []
        for index, item in enumerate(fixed_data):
            slot = self.make_fixed_slot(index)
            slot["label"] = item.get("label") or slot["label"]
            slot["mark"] = item.get("mark") or slot["mark"]
            shape_id = item.get("shape_id", "")
            if shape_id in self.shape_by_id:
                slot["shape_id"] = shape_id
                slot["shape"] = self.shape_by_id[shape_id][1]
            cells = set()
            for r, c in item.get("cells", []):
                rr = int(r) - 1
                cc = int(c) - 1
                if 0 <= rr < rows and 0 <= cc < cols:
                    cells.add((rr, cc))
            slot["cells"] = cells
            self.fixed_slots.append(slot)
        while len(self.fixed_slots) < 4:
            self.fixed_slots.append(self.make_fixed_slot(len(self.fixed_slots)))

        raw_board = data.get("board", [])
        self.board = [["empty" for _ in range(cols)] for _ in range(rows)]
        imported_marks = {slot["mark"] for slot in self.fixed_slots}
        for r in range(rows):
            if r >= len(raw_board):
                continue
            for c in range(cols):
                if c >= len(raw_board[r]):
                    continue
                value = raw_board[r][c]
                if value == "blocked":
                    self.board[r][c] = "blocked"
                elif value in imported_marks:
                    self.board[r][c] = value

        for slot in self.fixed_slots:
            for r, c in slot["cells"]:
                self.board[r][c] = slot["mark"]

        selected_rest = set(data.get("rest_shape_ids", []))
        if "rest_shape_ids" in data:
            for shape_id, var in self.rest_shape_vars.items():
                var.set(shape_id in selected_rest)
        preset_ids = {preset["id"] for preset in PRESET_FIXED_PIECES}
        self.active_preset_id.set(data.get("active_preset_id", "") if data.get("active_preset_id", "") in preset_ids else "")
        self.fill_mode.set(data.get("fill_mode", "full"))
        self.max_solutions.set(int(data.get("max_solutions", self.max_solutions.get())))
        self.fixed_slot.set(0)
        self.selected_fixed_shape.set(self.fixed_slots[0]["shape_id"] if self.fixed_slots else "")
        self.solutions = []
        self.solution_index.set(0)
        self.redraw_fixed_slot_buttons()
        self._draw_fixed_shape_library()
        self._draw_rest_shape_selectors()
        self.redraw_preset_buttons()
        self.apply_theme(redraw=False)
        self.draw_board()
        self.update_fixed_status()
        self.update_result_text()

    def export_json(self):
        if not self.solutions:
            messagebox.showerror("尚無結果", "請先求解再匯出。")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=(("JSON", "*.json"), ("All files", "*.*")),
            initialfile="yihuan_solutions.json",
        )
        if not path:
            return
        data = self.config_data()
        data.update({
            "solutions": [
                [
                    {"kind": kind, "shape_id": shape_id, "cells": sorted((r + 1, c + 1) for r, c in cells)}
                    for kind, shape_id, cells in solution
                ]
                for solution in self.solutions
            ],
        })
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.set_status(f"已匯出 {path}")

    def set_status(self, text):
        self.status.config(text=text)


if __name__ == "__main__":
    App().mainloop()
