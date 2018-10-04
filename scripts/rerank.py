from blog.models import Post

def run():
    for post in Post.with_votes.all():
        post.set_rank()