from os.path import join, dirname
import os

def save_file_subtitle(content: str, id: int, lang: str):
    output_path = join(dirname(__file__), '..', 'resources')

    file_path = f"{output_path}/{id}_{lang}.srt"
    if os.path.exists(file_path):
        return file_path

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

    return file_path