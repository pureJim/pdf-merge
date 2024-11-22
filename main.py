from fastapi import FastAPI

app = FastAPI()

img_list: list[str] = ['https://assets.pureglobal.cn/builder/demo-file/1.png','https://assets.pureglobal.cn/builder/demo-file/2.png','https://assets.pureglobal.cn/builder/demo-file/9.png']
pdf_list: list[str] = ['https://assets.pureglobal.cn/builder/demo-file/Res.No_.152%20Regulacion%20E%20100-21%20red%20(1).pdf']
word_list: list[str] = ['https://assets.pureglobal.cn/builder/demo-file/PROYECTO%20DE%20REGISTRO.docx','https://assets.pureglobal.cn/builder/demo-file/demo.docx']

@app.get("/")
async def read_root():
    res = combine_pdf()

    return {"Hello": "World"}


async def combine_pdf():
    convert_img_to_pdf('https://assets.pureglobal.cn/builder/demo-file/1.png')
    convert_word_to_pdf()
    pass

async def convert_img_to_pdf(img_url: str):
    pass

async def convert_word_to_pdf():
    pass