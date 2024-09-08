from Translate import long_zh_translate_en
from collections import defaultdict
import asyncio, glob, os, shutil, threading
from Keyphrase import Keyword

class FileProcessor:
    def __init__(self):
        self._thread = None
        self._stop = False

    def process_files(self):
        """依序執行指令"""
        self._stop = False  # 重置停止標誌
        pdf_files = self.get_pdf_files()
        for pdf_file in pdf_files:
            directory = os.path.dirname(pdf_file).replace('uploads', 'resource')
            file_name = os.path.basename(pdf_file).replace('.pdf', '')
            md_path = os.path.join(directory, file_name, f'{file_name}.md')
            en_path = os.path.join(directory, file_name, f'{file_name}_en.txt')
            keyphrase_path = os.path.join(directory, file_name, f'{file_name}_keyphrase.csv')
            if self._stop:
                print(f"Processing stopped at {pdf_file}")
                break
            if not os.path.exists(md_path):
                cmd = f'marker_single "{pdf_file}" "{directory}"'
                print(f"Executing: {cmd}")
                os.system(cmd)  # 使用同步方式執行外部命令
            if not os.path.exists(en_path):
                with open(md_path, 'r', encoding='UTF-8') as f:
                    text = f.read()
                en_text = long_zh_translate_en(text)
                with open(en_path, 'w', encoding='UTF-8') as f:
                    f.write(en_text)
            if not os.path.exists(keyphrase_path):
                kw = Keyword()
                kw_result = kw.run([keyphrase_path])
        self._thread = None

    def is_running(self):
        """檢查是否仍在執行"""
        return self._thread is not None and self._thread.is_alive()

    def stop_processing(self):
        """停止執行"""
        self._stop = True

    def start_processing(self):
        """啟動處理程序"""
        if not self.is_running():
            print("Processing will begin.")
            self._thread = threading.Thread(target=self.process_files)
            self._thread.daemon = True
            self._thread.start()
        else:
            print("Processing is already running")

    def get_pdf_files(self):
        """從指定資料夾中搜尋所有 PDF 檔案"""
        return glob.glob('uploads/**/*.pdf', recursive=True)

    def get_csv_files(self):
        """從指定資料夾中搜尋所有 PDF 檔案"""
        return glob.glob('resource/**/*.csv', recursive=True)
    
    def get_finished_files(self):
        pdf_files = self.get_pdf_files()
        csv_files = self.get_csv_files()
        pdf_files = [os.path.join(*os.path.normpath(path).split(os.sep)[1:])[:-4] for path in pdf_files]
        csv_files = [os.path.join(*os.path.normpath(path).split(os.sep)[1:-1]) for path in csv_files]
        common_files = set(pdf_files) & set(csv_files)
        return list(common_files)
    
    def move_file(self, folder, new_folder, file_name):
        try:
            file_path = os.path.join("uploads", folder, f'{file_name}.pdf')
            folder_path = os.path.join("resource", folder, file_name)
            file_new_path = os.path.join("uploads", new_folder, f'{file_name}.pdf')
            folder_new_path = os.path.join("resource", new_folder, file_name)
            if os.path.exists(file_path):
                shutil.move(file_path, file_new_path)
                print(f"File {file_path} has been successfully moved.")
            if os.path.exists(folder_path):
                shutil.move(folder_path, folder_new_path)
                print(f"Folder {folder_path} has been successfully moved.")
            return True
        except Exception as e:
            print(f"An error occurred while trying to move the file or folder: {e}")
            return False

    def delete_file(self, folder, file_name):
        try:
            file_path = os.path.join("uploads", folder, f'{file_name}.pdf')
            folder_path = os.path.join("resource", folder, file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"File {file_path} has been successfully deleted.")
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
                print(f"Folder {folder_path} has been successfully deleted.")
            return True
        except Exception as e:
            print(f"An error occurred while trying to delete the file or folder: {e}")
            return False

    def get_uploads_folders(self):
        # 初始化一個字典來存放資料夾名稱和對應的文件名稱
        folder_dict = defaultdict(list)

        # 遍歷 pdf_list，並將資料夾名稱與文件名稱進行分組
        for pdf_path in self.get_pdf_files():
            # 分離路徑和文件名稱
            folder_path, file_name = os.path.split(pdf_path)
            # 取得資料夾名稱
            folder_name = os.path.basename(folder_path)
            # 去除文件名稱的擴展名
            file_name_without_ext = os.path.splitext(file_name)[0]
            # 將文件名稱加入到對應的資料夾中
            folder_dict[folder_name].append(file_name_without_ext)

        # 將資料夾字典轉換為所需的列表格式
        folder_list = [{'name': folder, 'fileNames': files} for folder, files in folder_dict.items()]

        return folder_list
    
    def get_resource_folders(self):
        folder_dict = defaultdict(list)
        for csv_path in self.get_csv_files():
            folder_path, file_name = os.path.split(csv_path)
            folder_path, file_name = os.path.split(folder_path)
            folder_name = os.path.basename(folder_path)
            folder_dict[folder_name].append(file_name)
        return [{'name': folder, 'fileNames': files} for folder, files in folder_dict.items()]
