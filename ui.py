# ui.py
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import winsound
from PIL import Image, ImageTk

from sm3 import sm3_hash
from record_manager import (
    add_file_hash,
    get_file_hash,
    update_file_remark,
    get_all_records
)

class FileIntegrityGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("文件完整性保护系统 - 基于SM3")
        # Overall window background
        self.root.configure(bg="#FFFFFF")

        # Use the available theme; if "vista" is unavailable, fallback to "clam".
        style = ttk.Style()
        available_themes = style.theme_names()
        if "vista" in available_themes:
            style.theme_use("vista")
        else:
            style.theme_use("clam")

        # ------------- 1) Custom global style -------------
        # Main frame style: dark background
        style.configure("Dark.TFrame", background="#313131")

        # The background of the Label follows the parent container by default; here, the foreground color is set separately.
        style.configure("Dark.TLabel", background="#434343", foreground="#dcdcdc")

        # "Smooth" button style: remove the light blue border, keeping it purely smooth.
        style.configure("Smooth.TButton",
                        background="#dcdcdc",
                        foreground="#313131",
                        padding=6,
                        relief="flat")  # Do not display the frame
        # Color change on mouse hover/press
        style.map("Smooth.TButton",
                  background=[("active", "#434343"), ("pressed", "#434343")],
                  foreground=[("active", "#313131"), ("pressed", "#313131")])

        # Make the main window responsive to changes in width and height
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Main frame
        main_frame = ttk.Frame(root, style="Dark.TFrame", padding=10)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW)
        main_frame.rowconfigure(4, weight=1)  # Log area is expandable
        for col in range(4):
            main_frame.columnconfigure(col, weight=1)

        # ------------- 2) Usage Instructions -------------
        usage_text = (
            "使用说明：\n"
            "1. 点击“选择文件”按钮选择需要保护的文件。\n"
            "2. 点击“初装记录”按钮记录文件的 SM3 哈希值。\n"
            "3. 点击“完整性校验”按钮检查文件是否被篡改。\n"
            "4. 点击“查看记录”按钮查看和管理所有记录。\n\n"
            "作者：钟岩、封佳扬、覃大睿  武汉大学国家网络安全学院\n"
        )
        usage_label = ttk.Label(main_frame, text=usage_text, style="Dark.TLabel", justify=tk.LEFT, font=("宋体", 14))
        usage_label.grid(row=0, column=0, columnspan=4, sticky=tk.W, padx=5, pady=15)

        # ------------- 3) File selection row -------------
        self.file_path_var = tk.StringVar(value="未选择文件")
        self.file_entry = ttk.Entry(main_frame, textvariable=self.file_path_var, state='readonly')
        self.file_entry.grid(row=1, column=0, columnspan=3, sticky=tk.EW, padx=5, pady=5)

        self.select_button = self.create_button(main_frame, "选择文件", self.select_file)
        self.select_button.grid(row=1, column=3, padx=5, pady=5, sticky=tk.EW)

        # ------------- 4) Action button row -------------
        self.install_button = self.create_button(main_frame, "初装记录", self.record_file_hash)
        self.install_button.grid(row=2, column=0, padx=5, pady=5, sticky=tk.EW)

        self.check_button = self.create_button(main_frame, "完整性校验", self.check_file_integrity)
        self.check_button.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)

        self.view_button = self.create_button(main_frame, "查看记录", self.show_all_records_window)
        self.view_button.grid(row=2, column=2, padx=5, pady=5, sticky=tk.EW)

        self.exit_button = self.create_button(main_frame, "退出", root.quit)
        self.exit_button.grid(row=2, column=3, padx=5, pady=5, sticky=tk.EW)

        # ------------- 5) Log output area -------------
        self.result_text = tk.Text(main_frame, height=10, state='disabled',
                                   wrap="word",
                                   bg="#434343",       # Background unified with the overall design
                                   fg="#dcdcdc",       # Foreground color is light gray
                                   relief="flat")      # Remove the traditional border
        self.result_text.grid(row=4, column=0, columnspan=4, sticky=tk.NSEW, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        scrollbar.grid(row=4, column=4, sticky=tk.NS)
        self.result_text.configure(yscrollcommand=scrollbar.set)

        # ------------- 6) Animation progress indicator -------------
        self.spinner_label = ttk.Label(main_frame, style="Dark.TLabel")  # Background color
        self.spinner_label.grid(row=3, column=0, columnspan=4, pady=10)
        self.spinner_running = False
        self.spinner_images = []
        self.spinner_index = 0
        self.load_spinner_images()

    def create_button(self, parent, text, command):
        """Wrap the button click event, play sound effect + execute command"""
        def on_click():
            # Play click sound effect (requires click.wav in the same directory), ignore if it fails
            try:
                winsound.PlaySound("click.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
            except:
                pass
            command()

        # Use the custom style Smooth.TButton
        btn = ttk.Button(parent, text=text, command=on_click, style="Smooth.TButton")
        return btn

    # ---------------- Loading animation frame ----------------
    def load_spinner_images(self):
        """Load each frame of the animated GIF"""
        try:
            spinner_image = Image.open("spinner.gif")
            for frame in range(spinner_image.n_frames):
                spinner_image.seek(frame)
                frame_image = ImageTk.PhotoImage(
                    spinner_image.copy().resize((100, 10), Image.Resampling.LANCZOS)
                )
                self.spinner_images.append(frame_image)
        except Exception as e:
            self.log_message(f"[错误] 无法加载动画GIF: {e}")

    def start_spinner(self):
        if not self.spinner_images:
            return
        if not self.spinner_running:
            self.spinner_running = True
            self.animate_spinner()

    def animate_spinner(self):
        if not self.spinner_running:
            return
        frame = self.spinner_images[self.spinner_index]
        self.spinner_label.configure(image=frame)
        self.spinner_index = (self.spinner_index + 1) % len(self.spinner_images)
        self.root.after(50, self.animate_spinner)  # Switch frame every 50ms

    def stop_spinner(self):
        self.spinner_running = False
        self.spinner_label.configure(image='')  # Remove all the pictures

    # ---------------- File selection ----------------
    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_path_var.set(file_path)
            self.log_message("选择文件: " + file_path)

    # ---------------- Initial installation records ----------------
    def record_file_hash(self):
        file_path = self.file_path_var.get()
        if not file_path or file_path == "未选择文件" or not os.path.exists(file_path):
            messagebox.showerror("错误", "请先选择有效的文件")
            return

        # Before adding a new record, check if the file path already exists
        existing_record = get_file_hash(file_path)  # Get the saved hash value
        if existing_record:
            # If the record exists, prompt and display the original SM3 value
            existing_hash = existing_record
            messagebox.showinfo("提示", f"该文件已有记录。SM3值: {existing_hash}")
            self.log_message(f"[记录重复] 文件: {file_path} 已存在，SM3值: {existing_hash}")
            return

        thread = threading.Thread(target=self._record_task, args=(file_path,), daemon=True)
        thread.start()


    def _record_task(self, file_path):
        self.start_spinner()
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            hash_value = sm3_hash(data)
            add_file_hash(file_path, hash_value, remark=None)

            self.log_message(f"[初装记录] 文件: {file_path}\nSM3: {hash_value}\n记录已保存.")
            messagebox.showinfo("提示", "初装记录完成！")
        except Exception as e:
            self.log_message(f"[错误] 记录失败: {e}")
            messagebox.showerror("错误", f"记录失败: {e}")
        finally:
            self.stop_spinner()

    # ---------------- Integrity check ----------------
    def check_file_integrity(self):
        file_path = self.file_path_var.get()
        if not file_path or file_path == "未选择文件" or not os.path.exists(file_path):
            messagebox.showerror("错误", "请先选择有效的文件")
            return

        thread = threading.Thread(target=self._integrity_task, args=(file_path,), daemon=True)
        thread.start()

    def _integrity_task(self, file_path):
        self.start_spinner()
        try:
            stored_hash = get_file_hash(file_path)
            if not stored_hash:
                messagebox.showwarning("警告", "该文件没有初装记录，无法进行校验")
                self.log_message(f"[校验失败] 文件: {file_path} 没有初装记录。")
                return

            with open(file_path, 'rb') as f:
                data = f.read()

            current_hash = sm3_hash(data)

            if current_hash == stored_hash:
                self.log_message(f"[完整性校验] 文件: {file_path}\nSM3 校验通过!")
                messagebox.showinfo("完整性校验", "文件完整性校验通过！")
            else:
                self.log_message(f"[完整性校验] 文件: {file_path}\nSM3 校验失败!")
                messagebox.showerror("完整性校验", "文件完整性校验失败！")
        except Exception as e:
            self.log_message(f"[错误] 校验失败: {e}")
            messagebox.showerror("错误", f"校验失败: {e}")
        finally:
            self.stop_spinner()

    # ---------------- View records ----------------
    def show_all_records_window(self):
        records = get_all_records()
        if not records:
            messagebox.showinfo("提示", "还没有任何文件的记录。")
            return

        records_window = tk.Toplevel(self.root)
        records_window.title("查看/管理文件记录")
        records_window.geometry("850x450")
        records_window.configure(bg="#2D2A2E")

        columns = ("file_path", "hash_value", "remark")
        tree = ttk.Treeview(records_window, columns=columns, show='headings', height=15, style="Treeview")
        tree.heading("file_path", text="文件路径")
        tree.heading("hash_value", text="SM3哈希")
        tree.heading("remark", text="备注")

        tree.column("file_path", width=350, anchor='w')
        tree.column("hash_value", width=350, anchor='w')
        tree.column("remark", width=150, anchor='center')

        for fp, info in records.items():
            h = info.get("hash", "")
            r = info.get("remark", "")
            tree.insert("", tk.END, values=(fp, h, r))

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5), pady=5)

        scrollbar = ttk.Scrollbar(records_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y, pady=5)

        # Remark modification area
        frame_right = ttk.Frame(records_window, style="Dark.TFrame", padding=10)
        frame_right.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        remark_label = ttk.Label(frame_right, text="新的备注：", style="Dark.TLabel")
        remark_label.pack(pady=5)

        remark_var = tk.StringVar()
        remark_entry = ttk.Entry(frame_right, textvariable=remark_var)
        remark_entry.pack(pady=5)

        def update_remark():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("警告", "请先选中一条记录")
                return
            item_id = selection[0]
            vals = tree.item(item_id, "values")
            fpath = vals[0]
            new_remark = remark_var.get().strip()
            if not new_remark:
                messagebox.showwarning("警告", "备注不能为空")
                return
            update_file_remark(fpath, new_remark)
            tree.set(item_id, "remark", new_remark)
            remark_var.set("")
            self.log_message(f"[备注更新] {fpath} => {new_remark}")
            messagebox.showinfo("提示", "备注已更新！")

        update_btn = ttk.Button(frame_right, text="更新备注", command=update_remark, style="Smooth.TButton")
        update_btn.pack(pady=5, fill=tk.X)

        def delete_record():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("警告", "请先选中一条记录")
                return
            item_id = selection[0]
            vals = tree.item(item_id, "values")
            fpath = vals[0]

            confirm = messagebox.askyesno("确认", f"确定要删除记录?\n{fpath}")
            if confirm:
                all_recs = get_all_records()
                if fpath in all_recs:
                    del all_recs[fpath]
                    # Manual save
                    with open("hash_record.json", "w", encoding="utf-8") as f:
                        import json
                        json.dump(all_recs, f, ensure_ascii=False, indent=4)
                    tree.delete(item_id)
                    self.log_message(f"[记录删除] {fpath} 已删除")
                    messagebox.showinfo("提示", "记录已删除。")
                else:
                    messagebox.showerror("错误", "未找到该文件的记录。")

        del_btn = ttk.Button(frame_right, text="删除记录", command=delete_record, style="Smooth.TButton")
        del_btn.pack(pady=5, fill=tk.X)

    # ------------- Log printing -------------
    def log_message(self, message):
        """Add log message to the text box"""
        self.result_text.configure(state='normal')
        self.result_text.insert(tk.END, message + "\n")
        self.result_text.configure(state='disabled')
        self.result_text.yview(tk.END)

# ---------------- Main program entry ----------------
def main():
    root = tk.Tk()
    app = FileIntegrityGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
