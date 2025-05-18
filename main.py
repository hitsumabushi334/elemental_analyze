from ast import arg
from logging import root
from math import e
from multiprocessing import Value
import tkinter as tk
from unittest import result
import cvxpy as cp
import numpy as np
from tkinter import W, X, ttk
from tkinter import messagebox  # messagebox をインポート
import threading
import chemparse


class elemental_analysis:
    def __init__(self, root):
        self.root = root
        self.root.title("元素分析アウンデスチェッカー")
        self.root.geometry("400x500")
        self.root.minsize(400, 500)
        self.root.update_idletasks()
        self.compound_formula_var = tk.StringVar()
        self.observed_c_var = tk.DoubleVar(value="")
        self.observed_h_var = tk.DoubleVar(value="")  # NからHに変更
        self.observed_n_var = tk.DoubleVar(value="")  # SからNに変更
        self.observed_s_var = tk.DoubleVar(value="")  # HからSに変更

        self.SOLVENT_DATA = [  # (表示テキスト, 初期チェック状態)
            ("H2O", False),
            ("DMF", False),
            ("MeOH", False),
            ("n-hexane", False),
            ("n-pentane", False),
            ("CH2Cl2", False),
            ("Acetone", False),
            ("THF", False),
            ("EtOH", False),
            ("Et2O", False),
            ("DMSO", False),
            ("Toluene", False),
            ("CH3Cl", False),
            ("MeCN", False),
            ("Ethyl acetate", False),
        ]
        self.analysis_result_var = tk.StringVar(value="")
        self.checked_solvent_list = []
        self.solvent_element_mass_array = np.array([])  # solvent_mass_array から変更
        self.solvent_molecular_weight_array = np.array(
            []
        )  # solvent_mass_sum_array から変更
        self.compound_molecular_weight = 0  # composition_mass から変更
        self.compound_element_mass_array = np.array(
            []
        )  # composition_atom_mass から変更
        self.observed_element_fractions_array = np.array([])
        self.optimized_value = None
        # UIの作成
        compound_formula_frame = ttk.Frame(self.root, padding=(10, 15))
        compound_formula_frame.pack(fill=tk.X)
        compound_formula_label = ttk.Label(
            compound_formula_frame, text="組成式:", font=("TkDefaultFont", 14)
        )
        compound_formula_label.pack(side=tk.LEFT, padx=(5, 0), pady=5)
        self.compound_formula_entry = ttk.Entry(
            compound_formula_frame,
            font=("TkDefaultFont", 14),
            textvariable=self.compound_formula_var,
            width=45,
        )
        self.compound_formula_entry.pack(fill=tk.X, padx=5, pady=5)

        observed_values_main_frame = ttk.Frame(self.root, padding=10)
        observed_values_main_frame.pack(fill=tk.BOTH)
        observed_values_title_label = ttk.Label(
            observed_values_main_frame, text="実測値(%)", font=("TkDefaultFont", 14)
        )
        observed_values_title_label.pack(
            side=tk.TOP, fill=tk.X, anchor=W, padx=(5, 10), pady=(0, 10)
        )
        observed_element_labels_frame = ttk.Frame(
            observed_values_main_frame, padding=10, relief=tk.RAISED
        )
        observed_element_labels_frame.pack(fill=tk.X)

        element_label_padx = 5

        observed_c_label = ttk.Label(
            observed_element_labels_frame,
            text="C",
            font=("TkDefaultFont", 14),
            anchor=tk.CENTER,
        )
        observed_c_label.pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=element_label_padx, pady=5
        )
        observed_h_label = ttk.Label(  # NからHに変更
            observed_element_labels_frame,
            text="H",
            font=("TkDefaultFont", 14),
            anchor=tk.CENTER,
        )
        observed_h_label.pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=element_label_padx, pady=5
        )
        observed_n_label = ttk.Label(  # SからNに変更
            observed_element_labels_frame,
            text="N",
            font=("TkDefaultFont", 14),
            anchor=tk.CENTER,
        )
        observed_n_label.pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=element_label_padx, pady=5
        )
        observed_s_label = ttk.Label(  # HからSに変更
            observed_element_labels_frame,
            text="S",
            font=("TkDefaultFont", 14),
            anchor=tk.CENTER,
        )
        observed_s_label.pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=element_label_padx, pady=5
        )

        observed_value_entries_frame = ttk.Frame(
            observed_values_main_frame, padding=10, relief=tk.RAISED
        )
        observed_value_entries_frame.pack(fill=tk.X, pady=5, side=tk.TOP)

        self.observed_c_entry = ttk.Entry(
            observed_value_entries_frame,
            textvariable=self.observed_c_var,
            font=("TkDefaultFont", 14),
            width=5,
        )
        self.observed_c_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        self.observed_h_entry = ttk.Entry(  # NからHに変更
            observed_value_entries_frame,
            textvariable=self.observed_h_var,
            font=("TkDefaultFont", 14),
            width=5,
        )
        self.observed_h_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        self.observed_n_entry = ttk.Entry(  # SからNに変更
            observed_value_entries_frame,
            textvariable=self.observed_n_var,
            font=("TkDefaultFont", 14),
            width=5,
        )
        self.observed_n_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        self.observed_s_entry = ttk.Entry(  # HからSに変更
            observed_value_entries_frame,
            textvariable=self.observed_s_var,
            font=("TkDefaultFont", 14),
            width=5,
        )
        self.observed_s_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))

        solvent_selection_frame = ttk.Frame(self.root)
        solvent_selection_frame.pack(fill=tk.X)
        solvent_list_label = ttk.Label(
            solvent_selection_frame, text="溶媒リスト", font=("TkDefaultFont", 14)
        )
        solvent_list_label.pack(side=tk.TOP, anchor=tk.W, padx=(5, 0), pady=5)
        self.solvent_listbox = tk.Listbox(
            solvent_selection_frame,
            selectmode=tk.SINGLE,
            exportselection=False,
            height=5,
            font=("TkDefaultFont", 14),
        )
        self.solvent_listbox.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=10,
        )

        solvent_list_scrollbar = ttk.Scrollbar(
            solvent_selection_frame,
            orient=tk.VERTICAL,
            command=self.solvent_listbox.yview,
        )
        solvent_list_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.solvent_listbox.config(yscrollcommand=solvent_list_scrollbar.set)
        self.populate_solvent_listbox()

        self.solvent_listbox.bind("<<ListboxSelect>>", self.on_solvent_listbox_click)

        self.start_analysis_button = ttk.Button(
            solvent_selection_frame,
            text="チェック開始",
            command=self.on_start_analysis_button_click,
            style="Accent.TButton",
        )
        self.start_analysis_button.pack(
            side=tk.RIGHT,
            fill=tk.X,
            expand=True,
            padx=10,
            pady=10,
        )
        analysis_result_display_frame = ttk.Frame(
            self.root, padding=10, relief=tk.RAISED
        )
        analysis_result_display_frame.pack(fill=tk.BOTH, expand=True)
        self.analysis_result_title_label = ttk.Label(
            analysis_result_display_frame, text="分析結果", font=("TkDefaultFont", 14)
        )
        self.analysis_result_title_label.pack(
            side=tk.TOP, anchor=tk.W, padx=(5, 0), pady=5
        )
        self.analysis_result_content_label = tk.Label(
            analysis_result_display_frame,
            font=("TkDefaultFont", 14),
            anchor=tk.W,
            textvariable=self.analysis_result_var,  # textvariable を設定
            wraplength=350,  # この行を追加
        )
        self.analysis_result_content_label.pack(fill=tk.BOTH, expand=True)

    def populate_solvent_listbox(self):
        self.solvent_listbox.delete(0, tk.END)  # 既存のアイテムをクリア
        for text, checked in self.SOLVENT_DATA:
            prefix = "[x] " if checked else "[ ] "
            self.solvent_listbox.insert(tk.END, prefix + text)

    def on_solvent_listbox_click(self, event):
        widget = event.widget
        selection = widget.curselection()
        if not selection:
            return

        index = selection[0]
        original_text, current_checked_state = self.SOLVENT_DATA[index]
        self.SOLVENT_DATA[index] = (original_text, not current_checked_state)
        self.populate_solvent_listbox()
        self.solvent_listbox.selection_set(index)
        self.solvent_listbox.activate(index)

    def on_start_analysis_button_click(self):
        if not self.compound_formula_var.get():
            messagebox.showerror("入力エラー", "組成式を入力してください。")
            return

        try:
            # 実測値の取得
            observed_c = self.observed_c_var.get()
            observed_h = self.observed_h_var.get()
            observed_n = self.observed_n_var.get()
            observed_s = self.observed_s_var.get()
        except tk.TclError:
            messagebox.showerror(
                "入力エラー",
                "実測値には有効な数値を入力してください。\n（例: 12.34 または 0）",
            )
            return

        print("分析開始ボタンがクリックされました！")

        try:
            self.start_analysis_button.config(state=tk.DISABLED)
            self.compound_formula_entry.config(state=tk.DISABLED)
            self.solvent_listbox.config(state=tk.DISABLED)
            self.observed_c_entry.config(state=tk.DISABLED)
            self.observed_h_entry.config(state=tk.DISABLED)
            self.observed_n_entry.config(state=tk.DISABLED)
            self.observed_s_entry.config(state=tk.DISABLED)

            self.analysis_result_var.set("分析中...")  # textvariable を使用して更新
            analysis_thread = threading.Thread(
                target=self.run_analysis_calculations,
                daemon=True,  # perform_analysis から変更
            )
            analysis_thread.start()
            # スレッド開始後、すぐに完了メッセージを出すのではなく、スレッド内で結果を更新する
            # self.analysis_result_var.set("分析中... (計算が完了するまでお待ちください)")
        except AttributeError as e:
            print(f"UI要素の更新中にエラーが発生しました: {e}")
            messagebox.showerror("内部エラー", "UIコンポーネントの参照に失敗しました。")
            # UIを有効に戻す処理を追加することが望ましい
            self.enable_ui_elements()
        except tk.TclError as e:
            print(f"UI要素の更新中にTclエラーが発生しました: {e}")
            messagebox.showerror(
                "内部エラー", "UIの更新処理中に予期せぬエラーが発生しました。"
            )
            self.enable_ui_elements()

    def enable_ui_elements(self):
        """UI要素を有効状態に戻すヘルパーメソッド"""
        self.start_analysis_button.config(state=tk.NORMAL)
        self.compound_formula_entry.config(state=tk.NORMAL)
        self.solvent_listbox.config(state=tk.NORMAL)
        self.observed_c_entry.config(state=tk.NORMAL)
        self.observed_h_entry.config(state=tk.NORMAL)
        self.observed_n_entry.config(state=tk.NORMAL)
        self.observed_s_entry.config(state=tk.NORMAL)
        self.SOLVENT_DATA = [  # (表示テキスト, 初期チェック状態)
            ("H2O", False),
            ("DMF", False),
            ("MeOH", False),
            ("n-hexane", False),
            ("n-pentane", False),
            ("CH2Cl2", False),
            ("Acetone", False),
            ("THF", False),
            ("EtOH", False),
            ("Et2O", False),
            ("DMSO", False),
            ("Toluene", False),
            ("CH3Cl", False),
            ("MeCN", False),
            ("Ethyl acetate", False),
        ]
        self.populate_solvent_listbox()  # 溶媒リストを再描画
        self.optimized_value = None  # 最適化値をリセット

    def run_analysis_calculations(self):  # perform_analysis から変更
        try:
            parsed_compound_elements_dict = (
                self.parse_compound_formula()
            )  # extract_atom から変更
            if parsed_compound_elements_dict is None:  # パース失敗時
                # parse_compound_formula内でUI更新とenable_ui_elementsが呼ばれる想定
                return

            if self.validate_elements_in_formula(
                parsed_compound_elements_dict
            ):  # check_formula から変更
                self.root.after(
                    0,
                    lambda: self.analysis_result_var.set(
                        "エラー: 利用できない元素が組成式に含まれています。"
                    ),
                )  # textvariable を使用
                self.root.after(0, self.enable_ui_elements)  # UIを有効に戻す
                return
            self.prepare_calculation_data(
                parsed_compound_elements_dict
            )  # calculate_parameters

            # execute_optimization_calculations の返り値の修正を考慮
            result = self.execute_optimization_calculations()
            if (
                result is None
            ):  # execute_optimization_calculationsがNoneを返す場合(例: 溶媒未選択)
                # execute_optimization_calculations内でUI更新とenable_ui_elementsが呼ばれる想定
                return
            max_optimal_solvent_ratios, min_optimal_solvent_ratios = result

            is_valid = self.evaluate_elemental_analysis(
                max_optimal_solvent_ratios, min_optimal_solvent_ratios
            )
            self.root.after(0, lambda: self.finish_analysis_process(is_valid))
        except Exception as e:
            # 包括的なエラーハンドリング
            print(f"分析処理中に予期せぬエラーが発生しました: {e}")
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "内部エラー", f"分析処理中にエラーが発生しました: {e}"
                ),
            )
            self.root.after(0, self.enable_ui_elements)

    def finish_analysis_process(self, is_valid):
        """分析プロセスの終了処理"""
        if is_valid:
            self.analysis_result_var.set(
                f"溶媒分子10モル以内で解があります！\n 最適化値: {self.optimized_value}"
            )
        else:
            self.analysis_result_var.set("残念 アワンデス！")

        self.enable_ui_elements()  # この呼び出しはメインスレッドから行われるように run_analysis_calculations で制御

    def parse_compound_formula(self):  # extract_atom から変更
        formula_str = self.compound_formula_var.get()
        try:
            parsed_elements = chemparse.parse_formula(formula_str)
            print(f"パースされた組成式: {parsed_elements}")
            if not parsed_elements:  # chemparseが空の辞書を返す場合もエラーとする
                self.root.after(
                    0,
                    lambda: messagebox.showerror(
                        "入力エラー",
                        "組成式を正しくパースできませんでした。入力形式を確認してください。",
                    ),
                )
                self.root.after(0, self.enable_ui_elements)
                return None
            return parsed_elements
        except Exception as e:  # chemparseが例外を投げる場合
            print(f"組成式のパース中にエラー: {e}")
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "入力エラー", f"組成式のパースに失敗しました: {e}"
                ),
            )
            self.root.after(0, self.enable_ui_elements)
            return None

    def validate_elements_in_formula(
        self, parsed_elements_dict
    ):  # check_formula から変更
        ALLOWED_ELEMENTS_SET = {
            "C",
            "H",
            "N",
            "S",
            "B",
            "F",
            "Cl",
            "P",
            "O",
            "Co",
            "Ni",
            "Zn",
            "Na",
            "Mg",
            "Al",
            "Si",
            "K",
            "Ca",
            "Ti",
            "V",
            "Cr",
            "Mn",
            "Cu",
            "Br",
            "Mo",
            "Ru",
            "Pd",
            "Ag",
            "Pt",
            "Au",
            "Fe",
        }
        for element_symbol in parsed_elements_dict.keys():
            if element_symbol not in ALLOWED_ELEMENTS_SET:
                print(
                    f"エラー: 許可されていない元素 '{element_symbol}' が検出されました。"
                )
                return True  # エラーあり
        return False  # エラーなし

    def prepare_calculation_data(
        self, parsed_compound_elements_dict
    ):  # calculate_parameters から変更
        ATOMIC_WEIGHTS_DICT = {
            "C": 12.01,
            "H": 1.00794,
            "N": 14.007,
            "B": 10.81,
            "F": 18.9984,
            "Cl": 35.45,
            "P": 30.97,
            "S": 32.06,
            "O": 16.00,
            "Co": 58.93,
            "Ni": 58.6934,
            "Zn": 65.38,
            "Na": 22.98977,
            "Mg": 24.305,
            "Al": 26.98154,
            "Si": 28.0855,
            "K": 39.0983,
            "Ca": 40.08,
            "Ti": 47.9,
            "V": 50.9414,
            "Cr": 51.996,
            "Mn": 54.938,
            "Cu": 63.546,
            "Br": 79.904,
            "Mo": 95.94,
            "Ru": 101.07,
            "Pd": 106.4,
            "Ag": 107.868,
            "Pt": 195.09,
            "Au": 196.9665,
            "Fe": 55.85,
        }
        SOLVENT_ELEMENTAL_COMPOSITION_DATA = {
            "H2O": {"C": 0, "H": 2.01588, "N": 0, "S": 0, "sum": 18.0159},
            "DMF": {"C": 36.03, "H": 7.0558, "N": 14.007, "S": 0, "sum": 73.0926},
            "MeOH": {"C": 12.01, "H": 4.03176, "N": 0, "S": 0, "sum": 32.0418},
            "n-hexane": {"C": 72.06, "H": 14.1112, "N": 0, "S": 0, "sum": 86.1712},
            "n-pentane": {"C": 60.05, "H": 12.0953, "N": 0, "S": 0, "sum": 72.1453},
            "CH2Cl2": {
                "C": 12.01,
                "H": 2.01588,
                "N": 0,
                "S": 0,
                "sum": 84.9259,
            },  # Cl追加
            "Acetone": {"C": 36.03, "H": 6.04764, "N": 0, "S": 0, "sum": 58.0776},
            "THF": {"C": 48.04, "H": 8.06352, "N": 0, "S": 0, "sum": 72.1035},
            "EtOH": {"C": 24.02, "H": 6.04764, "N": 0, "S": 0, "sum": 46.0676},
            "Et2O": {"C": 48.04, "H": 10.0794, "N": 0, "S": 0, "sum": 74.1194},
            "DMSO": {"C": 24.02, "H": 6.04764, "N": 0, "S": 32.06, "sum": 78.1276},
            "Toluene": {"C": 84.07, "H": 8.06352, "N": 0, "S": 0, "sum": 92.1335},
            "CH3Cl": {
                "C": 12.01,
                "H": 3.02382,
                "N": 0,
                "S": 0,
                "sum": 50.4838,
            },  # Cl追加
            "MeCN": {"C": 24.02, "H": 3.02382, "N": 14.007, "S": 0, "sum": 41.0508},
            "Ethyl acetate": {"C": 48.04, "H": 8.06352, "N": 0, "S": 0, "sum": 88.1035},
        }
        print("計算パラメータ準備中...")
        self.checked_solvent_list = [
            solvent_name for solvent_name, is_checked in self.SOLVENT_DATA if is_checked
        ]

        TARGET_ELEMENT_ORDER_LIST = ["C", "H", "N", "S"]  # element_order から変更

        solvent_element_mass_columns_list = []
        solvent_molecular_weight_list = []
        # 各溶媒の分子量と元素質量を取得
        for solvent_name_str in self.checked_solvent_list:
            if solvent_name_str in SOLVENT_ELEMENTAL_COMPOSITION_DATA:
                solvent_data_dict = SOLVENT_ELEMENTAL_COMPOSITION_DATA[solvent_name_str]
                current_solvent_element_masses = []
                solvent_molecular_weight_list.append(solvent_data_dict.get("sum", 0.0))
                for element_symbol_str in TARGET_ELEMENT_ORDER_LIST:
                    current_solvent_element_masses.append(
                        solvent_data_dict.get(element_symbol_str, 0.0)
                    )
                solvent_element_mass_columns_list.append(current_solvent_element_masses)
            else:
                print(
                    f"警告: 溶媒 '{solvent_name_str}' の原子質量データが見つかりません。"
                )
        # 溶媒の分子量と元素質量を配列に変換
        if solvent_element_mass_columns_list:
            self.solvent_element_mass_array = np.array(
                solvent_element_mass_columns_list
            ).T
        else:
            self.solvent_element_mass_array = np.empty(
                (len(TARGET_ELEMENT_ORDER_LIST), 0)
            )

        if solvent_molecular_weight_list:
            self.solvent_molecular_weight_array = np.array(
                solvent_molecular_weight_list
            )
        else:
            # solvent_molecular_weight_array は1次元配列なので、(0,) または np.array([]) が適切
            self.solvent_molecular_weight_array = np.array([])
        # 化合物の分子量の計算
        self.compound_molecular_weight = 0  # 初期化
        for element_symbol, count in parsed_compound_elements_dict.items():
            if element_symbol in ATOMIC_WEIGHTS_DICT:
                self.compound_molecular_weight += (
                    count * ATOMIC_WEIGHTS_DICT[element_symbol]
                )
        # 化合物中のC,H,N,Sの元素質量の計算
        compound_specific_element_mass_list = []
        for target_element in TARGET_ELEMENT_ORDER_LIST:
            if target_element in parsed_compound_elements_dict:
                compound_specific_element_mass_list.append(
                    parsed_compound_elements_dict[target_element]
                    * ATOMIC_WEIGHTS_DICT[target_element]
                )
            else:
                compound_specific_element_mass_list.append(0.0)
        # 化合物の元素質量を配列に変換
        self.compound_element_mass_array = np.array(compound_specific_element_mass_list)
        # 実測値の取得
        observed_element_fractions_list = [
            self.observed_c_var.get(),
            self.observed_h_var.get(),
            self.observed_n_var.get(),
            self.observed_s_var.get(),
        ]
        # 実測値を配列に変換
        self.observed_element_fractions_array = np.array(
            observed_element_fractions_list
        )

        print(f"チェックされた溶媒: {self.checked_solvent_list}")
        print(f"溶媒元素質量配列 shape: {self.solvent_element_mass_array.shape}")
        print(f"溶媒元素質量配列 content:\n{self.solvent_element_mass_array}")
        print(f"溶媒分子量配列 shape: {self.solvent_molecular_weight_array.shape}")
        print(f"溶媒分子量配列 content:\n{self.solvent_molecular_weight_array}")
        print(f"化合物分子量: {self.compound_molecular_weight}")
        print(f"化合物中元素質量配列: {self.compound_element_mass_array}")
        print(f"実測値配列: {self.observed_element_fractions_array}")

    def execute_optimization_calculations(self):
        # 定数行列の定義
        num_solvents = len(self.checked_solvent_list)
        num_elements = 4  # C, H, N, S

        if num_solvents == 0:
            print("最適化エラー: 溶媒が選択されていません。")
            # UI更新は呼び出し元や専用の関数で行うことを推奨
            # ここで直接UIを更新すると、メインスレッド以外からの呼び出しになる可能性がある
            self.root.after(
                0,
                lambda: self.analysis_result_var.set(
                    "最適化エラー: 溶媒が選択されていません。"
                ),
            )
            self.root.after(0, self.enable_ui_elements)
            return None  # 呼び出し元でNoneを処理できるようにする

        compound_element_masses = self.compound_element_mass_array
        solvent_element_masses_matrix = self.solvent_element_mass_array
        compound_mw_scalar = self.compound_molecular_weight
        solvent_mw_vector = self.solvent_molecular_weight_array
        observed_fractions = self.observed_element_fractions_array  # 実測値 (%)

        max_percentage_values = []
        min_percentage_values = []
        max_optimal_solvent_ratios = []
        min_optimal_solvent_ratios = []

        element_symbols_for_debug = ["C", "H", "N", "S"]  # デバッグ出力用

        for i in range(num_elements):
            N_val = compound_element_masses[i]
            B_vec = solvent_element_masses_matrix[i, :]
            M_val = compound_mw_scalar
            A_vec = solvent_mw_vector
            obs_percentage_val = observed_fractions[i]

            y_cc_var = cp.Variable(num_solvents, name=f"y_cc_elem{i}")
            t_cc_var = cp.Variable(nonneg=True, name=f"t_cc_elem{i}")  # t >= 0

            common_constraints = [
                M_val * t_cc_var + A_vec @ y_cc_var == 1,  # 分母の線形化
                y_cc_var >= 0,  # 元の変数 x >= 0
                y_cc_var <= 10 * t_cc_var,  # 元の変数 x <= 5
                # t_cc_var >= 1e-8 #  t > 0 を数値的に保証する場合 (分母がほぼ0になるのを避ける)
            ]

            # 目的関数 (パーセント値)
            objective_percentage_expr = 100 * (N_val * t_cc_var + B_vec @ y_cc_var)

            # --- 最大化 ---
            # 制約: 計算されるパーセント値 <= 実測値パーセント値
            constraints_for_max = common_constraints + [
                objective_percentage_expr <= obs_percentage_val
            ]
            problem_obj_max = cp.Maximize(objective_percentage_expr)

            try:
                prob_instance_max = cp.Problem(problem_obj_max, constraints_for_max)
                prob_instance_max.solve(solver=cp.ECOS)  # ECOSソルバーを指定
                if prob_instance_max.status in [cp.OPTIMAL, cp.OPTIMAL_INACCURATE]:
                    max_percentage_values.append(prob_instance_max.value)
                    if t_cc_var.value is not None and abs(t_cc_var.value) > 1e-9:
                        max_optimal_solvent_ratios.append(
                            y_cc_var.value / t_cc_var.value
                        )
                    else:
                        max_optimal_solvent_ratios.append(np.full(num_solvents, np.nan))
                else:
                    max_percentage_values.append(np.nan)
                    max_optimal_solvent_ratios.append(np.full(num_solvents, np.nan))
                    print(
                        f"Max problem for element {element_symbols_for_debug[i]} (obs={obs_percentage_val:.2f}%) status: {prob_instance_max.status}"
                    )
            except Exception as e:
                print(
                    f"Max problem for element {element_symbols_for_debug[i]} exception: {e}"
                )
                max_percentage_values.append(np.nan)
                max_optimal_solvent_ratios.append(np.full(num_solvents, np.nan))

            # --- 最小化 ---
            # 制約: 計算されるパーセント値 >= 実測値パーセント値
            constraints_for_min = common_constraints + [
                objective_percentage_expr >= obs_percentage_val
            ]
            problem_obj_min = cp.Minimize(objective_percentage_expr)

            try:
                prob_instance_min = cp.Problem(problem_obj_min, constraints_for_min)
                prob_instance_min.solve(solver=cp.ECOS)  # ECOSソルバーを指定
                if prob_instance_min.status in [cp.OPTIMAL, cp.OPTIMAL_INACCURATE]:
                    min_percentage_values.append(prob_instance_min.value)
                    if t_cc_var.value is not None and abs(t_cc_var.value) > 1e-9:
                        min_optimal_solvent_ratios.append(
                            y_cc_var.value / t_cc_var.value
                        )
                    else:
                        min_optimal_solvent_ratios.append(np.full(num_solvents, np.nan))
                else:
                    min_percentage_values.append(np.nan)
                    min_optimal_solvent_ratios.append(np.full(num_solvents, np.nan))
                    print(
                        f"Min problem for element {element_symbols_for_debug[i]} (obs={obs_percentage_val:.2f}%) status: {prob_instance_min.status}"
                    )
            except Exception as e:
                print(
                    f"Min problem for element {element_symbols_for_debug[i]} exception: {e}"
                )
                min_percentage_values.append(np.nan)
                min_optimal_solvent_ratios.append(np.full(num_solvents, np.nan))
        # 結果の表示
        print(f"最大値{max_percentage_values}")
        print(f"ｘ：{max_optimal_solvent_ratios}")

        print(f"最小値{min_percentage_values}")
        print(f"X:{min_optimal_solvent_ratios}")

        return (
            max_optimal_solvent_ratios,
            min_optimal_solvent_ratios,
        )

    def evaluate_elemental_analysis(
        self, max_optimal_solvent_ratios, min_optimal_solvent_ratios
    ):
        # ここで、max_optimal_solvent_ratios と min_optimal_solvent_ratios を評価し、結果を表示するロジックを実装します。
        # 例えば、最適な溶媒比率やその意味をユーザーに伝えることができます。
        compound_element_masses = self.compound_element_mass_array
        solvent_element_masses_matrix = self.solvent_element_mass_array
        compound_mw_scalar = self.compound_molecular_weight
        solvent_mw_vector = self.solvent_molecular_weight_array
        observed_fractions = self.observed_element_fractions_array  # 実測値 (%)

        for array in max_optimal_solvent_ratios:
            print(f"Current array in max_optimal_solvent_ratios: {array}")
            if np.all(np.isnan(array)):  # array の全要素が nan かどうかをチェック
                print(f"Skipping calculation for array with all NaNs: {array}")
                continue  # すべて nan ならこの array での計算をスキップ
            istrue = abs(
                observed_fractions
                - 100
                * (
                    (compound_element_masses + solvent_element_masses_matrix @ array)
                    / (compound_mw_scalar + solvent_mw_vector @ array)
                )
            ) >= np.array([0.3, 0.3, 0.3, 0.3])
            if not istrue.any():
                print("アウンカモデス!")
                print(
                    100
                    * (
                        (
                            compound_element_masses
                            + solvent_element_masses_matrix @ array
                        )
                        / (compound_mw_scalar + solvent_mw_vector @ array)
                    )
                )
                self.optimized_value = 100 * (
                    (compound_element_masses + solvent_element_masses_matrix @ array)
                    / (compound_mw_scalar + solvent_mw_vector @ array)
                )
                return True
        for array in min_optimal_solvent_ratios:
            print(f"Current array in min_optimal_solvent_ratios: {array}")
            if np.all(np.isnan(array)):  # array の全要素が nan かどうかをチェック
                print(f"Skipping calculation for array with all NaNs: {array}")
                continue  # すべて nan ならこの array での計算をスキップ
            istrue = abs(
                observed_fractions
                - 100
                * (
                    (compound_element_masses + solvent_element_masses_matrix @ array)
                    / (compound_mw_scalar + solvent_mw_vector @ array)
                )
            ) >= np.array([0.3, 0.3, 0.3, 0.3])
            if not istrue.any():
                print("アウンカモデス!")
                print(
                    100
                    * (
                        (
                            compound_element_masses
                            + solvent_element_masses_matrix @ array
                        )
                        / (compound_mw_scalar + solvent_mw_vector @ array)
                    )
                )
                self.optimized_value = 100 * (
                    (compound_element_masses + solvent_element_masses_matrix @ array)
                    / (compound_mw_scalar + solvent_mw_vector @ array)
                )
                return True
        print("アワンデス!")
        return False


if __name__ == "__main__":
    # Example usage
    root = tk.Tk()
    analysis = elemental_analysis(root)
    root.mainloop()
