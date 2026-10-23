import json
import pytest
from pydantic import BaseModel

from django.test import RequestFactory
from django.views import View
from django.http import JsonResponse
from django.core.files.uploadedfile import SimpleUploadedFile

from utils.decorators import with_payload


class PayloadTestModel(BaseModel):
    title: str
    description: str


class PayloadTestView(View):
    @with_payload
    def post(self, request, payload: PayloadTestModel):
        return JsonResponse({"title": payload.title, "desc": payload.description})


class WithoutPayloadView(View):
    def post(self, request, init: PayloadTestModel):
        return JsonResponse({"title": init.title, "desc": init.description})


class WithoutPydanticModelView(View):
    def post(self, request, payload):
        return JsonResponse({"title": payload.title, "desc": payload.description})


@pytest.mark.django_db
class TestWithPayloadDecorator:
    @pytest.fixture
    def file(self):
        return SimpleUploadedFile("test.txt", b"dummy content")

    def test_valid_data(self, file):
        rf = RequestFactory()
        data = {
            "title": "Hello",
            "description": "World",
            "file": file
        }
        request = rf.post("/fake-url/", data)

        view = PayloadTestView.as_view()
        response = view(request)

        assert response.status_code == 200
        resp_data = json.loads(response.content)
        assert resp_data == {"title": "Hello", "desc": "World"}

    def test_invalid_data(self, file):
        rf = RequestFactory()
        data = {"title": "Only title", "file": file}
        request = rf.post("/fake-url/", data)

        view = PayloadTestView.as_view()
        response = view(request)

        assert response.status_code == 400
        resp_data = json.loads(response.content)
        print(resp_data)
        assert "errors" in resp_data

    def test_file_in_payload(self, file):
        rf = RequestFactory()
        data = {"title": "Hello", "description": "World"}
        request = rf.post("/fake-url/", data, FILES={"file": file})

        view = PayloadTestView.as_view()
        response = view(request)

        assert response.status_code == 200
        resp_data = json.loads(response.content)
        assert resp_data["title"] == "Hello"

    def test_without_payload(self, file):
        with pytest.raises(ValueError):
            with_payload(WithoutPayloadView().post)

    def test_not_pydantic_payload(self, file):
        with pytest.raises(ValueError):
            with_payload(WithoutPydanticModelView().post)
