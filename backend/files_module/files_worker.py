import os
import base64


def save_to_txt(file_name, file_data):
    """
    Сохраняет строки в txt-файл с обработкой ошибок.

    :param file_name: Имя сохраняемого файла
    :param file_data: Данные файла в формате base64
    """
    try:
        # Определяем путь для сохранения файла
        file_path = os.path.join('uploads', file_name)

        # Убеждаемся, что директория существует
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Декодируем и сохраняем файл
        with open(file_path, 'wb') as f:
            file_content = base64.b64decode(
                file_data.split(',')[1])  # Декодируем base64
            f.write(file_content)

        print(f"File {file_name} saved successfully!")
    except (IndexError, ValueError) as decode_error:
        print(f"""Ошибка декодирования base64 для файла
              {file_name}: {decode_error}""")
    except FileNotFoundError as fnf_error:
        print(f"""Ошибка: директория не найдена для файла
              {file_name}: {fnf_error}""")
    except Exception as e:
        print(f"""Произошла неожиданная ошибка при сохранении файла
              {file_name}: {e}""")
