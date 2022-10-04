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

    var xhr = new XMLHttpRequest();
    xhr.open("POST", requestURL, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(
        JSON.stringify({
            title: pageTitle,
            url: pageURL,
            desc: metaDescription,
            img: metaImage,
        })
    );
    if (xhr.status >= 400) {
        alert("error saving "+pageURL)
    }
    const _url = new URL(pageURL);

    window.location.href = _url;
})();