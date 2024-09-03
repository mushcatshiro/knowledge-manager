from blog.search import Document

import pytest


@pytest.fixture
def fake_document_list():
    doc_list = []
    title_list = [
        "Photolithography",
        "Photography",
        "Light sensor",
        "Image",
    ]
    content_list = [
        "A process used in the manufacturing of integrated circuits. It involves using light to transfer pattern onto a silicon wafer.",
        "Photography creating images by recording light, either electronically by means of an image sensor, or chemically by means of a light-sensitive material such as photographic film",
        "A light sensor is a photoelectric device that converts light energy (photons) detected to electrical energy (electrons)",
        "An image is a visual representation. An image can be two-dimensional, such as a drawing, painting, or photograph, or three-dimensional, such as a carving or sculpture.",
    ]
    for idx, doc in enumerate(zip(title_list, content_list)):
        doc_list.append(Document(idx, doc[0], doc[1]))
    return doc_list
