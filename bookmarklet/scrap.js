javascript:(() => {
    const input = prompt("xpath:");
    const content = document.evaluate(input, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
    console.log(out);

    const requestURL = "http://127.0.0.1:8080/api/bookmark";
    const pageURL = window.location.href;
    let token = "";

    const url = new URL(requestURL);
    const searchParams = url.searchParams;
    searchParams.set("url", pageURL);
    searchParams.set("content", content);
    searchParams.set("token", token);

    window.location.href = url;
})();
