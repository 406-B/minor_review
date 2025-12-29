import pytest


pytestmark = [pytest.mark.integration]


@pytest.mark.django_db
class TestPostViewsBranches:
    def test_create_post_audit_rejected_returns_400(self, auth_client, monkeypatch):
        # create_post view calls utils.audit.audit_content twice (content + title)
        from utils import audit as audit_module

        responses = [(False, "bad content"), (True, "")]

        def _fake_audit_content(*args, **kwargs):
            return responses.pop(0)

        monkeypatch.setattr(audit_module, "audit_content", _fake_audit_content)

        resp = auth_client.post(
            "/api/v1/posts/create/",
            {
                "subject": "测试标题",
                "content": "测试内容",
                "images": [],
            },
            format="json",
        )
        assert resp.status_code == 400
        body = resp.json()
        assert body["code"] == 400
        assert "发布失败" in body["message"]

    def test_post_detail_not_found_returns_404(self, api_client):
        resp = api_client.get("/api/v1/posts/999999/")
        assert resp.status_code == 404
        body = resp.json()
        assert body["code"] == 404

    def test_forum_home_invalid_sort_by_returns_400(self, api_client):
        resp = api_client.get("/api/v1/forum/home/?sort_by=unknown")
        assert resp.status_code == 400
        body = resp.json()
        assert body["code"] == 400

    def test_dish_posts_dish_not_found_returns_404(self, api_client):
        resp = api_client.get("/api/v1/dishes/999999/posts/")
        assert resp.status_code == 404
        body = resp.json()
        assert body["code"] == 404

    def test_create_comment_audit_rejected_returns_400(self, auth_client, monkeypatch):
        # Build a post via API so the request chain is consistent.
        from utils import audit as audit_module

        responses = [(True, ""), (True, "")]

        def _fake_audit_content_ok(*args, **kwargs):
            return responses.pop(0)

        monkeypatch.setattr(audit_module, "audit_content", _fake_audit_content_ok)
        create_post = auth_client.post(
            "/api/v1/posts/create/",
            {
                "subject": "帖子标题",
                "content": "帖子内容",
                "images": [],
            },
            format="json",
        )
        assert create_post.status_code in (200, 201)

        post_id = create_post.json()["data"]["id"]

        # create_comment view calls utils.audit.audit_content once
        monkeypatch.setattr(audit_module, "audit_content", lambda *a, **k: (False, "bad"))
        resp = auth_client.post(
            "/api/v1/comments/create/",
            {
                "post": post_id,
                "content": "评论内容",
                "images": [],
            },
            format="json",
        )
        assert resp.status_code == 400
        body = resp.json()
        assert body["code"] == 400
        assert "内容审核未通过" in body["message"]
