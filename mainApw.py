from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource
from datetime import datetime
import pandas as pd

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testApw.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    time = db.Column(db.String(15))


class PostSchema(ma.Schema):
    class Meta:
        fields = ("id", "user_id", "time")


post_schema = PostSchema()

posts_schema = PostSchema(many=True)


class PostListResource(Resource):

    def get(self):
        posts = Post.query.all()

        return posts_schema.dump(posts)

    def post(self):
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        new_post = Post(
            user_id=request.json['from'],
            time=dt_string
        )

        data = request.json['data']
        df = pd.DataFrame(data)

        writer = pd.ExcelWriter('testApw.xlsx', engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1')
        writer.save()

        db.session.add(new_post)
        db.session.commit()
        return post_schema.dump(new_post)


class PostResource(Resource):
    def get(self, post_id):
        post = Post.query.get_or_404(post_id)
        return post_schema.dump(post)

    def patch(self, post_id):

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        post = Post.query.get_or_404(post_id)

        if 'from' in request.json:
            post.user_id = request.json['from']
            post.time = dt_string

        db.session.commit()
        return post_schema.dump(post)

    def delete(self, post_id):
        post = Post.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()
        return '', 204


api.add_resource(PostListResource, '/posts')
api.add_resource(PostResource, '/post/<int:post_id>')


if __name__ == '__main__':
    app.run(debug=True)
