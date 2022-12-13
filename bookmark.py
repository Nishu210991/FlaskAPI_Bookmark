from flask import Blueprint, request, jsonify
import validators
from src.constants.http_status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_201_CREATED, HTTP_200_OK
from src.database import Bookmark,db
from flask_jwt_extended import get_jwt_identity, jwt_required

bookmark = Blueprint("bookmark", __name__, url_prefix="/api/v1/bookmark")


@bookmark.route("/", methods=['POST', 'GET'])
@jwt_required()
def handle_bookmark():
    current_user = get_jwt_identity()
    
    if request.method == 'POST':

        body = request.get_json().get('body', '')
        url = request.get_json().get('url', '')
        print(url, "kjkjkk")

        if not validators.url(url):
            return jsonify({"Error":"Url is not valid"}), HTTP_400_BAD_REQUEST

        if Bookmark.query.filter_by(url=url).first():
            return jsonify({
                "Error": 'URL is already exists'
            }), HTTP_409_CONFLICT

        bookmark = Bookmark(url=url, body=body, user_id=current_user)

        db.session.add(bookmark)
        db.session.commit()

        return jsonify({
            "id": bookmark.id,
            "url":bookmark.url,
            "short_url":bookmark.short_url,
            "visitor":bookmark.visits,
            "body":bookmark.body,
            "created_at":bookmark.created_at,
            "update_at":bookmark.updated_at

        }),HTTP_201_CREATED

    else:

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5,type=int)

        bookmark = Bookmark.query.filter_by(user_id=current_user).paginate(per_page=per_page)
        
        data = []

        for bookmark in bookmark:

            data.append({
            "id": bookmark.id,
            "url":bookmark.url,
            "short_url":bookmark.short_url,
            "visitor":bookmark.visits,
            "body":bookmark.body,
            "created_at":bookmark.created_at,
            "update_at":bookmark.updated_at
        })

        return jsonify({"data":data}), HTTP_200_OK