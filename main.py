from logging import root
from math import e
import tkinter as tk
from unittest import result
import cvxpy as cp
import numpy as np
from tkinter import W, X, ttk


class elemental_analysis:
    def __init__(self, root):
        self.root = root
        self.root.title("元素分析アウンデスチェッカー")
        self.root.geometry("400x500")
        self.root.minsize(400, 500)
        self.root.update_idletasks()
        self.composition_formula = tk.StringVar()
        self.observation_value_C = tk.DoubleVar(value="")
        self.observation_value_N = tk.DoubleVar(value="")
        self.observation_value_S = tk.DoubleVar(value="")
        self.observation_value_H = tk.DoubleVar(value="")
        self.items_data = [  # (表示テキスト, 初期チェック状態)
            ("Option 1", False),
            ("Option 2", True),
            ("Option 3", False),
            ("Option 4", False),
            ("Option 5", True),
        ]
        self.observation_result = tk.StringVar(value="分析結果")
        # UIの作成
        formula_frame = ttk.Frame(self.root, padding=(10, 15))
        formula_frame.pack(fill=tk.X)
        formula_label = ttk.Label(
            formula_frame, text="組成式:", font=("TkDefaultFont", 14)
        )
        formula_label.pack(side=tk.LEFT, padx=(5, 0), pady=5)
        self.formula_entry = ttk.Entry(
            formula_frame,
            font=("TkDefaultFont", 14),
            textvariable=self.composition_formula,
            width=45,
        )
        self.formula_entry.pack(fill=tk.X, padx=5, pady=5)
        observed_frame = ttk.Frame(self.root, padding=10)
        observed_frame.pack(fill=tk.BOTH)
        observed_label = ttk.Label(
            observed_frame, text="実測値(%)", font=("TkDefaultFont", 14)
        )
        # 「実測値」ラベルの右側にスペースを設ける
        observed_label.pack(
            side=tk.TOP, fill=tk.X, anchor=W, padx=(5, 10), pady=(0, 10)
        )
        observed_label_frame = ttk.Frame(observed_frame, padding=10, relief=tk.RAISED)
        observed_label_frame.pack(fill=tk.X)

        # 各要素ラベルに共通で適用する左右のパディング
        element_label_padx = 5

        observed_label_C = ttk.Label(
            observed_label_frame, text="C", font=("TkDefaultFont", 14), anchor=tk.CENTER
        )
        observed_label_C.pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=element_label_padx, pady=5
        )
        observed_label_N = ttk.Label(
            observed_label_frame, text="H", font=("TkDefaultFont", 14), anchor=tk.CENTER
        )
        observed_label_N.pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=element_label_padx, pady=5
        )
        observed_label_S = ttk.Label(
            observed_label_frame, text="N", font=("TkDefaultFont", 14), anchor=tk.CENTER
        )
        observed_label_S.pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=element_label_padx, pady=5
        )
        observed_label_H = ttk.Label(
            observed_label_frame, text="S", font=("TkDefaultFont", 14), anchor=tk.CENTER
        )
        observed_label_H.pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=element_label_padx, pady=5
        )
        observed_value_frame = ttk.Frame(observed_frame, padding=10, relief=tk.RAISED)
        observed_value_frame.pack(fill=tk.X, pady=5, side=tk.TOP)
        observed_value_C = ttk.Entry(
            observed_value_frame,
            textvariable=self.observation_value_C,
            font=("TkDefaultFont", 14),
            width=5,
        )
        observed_value_C.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        observed_value_N = ttk.Entry(
            observed_value_frame,
            textvariable=self.observation_value_N,
            font=("TkDefaultFont", 14),
            width=5,
        )
        observed_value_N.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        observed_value_S = ttk.Entry(
            observed_value_frame,
            textvariable=self.observation_value_S,
            font=("TkDefaultFont", 14),
            width=5,
        )
        observed_value_S.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        observed_value_H = ttk.Entry(
            observed_value_frame,
            textvariable=self.observation_value_H,
            font=("TkDefaultFont", 14),
            width=5,
        )
        observed_value_H.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        solvent_frame = ttk.Frame(self.root)
        solvent_frame.pack(fill=tk.X)
        solvent_label = ttk.Label(
            solvent_frame, text="溶媒リスト", font=("TkDefaultFont", 14)
        )
        solvent_label.pack(side=tk.TOP, padx=(5, 0), pady=5)
        self.listbox = tk.Listbox(
            solvent_frame,
            selectmode=tk.SINGLE,
            exportselection=False,
            height=5,
        )
        self.listbox.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=10,
        )

        window_scrollbar = ttk.Scrollbar(
            solvent_frame, orient=tk.VERTICAL, command=self.listbox.yview
        )
        window_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox.config(yscrollcommand=window_scrollbar.set)
        self.populate_listbox()

        self.listbox.bind("<<ListboxSelect>>", self.on_item_click)
        # または、より直接的なクリックイベントを拾う場合:
        # self.listbox.bind("<ButtonRelease-1>", self.on_item_click_button)
        self.analyze_button = ttk.Button(
            solvent_frame,
            text="チェック開始",
            command=self.analyze,
            style="Accent.TButton",
        )
        self.analyze_button.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=10,
            pady=10,
        )
        result_frame = ttk.Frame(self.root, padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True)
        result_label = ttk.Label(
            result_frame, text="分析結果", font=("TkDefaultFont", 14)
        )
        result_label.pack(side=tk.TOP, padx=(5, 0), pady=5)
        self.result_text = tk.Text(
            result_frame,
            font=("TkDefaultFont", 14),
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)

    def populate_listbox(self):
        self.listbox.delete(0, tk.END)  # 既存のアイテムをクリア
        for text, checked in self.items_data:
            prefix = "[x] " if checked else "[ ] "
            self.listbox.insert(tk.END, prefix + text)

    def on_item_click(self, event):
        widget = event.widget
        selection = widget.curselection()  # 選択されたアイテムのインデックスを取得
        if not selection:
            return

        index = selection[0]

        # チェック状態をトグル
        original_text, current_checked_state = self.items_data[index]
        self.items_data[index] = (original_text, not current_checked_state)

        # リストボックスの表示を更新
        self.populate_listbox()

        # クリック後もそのアイテムを選択状態に保つ (任意)
        self.listbox.selection_set(index)
        self.listbox.activate(index)

    def analyze(self):
        # 定数行列の定義
        n = 3  # 変数の次元
        m = 4  # 出力の次元 (要素数)

        # ランダムな定数行列（正値調整済み）
        np.random.seed(0)
        # N_coeffs と M_coeffs は各要素のスカラー定数項なので (m, 1) または (m,) が適切
        # B_coeffs と A_coeffs は各要素のxの係数ベクトルなので (m, n) が適切
        # ユーザー指定に合わせるために N と M の初期化とアクセスを調整
        N_mat = np.random.randn(1, m)  # (1, m) ユーザー指定に合わせる
        B_mat = np.random.randn(m, n)  # (m, n)
        M_mat = np.abs(np.random.randn(1, m)) + 1  # (1, m) ユーザー指定に合わせる
        A_mat = np.abs(np.random.randn(m, n))  # (m, n)

        max_values = []
        min_values = []
        max_solutions_x = []  # 元の変数 x の解を格納
        min_solutions_x = []  # 元の変数 x の解を格納

        for i in range(m):
            N_scalar = N_mat[0, i]  # N_mat が (1,m) の場合
            B_vector = B_mat[i, :]
            M_scalar = M_mat[0, i]  # M_mat が (1,m) の場合
            A_vector = A_mat[i, :]

            # 変数の定義 (Charnes-Cooper変換後の変数 y と t)
            y_cc = cp.Variable(n, name="y_cc")
            t_cc = cp.Variable(nonneg=True, name="t_cc")  # t >= 0

            # --- 最大化 ---
            obj_max = cp.Maximize(N_scalar * t_cc + B_vector @ y_cc)
            constraints_max = [
                M_scalar * t_cc + A_vector @ y_cc == 1,
                y_cc >= 0,  # From 0 <= x
                y_cc <= 5 * t_cc,  # From x <= 5
                1 >= 1e-6 * t_cc,  # From M_scalar + A_vector @ x >= 1e-6
                # t_cc >= 1e-7        # 必要に応じて t > 0 を数値的に保証 (通常は不要)
            ]
            try:
                prob_max = cp.Problem(obj_max, constraints_max)
                prob_max.solve()
                if prob_max.status == "optimal":
                    max_values.append(prob_max.value)
                    # t_cc.value が非常に小さい場合、数値誤差に注意
                    if (
                        t_cc.value is not None and abs(t_cc.value) > 1e-9
                    ):  # ゼロ割を避ける
                        max_solutions_x.append(y_cc.value / t_cc.value)
                    else:
                        max_solutions_x.append(None)  # t_cc がほぼ0か未定義
                else:
                    max_values.append(None)
                    max_solutions_x.append(None)
                    # print(f"Max problem {i+1} status: {prob_max.status}") # デバッグ用
            except Exception as e:
                # print(f"Max problem {i+1} exception: {e}") # デバッグ用
                max_values.append(None)
                max_solutions_x.append(None)

            # --- 最小化 ---
            obj_min = cp.Minimize(N_scalar * t_cc + B_vector @ y_cc)
            # 制約は最大化と同じ
            constraints_min = (
                constraints_max  # y_cc と t_cc は Minimize problem で再利用される
            )
            # (CVXPYでは問題ごとに変数がスコープされる)

            try:
                prob_min = cp.Problem(obj_min, constraints_min)
                prob_min.solve()
                if prob_min.status == "optimal":
                    min_values.append(prob_min.value)
                    if (
                        t_cc.value is not None and abs(t_cc.value) > 1e-9
                    ):  # ゼロ割を避ける
                        min_solutions_x.append(y_cc.value / t_cc.value)
                    else:
                        min_solutions_x.append(None)  # t_cc がほぼ0か未定義
                else:
                    min_values.append(None)
                    min_solutions_x.append(None)
                    # print(f"Min problem {i+1} status: {prob_min.status}") # デバッグ用
            except Exception as e:
                # print(f"Min problem {i+1} exception: {e}") # デバッグ用
                min_values.append(None)
                min_solutions_x.append(None)

        # 結果表示
        print("=== 各要素の最大値 ===")
        for i in range(m):
            print(f"要素 {i+1}: {max_values[i]}")
            print(f"  最適解 x: {max_solutions_x[i]}")

        print("\n=== 各要素の最小値 ===")
        for i in range(m):
            print(f"要素 {i+1}: {min_values[i]}")
            print(f"  最適解 x: {min_solutions_x[i]}")


if __name__ == "__main__":
    # Example usage
    root = tk.Tk()
    analysis = elemental_analysis(root)
    root.mainloop()
