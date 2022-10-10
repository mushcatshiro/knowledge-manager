function modal(title) {
    $.ajax({
        url: "/api/detail",
        dataType: "json",
        success: function(result) {
        var element = document.getElementById("modal-content")
        if (element) { element.innerHTML = "" }
        $("#modal-content").append(result.text)
        new bootstrap.Modal(document.getElementById('modal')).show()
        }
    })
}

function search(text) {
    if (text == "help") {
    var node = document.createElement("div")
    node.className = "form-text"
    node.id = "help-text"
    var textnode = document.createTextNode(
        `prefixes: blog|recommend;
        special keywords: surprise|reading list|change image
        `)
    node.appendChild(textnode)
    document.getElementById("searchhelp").appendChild(node)
    }
    else if (text == "reading list") {
    $.ajax({
        url: "/api/mock",
        dataType: "json",
        success: function(result) {
        $("#table").append("<ul>")
        for (let i=0; i < result.length; i++) {
            $("#table").append(
            `
            <li>
                <b>${result[i].title}</b>
                ${result[i].desc}
                <a href="${result[i].url}">link</a>
                <a onclick="modal()" data-bs-toggle="modal" data-bs-target="#exampleModal">modal</a>
            </li>
            `
            )
        }
        $("#table").append("</ul>")
        }
    })
    }
    else if (text == "suprise") {
    $.ajax({
        url: "/api/mock",
        dataType: "json",
        success: function(result) {
        for (let i=0; i < result.length; i++) {
            $("#table").append(
            `
            <h3>${result[i].title}</h3>
            <p>${result[i].desc}</p>
            <a href="${result[i].url}">link</a>
            `
            )
        }
        }
    })
    }
    else if (text.startsWith("change image")) {
    var probetxt = text.split(":")[1]
    if (!probetxt) { probetxt = "random" }
    $.ajax({
        url: "/api/image",
        method: "POST",
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({
        probe: probetxt
        }),
        success: function(result) {
        $("#coverimg").attr("src", result.url)
        }
    })
    }
    else if (text.startsWith("blog")) {}
    else if (text.startsWith("recommend")) {}
}

document.body.addEventListener("keydown", function(e) {
    if (e.key == "Escape") {
        var element = $("#table")[0]
        if (element) { element.innerHTML = "" }
        var element = $("#modal")[0]
        console.log(element)
        if (element) { element.innerHTML = "" }
        var element = $("#searchbox")
        element.innerText = ""
        var element = $("#help-text")
        if (element) { element.remove() }
    }
})