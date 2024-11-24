from io import BytesIO
import subprocess
import requests
from fastapi import FastAPI
from PIL import Image
from PyPDF2 import PdfMerger
import os

app = FastAPI()

img_list: list[str] = [
    'https://assets.pureglobal.cn/builder/demo-file/1.png',
    'https://assets.pureglobal.cn/builder/demo-file/2.png',
    'https://assets.pureglobal.cn/builder/demo-file/9.png',
]
pdf_list: list[str] = [
    'https://assets.pureglobal.cn/builder/demo-file/Res.No_.152%20Regulacion%20E%20100-21%20red%20(1).pdf'
]
word_list: list[str] = [
    'https://assets.pureglobal.cn/builder/demo-file/PROYECTO%20DE%20REGISTRO.docx',
    'https://assets.pureglobal.cn/builder/demo-file/demo.docx',
]


@app.get('/')
async def root():
    """
    root
    """
    output_pdf = 'final_combined.pdf'
    await combine_pdfs(img_list, word_list, pdf_list, output_pdf)

    return {'message': 'PDFs combined successfully!', 'output_pdf': output_pdf}



async def combine_pdfs(img_urls: list[str], word_urls: list[str], pdf_urls: list[str], output_pdf: str):
    """
    合并多个 PDF 文件
    :param img_urls: 图片 URL 列表
    :param word_urls: Word 文件 URL 列表
    :param pdf_urls: PDF 文件 URL 列表
    :param output_pdf: 最终合并的 PDF 文件路径
    """
    temp_pdfs = []  # 存储中间生成的 PDF 文件路径

    # 转换图片为 PDF
    for i, img_url in enumerate(img_urls):
        temp_pdf = f'temp_img_{i + 1}.pdf'
        await convert_img_to_pdf(img_url, temp_pdf)
        temp_pdfs.append(temp_pdf)

    # 转换 Word 为 PDF
    for i, word_url in enumerate(word_urls):
        temp_pdf = f'temp_word_{i + 1}.pdf'
        await convert_word_to_pdf(word_url, temp_pdf)
        temp_pdfs.append(temp_pdf)

    # 下载现有 PDF 文件
    for i, pdf_url in enumerate(pdf_urls):
        temp_pdf = f'temp_pdf_{i + 1}.pdf'
        await download_file(pdf_url, temp_pdf)
        temp_pdfs.append(temp_pdf)

    # 合并所有 PDF 文件
    merge_pdfs(temp_pdfs, output_pdf)

    # 清理临时文件
    for temp_file in temp_pdfs:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    print(f'所有临时文件已清理！最终 PDF 文件：{output_pdf}')


async def convert_img_to_pdf(image_url: str, output_pdf: str):
    """
    将线上图片 URL 下载并转换为 PDF
    :param image_url: 图片 URL
    :param output_pdf: 输出 PDF 文件路径
    """
    try:
        # 从 URL 下载图片
        response = requests.get(image_url)
        response.raise_for_status()  # 检查请求是否成功

        # 将下载的内容读取为图片
        image = Image.open(BytesIO(response.content))

        # 转换为 RGB 模式（部分图片可能是 RGBA 格式，PDF 不支持）
        if image.mode in ('RGBA', 'LA'):
            image = image.convert('RGB')

        # 保存为 PDF
        image.save(output_pdf, 'PDF', resolution=100.0)
        print(f'图片已成功转换为 PDF: {output_pdf}')
    except Exception as e:
        print(f'转换失败: {e}')


async def download_file(file_url: str, local_path: str):
    """
    下载 Word 文件到本地
    :param word_url: Word 文件 URL
    :param local_path: 保存的本地路径
    """
    try:
        response = requests.get(file_url, stream=True)
        response.raise_for_status()
        with open(local_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f'文件已成功下载: {local_path}')
    except Exception as e:
        print(f'文件下载失败: {e}')


async def word_to_pdf_with_libreoffice(word_path: str, output_dir: str):
    """
    使用 LibreOffice CLI 将 Word 转换为 PDF
    :param word_path: 本地 Word 文件路径
    :param output_dir: 输出 PDF 文件目录
    """
    try:
        subprocess.run(
            ["soffice", "--headless", "--convert-to", "pdf", "--outdir", output_dir, word_path],
            check=True
        )
        print(f"Word 转 PDF 成功，文件保存在目录: {output_dir}")
    except Exception as e:
        print(f"Word 转 PDF 失败: {e}")
        raise


async def convert_word_to_pdf(word_url: str, output_pdf: str):
    """
    从 URL 下载 Word 文件并转换为 PDF
    :param word_url: Word 文件 URL
    :param output_pdf: 输出 PDF 文件路径
    """
    local_word_path = 'temp_word_file.docx'
    await download_file(word_url, local_word_path)
    await word_to_pdf_with_libreoffice(local_word_path, os.path.dirname(output_pdf))
    # 重命名转换后的 PDF 文件
    converted_pdf = local_word_path.replace('.docx', '.pdf')
    os.rename(converted_pdf, output_pdf)
    # 删除临时 Word 文件
    if os.path.exists(local_word_path):
        os.remove(local_word_path)

def merge_pdfs(pdf_files: list[str], output_pdf: str):
    """
    合并多个 PDF 文件
    :param pdf_files: 待合并的 PDF 文件路径列表
    :param output_pdf: 合并后的输出 PDF 文件路径
    """
    merger = PdfMerger()
    for pdf in pdf_files:
        merger.append(pdf)
    merger.write(output_pdf)
    merger.close()
    print(f'所有 PDF 文件已成功合并为: {output_pdf}')