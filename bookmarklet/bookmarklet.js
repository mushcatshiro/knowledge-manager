javascript:(() => {
    const requestURL = "http://127.0.0.1:8080/api/bookmark";

    const pageTitle = document.title;
    const pageURL = window.location.href;
    let metaImage = "";
    let metaDescription = "";

    function getMetaValue(propName) {
        const x = document.getElementsByTagName("meta");
        for (let i = 0; i < x.length; i++) {
            const y = x[i];

            let metaName;
            if (y.attributes.property !== undefined) {
                metaName = y.attributes.property.value;
            }
            if (y.attributes.name !== undefined) {
                metaName = y.attributes.name.value;
            }

            if (metaName === undefined) {
                continue;
            }

            if (metaName === propName) {
                return y.attributes.content.value;
            }
        }
        return undefined;
    }

    {
        let desc = getMetaValue("og:description");
        if (desc !== undefined) {
            metaDescription = desc;
        } else {
            desc = getMetaValue("description");
            if (desc !== undefined) {
                metaDescription = desc;
            }
        }
    }

    {
        const img = getMetaValue("og:image");
        if (img !== undefined) {
            metaImage = img;
        }
    }

    console.log("BOOKMARKET PRESSED:", pageTitle, pageURL, metaDescription, metaImage);

    const url = new URL(requestURL);
    const searchParams = url.searchParams;
    searchParams.set("title", pageTitle);
    searchParams.set("url", pageURL);
    searchParams.set("description", metaDescription);
    searchParams.set("image", metaImage);
    searchParams.set("nexturl", pageURL);
    searchParams.set("token", token);

    window.location.href = url;
})();