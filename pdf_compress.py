import drive_functions
import os
from dotenv import load_dotenv
from pylovepdf.ilovepdf import ILovePdf

load_dotenv()

def compress_pdf(filename,compression=None):
    ilovepdf = ILovePdf(os.environ.get('ILP_PUBLIC_KEY'), verify_ssl=True)
    task = ilovepdf.new_task('compress')
    task.add_file(filename)
    task.set_output_folder('compressed')
    task.execute()
    task.download()
    task.delete_current_task()


if __name__ == '__main__':
    compress_pdf('DOCUMENTOS_0001.pdf')