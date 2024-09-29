import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
from deep_translator import GoogleTranslator
import os
import re
import json

# Übersetzungsfunktion
def translate_text(text, src_lang, dest_lang):
    try:
        if text.strip():  # Überspringe leere Zeilen
            translator = GoogleTranslator(source=src_lang, target=dest_lang)
            translated_text = translator.translate(text)
            return translated_text if translated_text else text  # Fallback auf Originaltext, wenn None zurückgegeben wird
        else:
            return text  # Leere Zeilen unverändert lassen
    except Exception as e:
        raise Exception(f"Fehler bei der Google Translate-Übersetzung: {str(e)}")

# JSON-Datei verarbeiten, ohne die Struktur zu verändern
def process_json_file(file_path, src_lang, dest_lang, progress_var, progress_bar, translate_names, translate_descs):
    with open(file_path, 'r', encoding='utf-8') as file:
        json_data = file.read()

    def translate_json_text(match):
        original_text = match.group(1)
        translated_text = translate_text(original_text, src_lang, dest_lang)
        return f'"{translated_text}"'

    # Regex für das Finden von Strings innerhalb der JSON-Datei
    string_pattern = r'\"(.*?)\"'  # Sucht nach Texten in Anführungszeichen
    translated_data = re.sub(string_pattern, translate_json_text, json_data)

    # Fortschritt aktualisieren
    progress_var.set(100)
    progress_bar.update()

    translated_file_path = file_path.replace('.json', '_translated.json')
    with open(translated_file_path, 'w', encoding='utf-8') as file:
        file.write(translated_data)

    return translated_file_path

# Text- oder RPY-Dateien verarbeiten
def process_text_file(file_path, src_lang, dest_lang, progress_var, progress_bar):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    total_lines = len(lines)
    translated_lines = []

    for i, line in enumerate(lines):
        # Nur nicht-leere Zeilen übersetzen
        if line.strip():
            translated_text = translate_text(line.strip(), src_lang, dest_lang)
            translated_lines.append((translated_text or line.strip()) + '\n')  # Fallback auf Originaltext bei None
        else:
            translated_lines.append('\n')  # Leere Zeilen beibehalten

        # Fortschritt aktualisieren
        progress_var.set((i + 1) / total_lines * 100)
        progress_bar.update()

    # Datei speichern
    translated_file_path = file_path.replace('.rpy', '_translated.rpy').replace('.txt', '_translated.txt')
    with open(translated_file_path, 'w', encoding='utf-8') as file:
        file.writelines(translated_lines)

    return translated_file_path

# Hauptübersetzungsprozess für verschiedene Dateitypen
def process_file(file_path, src_lang, dest_lang, progress_var, progress_bar):
    file_extension = os.path.splitext(file_path)[1]
    if file_extension == '.json':
        return process_json_file(file_path, src_lang, dest_lang, progress_var, progress_bar, True, True)
    elif file_extension == '.rpy' or file_extension == '.txt':
        return process_text_file(file_path, src_lang, dest_lang, progress_var, progress_bar)
    else:
        raise Exception("Nur JSON-, RPY- und TXT-Dateien werden unterstützt.")

# GUI-Elemente und Startlogik
def start_translation():
    src_lang = src_lang_var.get()
    dest_lang = dest_lang_var.get()
    file_path = file_path_var.get()

    if not file_path:
        messagebox.showwarning("Warnung", "Bitte wählen Sie eine Datei aus.")
        return

    try:
        translated_file_path = process_file(file_path, src_lang, dest_lang, progress_var, progress_bar)
        messagebox.showinfo("Erfolg", f"Die Datei wurde erfolgreich übersetzt: {translated_file_path}")
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler bei der Übersetzung: {str(e)}")

# Datei auswählen
def choose_file():
    file_path = filedialog.askopenfilename(title="Wählen Sie eine Datei", filetypes=[("JSON, TXT, RPY Dateien", "*.json *.txt *.rpy")])
    file_path_var.set(file_path)

# GUI
root = tk.Tk()
root.title("Übersetzungsprogramm für JSON, TXT und RPY")
root.geometry("500x400")

# Sprachoptionen
src_lang_var = tk.StringVar(value="auto")
dest_lang_var = tk.StringVar(value="de")

# Dateipfad-Variable
file_path_var = tk.StringVar()

# Fortschrittsvariable
progress_var = tk.DoubleVar(value=0)

# GUI-Elemente erstellen
tk.Label(root, text="Quelle Sprache (z.B., 'en')").pack(pady=5)
tk.Entry(root, textvariable=src_lang_var).pack(pady=5)

tk.Label(root, text="Ziel Sprache (z.B., 'de')").pack(pady=5)
tk.Entry(root, textvariable=dest_lang_var).pack(pady=5)

tk.Button(root, text="Datei auswählen", command=choose_file).pack(pady=10)
tk.Entry(root, textvariable=file_path_var, width=50).pack(pady=5)

tk.Button(root, text="Start", command=start_translation).pack(pady=10)

# Fortschrittsbalken
progress_bar = Progressbar(root, orient="horizontal", length=400, mode="determinate", variable=progress_var)
progress_bar.pack(pady=20)

# GUI-Schleife starten
root.mainloop()
