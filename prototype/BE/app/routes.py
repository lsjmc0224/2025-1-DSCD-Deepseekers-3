from flask import Blueprint, jsonify, request
from flask_restx import Api, Resource, Namespace
# from .models import db  # 모델이 있으면 불러와서 사용

api = Namespace("ping", description="Ping related operations")

@api.route("")
class Ping(Resource):
    @api.doc(description="간단한 핑 테스트")
    @api.response(200, "성공적으로 pong을 반환합니다.")
    def get(self):
        return {"message": "pong"}