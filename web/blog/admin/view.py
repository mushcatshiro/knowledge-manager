from urllib.parse import urlsplit, urlunsplit

from flask import (
    Blueprint,
    request,
    render_template,
    session,
    redirect,
    url_for,
    current_app,
)

from blog import CustomException
from blog.auth import verify_token


admin = Blueprint("admin", __name__)


@admin.before_request
def before_request_handler():
    """
    TODO
    ---
    - check token expiry
    """
    if request.path == url_for("admin.login"):
        pass
    elif not session.get("token"):
        l_url = urlsplit(url_for("admin.login"))
        c_url = urlsplit(request.url)
        current_url = request.url

        if (not l_url.scheme or l_url.scheme == c_url.scheme) and (
            not l_url.netloc or l_url.netloc == c_url.netloc
        ):
            current_url = urlunsplit(("", "", c_url.path, c_url.query, ""))
        return redirect(url_for("admin.login", next=current_url))
    elif not verify_token(session.get("token")):
        session.pop("token")
        raise CustomException(401, "Invalid token", "Unauthorized access")


@admin.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if verify_token(request.form["token"]):
            session["token"] = request.form["token"]
            next_url = request.args.get("next")
            if next_url is None or not next_url.startswith("/"):
                next_url = url_for("main.index")
            return redirect(next_url)
        raise CustomException(401, "Invalid token", "Unauthorized access")
    return render_template("login.html")


@admin.route("/logout", methods=["GET"])
def logout():
    session.pop("token")
    return redirect(url_for("main.index"))


@admin.route("/bookmarkletjs", methods=["GET"])
def bookmarkletjs():
    script = [
        "javascript:(() => {",
        f'const requestURL = "{current_app.config["SITE_BASE_URL"]}/api/bookmark";',
        "const pageTitle = document.title;",
        "const pageURL = window.location.href;",
        'let metaImage = "";',
        'let metaDescription = "";',
        f'let token = "{session.get("token")}";',
        "function getMetaValue(propName) {",
        'const x = document.getElementsByTagName("meta");',
        "for (let i = 0; i < x.length; i++) {",
        "const y = x[i];",
        "let metaName;",
        "if (y.attributes.property !== undefined) {",
        "metaName = y.attributes.property.value;}",
        "if (y.attributes.name !== undefined) {",
        "metaName = y.attributes.name.value;}",
        "if (metaName === undefined) {continue;}",
        "if (metaName === propName) {return y.attributes.content.value;}}",
        "return undefined;}",
        '{let desc = getMetaValue("og:description");',
        "if (desc !== undefined) {metaDescription = desc;}",
        'else {desc = getMetaValue("description");',
        "if (desc !== undefined) {metaDescription = desc;}}}",
        '{const img = getMetaValue("og:image");',
        "if (img !== undefined) {metaImage = img;}}",
        'console.log("BOOKMARKET PRESSED:", pageTitle, pageURL, metaDescription, metaImage);',
        "const url = new URL(requestURL);",
        "const searchParams = url.searchParams;",
        'searchParams.set("title", pageTitle);',
        'searchParams.set("url", pageURL);',
        'searchParams.set("desc", metaDescription);',
        'searchParams.set("img", metaImage);',
        'searchParams.set("token", token);',
        "window.location.href = url; })();",
    ]
    return render_template(
        "bookmarkletjs.html",
        script="".join(script)
        if request.args.get("min")
        else "\n".join(script),  # BUG test needed
    )
