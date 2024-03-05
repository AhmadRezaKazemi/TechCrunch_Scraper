import argparse
import peewee
# from scraper import scrap_url
# from output_manager import generate_output
from database_manager import DatabaseManager
from html_downloader import HtmlDownloader
import local_settings
from datetime import datetime


database_manager = DatabaseManager(
    database_name=local_settings.DATABASE['name'],
    user=local_settings.DATABASE['user'],
    password=local_settings.DATABASE['password'],
    host=local_settings.DATABASE['host'],
    port=local_settings.DATABASE['port'],
)


class BaseModel(peewee.Model):
    created_at = peewee.DateTimeField(default=datetime.now, verbose_name='Created At')
    # updated_at = peewee.DateTimeField(default=datetime.now, verbose_name='Updated At')

    class Meta:
        database = database_manager.db

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = datetime.now()
        # self.updated_at = datetime.now()
        return super().save(*args, **kwargs)


class Category(BaseModel):
    title = peewee.CharField(max_length=255, null=False, verbose_name='Title')


class Author(BaseModel):
    name = peewee.CharField(max_length=255, null=False, verbose_name='Name')


class Post(BaseModel):
    title = peewee.CharField(max_length=255, null=False, verbose_name='Title')
    post_url = peewee.CharField(max_length=255, null=False, verbose_name='Post URL')
    author = peewee.ForeignKeyField(model=Author, null=False, verbose_name='Author')


class PostCategories(BaseModel):
    category = peewee.ForeignKeyField(model=Category, null=False, verbose_name='Category')
    post = peewee.ForeignKeyField(model=Post, null=False, verbose_name='Post')


class Tag(BaseModel):
    title = peewee.CharField(max_length=255, null=False, verbose_name='Title')


class PostTags(BaseModel):
    tag = peewee.ForeignKeyField(model=Tag, null=False, verbose_name='Tag')
    post = peewee.ForeignKeyField(model=Post, null=False, verbose_name='Post')


class KeyWord(BaseModel):
    title = peewee.CharField(max_length=255, null=False, verbose_name='Title')


class KeyWordResult(BaseModel):
    keyword = peewee.ForeignKeyField(model=KeyWord, null=False, verbose_name='Keyword')


class KeyWordResultItem(BaseModel):
    KeyWordResult = peewee.ForeignKeyField(model=KeyWordResult, null=False, verbose_name='Keyword Result')
    post = peewee.ForeignKeyField(model=Post, null=False, verbose_name='Post')


def arg_parser():
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="libgen scrapper",
        epilog="Thanks for using"
    )

    parser.add_argument("-k", "--keywords", help="Search keywords", type=str, required=True)
    parser.add_argument("-d", "--detailed", help="Detailed scrap results", action="store_true")
    parser.add_argument(
        "-c",
        "--column",
        help="Search column. options: title, author, series, "
             "publisher, year, identifier(isbn), language, md5, tags",
        type=str,
        default="def"
    )
    parser.add_argument("-m", "--mask_option", help="search for close words too", action="store_true")
    parser.add_argument("-o", "--output", help="give report from scrapped files", action="store_true")
    parser.add_argument(
        "-of",
        "--output_format",
        help="choose output format, default is json",
        default='json',
    )
    parser.add_argument("-db", "--download_book", help="download book instead of saving url", action="store_true")
    parser.add_argument("-to", "--timeout", help="webpage request timeout, default: 3", default=3, type=int)

    return parser.parse_args()


def init_database():
    try:
        database_manager.create_tables(
            models=[
                Category,
                Author,
                Post,
                PostCategories,
                Tag,
                PostTags,
                KeyWord,
                KeyWordResult,
                KeyWordResultItem,
            ])
        return True
    except Exception as e:
        print(f'could not create tables. error:', e)
        return False
    #
    # categories = [1, 2, 3, 4, 5]
    #
    # for i in categories:
    #     Category.create(title=i)

    # for i in range(100):
    #     rand_int = random.randint(1000, 9999)
        # Post.create(title=f'Post{rand_int}', description=f'Post{rand_int} description',
        #             category=random.choice(categories))

    # posts = Post.select().where(Post.category == 1)
    # for post in posts:
    #     post.title += "Daneskar"
    #     # post.save() -> saves the change
    #     # post.delete_instance() -> deletes row
    #     print(post.title)


if __name__ == "__main__":
    if not init_database():
        exit()

    # url = 'https://techcrunch.com/2024/03/04/anthropic-claims-its-new-models-beat-gpt-4/'
    #
    # print(HtmlDownloader(url).download_page())

    # cli_args = arg_parser()
