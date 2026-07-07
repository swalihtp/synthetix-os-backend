def extract_txt_text(attachment):

    file_bytes = attachment["data"]

    return file_bytes.decode("utf-8")