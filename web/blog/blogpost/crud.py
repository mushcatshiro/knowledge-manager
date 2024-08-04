import logging

from sqlalchemy import select, func, update

from blog.core.crud import CRUDBase


logger = logging.getLogger(__name__)


class BlogPostCrud(CRUDBase):
    # TODO exceptions to be replaced by `CustomException`?
    def create_blog_post(self, session, query, **kwargs):
        # check if title exist
        instance = (
            session.execute(
                select(self.model).where(self.model.title == kwargs.get("title"))
            )
            .scalars()
            .first()
        )
        if instance and kwargs.get("version") is None:
            raise FileExistsError(
                "Blog post title already exists, version must be specified"
            )
        instance = self.model(title=kwargs.get("title"))
        if kwargs.get("version"):
            instance.version = kwargs.get("version")
        if kwargs.get("private"):
            instance.private = kwargs.get("private")
        session.add(instance)
        session.commit()
        return instance.to_json()

    def read_blog_post(self, session, query, title, logged_in=False):
        instance = (
            session.execute(
                select(self.model)
                .where(
                    self.model.title == title,
                    self.model.private <= int(logged_in),
                )
                .order_by(self.model.version.desc())
            )
            .scalars()
            .first()
        )
        if not instance:
            raise ValueError("Blog post not found")
        if instance.deleted == 1:
            raise FileNotFoundError("Blog post deleted")

        return instance.to_json()

    def read_blog_post_list(self, session, query, logged_in=False):
        """
        **TODO
        - pagination
        """
        instances = (
            session.execute(
                select(self.model.title, func.max(self.model.version))
                .where(self.model.private <= int(logged_in))
                .group_by(self.model.title)
                .having(self.model.deleted == 0)
            )
            .mappings()
            .all()
        )
        return instances

    def update_blog_post(self, session, query, title):
        # get current version
        instance = self.read_blog_post(session, query, title, logged_in=True)
        instance = self.create_blog_post(
            session, query, version=instance["version"] + 1, title=title
        )
        return instance

    def delete_blog_post(self, session, query, title: str):
        try:
            instance = self.read_blog_post(session, query, title, logged_in=True)
        except FileNotFoundError:
            # already deleted
            return True
        except ValueError:
            raise ValueError("Blog post not found")
        except Exception as e:
            logger.error(e)
            return False
        else:
            session.execute(
                update(self.model).where(self.model.title == title).values(deleted=1)
            )
            session.commit()
        return True
