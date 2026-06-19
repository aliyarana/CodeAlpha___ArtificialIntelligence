"""
TASK 1: LANGUAGE TRANSLATION TOOL
CodeAlpha Artificial Intelligence Internship

A GUI application that translates text between languages using
the Google Translate API (via deep-translator library).

Features:
- Enter text manually
- Select source and target language from dropdowns
- Translate with one click
- Copy translated text to clipboard
- Text-to-speech for translated text (optional feature)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from deep_translator import GoogleTranslator

# Optional: text-to-speech feature
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False


# ── Supported Languages ──────────────────────────────────────────
LANGUAGES = {
    "Auto Detect": "auto",
    "English": "en",
    "Urdu": "ur",
    "Arabic": "ar",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Chinese (Simplified)": "zh-CN",
    "Hindi": "hi",
    "Japanese": "ja",
    "Korean": "ko",
    "Russian": "ru",
    "Turkish": "tr",
    "Italian": "it",
    "Portuguese": "pt",
}


class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Language Translator — CodeAlpha")
        self.root.geometry("650x550")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        if TTS_AVAILABLE:
            self.engine = pyttsx3.init()

        self.build_ui()

    def build_ui(self):
        # Title
        title = tk.Label(
            self.root, text="🌐 AI Language Translator",
            font=("Segoe UI", 20, "bold"), bg="#1e1e2e", fg="#89b4fa"
        )
        title.pack(pady=15)

        # Language selection frame
        lang_frame = tk.Frame(self.root, bg="#1e1e2e")
        lang_frame.pack(pady=5)

        tk.Label(lang_frame, text="From:", font=("Segoe UI", 11),
                  bg="#1e1e2e", fg="#cdd6f4").grid(row=0, column=0, padx=10)
        self.source_lang = ttk.Combobox(
            lang_frame, values=list(LANGUAGES.keys()), width=20, state="readonly"
        )
        self.source_lang.set("Auto Detect")
        self.source_lang.grid(row=0, column=1, padx=5)

        swap_btn = tk.Button(
            lang_frame, text="⇄", font=("Segoe UI", 12, "bold"),
            bg="#313244", fg="#89b4fa", relief="flat", command=self.swap_languages
        )
        swap_btn.grid(row=0, column=2, padx=10)

        tk.Label(lang_frame, text="To:", font=("Segoe UI", 11),
                  bg="#1e1e2e", fg="#cdd6f4").grid(row=0, column=3, padx=10)
        self.target_lang = ttk.Combobox(
            lang_frame, values=list(LANGUAGES.keys()), width=20, state="readonly"
        )
        self.target_lang.set("Urdu")
        self.target_lang.grid(row=0, column=4, padx=5)

        # Input text box
        tk.Label(self.root, text="Enter text:", font=("Segoe UI", 11),
                  bg="#1e1e2e", fg="#cdd6f4").pack(anchor="w", padx=30, pady=(20, 0))
        self.input_text = tk.Text(
            self.root, height=6, width=68, font=("Segoe UI", 11),
            bg="#313244", fg="#cdd6f4", insertbackground="white", wrap="word"
        )
        self.input_text.pack(padx=30, pady=5)

        # Translate button
        translate_btn = tk.Button(
            self.root, text="Translate ➜", font=("Segoe UI", 12, "bold"),
            bg="#89b4fa", fg="#1e1e2e", relief="flat", padx=20, pady=8,
            command=self.translate_text
        )
        translate_btn.pack(pady=15)

        # Output text box
        tk.Label(self.root, text="Translated text:", font=("Segoe UI", 11),
                  bg="#1e1e2e", fg="#cdd6f4").pack(anchor="w", padx=30)
        self.output_text = tk.Text(
            self.root, height=6, width=68, font=("Segoe UI", 11),
            bg="#313244", fg="#a6e3a1", wrap="word"
        )
        self.output_text.pack(padx=30, pady=5)

        # Bottom buttons: Copy + Speak
        btn_frame = tk.Frame(self.root, bg="#1e1e2e")
        btn_frame.pack(pady=10)

        copy_btn = tk.Button(
            btn_frame, text="📋 Copy", font=("Segoe UI", 10),
            bg="#313244", fg="#cdd6f4", relief="flat", padx=15, pady=5,
            command=self.copy_to_clipboard
        )
        copy_btn.grid(row=0, column=0, padx=10)

        speak_btn = tk.Button(
            btn_frame, text="🔊 Speak", font=("Segoe UI", 10),
            bg="#313244", fg="#cdd6f4", relief="flat", padx=15, pady=5,
            command=self.speak_text
        )
        speak_btn.grid(row=0, column=1, padx=10)

    def swap_languages(self):
        src = self.source_lang.get()
        tgt = self.target_lang.get()
        if src != "Auto Detect":
            self.source_lang.set(tgt)
            self.target_lang.set(src)

    def translate_text(self):
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Empty Input", "Please enter some text to translate.")
            return

        src_code = LANGUAGES[self.source_lang.get()]
        tgt_code = LANGUAGES[self.target_lang.get()]

        try:
            translated = GoogleTranslator(source=src_code, target=tgt_code).translate(text)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, translated)
        except Exception as e:
            messagebox.showerror("Translation Error", f"Could not translate text.\n\n{e}")

    def copy_to_clipboard(self):
        translated = self.output_text.get("1.0", tk.END).strip()
        if translated:
            self.root.clipboard_clear()
            self.root.clipboard_append(translated)
            messagebox.showinfo("Copied", "Translated text copied to clipboard!")
        else:
            messagebox.showwarning("Nothing to Copy", "Translate some text first.")

    def speak_text(self):
        translated = self.output_text.get("1.0", tk.END).strip()
        if not translated:
            messagebox.showwarning("Nothing to Speak", "Translate some text first.")
            return
        if TTS_AVAILABLE:
            self.engine.say(translated)
            self.engine.runAndWait()
        else:
            messagebox.showinfo("TTS Not Available", "Install pyttsx3 to enable text-to-speech:\npip install pyttsx3")


# ── CONSOLE VERSION (fallback, no GUI needed) ───────────────────
def console_version():
    print("=" * 50)
    print("  AI LANGUAGE TRANSLATOR (Console Mode)")
    print("=" * 50)
    print("Available languages:", ", ".join(LANGUAGES.keys()))

    while True:
        text = input("\nEnter text to translate (or 'exit' to quit): ")
        if text.lower() == "exit":
            break
        src = input("Source language (e.g. English) [Auto Detect]: ") or "Auto Detect"
        tgt = input("Target language (e.g. Urdu): ")

        src_code = LANGUAGES.get(src, "auto")
        tgt_code = LANGUAGES.get(tgt, "en")

        try:
            result = GoogleTranslator(source=src_code, target=tgt_code).translate(text)
            print(f"\n✅ Translated ({tgt}): {result}")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    import sys
    if "--console" in sys.argv:
        console_version()
    else:
        try:
            root = tk.Tk()
            app = TranslatorApp(root)
            root.mainloop()
        except tk.TclError:
            print("No display found. Running console version instead.\n")
            console_version()
